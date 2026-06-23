# Python Environment Setup

Detailed Python setup for the assessment.

---

## Why a virtual environment?

A virtual environment isolates the assessment's Python packages from your system Python. Without it:
- Versions can conflict with other projects on your machine
- You may need admin rights to install packages
- Uninstalling becomes messy

**Always use a virtual environment for this assessment.**

---

## Step 1 — Verify Python version

```bash
python --version
```

You need Python **3.9 or higher**. If your version is lower:

| Platform | How to upgrade |
|---|---|
| Windows | Download latest from https://python.org/downloads — tick "Add to PATH" |
| Mac | `brew install python@3.11` |
| Linux | `sudo apt install python3.11 python3.11-venv` |

If `python --version` returns nothing or "command not found":
- Windows: Python isn't in your PATH — reinstall and tick the PATH option
- Mac/Linux: try `python3 --version` instead — use `python3` everywhere below

---

## Step 2 — Create a virtual environment

In the assessment repo folder:

```bash
python -m venv venv
```

This creates a `venv/` directory containing an isolated Python installation.

---

## Step 3 — Activate the environment

### Mac / Linux
```bash
source venv/bin/activate
```

### Windows (Command Prompt)
```cmd
venv\Scripts\activate.bat
```

### Windows (PowerShell)
```powershell
venv\Scripts\Activate.ps1
```

If PowerShell blocks the script with "execution policy" error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Confirm activation

Your prompt should now show `(venv)`:
```
(venv) $
```

`which python` (Mac/Linux) or `where python` (Windows) should point to inside the `venv/` folder.

---

## Step 4 — Upgrade pip

```bash
pip install --upgrade pip setuptools wheel
```

---

## Step 5 — Install requirements

```bash
pip install -r requirements.txt
```

This installs:

| Package | Purpose |
|---|---|
| pandas, numpy | Data manipulation |
| pyspark | Big data processing |
| kafka-python | Streaming pipeline |
| apache-airflow | Pipeline orchestration |
| duckdb, sqlalchemy | SQL engine |
| pyarrow | Parquet read/write |
| great-expectations | Optional DQ library |
| pytest | Testing framework |

Installation takes 3–5 minutes on first run.

---

## Step 6 — Verify installation

```bash
python -c "
import pandas as pd
import pyspark
import kafka
import airflow
import duckdb
import pyarrow

print('All packages installed successfully')
print(f'Pandas:   {pd.__version__}')
print(f'PySpark:  {pyspark.__version__}')
print(f'Airflow:  {airflow.__version__}')
print(f'DuckDB:   {duckdb.__version__}')
"
```

---

## Common installation issues

### PySpark requires Java

PySpark needs a Java Development Kit (JDK) version 8, 11, or 17.

**Mac:**
```bash
brew install openjdk@17
echo 'export JAVA_HOME=$(/usr/libexec/java_home -v 17)' >> ~/.zshrc
source ~/.zshrc
```

**Linux:**
```bash
sudo apt install openjdk-17-jdk
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
```

**Windows:**
1. Download OpenJDK 17 from https://adoptium.net/
2. Install with defaults
3. Set environment variable:
   - Search "Environment Variables" in Start menu
   - Add `JAVA_HOME` = installation path (e.g. `C:\Program Files\Eclipse Adoptium\jdk-17`)
   - Add `%JAVA_HOME%\bin` to `PATH`

Verify:
```bash
java -version
echo $JAVA_HOME       # Mac/Linux
echo %JAVA_HOME%      # Windows
```

---

### Airflow install fails on Windows

Airflow doesn't officially support Windows. Use one of these workarounds:

**Option A — WSL 2 (recommended)**
```powershell
# Install WSL
wsl --install
```
Then do all Python work inside WSL Ubuntu.

**Option B — Skip Airflow locally**
Run only the Airflow Docker container (already in `docker-compose.yml`). Edit your DAG file in any editor — it gets mounted into the container automatically.

**Option C — Constraints file**
```bash
pip install "apache-airflow==2.7.3" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.7.3/constraints-3.11.txt"
```

---

### "Failed building wheel for ..." errors

Usually means you're missing build tools.

**Windows:**
- Install **Microsoft C++ Build Tools** from https://visualstudio.microsoft.com/visual-cpp-build-tools/

**Mac:**
```bash
xcode-select --install
```

**Linux:**
```bash
sudo apt install build-essential python3-dev
```

---

### "No module named pip"

```bash
python -m ensurepip --upgrade
```

---

### Slow installs / timeouts

Try a different package index:
```bash
pip install -r requirements.txt -i https://pypi.org/simple/
```

Or increase timeout:
```bash
pip install -r requirements.txt --timeout 300
```

---

## Deactivating the environment

When you're done working:

```bash
deactivate
```

To reactivate later, just run the activate command from Step 3 again.

---

## Reinstalling from scratch

If something gets broken:

```bash
# Mac / Linux
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Windows
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
