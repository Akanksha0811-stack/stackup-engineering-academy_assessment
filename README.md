# Data Engineering Skills Assessment

> **StackUp Engineering Academy** — Learning Pathway: Data Analyst / Modeler / BI Specialist → Fullstack Data Engineer

This repository contains everything needed to complete the Data Engineering skills assessment. It includes test datasets, task instructions, and starter files aligned to the four learning pathway pillars: **Foundations**, **SQL & Data Visualization**, **Big Data Processing**, and **Infrastructure & Governance**.

---

## Getting Started

### Prerequisites

Ensure the following are installed before cloning:

| Tool | Minimum Version | Purpose |
|---|---|---|
| Python | 3.9+ | Core scripting and data tasks |
| Git | 2.x+ | Version control and submission |
| Docker | 20.x+ | Local environment setup |
| Apache Spark | 3.x | Big data processing tasks |
| Apache Kafka | 3.x | Streaming pipeline tasks |
| Apache Airflow | 2.x | Pipeline scheduling tasks |

> Optional: Scala 2.x if attempting the Scala bonus tasks.

---

### Setup Instructions

**1. Clone the repository**

```bash
git clone https://github.com/your-org/stackup-engineering-academy_assessment.git
cd stackup-engineering-academy_assessment
```

**2. Create your personal branch**

Use the naming convention `candidate/your-name`:

```bash
git checkout -b candidate/your-name
```

**3. Install Python dependencies**

```bash
pip install -r requirements.txt
```

**4. Start the local environment**

```bash
docker-compose up -d
```

This will spin up local instances of Kafka, Airflow, and any other required services.

---

## Repository Structure

```
de-skills-assessment/
│
├── datasets/                  # Test datasets for all tasks
│   ├── projects.csv
│   ├── employees.csv
│   ├── transactions.json
│   └── events_stream/
│
├── tasks/                     # One folder per assessment pillar
│   ├── 01_foundations/
│   ├── 02_sql_and_viz/
│   ├── 03_big_data/
│   └── 04_infrastructure/
│
├── starter_files/             # Starter scripts and notebooks
│   ├── etl_starter.py
│   ├── spark_starter.py
│   ├── kafka_starter.py
│   ├── airflow_dag_starter.py
│   └── data_model_starter.sql
│
├── solutions/                 # Do not open until after submission
│   └── .gitkeep
│
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Assessment Tasks

Each pillar folder contains a `INSTRUCTIONS.md` with full task details. A summary is below.

---

### Pillar 1 — Foundations

**Skills assessed:** Python scripting, data analysis, data modelling

| Task | Description | Starter File |
|---|---|---|
| 1.1 | Write a Python script to clean and transform the `projects.csv` dataset using Pandas | `etl_starter.py` |
| 1.2 | Build a normalised data model for the provided business scenario and document your design decisions | `data_model_starter.sql` |
| 1.3 | Identify and resolve at least three data quality issues in the `employees.csv` dataset | `etl_starter.py` |

---

### Pillar 2 — SQL & Data Visualization

**Skills assessed:** SQL querying, ETL, dashboard design

| Task | Description | Starter File |
|---|---|---|
| 2.1 | Write SQL queries to answer five business questions against the provided schema | `data_model_starter.sql` |
| 2.2 | Build an ETL pipeline using Python and SQL that ingests, transforms, and loads the `transactions.json` dataset | `etl_starter.py` |
| 2.3 | Optimise a provided slow-running query and explain your approach | `data_model_starter.sql` |
| 2.4 | Design a dashboard mockup (or build in Power BI) using the output of Task 2.2 | — |

---

### Pillar 3 — Big Data Processing

**Skills assessed:** Apache Spark, Apache Kafka, Apache Airflow

| Task | Description | Starter File |
|---|---|---|
| 3.1 | Process the `events_stream/` dataset using PySpark and produce an aggregated output | `spark_starter.py` |
| 3.2 | Build a real-time streaming pipeline using Apache Kafka — produce and consume a sample event stream | `kafka_starter.py` |
| 3.3 | Create an Airflow DAG that orchestrates the ETL pipeline from Pillar 2 on a scheduled basis | `airflow_dag_starter.py` |

---

### Pillar 4 — Infrastructure & Governance

**Skills assessed:** Cloud data engineering, DevOps, data governance

| Task | Description | Starter File |
|---|---|---|
| 4.1 | Containerise the ETL pipeline from Task 2.2 using Docker | — |
| 4.2 | Write a data governance document covering data classification, ownership, and retention policy for the provided dataset | — |
| 4.3 | Define a data quality check framework — at minimum three checks — and implement them in Python | `etl_starter.py` |

> **Bonus (optional):** Rewrite the Spark task (3.1) in Scala.

---

## Submission Instructions

Once all tasks are complete:

**1. Stage and commit your work**

```bash
git add .
git commit -m "Assessment submission — your-name"
```

**2. Push your branch**

```bash
git push origin candidate/your-name
```

**3. Open a Pull Request**

- Base branch: `main`
- Your branch: `candidate/your-name`
- PR title: `[Assessment] Your Full Name`
- In the PR description, include:
  - A brief summary of your approach for each pillar
  - Any assumptions made
  - Any tasks not completed, with a reason
  - Any bonus tasks attempted

---

## Assessment Criteria

Submissions will be reviewed against the following:

| Criteria | Weight |
|---|---|
| Correctness — does the code produce the expected output? | 40% |
| Code quality — is the code readable, modular, and well-commented? | 25% |
| Design decisions — are modelling and architectural choices justified? | 20% |
| Documentation — are assumptions and decisions clearly explained? | 15% |

---

## Learning Resources

This assessment is aligned to the StackUp Engineering Academy learning pathway. If you need to brush up before or during the assessment, refer to the course materials below.

**Foundations**
- Python Essential Training *(LinkedIn Learning, 4h 23m)*
- Pandas Essential Training *(LinkedIn Learning, 3h 10m)*
- Learning Data Modeling *(O'Reilly, 7h 56m)*

**SQL & Data Visualization**
- SQL Essential Training *(LinkedIn Learning, 4h 36m)*
- ETL in Python and SQL *(LinkedIn Learning, 1h 20m)*
- Power BI Essential Training *(LinkedIn Learning, 3h 34m)*

**Big Data Processing**
- Spark Programming in Python for Beginners *(O'Reilly, 6h 36m)*
- Complete Guide to Apache Kafka for Beginners *(LinkedIn Learning, 7h 48m)*
- Apache Airflow Essential Training *(LinkedIn Learning, 2h 14m)*

**Infrastructure & Governance**
- Data Engineering on Azure *(O'Reilly, 8h 13m)*
- Git Essential Training *(LinkedIn Learning, 1h 42m)*
- Docker for Developers *(LinkedIn Learning, 1h 15m)*
- Data Governance *(O'Reilly, 3h 40m)*
- Data Quality: Core Concepts *(LinkedIn Learning, 1h 28m)*

---

## Questions & Support

If you encounter any issues with the repository setup or have questions about a task, please open a GitHub Issue in this repository using the `question` label. Do not open a PR for questions.

---

*StackUp Engineering Academy — Data Engineering Skills Assessment*
