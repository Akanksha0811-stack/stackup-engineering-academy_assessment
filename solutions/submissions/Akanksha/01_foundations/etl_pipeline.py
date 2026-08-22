"""
=============================================================
StackUp Engineering Academy — Data Engineering Assessment
Starter File: etl_starter.py
Pillars: Foundations (Tasks 1.1, 1.3) | SQL & Viz (Task 2.2) | Infrastructure (Task 4.3)
=============================================================

SCENARIO
--------
You are a Data Engineer at Presight. The project management team has provided
three raw data extracts from their operational systems:
  - datasets/projects.csv        → project records
  - datasets/employees.csv       → employee/HR records
  - datasets/transactions.json   → financial transactions per project

Your job is to clean, transform, and load this data into a structured format
ready for analytics and reporting.

TASKS COVERED BY THIS FILE
---------------------------
  Task 1.1  → Clean and transform projects.csv and employees.csv using Pandas
  Task 1.3  → Identify and fix data quality issues in employees.csv
  Task 2.2  → Build a full ETL pipeline ingesting all three sources
  Task 4.3  → Implement a data quality check framework (min. 3 checks)

HOW TO RUN
----------
  python starter_files/etl_starter.py

OUTPUT
------
  Cleaned CSVs and a summary report written to: outputs/
"""

import pandas as pd
import numpy as np
import json
import os
import logging
from datetime import datetime

# ── Logging setup ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
DATA_DIR = os.path.join(BASE_DIR, "datasets")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ==============================================================================
# TASK 1.1 — Load and transform projects.csv
# ==============================================================================

def load_projects(filepath: str) -> pd.DataFrame:
    """
    Load projects.csv into a DataFrame.

    TODO:
      - Load the CSV
      - Parse date columns correctly (start_date, end_date)
      - Add a derived column: budget_variance = actual_cost - budget
      - Add a derived column: is_over_budget (True/False)
      - Add a derived column: duration_days (end_date - start_date, where available)
      - Return the cleaned DataFrame
    """
    logger.info("Loading projects data...")

    df = pd.read_csv(filepath, parse_dates=["start_date", "end_date"])
    df['budget_variance'] = df['actual_cost'] - df['budget']
    df['is_over_budget'] = df['actual_cost'] > df['budget']
    df['duration_days'] = (df['end_date'] - df['start_date']).dt.days

    return df


