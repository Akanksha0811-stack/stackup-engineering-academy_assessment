# Pillar 3 — Big Data Processing

> **Time allocation:** ~4 hours  
> **Starter files:** `starter_files/spark_starter.py`, `starter_files/kafka_starter.py`, `starter_files/airflow_dag_starter.py`

---

## Context

The project management platform now emits a continuous stream of user events. As the system scales to hundreds of projects and thousands of daily events, the batch ETL approach from Pillar 2 is no longer sufficient for real-time visibility. You will build the big data layer: distributed processing with Spark, real-time streaming with Kafka, and orchestrated scheduling with Airflow.

---

## Task 3.1 — Apache Spark: Process the events dataset at scale

**File:** `starter_files/spark_starter.py`

**Dataset:** `datasets/events_stream/events_2025_01.jsonl`

The events file contains platform activity logs — status changes, logins, escalations, task completions, document uploads, budget updates, and meeting schedules. New monthly files will be added as `events_2025_02.jsonl`, etc. Your pipeline must handle all files dynamically.

---

**3.1a — Load and parse**

- Define the schema explicitly using `StructType` — do not use `inferSchema`
- Load all `.jsonl` files from the `events_stream/` directory using a wildcard path
- The `payload` field is a nested JSON object — decide how to represent it in Spark (MapType or flatten individual fields)
- Parse the `timestamp` field correctly as `TimestampType`

---

**3.1b — Validate and clean**

- Drop rows where `event_id` or `user_id` is null
- Remove duplicate `event_id` values (keep first occurrence by timestamp)
- Add `event_date` (date only) and `event_hour` (hour of day) derived columns
- Log row counts before and after each drop operation

---

**3.1c — Produce four aggregated output tables**

Implement each aggregation function in the starter file. The outputs will feed the executive analytics dashboard.

**Table 1: project_activity_summary**

For each project, compute:
- `total_events` — all events linked to this project
- `escalation_count` — events where `event_type = 'escalation_raised'`
- `task_completions` — events where `event_type = 'task_completed'`
- `last_event_timestamp` — most recent event timestamp
- `unique_users` — count of distinct users who triggered events on this project

Exclude events where `project_id` is null (login events are not project-linked).

---

**Table 2: user_activity_summary**

For each user, compute:
- `login_count` — events where `event_type = 'login'`
- `actions_taken` — all events excluding logins
- `projects_touched` — distinct projects the user acted on (excluding nulls)
- `last_active` — most recent timestamp

---

**Table 3: escalation_log**

Join `escalation_raised` and `escalation_resolved` events to build a full escalation log per project.

- Extract `severity` from the payload of raised events
- Extract `resolved_by` from the payload of resolved events
- Compute `resolution_time_hours` = difference between raised and resolved timestamps
- Set `resolved = True/False` based on whether a matching resolution exists
- A project can only have one open escalation at a time for this dataset

---

**Table 4: daily_event_volume**

- Group by `event_date` and `event_type`
- Count events per group
- Sort by `event_date` ascending, `event_count` descending

---

**3.1d — Write outputs as Parquet**

- Write each table to `outputs/spark/<table_name>/`
- Use overwrite mode
- Partition `daily_event_volume` by `event_date`
- Print row count after each write

---

## Task 3.2 — Apache Kafka: Real-time streaming pipeline

**File:** `starter_files/kafka_starter.py`

**Prerequisites:** Kafka must be running. Start with: `docker-compose up -d`

---

**3.2a — Setup**

Create two Kafka topics:
- `presight.project.events` — all platform events (3 partitions)
- `presight.escalations.critical` — filtered critical escalations (1 partition)

---

**3.2b — Producer**

Build a Kafka producer that:
- Reads events from `datasets/events_stream/events_2025_01.jsonl` one line at a time
- Adds a `produced_at` timestamp to each message
- Sends to `presight.project.events` using `event_type` as the message key
- Sleeps 0.5 seconds between messages to simulate a live stream
- Logs each message sent

---

**3.2c — Consumer**

Build a Kafka consumer that:
- Subscribes to `presight.project.events`
- Logs the `event_id`, `event_type`, and `project_id` for each consumed message
- Accumulates a count of messages per `event_type`

---

**3.2d — Escalation forwarding**

Within the consumer:
- If `event_type = 'escalation_raised'` AND `payload.severity = 'Critical'`
  → Produce the full message to `presight.escalations.critical`
- Log how many messages were forwarded

---

**3.2e — Summary output**

After consuming, write `outputs/kafka/summary.json` containing:
- Run timestamp
- Source topic
- Count per event_type
- Count of critical escalations forwarded

---

## Task 3.3 — Apache Airflow: Schedule and orchestrate the ETL pipeline

**File:** `starter_files/airflow_dag_starter.py`

**Prerequisites:** Airflow must be running. Start with: `docker-compose up -d`

---

**3.3a — DAG configuration**

Define the DAG with:
- `dag_id`: `presight_etl_pipeline`
- Schedule: daily at **06:00 UAE time** (Asia/Dubai timezone, UTC+4 — convert to UTC cron)
- `catchup = False`
- `max_active_runs = 1`
- `retries = 2`, `retry_delay = 5 minutes`
- Tags: `['presight', 'etl', 'assessment']`

---

**3.3b — Tasks**

Implement each task as a `PythonOperator` calling the relevant function from `etl_starter.py`:

| Task ID | Function called | Notes |
|---|---|---|
| `extract_projects` | `load_projects()` | Push row count to XCom |
| `extract_employees` | `load_employees()` | Push row count to XCom |
| `extract_transactions` | `load_transactions()` | Push row count to XCom |
| `validate_data_quality` | `run_data_quality_checks()` | **DQ gate** — raise exception on failure |
| `transform_and_enrich` | `transform_projects()`, `clean_employees()`, `enrich_transactions()` | Push clean row counts |
| `load_to_output` | `write_outputs()` | Log file paths written |
| `generate_pipeline_report` | Custom | Pull all XCom values, write report |

---

**3.3c — Dependencies**

Wire the DAG as follows:
```
start
  ├── extract_projects ──┐
  ├── extract_employees ─┼──→ validate_data_quality → transform_and_enrich → load_to_output → generate_pipeline_report → end
  └── extract_transactions ┘
```

The three extract tasks run in **parallel**. All must complete before the DQ gate runs.

---

**3.3d — DQ gate behaviour**

The `validate_data_quality` task must:
- Reload and check all three datasets
- Raise a `ValueError` with a descriptive message if any critical check fails (e.g. completeness < 80% on a key column)
- If the gate fails, Airflow must mark the DAG run as **Failed** and downstream tasks must not execute

---

**3.3e — Pipeline report via XCom**

The final task `generate_pipeline_report` must:
- Pull XCom values from all upstream tasks
- Write `outputs/pipeline_report_{execution_date}.txt` with raw vs clean row counts, DQ results, and files written

---

## Completion checklist

- [ ] Spark pipeline runs end to end with `spark-submit`
- [ ] Four Parquet output tables written to `outputs/spark/`
- [ ] `daily_event_volume` is partitioned by `event_date`
- [ ] Kafka topics created and messages produced/consumed successfully
- [ ] Critical escalations forwarded to `presight.escalations.critical`
- [ ] `outputs/kafka/summary.json` written
- [ ] Airflow DAG appears in UI with correct schedule and dependencies
- [ ] DQ gate correctly blocks downstream tasks on failure
- [ ] Pipeline report written via XCom on successful run
