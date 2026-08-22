"""
Presight - Task 4.3: Configurable Data Quality Framework
Author: Akanksha Shreya
"""
import os
import json
import yaml
import pandas as pd
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dq_config.yaml")

TABLE_FILES = {
    "projects": os.path.join(OUTPUT_DIR, "projects_clean.csv"),
    "employees": os.path.join(OUTPUT_DIR, "employees_clean.csv"),
    "transactions": os.path.join(OUTPUT_DIR, "transactions_clean.csv"),
}


def load_config(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        config = yaml.safe_load(f)
    return config["checks"]


def load_tables():
    tables = {}
    for name, path in TABLE_FILES.items():
        tables[name] = pd.read_csv(path)
    return tables


def check_not_null(df, column, **kwargs):
    null_count = int(df[column].isna().sum())
    return {"passed": null_count == 0, "detail": f"{null_count} null values found"}


def check_unique(df, column, **kwargs):
    dup_count = int(df[column].duplicated().sum())
    return {"passed": dup_count == 0, "detail": f"{dup_count} duplicate values found"}


def check_range(df, column, min=None, max=None, **kwargs):
    series = df[column]
    below = int((series < min).sum()) if min is not None else 0
    above = int((series > max).sum()) if max is not None else 0
    out_of_range = below + above
    return {"passed": out_of_range == 0, "detail": f"{out_of_range} values out of range [{min}, {max}] ({below} below, {above} above)"}


def check_allowed_values(df, column, values=None, **kwargs):
    invalid = df[~df[column].isin(values)]
    invalid_count = len(invalid)
    return {"passed": invalid_count == 0, "detail": f"{invalid_count} rows with value outside {values}"}


def check_referential_integrity(df, column, reference_table=None, reference_column=None, tables=None, **kwargs):
    ref_df = tables[reference_table]
    valid_keys = set(ref_df[reference_column])
    orphans = df[~df[column].isin(valid_keys)]
    orphan_count = len(orphans)
    return {"passed": orphan_count == 0, "detail": f"{orphan_count} rows reference a missing {reference_table}.{reference_column}"}


CHECK_REGISTRY = {
    "not_null": check_not_null,
    "unique": check_unique,
    "range": check_range,
    "allowed_values": check_allowed_values,
    "referential_integrity": check_referential_integrity,
}


def run_all_checks():
    checks = load_config(CONFIG_PATH)
    tables = load_tables()

    results = []
    for check_def in checks:
        table_name = check_def["table"]
        column = check_def["column"]
        check_type = check_def["check_type"]
        description = check_def.get("description", "")

        df = tables[table_name]
        check_fn = CHECK_REGISTRY[check_type]

        params = {k: v for k, v in check_def.items()
                  if k not in ("table", "column", "check_type", "description")}
        params["tables"] = tables

        outcome = check_fn(df, column, **params)

        results.append({
            "table": table_name,
            "column": column,
            "check_type": check_type,
            "description": description,
            "passed": outcome["passed"],
            "detail": outcome["detail"],
        })

        status = "PASS" if outcome["passed"] else "FAIL"
        print(f"[{status}] {table_name}.{column} ({check_type}): {outcome['detail']}")

    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed

    summary = {
        "run_timestamp": datetime.now().isoformat(),
        "total_checks": total,
        "passed": passed,
        "failed": failed,
        "results": results,
    }

    print("\n" + "=" * 60)
    print(f"DQ SUMMARY: {passed}/{total} checks passed")
    print("=" * 60)

    output_path = os.path.join(OUTPUT_DIR, "dq_report.json")
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Report written to: {output_path}")

    return summary


if __name__ == "__main__":
    run_all_checks()

