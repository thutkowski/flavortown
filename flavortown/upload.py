from flask import Flask, request, jsonify, render_template,Blueprint,current_app
import pandas as pd
import os 
from flavortown.budgetImport import importFile,processFile
from flavortown.database import get_db
bp = Blueprint('upload', __name__,url_prefix='/upload')

@bp.route('/')
def index():
    return render_template('upload/upload.html')  # Simple HTML form for uploading files

@bp.route('/uploadFile', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Process the file (Example: Read CSV or Excel)
    if file.filename.endswith('.csv'):
        temp_df = importFile(file,request.form["fileType"])
        temp_df=processFile(temp_df)
        db = get_db()
        df=pd.read_sql_query('SELECT * FROM transactions',db)
        df["Date"]=pd.to_datetime(df["Date"])
        df_un=temp_df
        
        validateColumns=["Date","Desc","Amount","TransactionType","Category","Source"]
        df_un['IsValid'] = df_un[validateColumns].apply(tuple, axis=1).isin(df[validateColumns].apply(tuple, axis=1))
        df_un=df_un[df_un["IsValid"]==False]
        df_un=df_un[["Date","Desc","Amount","TransactionType","Category","Source","Week","Year","CategoryStatus"]]
        df_un.to_sql("transactions",db, if_exists="append",index=False)

    else:
        return jsonify({'error': 'Unsupported file format'}), 400

    # Example Processing: Return the first 5 rows as JSON
    processed_data = df.head().to_dict(orient="records")

    return render_template('upload/upload.html')
