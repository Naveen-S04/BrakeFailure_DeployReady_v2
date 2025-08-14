#!/usr/bin/env bash
set -euo pipefail
: "${AWS_REGION:?set AWS_REGION}"
: "${AWS_ACCOUNT_ID:?set AWS_ACCOUNT_ID}"
REPO_NAME=${1:-brake-failure-api}
aws ecr describe-repositories --repository-names "$REPO_NAME" --region "$AWS_REGION" >/dev/null 2>&1 ||   aws ecr create-repository --repository-name "$REPO_NAME" --region "$AWS_REGION" >/dev/null
echo "ECR repo ensured: ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO_NAME}"
