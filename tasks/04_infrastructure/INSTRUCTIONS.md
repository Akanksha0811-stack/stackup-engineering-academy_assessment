# Pillar 4 — Infrastructure & Governance

> **Time allocation:** ~3 hours  
> **Starter files:** `starter_files/etl_starter.py` (Task 4.3), new files you create

---

## Context

Your pipeline works. Now it needs to be deployable, maintainable, and compliant. The DevOps team needs the ETL pipeline containerised. The Data Governance team needs a formal classification and ownership document. And the Data Quality team needs an automated check framework they can extend without touching pipeline code.

---

## Task 4.1 — Docker: Containerise the ETL pipeline

**What to build:**

Create a `Dockerfile` in the root of the repository that packages and runs the ETL pipeline from Task 2.2.

**Requirements:**

1. **Base image:** Use `python:3.11-slim`
2. **Dependencies:** Install from `requirements.txt`
3. **Entry point:** Running the container must execute `etl_starter.py` automatically
4. **Output mounting:** The container must write outputs to a mounted volume so results are accessible on the host after the container exits
5. **Environment variables:** The pipeline must read `DATA_DIR` and `OUTPUT_DIR` from environment variables (with sensible defaults if not set)

**Files to create:**
- `Dockerfile` — in the repo root
- `.dockerignore` — exclude `outputs/`, `.git/`, `__pycache__/`, and `*.pyc`

**Test your container:**
```bash
docker build -t presight-etl .
docker run -v $(pwd)/outputs:/app/outputs presight-etl
```

The `outputs/` folder on your host machine should contain the pipeline results after the container exits.

**Bonus:** Add a `docker-compose.override.yml` that mounts the datasets directory and passes environment variables, so the pipeline can be run with `docker-compose run etl`

---

**Assessment focus:**
- Container builds without errors
- Output files appear in the mounted volume after the container runs
- `.dockerignore` is correct — image does not contain unnecessary files
- Environment variable handling is clean

---

## Task 4.2 — Data Governance: Classification, ownership, and retention policy

**What to produce:**

Write a data governance document for the Presight project management data. Save it as `outputs/data_governance_document.md`.

The document must cover all three datasets: `projects`, `employees`, and `transactions`.

---

**Section 1 — Data inventory**

Complete the following table for each dataset:

| Dataset | Source system | Format | Update frequency | Volume estimate |
|---|---|---|---|---|
| projects | | | | |
| employees | | | | |
| transactions | | | | |

---

**Section 2 — Data classification**

Classify each column in each dataset using the scheme below:

| Classification | Definition |
|---|---|
| **Public** | Non-sensitive, can be shared externally |
| **Internal** | For internal use only, no regulatory requirement |
| **Confidential** | Sensitive business data — restricted access |
| **Personal** | Contains personally identifiable information (PII) — regulatory requirements apply |

For each PII column, state which regulation applies (GDPR, UAE PDPL, or both).

---

**Section 3 — Data ownership**

Define ownership for each dataset:

| Dataset | Data Owner (role) | Data Steward (role) | Access approver |
|---|---|---|---|

Explain the difference between a Data Owner and a Data Steward in your own words.

---

**Section 4 — Retention policy**

For each dataset, define:
- Retention period (how long should data be kept?)
- Justification (business need, regulatory requirement, or both)
- Disposal method (delete, anonymise, archive)
- Who is responsible for enforcing the policy

Consider: do financial transaction records have different retention requirements than employee HR data?

---

**Section 5 — Access control recommendations**

Recommend role-based access for the following personas:

| Persona | Projects | Employees | Transactions |
|---|---|---|---|
| Data Engineer | | | |
| BI Analyst | | | |
| Finance Team | | | |
| HR Team | | | |
| Executive / Director | | | |

Access levels: `None`, `Read`, `Read + Write`, `Full (including delete)`

---

**Assessment focus:**
- Completeness — all columns classified, all sections filled
- Quality of reasoning — are decisions justified?
- Awareness of UAE PDPL in addition to GDPR
- Practical, implementable recommendations (not just theory)

---

## Task 4.3 — Data Quality Framework

**File:** `starter_files/etl_starter.py` → function `run_data_quality_checks()`

Build a reusable data quality check framework that the team can extend by adding new rules without modifying pipeline code.

**Minimum requirements — implement at least five checks:**

| Check | Type | Description |
|---|---|---|
| Completeness | Column-level | % of non-null values per column; flag columns below threshold |
| Uniqueness | Table-level | Verify primary key columns contain no duplicates |
| Validity — numeric | Column-level | Numeric columns within expected min/max range |
| Validity — date | Column-level | Date columns contain valid, non-future dates where expected |
| Consistency | Cross-column | `start_date` must be before `end_date`; `actual_cost` must be ≥ 0 |

**Bonus checks (optional):**
- Referential integrity — `project_manager_id` in projects exists in employees
- Distribution check — flag if more than 30% of a column's values are the same (potential data loading error)
- Freshness check — flag if the most recent `transaction_date` is more than 30 days old

**Framework design requirements:**

The framework must be configurable — rules and thresholds should be defined in a config dict or file, not hardcoded. For example:

```python
DQ_CONFIG = {
    "projects": {
        "completeness_threshold": 0.90,
        "pk_columns": ["project_id"],
        "numeric_ranges": {
            "budget": {"min": 0, "max": 10_000_000},
            "actual_cost": {"min": 0, "max": 10_000_000}
        },
        "date_columns": ["start_date", "end_date"],
        "consistency_rules": [("start_date", "<", "end_date")]
    }
}
```

**Return format:**

The function must return a dictionary of results:

```python
{
    "completeness": {"status": "PASS", "details": {"project_id": 1.0, "budget": 0.95, ...}},
    "uniqueness":   {"status": "PASS", "details": "project_id: 20 unique / 20 total"},
    "validity":     {"status": "FAIL", "details": "budget: 1 value(s) below minimum (0)"},
    ...
}
```

Log a `WARNING` for every `FAIL` result.

---

## Completion checklist

- [ ] `Dockerfile` builds successfully
- [ ] Container runs and writes outputs to mounted volume
- [ ] `.dockerignore` excludes outputs, git, and cache files
- [ ] `outputs/data_governance_document.md` covers all three datasets
- [ ] All columns classified with correct level and regulation noted for PII
- [ ] Retention policy defined and justified for each dataset
- [ ] DQ framework implements minimum 5 checks
- [ ] Framework is configurable — rules defined in config, not hardcoded
- [ ] Return format matches specification above
- [ ] WARN logged for every failing check
