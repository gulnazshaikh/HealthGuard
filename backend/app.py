from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

df = None  # Global dataframe to hold uploaded data

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
            "message": "Uploaded",
            "columns": df.columns.tolist(),
            "data": df.head(10).to_dict(orient='records')
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/preview')
def preview():
    global df
    if df is not None:
        return jsonify({
            "columns": df.columns.tolist(),
            "data": df.to_dict(orient='records')  # ✅ return full data
        })
    return jsonify({"error": "No data uploaded"}), 400

@app.route('/clean')
def clean_data():
    global df
    if df is not None:
        df.fillna(df.mean(numeric_only=True), inplace=True)

        # Sample visual data
        sugar = df['Sugar'].tolist() if 'Sugar' in df else []
        bp = df['BP'].tolist() if 'BP' in df else []
        time = list(range(len(sugar)))

        radar = [
            df['Age'].mean() if 'Age' in df else 0,
            df['BP'].mean() if 'BP' in df else 0,
            df['Sugar'].mean() if 'Sugar' in df else 0,
            df['Cholesterol'].mean() if 'Cholesterol' in df else 0
        ]

        return jsonify({
            "sugar": sugar[:10],
            "bp": bp[:10],
            "time": time[:10],
            "radar": radar
        })
    return jsonify({"error": "No data uploaded"}), 400

if __name__ == '__main__':
    app.run(debug=True)
