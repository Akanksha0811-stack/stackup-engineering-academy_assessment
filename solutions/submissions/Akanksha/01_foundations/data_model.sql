-- =============================================================
-- StackUp Engineering Academy — Data Engineering Assessment
-- Starter File: data_model_starter.sql
-- Pillars: Foundations (Task 1.2) | SQL & Viz (Tasks 2.1, 2.3)
-- =============================================================
--
-- SCENARIO
-- --------
-- Presight runs a project management platform. You are designing
-- the data warehouse layer that will power analytics dashboards
-- for Finance, Operations, and Executive leadership.
--
-- The source data comes from three operational tables:
--   projects      → datasets/projects.csv
--   employees     → datasets/employees.csv
--   transactions  → datasets/transactions.json
--
-- HOW TO USE
-- ----------
-- This file is divided into four sections.
-- Work through each section in order.
-- Run against your local database (SQLite, PostgreSQL, or DuckDB all work).
-- =============================================================


-- ===========================================================================
-- SECTION 1 — TASK 1.2: Design the data model (Star Schema)
-- ===========================================================================
--
-- Design a star schema for the Presight project analytics warehouse.
--
-- REQUIREMENTS:
--   - One central fact table: fact_transactions
--   - At minimum four dimension tables:
--       dim_project, dim_employee, dim_vendor, dim_date
--   - fact_transactions must include foreign keys to all four dimensions
--   - dim_date must be a proper date dimension (not just a date column)
--     with columns for year, quarter, month, month_name, week, day, is_weekend
--   - Use surrogate keys (integer PKs) on all dimension tables
--   - Preserve the original source system IDs as natural keys
--   - Add a dim_employee_project bridge table to handle the many-to-many
--     relationship between employees and projects (one employee can manage
--     multiple projects; one project can have multiple team members)
--
-- BONUS:
--   - Add a slowly-changing dimension (SCD Type 2) design to dim_employee
--     to track salary changes over time
--
-- DOCUMENT YOUR DECISIONS:
--   Write a comment before each table explaining why you designed it that way.

-- dim_date: standard date dimension, generated as a spine of every calendar
-- date the warehouse will need. Pre-computing calendar attributes (quarter,
-- weekday, etc.) here means fact/report queries never need to recalculate
-- them, and can simply join on date_key. surrogate key = date_key.
CREATE TABLE dim_date (
    date_key        INTEGER PRIMARY KEY,   -- surrogate key, format YYYYMMDD
    full_date        DATE NOT NULL,
    year             INTEGER NOT NULL,
    quarter          INTEGER NOT NULL,
    month            INTEGER NOT NULL,
    month_name       VARCHAR(20) NOT NULL,
    week             INTEGER NOT NULL,
    day              INTEGER NOT NULL,
    day_of_week      INTEGER NOT NULL,      -- 1=Monday ... 7=Sunday
    is_weekend       BOOLEAN NOT NULL
);


-- dim_project: one row per project, current-state only (no history tracking
-- needed here since the task only requires SCD2 on dim_employee). Sourced
-- from projects_clean.csv. project_id is preserved as the natural key;
-- project_key is the surrogate key used by fact_transactions.
CREATE TABLE dim_project (
    project_key         INTEGER PRIMARY KEY,   -- surrogate key
    project_id          VARCHAR(20) NOT NULL UNIQUE,  -- natural key from source
    project_name        VARCHAR(200) NOT NULL,
    department           VARCHAR(100),
    status                VARCHAR(50),
    status_category      VARCHAR(20),
    start_date            DATE,
    end_date              DATE,
    budget                DECIMAL(14,2),
    actual_cost           DECIMAL(14,2),
    budget_variance       DECIMAL(14,2),
    is_over_budget        BOOLEAN,
    duration_days         INTEGER,
    budget_utilisation_pct DECIMAL(6,2),
    risk_level             VARCHAR(10),
    priority               VARCHAR(20),
    region                 VARCHAR(50),
    project_manager_id     VARCHAR(20)   -- natural key, resolved to employee_key via dim_employee at query time
);


