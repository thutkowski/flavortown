import pandas as pd
import csv

def importFile(file_path):
    file_content = file_path.getvalue().decode("utf-8") 
    if file_content.splitlines()[0] == '"Account Name : Free Checking"' or file_content.splitlines()[0] == "Account Name : Free Checking":
        source="ESL"
        df = pd.read_csv(file_path, skiprows=3, engine='python', on_bad_lines="skip")
    else:
        df = pd.read_csv(file_path)

    colList=df.columns.tolist()

    validDiscoverHead=["Trans. Date","Post Date","Description","Amount","Category"]
    if colList==validDiscoverHead:
        source="Discover"
        df=df.rename(columns={"Trans. Date":"Date","Description":"Desc"})
        df["Date"]=pd.to_datetime(df.loc[:,"Date"])
        df["Source"]="Discover"
        df["TransactionType"] = df["Amount"].apply(lambda x: "Credit" if x > 0 else "Debit")
        df=df[["Date","Amount","TransactionType","Desc","Source","Category"]]

    validEslHead=["Transaction Number","Date","Description","Memo","Amount Debit","Amount Credit","Balance","Check Number","Fees  "]
    if colList==validEslHead:
        source="ESL"
        df["Amount Credit"]=df["Amount Credit"].fillna(0)
        df["Amount Debit"]=df["Amount Debit"].fillna(0)
        df.fillna("", inplace=True)
        df["Desc"]=df["Description"]+df["Memo"]
        df["Amount"]=df["Amount Debit"] +df["Amount Credit"]
        df["TransactionType"] = df["Amount"].apply(lambda x: "Debit" if x > 0 else "Credit")
        print(df.info())
        df=df[["Date","Amount","TransactionType","Desc"]]
        new_row=["1/1/2024",1665.99,"Debit","Initial balance"]
        df.loc[len(df)]=new_row
        df["Date"]=pd.to_datetime(df.loc[:,"Date"])
        df["Desc"]=df["Desc"].astype(str)
        df["Category"]="Reset"
        df["Source"]=source

    validAllyHead=["Date"," Time"," Amount"," Type"," Description"]
    if colList==validAllyHead:
        df=df[["Date"," Amount"," Type"," Description"]]
        df=df.rename(columns={" Type":"TransactionType"," Amount":"Amount" ," Description":"Desc"})
        df["TransactionType"]=df["TransactionType"].replace({"Withdrawal":"Credit","Deposit":"Debit"})
        df.loc[:,"Date"]=df.loc[:,"Date"].astype(str)
        newRow=["2024-07-30",912.28,"Debit","Initial Balance"]
        df.loc[len(df)]=newRow
        df["Date"]=pd.to_datetime(df.loc[:,"Date"])
        df["Category"]="Reset"
        df["Source"]="Ally"
        df=df[["Date","Desc","Amount","TransactionType","Category","Source"]]

    #Extra processing for all df's
    df["Week"] = df["Date"].dt.isocalendar().week
    df["Year"] = df["Date"].dt.isocalendar().year

    return df


