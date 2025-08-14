from flask import Flask, request, jsonify
import mlflow.sklearn
import os

app = Flask(__name__)

# Load model from MLflow
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))
model_uri = "models:/BrakeFailureModel/Production"  # Change if needed
model = mlflow.sklearn.load_model(model_uri)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    prediction = model.predict([data["features"]])
    return jsonify({"prediction": int(prediction[0])})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
