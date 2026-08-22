"""
=============================================================
StackUp Engineering Academy — Data Engineering Assessment
Starter File: spark_starter.py
Pillar: Big Data Processing — Task 3.1
=============================================================

SCENARIO
--------
The events_stream/ folder contains a growing log of platform events emitted
by the project management system (status changes, logins, escalations,
document uploads, meetings, budget updates, task completions).

New event files will be added monthly (events_2025_01.jsonl, events_2025_02.jsonl, ...).
Your pipeline must process ALL files in the folder, not just one.

Your job is to use PySpark to process the events at scale and produce four
aggregated output tables that feed the executive analytics dashboard.

TASKS
-----
  Task 3.1a → Load and parse all JSONL files from events_stream/
  Task 3.1b → Clean and validate the event schema
  Task 3.1c → Produce four aggregated output DataFrames (see below)
  Task 3.1d → Write outputs in Parquet format to outputs/spark/

OUTPUT TABLES REQUIRED
----------------------
  1. project_activity_summary
       project_id | total_events | escalation_count | task_completions |
       last_event_timestamp | unique_users

  2. user_activity_summary
       user_id | login_count | actions_taken | projects_touched | last_active

  3. escalation_log
       event_id | project_id | raised_by | raised_at | severity |
       resolved | resolved_by | resolved_at | resolution_time_hours

  4. daily_event_volume
       event_date | event_type | event_count

HOW TO RUN
----------
  spark-submit starter_files/spark_starter.py

  Or in a notebook / local Spark session:
  exec(open('starter_files/spark_starter.py').read())
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import Window
from pyspark.sql.types import (
    StructType, StructField, StringType, TimestampType, MapType
)
import os

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
EVENTS_DIR = os.path.join(BASE_DIR, "datasets", "events_stream")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "spark")


# ==============================================================================
# STEP 1 — Initialise Spark
# ==============================================================================

def get_spark_session() -> SparkSession:
    """
    Create and return a local SparkSession.
    """
    spark = (
        SparkSession.builder
        .appName("PresightEventsProcessing")
        .master("local[*]")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark


# ==============================================================================
# STEP 2 — Load events
# ==============================================================================

def load_events(spark: SparkSession, events_dir: str):
    """
    Load all JSONL files from the events_stream directory.
    """
    schema = StructType([
        StructField("event_id", StringType(), True),
        StructField("event_type", StringType(), True),
        StructField("project_id", StringType(), True),
        StructField("user_id", StringType(), True),
        StructField("timestamp", StringType(), True),   # parsed to TimestampType below
        StructField("payload", MapType(StringType(), StringType()), True),
    ])

        # On Windows without winutils.exe, Spark's own wildcard path-globbing
    # crashes (it needs Hadoop's native Windows file-access layer). We
    # sidestep this by expanding the wildcard with Python's glob module
    # instead, then handing Spark an explicit list of file paths — this
    # avoids Spark ever needing to call Hadoop's native listStatus/glob.
    import glob
    file_list = sorted(glob.glob(os.path.join(events_dir, "events_*.jsonl")))
    print(f"Found {len(file_list)} event files to load")

    df = spark.read.schema(schema).json(file_list)
    df = df.withColumn("timestamp", F.to_timestamp("timestamp"))

    row_count = df.count()
    print(f"Loaded {row_count} events total")

    return df

# ==============================================================================
# STEP 3 — Validate and clean
# ==============================================================================

def validate_events(df):
    """
    Validate and clean the raw events DataFrame.
    """
    initial_count = df.count()
    print(f"Initial event count: {initial_count}")

    # Drop rows with null event_id or user_id
    df = df.filter(F.col("event_id").isNotNull() & F.col("user_id").isNotNull())
    after_null_drop = df.count()
    print(f"Dropped {initial_count - after_null_drop} rows with null event_id/user_id")

    # Remove duplicate event_ids, keeping the first occurrence by timestamp
    from pyspark.sql import Window
    window_spec = Window.partitionBy("event_id").orderBy("timestamp")
    df = df.withColumn("row_num", F.row_number().over(window_spec)) \
           .filter(F.col("row_num") == 1) \
           .drop("row_num")
    after_dedup = df.count()
    print(f"Dropped {after_null_drop - after_dedup} duplicate event_id rows")

    # Derived columns
    df = df.withColumn("event_date", F.to_date("timestamp"))
    df = df.withColumn("event_hour", F.hour("timestamp"))
    df = df.withColumn("event_month", F.date_format("timestamp", "yyyy-MM"))

    print(f"Final clean event count: {after_dedup}")
    return df


# ==============================================================================
# STEP 4 — Aggregations
# ==============================================================================

def project_activity_summary(df):
    """
    Produce a per-project activity summary.
    """
    filtered = df.filter(F.col("project_id").isNotNull())

    result = filtered.groupBy("project_id").agg(
        F.count("*").alias("total_events"),
        F.sum(F.when(F.col("event_type") == "escalation_raised", 1).otherwise(0)).alias("escalation_count"),
        F.sum(F.when(F.col("event_type") == "task_completed", 1).otherwise(0)).alias("task_completions"),
        F.sum(F.when(F.col("event_type") == "document_uploaded", 1).otherwise(0)).alias("document_uploads"),
        F.max("timestamp").alias("last_event_timestamp"),
        F.countDistinct("user_id").alias("unique_users"),
        F.countDistinct("event_type").alias("unique_event_types"),
    ).orderBy(F.desc("total_events"))

    return result


def user_activity_summary(df):
    """
    Produce a per-user activity summary.
    """
    result = df.groupBy("user_id").agg(
        F.sum(F.when(F.col("event_type") == "login", 1).otherwise(0)).alias("login_count"),
        F.sum(F.when(F.col("event_type") == "logout", 1).otherwise(0)).alias("logout_count"),
        F.sum(F.when(~F.col("event_type").isin("login", "logout"), 1).otherwise(0)).alias("actions_taken"),
        F.countDistinct(F.when(F.col("project_id").isNotNull(), F.col("project_id"))).alias("projects_touched"),
        F.min("timestamp").alias("first_active"),
        F.max("timestamp").alias("last_active"),
        F.countDistinct("event_date").alias("active_days"),
    ).orderBy(F.desc("actions_taken"))

    return result


def escalation_log(df):
    """
    Build a complete escalation log by joining escalation_raised
    and escalation_resolved events.
    """
    raised = df.filter(F.col("event_type") == "escalation_raised").select(
        F.col("event_id"),
        F.col("project_id"),
        F.col("user_id").alias("raised_by"),
        F.col("timestamp").alias("raised_at"),
        F.col("payload").getItem("severity").alias("severity"),
    )

    resolved = df.filter(F.col("event_type") == "escalation_resolved").select(
        F.col("project_id").alias("r_project_id"),
        F.col("timestamp").alias("resolved_at"),
        F.col("payload").getItem("resolved_by").alias("resolved_by"),
    )

    # Left join: every raised escalation appears once. If a matching
    # resolved event exists for the same project (with resolved_at AFTER
    # raised_at), we pick it up; otherwise resolved_at/resolved_by stay null.
    joined = raised.join(
        resolved,
        (raised.project_id == resolved.r_project_id) & (resolved.resolved_at >= raised.raised_at),
        how="left"
    )

    # A project can have multiple raise/resolve cycles over the year, so
    # keep only the earliest resolution that comes after each raise event
    # (closest matching resolution), not every possible pairing.
    window_spec = Window.partitionBy("event_id").orderBy(F.col("resolved_at").asc_nulls_last())
    joined = joined.withColumn("rn", F.row_number().over(window_spec)) \
                    .filter(F.col("rn") == 1) \
                    .drop("rn", "r_project_id")

    result = joined.withColumn(
        "resolution_time_hours",
        F.when(
            F.col("resolved_at").isNotNull(),
            (F.col("resolved_at").cast("long") - F.col("raised_at").cast("long")) / 3600.0
        )
    ).withColumn(
        "resolved",
        F.col("resolved_at").isNotNull()
    )

    return result.select(
        "event_id", "project_id", "raised_by", "raised_at", "severity",
        "resolved", "resolved_by", "resolved_at", "resolution_time_hours"
    )


def daily_event_volume(df):
    """
    Produce a daily event volume breakdown by event type, with a
    cumulative running total per event type.
    """
    daily = df.groupBy("event_date", "event_type").agg(
        F.count("*").alias("event_count")
    )

    # Cumulative count per event_type, ordered chronologically by event_date
    cumulative_window = Window.partitionBy("event_type").orderBy("event_date") \
                               .rowsBetween(Window.unboundedPreceding, Window.currentRow)
    daily = daily.withColumn(
        "cumulative_count",
        F.sum("event_count").over(cumulative_window)
    )

    result = daily.orderBy(F.asc("event_date"), F.desc("event_count"))
    return result

def peak_usage_analysis(df):
    """
    For each event_date x event_hour combination, compute total events,
    unique users active, and distinct event types touched — identifies
    peak usage windows for capacity planning.
    """
    result = df.groupBy("event_date", "event_hour").agg(
        F.count("*").alias("total_events"),
        F.countDistinct("user_id").alias("unique_users"),
        F.countDistinct("event_type").alias("event_types_per_hour"),
    ).orderBy(F.desc("total_events")).limit(20)

    return result


# ==============================================================================
# STEP 5 — Write outputs
# ==============================================================================

def write_parquet(df, name: str, output_dir: str, partition_by: str = None, coalesce_to_one: bool = False):
    """
    Write a DataFrame to Parquet.

    NOTE: Uses pandas.to_parquet() rather than Spark's native writer. On
    Windows without winutils.exe (Hadoop's native filesystem binding),
    Spark's own Parquet writer fails when it tries to set file permissions
    via Hadoop's local filesystem layer. Converting to pandas first avoids
    that code path entirely (pandas writes files directly via pyarrow, no
    Hadoop dependency) while still producing standard, readable Parquet
    output. For partitioned tables, we partition manually by writing one
    file per partition value into partition_by=value/ subfolders, mimicking
    Spark/Hive's partitioned-directory convention.
    """
    import shutil
    path = os.path.join(output_dir, name)
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)

    pdf = df.toPandas()
    row_count = len(pdf)

    if partition_by:
        for value, group in pdf.groupby(partition_by):
            part_dir = os.path.join(path, f"{partition_by}={value}")
            os.makedirs(part_dir, exist_ok=True)
            group.to_parquet(os.path.join(part_dir, "part-0000.parquet"), index=False)
        print(f"Wrote {row_count} rows to {path} (partitioned by {partition_by})")
    else:
        pdf.to_parquet(os.path.join(path, "part-0000.parquet"), index=False)
        print(f"Wrote {row_count} rows to {path}")

# ==============================================================================
# PIPELINE ENTRY POINT
# ==============================================================================

def run_pipeline():
    import time
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    pipeline_start = time.time()
    timings = {}

    spark = get_spark_session()

    t0 = time.time()
    raw = load_events(spark, EVENTS_DIR)
    clean = validate_events(raw)
    timings["load_and_validate"] = time.time() - t0

    total_rows = clean.count()

    t0 = time.time()
    proj_summary = project_activity_summary(clean)
    write_parquet(proj_summary, "project_activity_summary", OUTPUT_DIR)
    timings["project_activity_summary"] = time.time() - t0

    t0 = time.time()
    user_summary = user_activity_summary(clean)
    write_parquet(user_summary, "user_activity_summary", OUTPUT_DIR)
    timings["user_activity_summary"] = time.time() - t0

    t0 = time.time()
    esc_log = escalation_log(clean)
    write_parquet(esc_log, "escalation_log", OUTPUT_DIR, partition_by="severity")
    timings["escalation_log"] = time.time() - t0

    t0 = time.time()
    daily_vol = daily_event_volume(clean)
    write_parquet(daily_vol, "daily_event_volume", OUTPUT_DIR, partition_by="event_date")
    timings["daily_event_volume"] = time.time() - t0

    t0 = time.time()
    peak_usage = peak_usage_analysis(clean)
    write_parquet(peak_usage, "peak_usage_analysis", OUTPUT_DIR)
    timings["peak_usage_analysis"] = time.time() - t0

    total_elapsed = time.time() - pipeline_start

    print("\n" + "=" * 60)
    print("PERFORMANCE BASELINE")
    print("=" * 60)
    print(f"Total rows processed: {total_rows}")
    print(f"Total execution time: {total_elapsed:.2f} seconds")
    print(f"Events processed per second: {total_rows / total_elapsed:.1f}")
    print("\nPer-aggregation timing:")
    for name, elapsed in timings.items():
        print(f"  {name}: {elapsed:.2f}s")
    print("=" * 60)

    spark.stop()
    print("\nSpark pipeline complete.")


if __name__ == "__main__":
    run_pipeline()