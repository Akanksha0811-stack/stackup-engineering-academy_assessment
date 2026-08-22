import duckdb

con = duckdb.connect()

with open("solutions/submissions/Akanksha/01_foundations/data_model.sql") as f:
    sql = f.read()

section1 = sql.split("SECTION 2")[0]
con.execute(section1)

print(con.execute("SHOW TABLES").fetchall())