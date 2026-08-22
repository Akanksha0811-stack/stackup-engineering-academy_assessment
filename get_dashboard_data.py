import duckdb, json

con = duckdb.connect()
with open("solutions/submissions/Akanksha/01_foundations/data_model.sql", encoding="utf-8") as f:
    sql = f.read()
con.execute(sql.split("SECTION 3")[0])

data = {}

# KPI cards
data["kpis"] = con.execute("""
    SELECT
        SUM(budget) AS total_budget,
        SUM(actual_cost) AS total_actual_spend,
        ROUND(100.0 * SUM(CASE WHEN is_over_budget THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_over_budget,
        (SELECT COUNT(*) FROM fact_transactions) AS total_transactions
    FROM dim_project
""").fetchone()

# Bar chart: spend vs budget by department
data["dept_spend"] = con.execute("""
    SELECT department, SUM(budget) AS total_budget, SUM(actual_cost) AS total_actual
    FROM dim_project GROUP BY department ORDER BY total_budget DESC
""").fetchall()

# Top 10 projects by budget variance (most over budget)
data["top_variance"] = con.execute("""
    SELECT project_name, department, budget, actual_cost, budget_variance
    FROM dim_project ORDER BY budget_variance DESC LIMIT 10
""").fetchall()

# Vendor concentration: top 5 + other
data["vendor_all"] = con.execute("""
    SELECT v.vendor_name, SUM(f.amount) AS total_spend
    FROM fact_transactions f JOIN dim_vendor v ON v.vendor_key = f.vendor_key
    GROUP BY v.vendor_name ORDER BY total_spend DESC
""").fetchall()

# Monthly trend (last 12 months by category, top categories)
data["monthly_trend"] = con.execute("""
    SELECT d.year || '-' || LPAD(CAST(d.month AS VARCHAR),2,'0') AS ym, f.category, SUM(f.amount) AS spend
    FROM fact_transactions f JOIN dim_date d ON d.date_key = f.date_key
    GROUP BY 1, 2 ORDER BY 1 DESC LIMIT 60
""").fetchall()

with open("dashboard_data.json", "w") as f:
    json.dump({
        "kpis": data["kpis"],
        "dept_spend": data["dept_spend"],
        "top_variance": data["top_variance"],
        "vendor_all": data["vendor_all"],
        "monthly_trend": [[str(x) for x in row] for row in data["monthly_trend"]],
    }, f, default=str, indent=2)

print("KPIs:", data["kpis"])
print("\nDept spend:", data["dept_spend"])
print("\nTop variance (first 3):", data["top_variance"][:3])
print("\nVendor top 5:", data["vendor_all"][:5])
print("\nTotal vendors:", len(data["vendor_all"]))
print("\nSaved full data to dashboard_data.json")