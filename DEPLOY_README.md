# Brake Failure — CI/CD & Deployment (AWS ECR + EC2 + MLflow)

## 1) AWS Setup (one-time)
- Create an **ECR** repo: `brake-failure-api` in `ap-south-1` (or change in workflow).
- Launch an **EC2 Ubuntu 22.04** instance with a public IP. Use `deploy/ec2_bootstrap.sh` as user data.
- Open **Security Group** for ports 22 (SSH) and 80 (HTTP).
- On GitHub repo **Settings → Secrets and variables → Actions**, add:
  - `AWS_ACCOUNT_ID`
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `EC2_HOST` (e.g., `ec2-xx-xx-xx-xx.compute.amazonaws.com`)
  - `EC2_USER` (e.g., `ubuntu`)
  - `EC2_SSH_KEY` (private key contents)
  - `MLFLOW_TRACKING_URI` (e.g., `http://<mlflow-host>:5000`)
  - `MODEL_REGISTRY_URI` (e.g., `models:/BrakeFailurePrediction/Production` or leave empty to use run_id)

## 2) Local Test
```bash
python -m pip install -r requirements.txt
python train_model.py  # writes model/run_id.txt and logs to MLflow
export MLFLOW_TRACKING_URI=http://localhost:5000  # or your MLflow
export MODEL_URI=runs:/$(cat model/run_id.txt)/model
python app.py
curl -X POST http://127.0.0.1:5000/predict -H "Content-Type: application/json"       -d '{"brake_pressure": 135, "brake_temp": 98, "vehicle_speed": 70, "pad_wear_level": 92}'
```

## 3) Build & Run Container Locally
```bash
docker build -t brake-failure-api:dev .
docker run --rm -p 5000:5000 -e MLFLOW_TRACKING_URI=$MLFLOW_TRACKING_URI -e MODEL_URI=$MODEL_URI brake-failure-api:dev
```

## 4) CI/CD (GitHub Actions)
- Push to `main` → pipeline trains, pushes image to ECR, deploys to EC2.
- EC2 container starts with `MODEL_URI` from your secret `MODEL_REGISTRY_URI`.

## 5) Predict
```bash
curl http://<EC2_PUBLIC_IP>/health
curl -X POST http://<EC2_PUBLIC_IP>/predict -H "Content-Type: application/json"       -d '{"brake_pressure": 135, "brake_temp": 98, "vehicle_speed": 70, "pad_wear_level": 92}'
```



---

## 6) Local one-command test with Docker Compose
```bash
# start MLflow on :5000 and API on :8080
docker compose up -d --build
# train locally and log to MLflow (hosted in the compose stack)
export MLFLOW_TRACKING_URI=http://localhost:5000
python train_model.py
# get run id then call API
export MODEL_URI=runs:/$(cat model/run_id.txt)/model
curl -X POST http://localhost:8080/predict -H "Content-Type: application/json"   -d '{"brake_pressure": 135, "brake_temp": 98, "vehicle_speed": 70, "pad_wear_level": 92}'
```

## 7) Makefile shortcuts
```bash
# train locally
make train

# bring up MLflow+API stack
make compose-up

# build local image
make build

# push to ECR (after login)
export AWS_REGION=ap-south-1 AWS_ACCOUNT_ID=<id>
make ecr-login
make push
```

## 8) Create ECR repo quickly
```bash
export AWS_REGION=ap-south-1 AWS_ACCOUNT_ID=<id>
./scripts/create_ecr_repo.sh brake-failure-api
```
