from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'data'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
df = None  # global DataFrame


@app.route('/')
def home():
    return "HealthGuard API is running!"


@app.route('/upload', methods=['POST'])
def upload_csv():
    global df
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        df = pd.read_csv(filepath)

        return jsonify({
            "message": "Uploaded",
            "filename": file.filename,
            "columns": df.columns.tolist(),
            "data": df.head(10).to_dict(orient='records')
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/clean', methods=['POST'])
def clean_data():
    global df
    try:
        if df is None:
            return jsonify({"error": "No data uploaded"}), 400

        df_cleaned = df.copy()

        # 1. Trim whitespace from string columns
        for col in df_cleaned.select_dtypes(include='object').columns:
            df_cleaned[col] = df_cleaned[col].str.strip()

        # 2. Replace 0 with NaN in critical numeric columns
        critical_columns = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
        for col in critical_columns:
            if col in df_cleaned.columns:
                df_cleaned[col] = df_cleaned[col].replace(0, np.nan)

        # 3. Fill NaN with mean (numeric only)
        df_cleaned.fillna(df_cleaned.mean(numeric_only=True), inplace=True)

        return jsonify({
            "message": "Cleaned successfully",
            "columns": df_cleaned.columns.tolist(),
            "data": df_cleaned.head(10).to_dict(orient='records')
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)
