import pandas as pd
import sqlite3 as sqlite

# df=pd.read_csv("all.csv")
conn=sqlite.connect("budget.db")
cur=conn.cursor()
# df.to_sql("transactions",conn)

cur.execute("""CREATE TABLE transactions (
    [index]         INTEGER,
    Date            TEXT,
    Desc            TEXT,
    Amount          REAL,
    TransactionType TEXT,
    Category        TEXT,
    Source          TEXT,
    CategoryStatus  TEXT,
    Week            INTEGER,
    Year            INTEGER
);""")

