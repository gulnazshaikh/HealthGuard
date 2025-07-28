from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

df = None  # Global DataFrame

@app.route('/')
def home():
    return "HealthGuard API is running!"

@app.route('/upload', methods=['POST'])
def upload_csv():
    global df
    try:
        file = request.files['file']
        df = pd.read_csv(file)

        return jsonify({
            "message": "Uploaded successfully",
            "columns": df.columns.tolist(),
            "data": df.head(10).to_dict(orient='records')
        })
    except Exception as e:
        return jsonify({"error": f"Upload failed: {str(e)}"}), 400

@app.route('/clean', methods=['GET'])
def clean_data():
    global df
    if df is None:
        return jsonify({"error": "No data uploaded"}), 400

    try:
        # Trim whitespace
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        # Fill missing values with mean (for numeric columns)
        df.fillna(df.mean(numeric_only=True), inplace=True)

        # Replace 0s with mean for selected columns if 0 is invalid
        zero_replace_cols = ['Glucose', 'BloodPressure', 'BMI', 'Insulin', 'SkinThickness']
        for col in zero_replace_cols:
            if col in df.columns:
                df[col] = df[col].replace(0, df[col].mean())

        return jsonify({
            "message": "Cleaned successfully",
            "data": df.head(10).to_dict(orient='records')
        })

    except Exception as e:
        return jsonify({"error": f"Cleaning failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
