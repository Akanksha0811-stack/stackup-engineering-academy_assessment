# Pillar 2 — SQL & Data Visualization

> **Time allocation:** ~3.5 hours  
> **Starter files:** `starter_files/etl_starter.py` (Task 2.2), `starter_files/data_model_starter.sql` (Tasks 2.1 & 2.3)

---

## Context

With clean data from Pillar 1, you now build the analytics layer. The Finance and Operations teams need reliable SQL queries for their dashboards, and the Head of Data has asked for a demonstration Power BI report showing project spend performance.

---

## Task 2.1 — SQL: Answer five business questions

**File:** `starter_files/data_model_starter.sql` → Section 3

First, load your cleaned data from Pillar 1 into your database using Section 2 of the SQL file.

Then write a SQL query for each of the five questions below. Each query must:
- Run without errors
- Include a comment explaining your approach
- Return results in the exact column format specified

---

**Q1 — Budget performance by department**

Which departments have spent more than 90% of their total allocated budget across all projects? Include departments that are over budget.

Required columns: `department`, `total_budget`, `total_actual_cost`, `spend_percentage`, `over_budget`  
Order by: `spend_percentage` descending

---

**Q2 — Project manager workload**

Which project managers are currently managing more than one active project (status = In Progress)? A manager overseeing too many active projects is a delivery risk.

Required columns: `full_name`, `email`, `active_project_count`, `combined_budget_responsibility`  
Order by: `active_project_count` descending

---

**Q3 — Vendor concentration risk**

Identify vendors who account for more than 30% of total transaction spend across all projects. High vendor concentration is a financial and operational risk.

Required columns: `vendor_name`, `total_spend`, `percentage_of_total_spend`, `risk_flag` (set to 'HIGH' if above 30%, else 'NORMAL')  
Order by: `percentage_of_total_spend` descending

---

**Q4 — Projects with open issues**

Find all projects that have at least one transaction in 'Pending' or 'Disputed' status. These projects need finance team attention.

Required columns: `project_id`, `project_name`, `department`, `project_status`, `open_transaction_count`, `open_transaction_value`  
Order by: `open_transaction_value` descending

---

**Q5 — Monthly spend trend with running total**

Show total transaction spend per month, per category, for all available data. Include a running total that accumulates within each category across months — this shows how category spend compounds over time.

Required columns: `year_month` (formatted as YYYY-MM), `category`, `monthly_spend`, `running_total`  
Order by: `category`, `year_month` ascending

---

## Task 2.2 — ETL Pipeline: Ingest, transform, and load all three sources

**File:** `starter_files/etl_starter.py` → functions `load_transactions()`, `enrich_transactions()`, `write_outputs()`

Complete the full ETL pipeline that ingests and joins all three data sources.

**What to do:**

1. **Load** `datasets/transactions.json` into a Pandas DataFrame
   - Flatten the JSON into a tabular structure
   - Parse `transaction_date` as a date type
   - Decide how to handle null `amount` and null `approved_by` values — document your decision

2. **Enrich** transactions by joining project and employee context:
   - Add `project_name` and `department` from the projects dataset (via `project_id`)
   - Add approver `full_name` from the employees dataset (via `approved_by` = `employee_id`)
   - Add `is_approved` = True if `approved_by` is not null, else False
   - Add `amount_aed` = `amount` cast to float, nulls set to 0.0

3. **Write outputs:**
   - Write all three cleaned DataFrames to `outputs/` as CSVs
   - Write `outputs/pipeline_summary.txt` containing:
     - Run timestamp
     - Row counts (before and after cleaning) for each dataset
     - List of data quality decisions made

**Assessment focus:**
- Correct handling of JSON → tabular conversion
- Clean join logic with no row duplication
- Null handling decisions are documented
- Pipeline summary is human-readable

---

## Task 2.3 — Query Optimisation

**File:** `starter_files/data_model_starter.sql` → Section 4

A slow query used by the Finance dashboard is provided in Section 4 of the SQL starter file.

**What to do:**

1. Run `EXPLAIN` (or `EXPLAIN ANALYZE`) on the original query and paste the output as a SQL comment
2. Identify the performance bottleneck — explain it in plain English
3. Rewrite the query to improve performance. You may:
   - Restructure the query
   - Use CTEs
   - Change implicit joins to explicit joins
   - Refactor the correlated subquery
4. Write a comment explaining:
   - What was wrong with the original
   - What you changed and why
   - What indexes you would create in production and why

**Note:** If running on a small test dataset, the performance difference may not be measurable. In that case, describe what you would observe at scale and why.

---

## Task 2.4 — Dashboard design

**Tools:** Power BI Desktop, or a hand-drawn mockup submitted as a PDF/image

Design or build a one-page executive dashboard for project spend performance.

**Requirements — the dashboard must show:**

| Visual | Description |
|---|---|
| KPI cards | Total budget allocated, total actual spend, % over budget projects |
| Bar chart | Actual spend vs budget by department |
| Line chart | Monthly transaction spend trend (from Q5 above) |
| Table | Top 5 projects by budget variance (most over/under budget) |
| Filter | Slicer by region and project status |

**If building in Power BI:**
- Export as `.pbix` and save to `outputs/`
- Add your name and date to the report title

**If submitting a mockup:**
- Use any tool (Figma, PowerPoint, hand-drawn)
- Export as PDF to `outputs/dashboard_mockup.pdf`
- Annotate each visual with what data it shows and why you chose that chart type

---

## Completion checklist

- [ ] Five SQL queries written and executable in Section 3
- [ ] Each query has a comment explaining the approach
- [ ] ETL pipeline completes without errors
- [ ] `outputs/transactions_clean.csv` written
- [ ] `outputs/pipeline_summary.txt` written with row counts and decisions
- [ ] Slow query analysed with EXPLAIN output pasted as comment
- [ ] Rewritten query with explanation of changes
- [ ] Dashboard `.pbix` or `dashboard_mockup.pdf` in `outputs/`
