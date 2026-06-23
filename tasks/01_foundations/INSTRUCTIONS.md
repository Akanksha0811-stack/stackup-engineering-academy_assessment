# Pillar 1 — Foundations

> **Time allocation:** ~3 hours  
> **Starter file:** `starter_files/etl_starter.py` (Tasks 1.1 & 1.3), `starter_files/data_model_starter.sql` (Task 1.2)

---

## Context

You are joining the data engineering team at **Presight**, a technology company running a project management platform used by government and enterprise clients. The team has received three raw data exports from the operational systems:

| File | Description |
|---|---|
| `datasets/projects.csv` | Project records including status, budget, and dates |
| `datasets/employees.csv` | Employee records — contains known data quality issues |
| `datasets/transactions.json` | Financial transactions linked to projects |

Your foundations tasks establish the clean, reliable data layer that every downstream task depends on.

---

## Task 1.1 — Python: Clean and transform projects.csv

**File:** `starter_files/etl_starter.py` → functions `load_projects()` and `transform_projects()`

**What to do:**

1. Load `datasets/projects.csv` into a Pandas DataFrame with correct data types
2. Parse `start_date` and `end_date` as proper date columns (not strings)
3. Add three derived columns:
   - `budget_variance` = `actual_cost` minus `budget`
   - `is_over_budget` = True if `actual_cost` exceeds `budget`, False otherwise. Handle nulls.
   - `duration_days` = number of days between `start_date` and `end_date` where both are available
4. Standardise `status` values (strip whitespace, consistent casing)
5. Map statuses to a simplified `status_category`: Active, Closed, or Pending
6. Replace null `budget` or `actual_cost` values with 0

**Expected output:** A cleaned DataFrame written to `outputs/projects_clean.csv`

**Assessment focus:**
- Correct dtype handling
- Sensible handling of nulls in derived columns
- Readable, commented code

---

## Task 1.2 — Data Modelling: Design a star schema

**File:** `starter_files/data_model_starter.sql` → Section 1

**What to do:**

Design a star schema for the Presight project analytics warehouse. Write valid SQL DDL (`CREATE TABLE` statements) for the following:

| Table | Type | Notes |
|---|---|---|
| `dim_date` | Dimension | Full date dimension — year, quarter, month, month_name, week, day, is_weekend |
| `dim_project` | Dimension | From projects.csv |
| `dim_employee` | Dimension | From employees.csv |
| `dim_vendor` | Dimension | Derived from transactions.json vendor fields |
| `bridge_employee_project` | Bridge | Many-to-many between employees and projects |
| `fact_transactions` | Fact | Central fact table with FK to all dimensions |

**Constraints:**
- Use surrogate integer keys on all dimension tables
- Preserve original source IDs (e.g. `project_id`, `employee_id`) as natural keys
- `fact_transactions` must include: `transaction_key`, `project_key`, `employee_key`, `vendor_key`, `date_key`, `amount`, `category`, `payment_status`
- Add a comment before each table explaining your design decision

**Bonus:** Add SCD Type 2 columns to `dim_employee` to track salary history (`valid_from`, `valid_to`, `is_current`)

**Assessment focus:**
- Correct use of star schema principles (no normalisation in dimensions)
- Correct FK relationships
- Justification of decisions in comments
- Bridge table correctly resolves the many-to-many

---

## Task 1.3 — Data Quality: Find and fix issues in employees.csv

**File:** `starter_files/etl_starter.py` → function `clean_employees()`

**What to do:**

There are **at least five data quality issues** embedded in `datasets/employees.csv`. Find them all.

For each issue:
1. Write a comment in the code describing what you found (the column, the problem, and how many rows are affected)
2. Apply a fix
3. Log how many rows were affected using Python's logging module

**Hints — categories of issues to look for:**
- Missing values in columns that should always be populated
- Invalid date formats or impossible date values
- Numeric values outside any reasonable business range
- Logical inconsistencies between columns
- Records whose state contradicts another column value

**Expected output:** A cleaned DataFrame written to `outputs/employees_clean.csv` with a log of all issues found

**Assessment focus:**
- Thoroughness — did you find all issues?
- Quality of documentation (comments explaining each issue)
- Fix approach — are decisions defensible?

---

## Completion checklist

- [ ] `outputs/projects_clean.csv` written with correct dtypes and derived columns
- [ ] `outputs/employees_clean.csv` written with all issues documented and fixed
- [ ] `data_model_starter.sql` Section 1 contains valid DDL for all 6 tables
- [ ] Each table has a comment explaining design decisions
- [ ] At least 5 data quality issues identified and fixed in employees.csv
- [ ] All fixes are logged with row counts affected
