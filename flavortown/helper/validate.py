import pandas as pd
import sqlite3 as sqlite

def getValidData():
    db="budget.db"
    conn=sqlite.connect(db)

    df=pd.read_sql_query("SELECT * FROM transactions",conn)
    df["Date"]=pd.to_datetime(df["Date"])
    return df

def validate(df):
    df_un=df
    df_valid=getValidData()
    validateColumns=["Date","Desc","Amount","TransactionType","Category","Source"]
    df_un['IsValid'] = df_un[validateColumns].apply(tuple, axis=1).isin(df_valid[validateColumns].apply(tuple, axis=1))

    return df_un
