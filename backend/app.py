from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import numpy as np
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# paths
CURRENT_FILE_PATH = None
CLEANED_FILE_PATH = os.path.join(UPLOAD_FOLDER, "cleaned_file.csv")


@app.route("/")
def home():
    return "✅ HealthGuard API is running!"


# ----------------- Upload CSV -----------------
@app.route("/upload", methods=["POST"])
def upload_csv():
    global CURRENT_FILE_PATH
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        save_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(save_path)
        CURRENT_FILE_PATH = save_path

        # preview
        df = pd.read_csv(save_path)
        preview = df.head(10).to_dict(orient="records")

        return jsonify({
            "message": "Uploaded successfully",
            "filename": file.filename,
            "columns": df.columns.tolist(),
            "data": preview
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ----------------- Clean CSV -----------------
@app.route("/clean", methods=["POST"])
def clean_csv():
    global CURRENT_FILE_PATH, CLEANED_FILE_PATH
    try:
        if CURRENT_FILE_PATH is None:
            return jsonify({"error": "No data uploaded"}), 400

        df = pd.read_csv(CURRENT_FILE_PATH)

        # 1) trim whitespace
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].astype(str).str.strip()

        # 2) replace invalid zeros
        critical_cols = ["Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI"]
        for col in critical_cols:
            if col in df.columns:
                df[col] = df[col].replace(0, np.nan)

        # 3) fill NaNs with mean
        df.fillna(df.mean(numeric_only=True), inplace=True)

        # 4) drop duplicates
        df = df.drop_duplicates().reset_index(drop=True)

        # save cleaned file
        df.to_csv(CLEANED_FILE_PATH, index=False)
        CURRENT_FILE_PATH = CLEANED_FILE_PATH

        return jsonify({
            "message": "Cleaned successfully",
            "columns": df.columns.tolist(),
            "data": df.head(10).to_dict(orient="records")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ----------------- Download Cleaned CSV -----------------
@app.route("/download-cleaned", methods=["GET"])
def download_cleaned():
    try:
        if os.path.exists(CLEANED_FILE_PATH):
            return send_file(CLEANED_FILE_PATH, as_attachment=True, download_name="cleaned_file.csv")
        return jsonify({"error": "Cleaned file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ----------------- Quick Review -----------------
@app.route("/review", methods=["GET"])
def quick_review():
    try:
        if not os.path.exists(CLEANED_FILE_PATH):
            return jsonify({"error": "No cleaned file found. Upload and clean first."}), 400

        df = pd.read_csv(CLEANED_FILE_PATH)

        # describe safely
        try:
            describe = df.describe(include="all").where(
                pd.notnull(df.describe(include="all")), None
            ).to_dict()
        except Exception:
            describe = df.describe().where(pd.notnull(df.describe()), None).to_dict()

        missing = df.isnull().sum().to_dict()
        dtypes = {c: str(t) for c, t in df.dtypes.items()}

        return jsonify({
            "message": "Review generated",
            "shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
            "columns": df.columns.tolist(),
            "dtypes": dtypes,
            "missing_values": missing,
            "describe": describe
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
