import sqlite3 as sqlite
import pandas as pd

db="budget.db"
conn=sqlite.connect(db)

df=pd.read_sql_query("SELECT * FROM transactions",conn)
df.to_csv("all.csv")
