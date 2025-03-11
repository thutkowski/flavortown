import pandas as pd

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
    # if df["Source"][0]=="ESL":
    #     df.to_csv("eslRefined.csv")
    # if df["Source"][0]=="Discover":
    #     df.to_csv("discoverlRefined.csv")
    # if df["Source"][0]=="Ally":
    #     df.to_csv("allyRefined.csv")

    mask = df[df['Desc'].str.contains('Rent')]
    mask=mask[mask["Amount"]>845.00]
    if not mask.empty:
        water_rows = df[mask].copy()
        water_rows['Desc'] = 'Water Bill'
        water_rows['Amount'] = df[mask]['Amount'] + 845.0  # Water bill is remaining amount
        mask = all['Desc'].str.contains('Rent')
        # Adjust rent transactions to be exactly $800
        df.loc[mask, 'Amount'] = -845.0

    return df




