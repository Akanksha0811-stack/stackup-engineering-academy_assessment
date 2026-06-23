# StackUp Engineering Academy — Data Engineering Assessment

> **Learning Pathway:** Data Analyst / Modeler / BI Specialist → Fullstack Data Engineer

This repository contains the complete data engineering skills assessment. It includes realistically-sized test datasets, task instructions, and starter files aligned to the four learning pathway pillars: **Foundations**, **SQL & Data Visualization**, **Big Data Processing**, and **Infrastructure & Governance**.

---

## 📊 Dataset overview

This assessment uses production-scale data so candidates work with realistic volumes:

| Dataset | File | Rows | Format |
|---|---|---|---|
| Projects | `datasets/projects.csv` | 500 | CSV |
| Employees (current state) | `datasets/employees.csv` | 1,000 | CSV |
| Employee salary history | `datasets/employees_salary_history.csv` | ~1,800 | CSV |
| Transactions | `datasets/transactions.json` | 50,000 | JSON |
| Event stream | `datasets/events_stream/events_2025_*.jsonl` | 100,000 (12 monthly files) | JSONL |



---

## ⚙️ Getting Started



### Prerequisites at a glance

You must install or have access to the following:

| # | Tool | Minimum Version | Purpose | Install method |
|---|---|---|---|---|
| 1 | **Python** | 3.9+ | Core scripting, data processing, ETL | Manual install |
| 2 | **Git** | 2.x+ | Version control and PR submission | Manual install |
| 3 | **Docker Desktop** | 20.x+ | Runs Kafka, Airflow, PostgreSQL locally | Manual install |
| 4 | **Java JDK** | 17 (LTS) | Required runtime for Apache Spark | Manual install |
| 5 | **VS Code** (or equivalent IDE) | Latest | Python + SQL development | Manual install |
| 6 | **Power BI Desktop** *(Windows only)* | Latest | Task 2.4 dashboard | Manual install — alternatives accepted |

These are installed automatically by `pip install -r requirements.txt` (no separate install needed):

| # | Tool | Version | Purpose |
|---|---|---|---|
| 7 | **PySpark** | 3.4+ | Distributed data processing (Task 3.1) |
| 8 | **kafka-python** | 2.0+ | Kafka client (Task 3.2) |
| 9 | **Apache Airflow** | 2.7+ | Workflow orchestration (Task 3.3) |
| 10 | **DuckDB** | 0.9+ | Embedded SQL engine (Tasks 1.2, 2.1, 2.3) |
| 11 | **Pandas** | 2.0+ | Data manipulation |
| 12 | **PyArrow** | 12.0+ | Parquet read/write |

These run inside Docker containers — started via `docker compose up -d`:

| # | Service | Image | Port | Purpose |
|---|---|---|---|---|
| 13 | **Apache Kafka** | confluentinc/cp-kafka | 9092 | Streaming (Task 3.2) |
| 14 | **Zookeeper** | confluentinc/cp-zookeeper | 2181 | Kafka dependency |
| 15 | **Kafka UI** | provectuslabs/kafka-ui | 8080 | Browse Kafka topics |
| 16 | **Apache Airflow** | apache/airflow:2.7.3 | 8081 | Pipeline orchestration UI |
| 17 | **PostgreSQL** | postgres:15 | 5432 | Airflow metadata + optional SQL practice |

**System requirements:**
- RAM: 8 GB minimum (16 GB recommended)
- Disk: 25 GB free
- OS: Windows 10/11, macOS 10.15+, Ubuntu 20.04+

### 📚 Detailed setup guides

For first-time setup, follow the master guide:

→ **[docs/setup/SETUP_GUIDE.md](docs/setup/SETUP_GUIDE.md)**

---

### Quick start (after prerequisites installed)

```bash
# 1. Clone the repo
git clone https://github.com/Presight-AI/stackup-engineering-academy_assessment.git
cd stackup-engineering-academy_assessment

# 2. Create your personal branch
git checkout -b candidate/your-name

# 3. Set up Python environment
python -m venv venv
source venv/bin/activate          # Mac/Linux
# OR: venv\Scripts\activate       # Windows
pip install -r requirements.txt

# 4. Start Docker services
docker-compose up -d

# 5. Start with Pillar 1
cat tasks/01_foundations/INSTRUCTIONS.md
```

---

## 📁 Repository Structure