def transform_projects(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply business logic transformations to the projects DataFrame.

    TODO:
      - Standardise the 'status' column values (strip whitespace, title case)
      - Replace any missing budget or actual_cost values with 0
      - Add a 'status_category' column: group statuses into
        ['Active', 'Closed', 'Pending'] using the mapping below:
          Active  → In Progress
          Closed  → Completed
          Pending → Not Started, On Hold
      - Return the transformed DataFrame
    """
    logger.info("Transforming projects data...")

    # Status mapping
    status_map = {
        "In Progress": "Active",
        "Completed": "Closed",
        "Not Started": "Pending",
        "On Hold": "Pending"
    }

    df['status'] = df['status'].str.strip().str.title()
    df[['budget', 'actual_cost']] = df[['budget', 'actual_cost']].fillna(0)
    df['status_category'] = df['status'].map(status_map)
    df['budget_utilisation_pct'] = np.where(
        df['budget'] == 0,
        0,
        (df['actual_cost'] / df['budget']) * 100
    )
    conditions = [
        (df['priority'] == 'Critical') | (df['is_over_budget'] == True),
        (df['priority'] == 'High') | (df['budget_utilisation_pct'] > 90)
    ]
    choices = ['High', 'Medium']
    df['risk_level'] = np.select(conditions, choices, default='Low')

    return df


# ==============================================================================
# TASK 1.3 — Data quality issues in employees.csv
# ==============================================================================

def load_employees(filepath: str) -> pd.DataFrame:
    """
    Load employees.csv and identify data quality issues.

    TODO:
      - Load the CSV
      - Log a summary: total rows, null counts per column
      - Return the raw DataFrame (do not fix issues here — fix in clean_employees)
    """
    logger.info("Loading employees data...")

    df = pd.read_csv(filepath)
    logger.info(f"Loaded {len(df)} employee records")
    logger.info(f"Null counts per column:\n{df.isna().sum()}")

    return df


def clean_employees(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fix at least THREE data quality issues found in employees.csv.

    Known issues to find and fix (there may be more — find them all):
      1. Missing values in key columns
      2. Invalid date values
      3. Implausible numeric values (salary, years_experience)
      4. Records that should not be active

    TODO:
      - Document each issue you find in a comment before fixing it
      - Apply your fixes
      - Log a summary of changes made (rows affected per issue)
      - Return the cleaned DataFrame

    HINT: Look carefully at every column. Some issues are subtle.
    """
    logger.info("Cleaning employees data...")

    # Issue 1: Missing emails — 10 rows have null email values.
    # Fix: replace with a placeholder so downstream joins/reports don't break on NaN.
    missing_email = df['email'].isna()
    logger.info(f"Missing emails: {missing_email.sum()}")
    df.loc[missing_email, 'email'] = 'unknown@presight.ai'

    # Issue 2: Invalid hire_date values — 8 rows contain sentinel garbage
    # ("-999" or "99999-01-01") instead of a real date.
    # Fix: convert to proper datetime, coercing invalid values to NaT (null)
    # rather than guessing a fake date.
    df['hire_date'] = pd.to_datetime(df['hire_date'], errors='coerce')
    invalid_dates = df['hire_date'].isna()
    logger.info(f"Invalid hire_date values converted to null: {invalid_dates.sum()}")

    # Issue 3: Invalid years_experience — 5 rows have a value of -1,
    # which is impossible (negative work experience). This looks like a
    # sentinel for "unknown" rather than a real measurement.
    # Fix: convert to null rather than guessing a fabricated value.
    invalid_experience = df['years_experience'] < 0
    logger.info(f"Invalid years_experience values converted to null: {invalid_experience.sum()}")
    df.loc[invalid_experience, 'years_experience'] = np.nan

    # Issue 4: Salary/level mismatch — 3 Junior-level employees have salaries
    # far outside the normal Junior range (detected via IQR outlier bounds
    # per level, not a fixed threshold, since "normal" salary varies by level).
    # Fix: flag rather than overwrite — the anomaly is suspicious but we have
    # no reliable source of truth to correct it to, so silently changing the
    # value risks losing real information.
    def iqr_outlier_mask(group):
        q1, q3 = group.quantile([0.25, 0.75])
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        return (group < lower) | (group > upper)

    df['salary_anomaly'] = df.groupby('level')['salary'].transform(iqr_outlier_mask)
    logger.info(f"Salary anomalies flagged (outside IQR bounds for their level): {df['salary_anomaly'].sum()}")# Add more as needed...

    return df


# ==============================================================================
# TASK 2.2 — Full ETL pipeline
# ==============================================================================

def load_transactions(filepath: str) -> pd.DataFrame:
    """
    Load transactions.json into a DataFrame.

    TODO:
      - Load the JSON file
      - Flatten into a tabular structure
      - Parse transaction_date as a date type
      - Handle null values appropriately (document your decisions)
      - Return the DataFrame
    """
    logger.info("Loading transactions data...")

    logger.info("Loading transactions data...")

    df = pd.read_json(filepath)
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])

    # Null handling decisions (documented per task requirement):
    # - amount: 740 nulls -> fill with 0.0. A transaction with no recorded
    #   amount is treated as zero-value rather than dropped, so it still
    #   appears in counts/audits but doesn't distort sum/average calculations.
    # - approved_by: 2,444 nulls -> left as null (NOT fabricated). A missing
    #   approver is a real business state ("not yet approved"), not missing
    #   data to be guessed. enrich_transactions() will derive an is_approved
    #   boolean flag from this for easy filtering downstream.
    df['amount'] = df['amount'].fillna(0.0)

    logger.info(f"Loaded {len(df)} transaction records")
    logger.info(f"Null amounts filled with 0.0: {(df['amount'] == 0.0).sum()}")
    logger.info(f"Transactions with no approver: {df['approved_by'].isna().sum()}")

    return df


def enrich_transactions(
    transactions: pd.DataFrame,
    projects: pd.DataFrame,
    employees: pd.DataFrame
) -> pd.DataFrame:
    """
    Enrich transactions with project and employee context.

    TODO:
      - Join project_name and department from projects onto transactions via project_id
      - Join approver full_name from employees onto transactions via approved_by = employee_id
      - Add a column: is_approved (True if approved_by is not null, else False)
      - Add a column: amount_aed — same as amount but cast to float, nulls → 0.0
      - Return the enriched DataFrame
    """
    logger.info("Enriching transactions...")

        # Join project context (project_name, department) via project_id.
    # Using how='left' + explicit `on=` so every transaction is preserved
    # even if a project_id somehow doesn't match (shouldn't happen, but
    # left join is the safe default for enrichment rather than dropping data).
    transactions = transactions.merge(
        projects[['project_id', 'project_name', 'department']],
        on='project_id',
        how='left'
    )

    # Join approver's name via approved_by -> employee_id. Only current
    # employee records are relevant here (an approver's identity doesn't
    # change even if their salary/role has SCD2 history), so this uses the
    # employees_clean.csv current-state table, not the SCD2 dim_employee.
    transactions = transactions.merge(
        employees[['employee_id', 'full_name']].rename(
            columns={'employee_id': 'approved_by', 'full_name': 'approver_name'}
        ),
        on='approved_by',
        how='left'
    )

    transactions['is_approved'] = transactions['approved_by'].notna()
    transactions['amount_aed'] = transactions['amount'].astype(float).fillna(0.0)
    transactions['transaction_year_month'] = transactions['transaction_date'].dt.to_period('M').astype(str)

    logger.info(f"Enriched {len(transactions)} transactions")
    logger.info(f"Approved transactions: {transactions['is_approved'].sum()}")
    logger.info(f"Unapproved transactions: {(~transactions['is_approved']).sum()}")

    return transactions


