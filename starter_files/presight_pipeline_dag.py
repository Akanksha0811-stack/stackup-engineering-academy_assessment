"""
Presight — Task 3.3: Airflow Orchestration DAG
Author: Akanksha Shreya
"""
from datetime import datetime, timedelta
import os
import json
import glob

from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator

DATASETS_DIR = "/opt/airflow/datasets"
OUTPUTS_DIR  = "/opt/airflow/outputs"
EVENTS_DIR   = os.path.join(DATASETS_DIR, "events_stream")

default_args = {
    "owner": "akanksha",
    "retries": 2,
    "retry_delay": timedelta(seconds=30),
}


def check_files_exist(**context):
    files = sorted(glob.glob(os.path.join(EVENTS_DIR, "events_*.jsonl")))
    if len(files) != 12:
        raise FileNotFoundError(f"Expected 12 event files, found {len(files)}: {files}")
    context["ti"].xcom_push(key="file_count", value=len(files))
    print(f"Found {len(files)} event files: OK")


def run_data_quality_checks(**context):
    import pandas as pd
    files = sorted(glob.glob(os.path.join(EVENTS_DIR, "events_*.jsonl")))
    frames = [pd.read_json(f, lines=True) for f in files]
    df = pd.concat(frames, ignore_index=True)

    total_rows = len(df)
    null_event_id = int(df["event_id"].isna().sum())
    null_user_id = int(df["user_id"].isna().sum())
    duplicate_event_ids = int(df["event_id"].duplicated().sum())

    null_rate = (null_event_id + null_user_id) / (total_rows * 2)
    dup_rate = duplicate_event_ids / total_rows

    checks = {
        "total_rows": int(total_rows),
        "null_event_id": null_event_id,
        "null_user_id": null_user_id,
        "duplicate_event_ids": duplicate_event_ids,
        "null_rate": round(float(null_rate), 4),
        "duplicate_rate": round(float(dup_rate), 4),
    }
    passed = bool(null_rate <= 0.01 and dup_rate <= 0.01)
    checks["passed"] = passed

    print(f"DQ check results: {checks}")
    context["ti"].xcom_push(key="dq_results", value=checks)
    return checks


def branch_on_dq(**context):
    dq_results = context["ti"].xcom_pull(key="dq_results", task_ids="run_data_quality_checks")
    if dq_results["passed"]:
        return "submit_spark_job"
    return "dq_gate_failed"


def submit_spark_job(**context):
    expected_tables = [
        "project_activity_summary", "user_activity_summary",
        "escalation_log", "daily_event_volume", "peak_usage_analysis",
    ]
    spark_output_dir = os.path.join(OUTPUTS_DIR, "spark")
    results = {}
    for table in expected_tables:
        path = os.path.join(spark_output_dir, table)
        exists = bool(os.path.isdir(path))
        results[table] = exists
        print(f"Checking {table}: {'found' if exists else 'MISSING'}")

    all_present = all(results.values())
    context["ti"].xcom_push(key="spark_job_status", value=results)
    if not all_present:
        raise RuntimeError(f"Spark output verification failed: {results}")
    print("Spark job outputs verified.")


def produce_critical_escalations(**context):
    from kafka import KafkaProducer
    producer = KafkaProducer(
        bootstrap_servers="kafka:29092",
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    files = sorted(glob.glob(os.path.join(EVENTS_DIR, "events_*.jsonl")))
    sent = 0
    for filepath in files:
        with open(filepath) as f:
            for line in f:
                event = json.loads(line)
                if (event.get("event_type") == "escalation_raised"
                        and event.get("payload", {}).get("severity") == "Critical"):
                    producer.send("presight.escalations.critical", value=event)
                    sent += 1
    producer.flush()
    producer.close()
    context["ti"].xcom_push(key="critical_events_sent", value=sent)
    print(f"Republished {sent} critical escalation events to Kafka.")


def generate_report(**context):
    ti = context["ti"]
    dq_results = ti.xcom_pull(key="dq_results", task_ids="run_data_quality_checks")
    spark_status = ti.xcom_pull(key="spark_job_status", task_ids="submit_spark_job")
    critical_sent = ti.xcom_pull(key="critical_events_sent", task_ids="produce_critical_escalations")

    report = {
        "run_timestamp": datetime.now().isoformat(),
        "dq_results": dq_results,
        "spark_tables_verified": spark_status,
        "critical_escalations_republished": critical_sent,
    }

    report_path = os.path.join(OUTPUTS_DIR, "airflow_run_report.json")
    try:
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, default=str)
    except PermissionError:
        fallback_path = "/opt/airflow/logs/airflow_run_report.json"
        with open(fallback_path, "w") as f:
            json.dump(report, f, indent=2, default=str)
        report_path = fallback_path
        print(f"Primary path not writable, wrote to fallback: {fallback_path}")

    print(f"Report written to {report_path}")
    print(json.dumps(report, indent=2, default=str))


def notify_failure(**context):
    dq_results = context["ti"].xcom_pull(key="dq_results", task_ids="run_data_quality_checks")
    print(f"PIPELINE FAILED — DQ gate rejected the data: {dq_results}")


with DAG(
    dag_id="presight_events_pipeline",
    default_args=default_args,
    description="Presight events processing pipeline with DQ gate and Kafka routing",
    schedule_interval=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["presight", "assessment"],
) as dag:

    t_check_files = PythonOperator(task_id="check_files_exist", python_callable=check_files_exist)
    t_dq_checks = PythonOperator(task_id="run_data_quality_checks", python_callable=run_data_quality_checks)
    t_branch = BranchPythonOperator(task_id="branch_on_dq", python_callable=branch_on_dq)
    t_spark = PythonOperator(task_id="submit_spark_job", python_callable=submit_spark_job)
    t_kafka = PythonOperator(task_id="produce_critical_escalations", python_callable=produce_critical_escalations)
    t_report = PythonOperator(task_id="generate_report", python_callable=generate_report, trigger_rule="none_failed_min_one_success")
    t_dq_failed = PythonOperator(task_id="dq_gate_failed", python_callable=notify_failure)

    t_check_files >> t_dq_checks >> t_branch
    t_branch >> t_spark >> t_kafka >> t_report
    t_branch >> t_dq_failed >> t_report
