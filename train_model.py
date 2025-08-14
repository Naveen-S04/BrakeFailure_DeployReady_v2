# ✅ train_model.py — Train ML model & log with MLflow
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, roc_auc_score
import os

# ✅ Simulated Dataset Generator (Run Once)
def simulate_sensor_data(output_path="data/brake_sensor_data.csv", n_samples=1000):
    import numpy as np
    np.random.seed(42)

    brake_pressure = np.random.normal(100, 15, n_samples)
    brake_temp = np.random.normal(80, 10, n_samples)
    vehicle_speed = np.random.normal(60, 20, n_samples)
    pad_wear = np.random.uniform(0, 100, n_samples)

    failure = ((brake_pressure > 130) | (brake_temp > 95) | (pad_wear > 90)).astype(int)

    df = pd.DataFrame({
        "brake_pressure": brake_pressure,
        "brake_temp": brake_temp,
        "vehicle_speed": vehicle_speed,
        "pad_wear_level": pad_wear,
        "failure": failure
    })

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"✅ Simulated sensor data written to {output_path}")

# Generate data before training
#simulate_sensor_data()

# Create experiment
mlflow.set_experiment("BrakeFailurePrediction")

# Load data
df = pd.read_csv("data/brake_sensor_data.csv")
X = df.drop("failure", axis=1)
y = df["failure"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# MLflow tracking
with mlflow.start_run() as run:
    model = LogisticRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    roc = roc_auc_score(y_test, model.predict_proba(X_test)[:,1])

    mlflow.log_param("model_type", "LogisticRegression")
    mlflow.log_metric("accuracy", acc)
    mlflow.log_metric("roc_auc", roc)
    mlflow.sklearn.log_model(model, "model")
    print(f"Model trained with Accuracy: {acc}, ROC AUC: {roc}")

    # Store run ID for prediction script
    os.makedirs("model", exist_ok=True)
    with open("model/run_id.txt", "w") as f:
        f.write(run.info.run_id)

# ✅ predict.py — Load model & predict new input
def predict_failure(input_dict):
    import mlflow.sklearn
    import pandas as pd

    with open("model/run_id.txt", "r") as f:
        run_id = f.read().strip()

    model = mlflow.sklearn.load_model(f"runs:/{run_id}/model")
    df_input = pd.DataFrame([input_dict])
    prob = model.predict_proba(df_input)[0][1]
    prediction = int(prob > 0.5)
    return {"failure_probability": round(prob, 3), "will_fail": prediction}

# ✅ app.py — REST API for real-time prediction
from flask import Flask, request, jsonify, render_template_string
app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict():
    try:
        input_data = request.json if request.is_json else request.form
        result = predict_failure({
            "brake_pressure": float(input_data["brake_pressure"]),
            "brake_temp": float(input_data["brake_temp"]),
            "vehicle_speed": float(input_data["vehicle_speed"]),
            "pad_wear_level": float(input_data["pad_wear_level"])
        })
        if request.is_json:
            return jsonify(result)
        else:
            return render_template_string("""
            <h2>Prediction Result</h2>
            <p><strong>Failure Probability:</strong> {{ result.failure_probability }}</p>
            <p><strong>Will Fail:</strong> {{ result.will_fail }}</p>
            <a href='/'>Back</a>
            """, result=result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def form():
    return render_template_string("""
    <h2>Brake Failure Prediction</h2>
    <form action="/predict" method="post">
        Brake Pressure: <input name="brake_pressure" type="number" step="any" required><br>
        Brake Temperature: <input name="brake_temp" type="number" step="any" required><br>
        Vehicle Speed: <input name="vehicle_speed" type="number" step="any" required><br>
        Pad Wear Level: <input name="pad_wear_level" type="number" step="any" required><br>
        <input type="submit" value="Predict">
    </form>
    """)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

# ✅ Example cURL request:
# curl -X POST http://localhost:5000/predict \
# -H "Content-Type: application/json" \
# -d '{"brake_pressure": 135, "brake_temp": 98, "vehicle_speed": 70, "pad_wear_level": 92}'

# ✅ requirements.txt
# Save as requirements.txt in your project folder
'''
pandas
scikit-learn
mlflow
flask
numpy
'''
