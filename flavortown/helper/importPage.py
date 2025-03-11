import streamlit as st
from importFile import importFile
from process import processFile
from flavortown.validate import validate,getValidData
from addRecords import addRecords


transactionFile=st.file_uploader("Enter csv's",type=["csv"])
if transactionFile is not None:
    temp_df=importFile(transactionFile)
    temp_df=processFile(temp_df)
    temp_df=validate(temp_df)
    temp_df=temp_df[temp_df["IsValid"]==False]
    addRecords(temp_df)
    # df=df[["Date","Desc","Amount","TransactionType","Category","Source"]]
    # st.table(df)