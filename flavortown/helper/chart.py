import streamlit as st
import pandas as pd
from datetime import datetime
import altair as alt
from flavortown.validate import validate,getValidData

# pg.mainProgram()
df= getValidData()
st.set_page_config(layout="wide")

df["Date"]=pd.to_datetime(df.loc[:,"Date"])
df['Balance'] = df['Amount'].cumsum()

# df["Category"].to_csv("1.csv")
col1, col2, col3 = st.columns(3)

transactionTypeOptions=["Debit","Credit"]
transactionTypeCheckboxes = {}
with col1:
    for option in transactionTypeOptions:
        transactionTypeCheckboxes[option] = st.checkbox(option,True)

if not transactionTypeCheckboxes["Debit"]:
    df=df[df["TransactionType"] != "Debit"]
if not transactionTypeCheckboxes["Credit"]:
    df=df[df["TransactionType"] != "Credit"]


catStatusOptions=["Fixed","Variable","?"]

catStatusCheckboxes = {}
with col2:
    for option in catStatusOptions:
        catStatusCheckboxes[option] = st.checkbox(option,True)

if not catStatusCheckboxes["Fixed"]:
    df=df[df["CategoryStatus"] != "Fixed"]
if not catStatusCheckboxes["Variable"]:
    df=df[df["CategoryStatus"] != "Variable"]
if not catStatusCheckboxes["?"]:
    df=df[df["CategoryStatus"] != "?"]

sourceOptions = ['ESL', "Ally", "Discover"]
soourceCheckboxes = {}
with col3:
    for option in sourceOptions:
        soourceCheckboxes[option] = st.checkbox(option,True)

if not soourceCheckboxes["Ally"]:
     df=df[df["Source"] != "Ally"]
if not soourceCheckboxes["ESL"]:
    df=df[df["Source"] != "ESL"]
if not soourceCheckboxes["Discover"]:
    df=df[df["Source"] != "Discover"]


 
col4,col5,col6=st.columns(3)
with col4:
    categories=st.multiselect("Category",df["Category"].unique())

if categories:
    df = df[df["Category"].isin(categories)]

with col5:
    yValue=st.selectbox("Y-Value",["Raw","Total","Average"])

with col6:
    afterDate=st.text_input("See after:")
if afterDate=="":
    afterDate="12/31/23"

df=df[df['Date'] > pd.to_datetime(afterDate)]


aggregation_level=st.radio("Slice by what",["Daily","Weekly","Monthly"])
if aggregation_level == "Daily":
        grouped_data = df
elif aggregation_level == "Weekly":
    if yValue == "Raw":
        # Return unsummarized data, just reindexed to weekly
        grouped_data = df.set_index('Date').resample('W').agg({
            'Amount': 'sum' if yValue == "Total" else 'mean'
        })
    else:
        grouped_data = df.set_index('Date').resample('W').agg({
            'Amount': 'sum' if yValue == "Total" else 'mean'
        })
else:  # Monthly
    grouped_data = df.set_index('Date').resample('M').agg({
        'Amount': 'sum' if yValue == "Total" else 'mean'
    })

st.altair_chart(alt.Chart(grouped_data.reset_index()).mark_line().encode(
    x="Date",
    y="Amount"
).properties(
    width=500,
    height=300
)
)

st.data_editor(df)


def highlight_ledger(row):
    """Color debits in light red and credits in light green."""
    color = "background-color: "
    if row.TransactionType =="Debit":
        return [color + "#FFDDDD"] * len(row)  # Light red for debits
    elif row.TransactionType =="Credit":
        return [color + "#DDFFDD"] * len(row)  # Light green for credits
    return [""] * len(row)

# Display Ledger in Streamlit with Styling
st.write("### **Transaction Ledger** (Two-Account Format)")
st.data_editor(df.style.apply(highlight_ledger, axis=1), use_container_width=True, height=400)