-- dim_employee: SCD Type 2 dimension. Each employee can have multiple rows
-- (one per historical salary/role version), so employee_key (surrogate)
-- uniquely identifies a specific version, while employee_id (natural key)
-- repeats across an employee's version history. valid_from/valid_to define
-- the time window each version was in effect; is_current flags exactly one
-- row per employee_id as the present-day version. This lets fact queries
-- join on "employee_id + transaction_date BETWEEN valid_from AND valid_to"
-- to get the historically accurate salary/role for any point in time,
-- rather than only ever seeing today's values.
CREATE TABLE dim_employee (
    employee_key    INTEGER PRIMARY KEY,   -- surrogate key, unique per version
    employee_id     VARCHAR(20) NOT NULL,  -- natural key, repeats across versions
    full_name       VARCHAR(200) NOT NULL,
    email           VARCHAR(200),
    department      VARCHAR(100),
    role            VARCHAR(100),
    level           VARCHAR(20),
    salary          DECIMAL(12,2),
    region          VARCHAR(50),
    status          VARCHAR(20),
    valid_from      DATE NOT NULL,
    valid_to        DATE NOT NULL,          -- 9999-12-31 sentinel for current row
    is_current      BOOLEAN NOT NULL,
    change_reason   VARCHAR(200)            -- bonus: populated from history file where available
);


