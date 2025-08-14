.PHONY: help train build run stop logs ecr-login push deploy compose-up compose-down

help:
	@echo "Targets:"
	@echo "  train        - Train locally and log to MLflow (requires MLFLOW_TRACKING_URI env)"
	@echo "  build        - Build Docker image 'brake-failure-api:dev'"
	@echo "  run          - Run container locally on :8080"
	@echo "  stop         - Stop local container"
	@echo "  logs         - Tail API logs"
	@echo "  compose-up   - Start local MLflow + API via docker-compose"
	@echo "  compose-down - Stop local compose stack"
	@echo "  ecr-login    - Docker login to ECR"
	@echo "  push         - Tag & push image to ECR"
	@echo "  deploy       - Pull & run on EC2 via SSH (requires SSH_* env variables)"

train:
	python -m pip install -r requirements.txt
	python train_model.py

build:
	docker build -t brake-failure-api:dev .

run:
	docker run -d --name brake-failure-api -p 8080:5000 \
	  -e MLFLOW_TRACKING_URI=$${MLFLOW_TRACKING_URI} \
	  -e MODEL_URI=$${MODEL_URI} \
	  brake-failure-api:dev

stop:
	-docker stop brake-failure-api || true && docker rm brake-failure-api || true

logs:
	docker logs -f brake-failure-api

compose-up:
	docker compose up -d --build

compose-down:
	docker compose down -v

ecr-login:
	aws ecr get-login-password --region $${AWS_REGION} | docker login --username AWS --password-stdin $${AWS_ACCOUNT_ID}.dkr.ecr.$${AWS_REGION}.amazonaws.com

push:
	docker tag brake-failure-api:dev $${AWS_ACCOUNT_ID}.dkr.ecr.$${AWS_REGION}.amazonaws.com/brake-failure-api:latest
	docker push $${AWS_ACCOUNT_ID}.dkr.ecr.$${AWS_REGION}.amazonaws.com/brake-failure-api:latest

deploy:
	ssh -i "$${SSH_KEY_PATH}" $${SSH_USER}@$${SSH_HOST} \
	  'docker login -u AWS -p $$(aws ecr get-login-password --region '"$${AWS_REGION}"') $${AWS_ACCOUNT_ID}.dkr.ecr.$${AWS_REGION}.amazonaws.com && \
	   docker pull $${AWS_ACCOUNT_ID}.dkr.ecr.$${AWS_REGION}.amazonaws.com/brake-failure-api:latest && \
	   docker stop brake-failure-api || true && docker rm brake-failure-api || true && \
	   docker run -d --name brake-failure-api -p 80:5000 \
	     -e MLFLOW_TRACKING_URI=$${MLFLOW_TRACKING_URI} \
	     -e MODEL_URI=$${MODEL_URI} \
	     $${AWS_ACCOUNT_ID}.dkr.ecr.$${AWS_REGION}.amazonaws.com/brake-failure-api:latest'
