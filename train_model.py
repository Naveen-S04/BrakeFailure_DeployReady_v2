import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
import os
from mlflow.models.signature import infer_signature

# Load dataset
df = pd.read_csv("data/brake_sensor_data.csv")  # Change to your dataset path
X = df.drop("failure", axis=1)
y = df["failure"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = LogisticRegression(max_iter=200)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_pred)

print(f"Model trained with Accuracy: {accuracy:.3f}, ROC AUC: {roc_auc}")

# Log with MLflow
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))
mlflow.set_experiment("Brake Failure Detection")

with mlflow.start_run():
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("roc_auc", roc_auc)
    mlflow.sklearn.log_model(model, "model")
