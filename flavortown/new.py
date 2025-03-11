from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,jsonify
)
from werkzeug.exceptions import abort
import pandas as pd
from flavortown.auth import login_required
from flavortown.database import get_db
from datetime import datetime
import calendar
import matplotlib.pyplot as plt
import io
import base64

@("/")
def index():
    db = get_db()
    budget=pd.read_sql_query('SELECT * FROM transactions',db)
    budget=budget.sort_values("Date")
    
    categories = budget.loc[:,'Category'].unique().tolist()
    categories.append("All")
    budget["Date"] = budget["Date"].astype(str)
    budgetJson=budget.to_json(orient="records")
    budget= budget.to_dict(orient="records") 
    

    return render_template('budget/index.html', budget=budget,budgetJson=budgetJson,categories=categories)

@bp.route("/filter", methods=["POST"])
def filter_data():
    db = get_db()

    string ="SELECT "
    budget=pd.read_sql_query('SELECT * FROM transactions',db)
    budget.to_csv("all.csv")
    budget["Date"]=pd.to_datetime(budget.loc[:,"Date"])
    budget=budget.sort_values("Date")
    budget["Date"]=pd.to_datetime(budget.loc[:,"Date"])
    
    filters = request.json
    if filters:
        budget = budget[budget["TransactionType"].isin(filters["transactionType"])]
        if filters["yValue"] != "Balance":
            if len(filters["categories"]) != 0:
                budget = budget[budget["Category"].isin(filters["categories"])]
        else:
            budget = budget.sort_values("Date")
            budget['RunningBalance'] = budget['Amount'].cumsum()
            budget["Amount"]=budget["RunningBalance"]
            
            budget["Date"] = budget["Date"].astype(str)
            return jsonify(budget.to_dict(orient="records"))
        
    
        if filters['aggregation']=="Daily":
            budget=budget

        elif filters['aggregation']=="Monthly":
            budget=budget.groupby([
            budget['Date'].dt.to_period('M'),
            'Source','TransactionType',
            'Category']).agg({'Amount': 'sum' if filters["yValue"] == "Raw" else 'mean'}).reset_index()
            if filters["yValue"] == "Balance":
                 budget['Amount'] = budget['Amount'].cumsum()

        else:
            budget=budget.groupby([
            budget['Date'].dt.to_period('W'),
            'Source','TransactionType',
            'Category']).agg({'Amount': 'sum' if filters["yValue"] == "Raw" else 'mean'}).reset_index()
            if filters["yValue"] == "Balance":
                budget['Amount'] = budget.loc[:,'Amount'].cumsum()
    else:
        budget = budget  # No filters, return all data

    

    budget["Date"] = budget["Date"].astype(str)
    dates = budget["Date"].tolist()
    amounts = budget["Amount"].tolist()

    plt.figure(figsize=(10, 5))
    plt.plot(dates, amounts, marker='o')
    # plt.title(f"Financial Trends ({filters['aggregation']})")
    plt.xlabel('Date')
    # plt.ylabel(f"Amount ({filters['yValue']})")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show(block=False)
    # Save the plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    chart_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return f"data:image/png;base64,{chart_url}"


# def generate_chart(data, filters):
#     dates = [row['Date'] for row in data]
#     amounts = [row['Amount'] for row in data]

#     plt.figure(figsize=(10, 5))
#     plt.plot(dates, amounts, marker='o')
#     plt.title(f"Financial Trends ({filters['aggregation']})")
#     plt.xlabel('Date')
#     plt.ylabel(f"Amount ({filters['yValue']})")
#     plt.xticks(rotation=45)
#     plt.tight_layout()

#     # Save the plot to a BytesIO object
#     img = io.BytesIO()
#     plt.savefig(img, format='png')
#     img.seek(0)
#     chart_url = base64.b64encode(img.getvalue()).decode()
#     plt.close()

#     return f"data:image/png;base64,{chart_url}"