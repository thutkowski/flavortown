import sqlite3 as sqlite
import pandas as pd
from database import get_db

dbPath="C:\\Users\\Tim\\Documents\\codingProjects\\bugdetApp\\budget.db"

conn=sqlite.connect(dbPath)

df=pd.read_sql_query("SELECT * FROM transactions",conn)
df["Date"]=pd.to_datetime(df["Date"])
dbPathTo="C:\\Users\\Tim\\Documents\\codingProjects\\flavortown\\instance\\flavortown.db"
conn=sqlite.Connection(dbPathTo)
df.to_sql("transactions",conn)