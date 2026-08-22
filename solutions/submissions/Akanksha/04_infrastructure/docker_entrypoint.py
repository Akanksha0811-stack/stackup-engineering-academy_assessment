"""
Docker entry point wrapper for the ETL pipeline.

The core pipeline (etl_pipeline.py) computes its paths relative to its own
file location, which assumes the deeply nested solutions/ folder structure
used for assessment submission. Inside the container it sits flat at
/app/etl_pipeline.py, so this wrapper overrides DATA_DIR/OUTPUT_DIR from
environment variables (with sensible defaults) before invoking the real
pipeline logic, satisfying the container's env-var requirement without
duplicating or modifying the already-tested pipeline code.
"""
import os
import etl_pipeline

etl_pipeline.DATA_DIR = os.environ.get("DATA_DIR", "/app/datasets")
etl_pipeline.OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "/app/outputs")

os.makedirs(etl_pipeline.OUTPUT_DIR, exist_ok=True)

etl_pipeline.run_pipeline()