```
stackup-engineering-academy_assessment/
│
├── datasets/                       # Test datasets (~40 MB total)
│   ├── projects.csv                # 500 rows
│   ├── employees.csv               # 1,000 rows (with DQ issues)
│   ├── employees_salary_history.csv # ~1,800 rows (for SCD2)
│   ├── transactions.json           # 50,000 rows
│   └── events_stream/              # 12 monthly files
│       ├── events_2025_01.jsonl    # ~8,333 events
│       ├── events_2025_02.jsonl
│       └── ... (10 more)
│
│
├── tasks/                          # Assessment instructions
│   ├── 01_foundations/INSTRUCTIONS.md
│   ├── 02_sql_and_viz/INSTRUCTIONS.md
│   ├── 03_big_data/INSTRUCTIONS.md
│   └── 04_infrastructure/INSTRUCTIONS.md
│
├── starter_files/                  # Scaffolded starter code
│   ├── etl_starter.py
│   ├── spark_starter.py
│   ├── kafka_starter.py
│   ├── airflow_dag_starter.py
│   └── data_model_starter.sql
│
├── docs/setup/                     # Setup guides
│   ├── SETUP_GUIDE.md              # Start here
│   ├── PYTHON_SETUP.md
│   ├── GIT_GITHUB_SETUP.md
│   ├── DOCKER_SETUP.md
│   └── POWER_BI_SETUP.md
│
├── outputs/                        # Your work goes here (gitignored)
├── solutions/                      # Reviewer use only
│
├── docker-compose.yml              # Local services (Kafka, Airflow, PostgreSQL)
├── requirements.txt                # Python dependencies
└── README.md
```

---

## 🎯 Assessment Tasks Overview

Each pillar has detailed instructions in its respective `INSTRUCTIONS.md`. Summary:

---

### Pillar 1 — Foundations (~3.5 hours)

**Skills:** Python, Pandas, data modelling, SCD2, data quality

| Task | Description | Output |
|---|---|---|
| 1.1 | Clean and transform 500 projects with 7 derived columns | `outputs/projects_clean.csv` |
| 1.2 | Star schema design with `dim_employee` as SCD Type 2 | DDL in starter SQL |
| 1.3 | Find ALL data quality issues across 1,000 employees | `outputs/employees_clean.csv` |

---

### Pillar 2 — SQL & Data Visualization (~4 hours)

**Skills:** SQL, window functions, query optimisation, dashboards

| Task | Description | Output |
|---|---|---|
| 2.1 | Six business questions including SCD2 history queries | SQL queries with explanations |
| 2.2 | Full ETL on 50K transactions, completing in < 30 seconds | `outputs/transactions_clean.csv` |
| 2.3 | **Measurable** query optimisation with EXPLAIN ANALYZE | Before/after benchmarks |
| 2.4 | Power BI dashboard (or annotated mockup) | `.pbix` or PDF |

---

### Pillar 3 — Big Data Processing (~4 hours)

**Skills:** PySpark, Kafka, Airflow

| Task | Description | Output |
|---|---|---|
| 3.1 | Process 100K events across 12 files into 5 aggregated tables | 5 Parquet tables in `outputs/spark/` |
| 3.2 | Real-time Kafka producer/consumer with severity-based forwarding | Topics + `outputs/kafka/summary.json` |
| 3.3 | Airflow DAG with DQ gate, retries, XCom-driven reporting | DAG visible in Airflow UI |

---

### Pillar 4 — Infrastructure & Governance (~3.5 hours)

**Skills:** Docker, data governance, DQ frameworks

| Task | Description | Output |
|---|---|---|
| 4.1 | Containerise the ETL pipeline | `Dockerfile`, `.dockerignore` |
| 4.2 | Data governance document with PII classification, retention, access | `outputs/data_governance_document.md` |
| 4.3 | Configurable DQ framework with 6+ checks | Framework in `etl_starter.py` + DQ reports |

---

## 📤 Submission Instructions

Once tasks are complete:

```bash
# 1. Stage and commit
git add .
git commit -m "Assessment submission — your name"

# 2. Push your branch
git push -u origin candidate/your-name
```

**3. Open a Pull Request:**
- Base: `main`
- Compare: `candidate/your-name`
- Title: `[Assessment] Your Full Name`
- Description must include:
  - Summary of approach per pillar
  - Assumptions made
  - Any tasks not completed (with reasons)
  - Bonus tasks attempted
  - Total time spent

---


## What Each Task Outputs

