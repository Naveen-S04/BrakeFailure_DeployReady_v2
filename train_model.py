import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
import os
from mlflow.models.signature import infer_signature
from flask import Flask, request, jsonify

# -----------------------
# 1. Load Dataset
# -----------------------
df = pd.read_csv("data/brake_sensor_data.csv")  # Update path if needed
X = df.drop("failure", axis=1)
y = df["failure"]

# -----------------------
# 2. Train/Test Split
# -----------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -----------------------
# 3. Train Model
# -----------------------
model = LogisticRegression(max_iter=200)
model.fit(X_train, y_train)

# -----------------------
# 4. Evaluate
# -----------------------
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]
accuracy = accuracy_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_prob)

print(f"Model trained with Accuracy: {accuracy:.3f}, ROC AUC: {roc_auc:.3f}")

# -----------------------
# 5. MLflow Logging (corrected)
# -----------------------
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))
mlflow.set_experiment("Brake Failure Detection")

# Create input example and signature
input_example = X_train.head(5)
signature = infer_signature(X_train, model.predict(X_train))

with mlflow.start_run():
    # Log metrics
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("roc_auc", roc_auc)

    # Log model properly
    mlflow.sklearn.log_model(
        sk_model=model,
        name="BrakeFailureModel",     # ✅ use 'name' instead of deprecated 'artifact_path'
        signature=signature,          # ✅ input/output schema
        input_example=input_example   # ✅ example input
    )
    print("✅ Model logged successfully with MLflow")

# -----------------------
# 6. Flask API for Prediction
# -----------------------
app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        df_input = pd.DataFrame(data)
        preds = model.predict(df_input)
        probs = model.predict_proba(df_input)[:, 1]
        return jsonify({"prediction": preds.tolist(), "probability": probs.tolist()})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
