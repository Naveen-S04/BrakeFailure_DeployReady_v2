import os
import json
from flask import Flask, request, jsonify
import mlflow.pyfunc
import traceback

app = Flask(__name__)

# Load model on startup
MODEL_URI = os.environ.get("MODEL_URI")  # e.g., models:/BrakeFailurePrediction/Production or runs:/<run_id>/model
MLFLOW_TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI")

model = None
load_error = None

def discover_model_uri():
    # Try env first
    if MODEL_URI:
        return MODEL_URI
    # Try run_id.txt
    run_id_path = os.path.join(os.path.dirname(__file__), "model", "run_id.txt")
    if os.path.exists(run_id_path):
        rid = open(run_id_path).read().strip()
        if rid:
            return f"runs:/{rid}/model"
    # Fallback: local MLflow model path (if present)
    local_model_path = os.path.join(os.path.dirname(__file__), "model")
    if os.path.exists(local_model_path):
        return local_model_path
    return None

try:
    if MLFLOW_TRACKING_URI:
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    resolved_uri = discover_model_uri()
    if not resolved_uri:
        raise RuntimeError("No model location found. Set MODEL_URI or include model/run_id.txt or a local MLflow model directory.")
    model = mlflow.pyfunc.load_model(resolved_uri)
except Exception as e:
    load_error = str(e) + "\n" + traceback.format_exc()

@app.route("/health", methods=["GET"])
def health():
    status = "ok" if model is not None else "error"
    return jsonify({"status": status, "error": load_error})

@app.route("/predict", methods=["POST"])
def predict():
    try:
        if model is None:
            return jsonify({"error": "Model not loaded", "details": load_error}), 500
        data = request.get_json(force=True)
        # Expect flat JSON with numeric fields used in training
        # Convert to single-row DataFrame-like structure accepted by pyfunc
        import pandas as pd
        df = pd.DataFrame([data])
        preds = model.predict(df)
        # Support either class or probability
        if hasattr(preds, "tolist"):
            preds = preds.tolist()
        return jsonify({"prediction": preds})
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
