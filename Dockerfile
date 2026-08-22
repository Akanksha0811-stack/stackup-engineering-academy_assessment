# Presight ETL Pipeline - Multi-stage build
# Author: Akanksha Shreya

# ---- Stage 1: Builder ----
# Installs dependencies into a virtual environment. Keeping this in a
# separate stage means build tools and pip caches never make it into the
# final image, reducing its size.
FROM python:3.11-slim AS builder

WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Stage 2: Runtime ----
# Copies only the built virtual environment and application code from the
# builder stage, resulting in a smaller final image with no build toolchain.
FROM python:3.11-slim AS runtime

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# NOTE: packaging the completed pipeline (Task 1.1/2.2), not the raw
# starter stub, since the stub has unimplemented functions that produce
# no output -- this container needs to genuinely run end to end.
COPY solutions/submissions/Akanksha/01_foundations/etl_pipeline.py .
COPY solutions/submissions/Akanksha/04_infrastructure/docker_entrypoint.py .

# Pipeline reads these at runtime, with sensible defaults if not overridden
# by `docker run -e DATA_DIR=... -e OUTPUT_DIR=...`
ENV DATA_DIR=/app/datasets
ENV OUTPUT_DIR=/app/outputs

RUN mkdir -p /app/datasets /app/outputs

ENTRYPOINT ["python", "docker_entrypoint.py"]