-- dim_vendor: one row per distinct vendor, derived from the vendor fields
-- present in transactions.json. Current-state only (vendors don't need
-- history tracking for this warehouse's purposes). vendor_id preserved
-- as natural key where the source system provides one.
CREATE TABLE dim_vendor (
    vendor_key      INTEGER PRIMARY KEY,          -- surrogate key
    vendor_id       VARCHAR(20) UNIQUE,            -- natural key from source, if present
    vendor_name     VARCHAR(200) NOT NULL,
    vendor_category VARCHAR(100)                   -- e.g. Software, Consulting, Cloud Services
);


-- bridge_employee_project: resolves the many-to-many relationship between
-- employees and projects (an employee can be staffed on multiple projects;
-- a project can have multiple team members beyond just its manager).
-- A composite primary key (employee_key, project_key) prevents duplicate
-- assignment rows while allowing each employee/project pair to appear once.
CREATE TABLE bridge_employee_project (
    employee_key    INTEGER NOT NULL REFERENCES dim_employee(employee_key),
    project_key     INTEGER NOT NULL REFERENCES dim_project(project_key),
    role_on_project VARCHAR(100),        -- e.g. 'Manager', 'Team Member', 'Contributor'
    PRIMARY KEY (employee_key, project_key)
);


-- fact_transactions: one row per financial transaction, the grain of this
-- fact table. Foreign keys resolve to the surrogate keys of each dimension
-- (date_key resolved from transaction_date; employee_key resolved to the
-- SCD2 version that was current AT THE TIME of the transaction, not
-- necessarily today's version). Measures (amount) and degenerate dimensions
-- (category, payment_status) live directly on the fact row since they don't
-- warrant their own dimension table at this grain.
CREATE TABLE fact_transactions (
    transaction_key  INTEGER PRIMARY KEY,   -- surrogate key
    transaction_id   VARCHAR(20) UNIQUE,     -- natural key from source, if present
    project_key      INTEGER NOT NULL REFERENCES dim_project(project_key),
    employee_key     INTEGER REFERENCES dim_employee(employee_key),   -- approver, may be null
    vendor_key       INTEGER REFERENCES dim_vendor(vendor_key),
    date_key         INTEGER NOT NULL REFERENCES dim_date(date_key),
    amount           DECIMAL(14,2) NOT NULL,
    category         VARCHAR(100),
    payment_status   VARCHAR(50)
);


-- ===========================================================================
-- SECTION 2 — Load staging data
-- ===========================================================================
--
-- Before answering the business questions, load your cleaned data
-- (output of etl_starter.py) into the tables above.
--
-- If using SQLite: use .import or INSERT statements
-- If using DuckDB: use read_csv_auto() or read_json_auto()
-- If using PostgreSQL: use COPY or \copy

-- Example (DuckDB):
-- INSERT INTO dim_project SELECT * FROM read_csv_auto('outputs/projects_clean.csv');

-- Populate dim_employee using SCD Type 2 logic.
-- employees_salary_history.csv is a change-event log (one row per change,
-- with previous_*/new_* pairs and an effective_date). We convert this into
-- one row per employee-version using LEAD() to find each version's end date:
-- the next change's effective_date (minus a day) becomes this version's
-- valid_to. The final version per employee (LEAD is NULL) gets the
-- 9999-12-31 sentinel and is_current = TRUE.
--
-- Employees absent from the history file entirely get a single row sourced
-- directly from employees.csv, with valid_from = hire_date.
--
-- ASSUMPTION: department, email, region, and status are treated as
-- present-day-only attributes (not tracked historically), since the source
-- history file doesn't carry versions of these fields — only salary/role/level.
INSERT INTO dim_employee (
    employee_key, employee_id, full_name, email, department, role, level,
    salary, region, status, valid_from, valid_to, is_current, change_reason
)
WITH emp_raw AS (
    SELECT * FROM read_csv_auto('outputs/employees_clean.csv')
),
history_raw AS (
    SELECT * FROM read_csv_auto('datasets/employees_salary_history.csv')
),
history_versions AS (
    SELECT
        employee_id,
        new_salary AS salary,
        new_role AS role,
        new_level AS level,
        CAST(effective_date AS DATE) AS valid_from,
        LEAD(CAST(effective_date AS DATE)) OVER (
            PARTITION BY employee_id ORDER BY effective_date
        ) AS next_effective_date,
        change_reason
    FROM history_raw
),
history_final AS (
    SELECT
        h.employee_id,
        e.full_name,
        e.email,
        e.department,
        h.role,
        h.level,
        h.salary,
        e.region,
        e.status,
        h.valid_from,
        COALESCE(h.next_effective_date - INTERVAL 1 DAY, DATE '9999-12-31') AS valid_to,
        (h.next_effective_date IS NULL) AS is_current,
        h.change_reason
    FROM history_versions h
    JOIN emp_raw e ON e.employee_id = h.employee_id
),
no_history_final AS (
    SELECT
        e.employee_id,
        e.full_name,
        e.email,
        e.department,
        e.role,
        e.level,
        e.salary,
        e.region,
        e.status,
        -- Fallback: 8 employees have no salary history AND a null hire_date
        -- (nulled during cleaning due to unparseable source values like
        -- "-999"/"99999-01-01"). Rather than drop these employees from the
        -- dimension entirely (which would orphan any fact rows referencing
        -- them), we use a 1900-01-01 sentinel to signal "start date unknown"
        -- while still making the employee queryable.
        COALESCE(CAST(e.hire_date AS DATE), DATE '1900-01-01') AS valid_from,
        DATE '9999-12-31' AS valid_to,
        TRUE AS is_current,
        NULL AS change_reason
    FROM emp_raw e
    WHERE e.employee_id NOT IN (SELECT DISTINCT employee_id FROM history_raw)
),
combined AS (
    SELECT * FROM history_final
    UNION ALL
    SELECT * FROM no_history_final
)
SELECT
    ROW_NUMBER() OVER (ORDER BY employee_id, valid_from) AS employee_key,
    employee_id, full_name, email, department, role, level, salary, region,
    status, valid_from, valid_to, is_current, change_reason
FROM combined;

-- ---------------------------------------------------------------------------
-- SCD2 Validation Queries (required by Task 1.2)
-- ---------------------------------------------------------------------------

-- Q1: No employee has more than one current record.
-- Confirms is_current integrity — must return zero rows.
SELECT employee_id, COUNT(*) AS current_count
FROM dim_employee
WHERE is_current = TRUE
GROUP BY employee_id
HAVING COUNT(*) > 1;

-- Q2: Show employees with version history.
-- Sanity check that multi-version employees exist and the counts look
-- reasonable (expect 2-5 versions per employee who appears in the history file).
SELECT employee_id, COUNT(*) AS version_count
FROM dim_employee
GROUP BY employee_id
ORDER BY version_count DESC
LIMIT 10;

-- Q3: Self-join to detect overlapping periods per employee.
-- For each employee, compare every pair of its own version rows (excluding
-- comparing a row to itself). Two periods overlap if one's valid_from falls
-- strictly between the other's valid_from and valid_to. A properly built
-- SCD2 table should return zero rows here — any result indicates a bug in
-- the valid_from/valid_to boundary logic (e.g. an off-by-one in the LEAD()
-- calculation, or a duplicate/conflicting history entry).
SELECT
    a.employee_id,
    a.employee_key AS version_a,
    b.employee_key AS version_b,
    a.valid_from AS a_start, a.valid_to AS a_end,
    b.valid_from AS b_start, b.valid_to AS b_end
FROM dim_employee a
JOIN dim_employee b
    ON a.employee_id = b.employee_id
    AND a.employee_key < b.employee_key
WHERE a.valid_from <= b.valid_to
  AND b.valid_from <= a.valid_to;


-- ===========================================================================
-- SECTION 3 — TASK 2.1: Answer five business questions
-- ===========================================================================
--
-- Write a SQL query to answer each question.
-- For each query, add a comment explaining your approach.
-- Queries must run without errors against your loaded data.

-- ---------------------------------------------------------------------------
-- Q1. BUDGET PERFORMANCE
-- Which departments have spent more than 90% of their total budget across
-- all projects? Show department, total_budget, total_actual_cost,
-- spend_percentage, and whether they are over budget.
-- Order by spend_percentage descending.
-- ---------------------------------------------------------------------------

-- YOUR CODE HERE


-- ---------------------------------------------------------------------------
-- Q2. PROJECT MANAGER WORKLOAD
-- Which project managers are currently managing more than one active project
-- (status = 'In Progress')? Show their full name, email, number of active
-- projects, and the combined budget they are responsible for.
-- ---------------------------------------------------------------------------

-- YOUR CODE HERE


-- ---------------------------------------------------------------------------
-- Q3. VENDOR CONCENTRATION RISK
-- Identify vendors who account for more than 30% of total transaction spend
-- across all projects. Show vendor_name, total_spend, percentage_of_total.
-- This is a risk indicator — flag these vendors in the output.
-- ---------------------------------------------------------------------------

-- YOUR CODE HERE


-- ---------------------------------------------------------------------------
-- Q4. ESCALATION-TO-COMPLETION RATE
-- Using the events data (if loaded), calculate the percentage of projects
-- that had at least one escalation event during their lifecycle.
-- If events data is not available, use the transactions data instead:
-- calculate the percentage of projects with a 'Disputed' transaction.
-- Show project_id, project_name, status, had_issue (True/False).
-- ---------------------------------------------------------------------------

-- YOUR CODE HERE


-- ---------------------------------------------------------------------------
-- Q5. MONTHLY SPEND TREND
-- Show the total transaction amount per month for the past 12 months,
-- broken down by category (Software, Consulting, Cloud Services, etc.)
-- Format the output as: year_month | category | total_amount | running_total
-- (running_total should accumulate within each category across months)
-- ---------------------------------------------------------------------------

-- YOUR CODE HERE


-- ===========================================================================
-- SECTION 4 — TASK 2.3: Query optimisation
-- ===========================================================================
--
-- The following query runs slowly in production. It is used on the finance
-- dashboard and executes hundreds of times per day.
--
-- YOUR TASKS:
--   a) Run EXPLAIN or EXPLAIN ANALYZE on the query (depending on your DB)
--      and paste the output as a comment. Identify the bottleneck.
--
--   b) Rewrite the query to improve performance.
--      You may restructure it, add CTEs, change joins, etc.
--
--   c) Write a comment explaining:
--      - What was wrong with the original query
--      - What you changed and why
--      - What indexes (if any) you would add in production
--
-- NOTE: Load sufficient data to make the performance difference meaningful.
--       If running on a small dataset, describe what you would observe at scale.