| Task | Output Location | Format | Size | Notes |
|------|-----------------|--------|------|-------|
| 1.1 | outputs/projects_clean.csv | CSV | 500 rows × 15 cols | Must include derived columns: budget_variance, is_over_budget, duration_days, status_category, risk_flag |
| 1.2 | starter_files/data_model_starter.sql Section 1 | SQL DDL | 6 tables | dim_date, dim_project, dim_employee (SCD2), dim_vendor, bridge_employee_project, fact_transactions |
| 1.3 | outputs/employees_clean.csv | CSV | 1000 rows | All data quality issues fixed; logging shows what was fixed |
| 2.1 | starter_files/data_model_starter.sql Section 3 | SQL queries × 6 | - | Q1-Q6 with comments explaining approach. Q6 uses SCD2 self-join |
| 2.2 | outputs/transactions_clean.csv | CSV | 50K rows | Enriched with project names, approver names, derived columns |
| 2.2 | outputs/pipeline_summary.txt | Text | 1 file | Run timestamp, before/after row counts, decisions, execution time |
| 2.3 | starter_files/data_model_starter.sql Section 4 | SQL + EXPLAIN | Comments | Original EXPLAIN ANALYZE, bottleneck analysis, optimized query, CREATE INDEX statements, speedup factor |
| 2.4 | outputs/presight_dashboard.pbix | Power BI | 1 file | OR outputs/dashboard_mockup.pdf if not using Power BI |
| 3.1 | outputs/spark/project_activity_summary/ | Parquet | 500 partitions | 4 tables total (project, user, escalation, daily_volume summaries) |
| 3.1 | outputs/spark/user_activity_summary/ | Parquet | 1000+ partitions | - |
| 3.1 | outputs/spark/escalation_log/ | Parquet | ~200 partitions | - |
| 3.1 | outputs/spark/daily_event_volume/ | Parquet | 365×15 partitions | Partitioned by event_date |
| 3.2 | outputs/kafka/summary.json | JSON | 1 file | Total events consumed, event_type counts, critical escalations forwarded |
| 3.3 | starter_files/airflow_dag_starter.py | Python | DAG code | (Or mounted in docker-compose; no output file) |
| 4.1 | Dockerfile (repo root) | Dockerfile | 1 file | Builds & runs etl_starter.py with mounted volumes |
| 4.1 | .dockerignore (repo root) | Text | 1 file | Excludes outputs/, .git/, __pycache__, *.pyc |
| 4.2 | outputs/data_governance_document.md | Markdown | 1 file | Covers projects, employees, transactions, **employees_salary_history** |
| 4.3 | outputs/dq_report_projects.md | Markdown | Optional | Check results in readable format (bonus) |
| 4.3 | outputs/dq_report_employees.md | Markdown | Optional | Check results in readable format (bonus) |
| 4.3 | outputs/dq_report_transactions.md | Markdown | Optional | Check results in readable format (bonus) |

---


## 📊 Assessment Criteria

| Criterion | Weight |
|---|---|
| **Correctness** — does the code produce expected output? | 35% |
| **Code quality** — readable, modular, well-commented, vectorised | 25% |
| **Design decisions** — modelling and architecture justified? | 20% |
| **Performance** — does it scale to the dataset size? | 10% |
| **Documentation** — assumptions and decisions clear? | 10% |

---

## ❓ Questions & Support

If you encounter issues or have questions:

1. Check existing [Issues](../../issues) — your question may be answered
2. If not, [open a new issue](../../issues/new) with:
   - The `question` label
   - Clear description of what's blocking you
   - What you've already tried
   - Your OS and any error messages

**Do not open a PR for questions** — PRs are for submitting work only.

We aim to respond within 1 business day.

---

## 📚 Learning Resources

This assessment is aligned to the StackUp Engineering Academy learning pathway. Course references in the original curriculum cover:

**Foundations**
- Python Essential Training (LinkedIn Learning)
- Pandas Essential Training (LinkedIn Learning)
- Learning Data Modeling (O'Reilly)

**SQL & Data Visualization**
- SQL Essential Training (LinkedIn Learning)
- ETL in Python and SQL (LinkedIn Learning)
- Advanced SQL for Query Tuning (LinkedIn Learning)
- Power BI Essential Training (LinkedIn Learning)

**Big Data Processing**
- Spark Programming in Python (O'Reilly)
- Complete Guide to Apache Kafka (LinkedIn Learning)
- Apache Airflow Essential Training (LinkedIn Learning)

**Infrastructure & Governance**
- Data Engineering on Azure (O'Reilly)
- Docker for Developers (LinkedIn Learning)
- Data Governance (O'Reilly)
- Data Quality: Core Concepts (LinkedIn Learning)

---

*StackUp Engineering Academy — Data Engineering Assessment*
