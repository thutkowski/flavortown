import pandas as pd
import streamlit as st

df=pd.read_csv("Files/budget.csv")
st.table(df['Expenses'])
# df['Expenses'].to_csv("2.csv")