-- ORIGINAL QUERY (do not modify this — rewrite it in section 4b below)
-- ---------------------------------------------------------------------------
SELECT
    e.full_name,
    e.department,
    e.role,
    p.project_name,
    p.status,
    p.budget,
    p.actual_cost,
    t.amount,
    t.category,
    t.payment_status,
    t.transaction_date
FROM employees e, projects p, transactions t
WHERE e.employee_id = p.project_manager_id
AND   p.project_id  = t.project_id
AND   p.status NOT IN ('Completed', 'On Hold')
AND   t.payment_status = 'Pending'
AND   t.amount > (
        SELECT AVG(amount)
        FROM transactions
        WHERE payment_status = 'Pending'
      )
ORDER BY e.department, t.amount DESC;

-- ---------------------------------------------------------------------------
-- 4a) EXPLAIN output and bottleneck analysis (paste as comment):
-- ---------------------------------------------------------------------------
-- YOUR ANALYSIS HERE


-- ---------------------------------------------------------------------------
-- 4b) REWRITTEN QUERY
-- ---------------------------------------------------------------------------
-- YOUR CODE HERE


-- ---------------------------------------------------------------------------
-- 4c) Explanation of changes and indexing strategy
-- ---------------------------------------------------------------------------
-- YOUR EXPLANATION HERE