from flask import Flask, request, jsonify
from flask_cors import CORS  # ✅ required for React connection
import pandas as pd

app = Flask(__name__)
CORS(app)  # ✅ allow frontend (localhost:3000) to access backend

@app.route('/')
def home():
    return "HealthGuard API is running!"

@app.route('/upload', methods=['POST'])
def upload_csv():
    try:
        file = request.files['file']
        df = pd.read_csv(file)

        return jsonify({
            "message": "CSV uploaded successfully!",
            "columns": df.columns.tolist(),
            "rows": df.shape[0]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