def write_outputs(projects: pd.DataFrame, employees: pd.DataFrame, transactions: pd.DataFrame, elapsed_seconds: float = None):
    """
    ...
    """
    logger.info("Writing outputs...")

    projects.to_csv(os.path.join(OUTPUT_DIR, "projects_clean.csv"), index=False)
    employees.to_csv(os.path.join(OUTPUT_DIR, "employees_clean.csv"), index=False)
    transactions.to_csv(os.path.join(OUTPUT_DIR, "transactions_clean.csv"), index=False)
    logger.info(f"Wrote projects_clean.csv ({len(projects)} rows)")
    logger.info(f"Wrote employees_clean.csv ({len(employees)} rows)")
    logger.info(f"Wrote transactions_clean.csv ({len(transactions)} rows)")

    summary_path = os.path.join(OUTPUT_DIR, "pipeline_summary.txt")
    with open(summary_path, "w") as f:
        f.write(f"Pipeline run timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Pipeline execution time: {elapsed_seconds:.2f} seconds\n" if elapsed_seconds else "")
        f.write("\n--- Row counts ---\n")
        f.write(f"projects_clean.csv:     {len(projects)} rows\n")
        f.write(f"employees_clean.csv:    {len(employees)} rows\n")
        f.write(f"transactions_clean.csv: {len(transactions)} rows\n")
        f.write("\n--- Data quality decisions ---\n")
        f.write("- projects.budget/actual_cost nulls filled with 0\n")
        f.write("- employees.email nulls (10) filled with placeholder 'unknown@presight.ai'\n")
        f.write("- employees.hire_date invalid values (8: '-999'/'99999-01-01') converted to null\n")
        f.write("- employees.years_experience invalid values (5: -1 sentinel) converted to null\n")
        f.write("- employees.salary anomalies (3 Junior-level outliers) flagged via salary_anomaly column, not overwritten\n")
        f.write("- transactions.amount nulls (740) filled with 0.0\n")
        f.write("- transactions.approved_by nulls (2,444) left as null; is_approved boolean derived instead\n")
    logger.info(f"Wrote pipeline_summary.txt")


# ==============================================================================
# TASK 4.3 — Data quality check framework
# ==============================================================================

def run_data_quality_checks(df: pd.DataFrame, dataset_name: str) -> dict:
    """
    Run a suite of data quality checks on a DataFrame.

    Implement AT LEAST the following checks:
      1. Completeness   — what % of values are non-null per column?
      2. Uniqueness     — are primary key columns unique?
      3. Validity       — do numeric columns fall within expected ranges?
      4. Consistency    — do date columns follow logical ordering (start < end)?
      5. Referential integrity — do foreign keys exist in the referenced table?
                                 (implement this in the pipeline function below)

    TODO:
      - Run each check
      - Return a dict with check name → result (pass/fail + details)
      - Log a warning for any failed check
    """
    logger.info(f"Running data quality checks on: {dataset_name}")

    results = {}

    # Check 1: Completeness
    # YOUR CODE HERE

    # Check 2: Uniqueness
    # YOUR CODE HERE

    # Check 3: Validity
    # YOUR CODE HERE

    # Check 4: Consistency
    # YOUR CODE HERE

    return results


# ==============================================================================
# PIPELINE ENTRY POINT
# ==============================================================================

def run_pipeline():
    """
    Orchestrates the full ETL pipeline end to end.
    Call each function in the correct order.
    """
    import time
    start_time = time.time()

    logger.info("=" * 60)
    logger.info("Starting ETL pipeline")
    logger.info("=" * 60)

    # Step 1: Load raw data
    raw_projects      = load_projects(os.path.join(DATA_DIR, "projects.csv"))
    raw_employees     = load_employees(os.path.join(DATA_DIR, "employees.csv"))
    raw_transactions  = load_transactions(os.path.join(DATA_DIR, "transactions.json"))

    # Step 2: Clean
    clean_projects    = transform_projects(raw_projects)
    clean_emp         = clean_employees(raw_employees)

    # Step 3: Enrich
    enriched_txn      = enrich_transactions(raw_transactions, clean_projects, clean_emp)

    # Step 4: Data quality checks
    dq_projects       = run_data_quality_checks(clean_projects, "projects")
    dq_employees      = run_data_quality_checks(clean_emp, "employees")
    dq_transactions   = run_data_quality_checks(enriched_txn, "transactions")

    logger.info("DQ Results — Projects:     %s", dq_projects)
    logger.info("DQ Results — Employees:    %s", dq_employees)
    logger.info("DQ Results — Transactions: %s", dq_transactions)

    # Step 5: Write outputs
    elapsed = time.time() - start_time
    write_outputs(clean_projects, clean_emp, enriched_txn, elapsed_seconds=elapsed)

    logger.info("Pipeline complete in %.2f seconds. Outputs written to: %s", elapsed, OUTPUT_DIR)

    logger.info("Pipeline complete. Outputs written to: %s", OUTPUT_DIR)


if __name__ == "__main__":
    run_pipeline()
