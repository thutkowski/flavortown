import pandas as pd
import sqlite3 as sqlite
import pandas as pd
import sqlite3 as sqlite

def addRecords(df):
    db="budget.db"
    conn=sqlite.connect(db)
    df=df[["Date","Desc","Amount","TransactionType","Category","Source","Week","Year","CategoryStatus"]]
    df.to_sql("transactions",conn, if_exists="append")




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

def setCategory(row):
    if "APPLE" in row["Desc"].upper() or "MEATBUS" in row["Desc"].upper() or "YNAB" in row["Desc"].upper():
        return "Subscription"
    elif "COMCAST" in row["Desc"].upper() or "PUGET SOUND ENERGY" in row["Desc"].upper() or "SANITARY SERVICE" in row["Desc"].upper():
        return "Utilities"
    elif "ABELSPEAKS" in row["Desc"].upper() or "WEGMANSEASTAVEN" in row["Desc"].upper():
        return "Charity"
    else:
        return row["Category"]

def setDesc(row):
    if row["Amount"] == 10.89 and "APPLE" in row["Desc"].upper():
        return "MAX"
    elif row["Amount"] == 2.99 and "APPLE" in row["Desc"].upper():
        return "iCloud Storage"
    else:
        return row["Desc"]

def categorize_descriptions(df,category_dict,catStat_dict,desc_mapping):
    """
    Maps description strings to standardized categories using a mapping dictionary
    and tracks changes in a 'changed' column.
    
    Args:
        df (pd.DataFrame): DataFrame containing a 'Desc' column
        
    Returns:
        pd.DataFrame: DataFrame with updated 'Desc' and 'changed' columns
    """

    # Create a copy of the DataFrame to avoid modifying the original
    df = df.copy()

    def map_category(row):
        if row['Desc']=="nan":
            if 'TransactionType' in row:
                if row['TransactionType'].upper() == 'DEBIT':
                   'Unknown Expense'
                elif row['TransactionType'].upper() == 'CREDIT':
                    return 'Unknown Income'
            return 'Unknown Transaction'
        
        desc_upper = row['Desc'].upper()
        original_desc = row['Desc']
        
        for search_term, desc in desc_mapping.items():
            if search_term.upper() in desc_upper:
                return desc
        return original_desc

    def match_category(row):
        # desc_upper = row['Desc'].upper() if pd.notna(row['Desc']) else ''
        desc = row['Desc']
        # Check for exact match first
        if desc.upper() in category_dict:
            return category_dict[desc.upper()]
        
        # Check for partial matches
        for lookup_desc, category in category_dict.items():
            if lookup_desc in desc:
                return category
        
        # No match found
        return row["Category"]

    def match_CategoryStatus(row):
        category_upper = row['Category'].upper() if pd.notna(row['Category']) else ''
        
        # Check for exact match first
        if category_upper.upper() in catStat_dict:
            return catStat_dict[category_upper]

    # Apply the mapping function to each row
    result = df.apply(map_category, axis=1)
    df['Desc'] = result    

    df['Category'] = df.apply(match_category,axis=1)

    df["CategoryStatus"] = df.apply(match_CategoryStatus, axis=1).fillna(df.get("categoryStatus", "Unknown"))

    return df

def createSupportFiles():
    descDf=pd.read_csv("Files/desc_mapping.csv")
    desc_mapping=dict(zip(descDf['Term'].str.upper(), descDf['Desc']))
    catDF=pd.read_csv("Files/categoryLookup.csv")
    category_dict = dict(zip(catDF['Desc'].str.upper(), catDF['Category']))
    catStatDF=pd.read_csv("Files/categoryStatusLookup.csv")
    catStat_dict=dict(zip(catStatDF["Category"].str.upper(),catStatDF["CategoryStatus"]))
    return category_dict,catStat_dict,desc_mapping

def processFile(df):
    category_dict,catStat_dict,desc_mapping=createSupportFiles()
    df["Category"]=df.apply(setCategory,axis=1)
    df= categorize_descriptions(df,category_dict,catStat_dict,desc_mapping)
    df['IsValid'] = df.apply(lambda row: row['Category'] in category_dict.values(), axis=1)

    mask = df[df['Desc'].str.contains('Rent')]
    mask=mask[mask["Amount"]>845.00]
    if not mask.empty:
        water_rows = df[mask].copy()
        water_rows['Desc'] = 'Water Bill'
        water_rows['Amount'] = df[mask]['Amount'] + 845.0  # Water bill is remaining amount
        mask = all['Desc'].str.contains('Rent')
        df.loc[mask, 'Amount'] = -845.0

    return df

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