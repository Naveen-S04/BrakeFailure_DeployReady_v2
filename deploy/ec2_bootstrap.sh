#!/usr/bin/env bash
set -e
sudo apt-get update -y
sudo apt-get install -y docker.io
sudo usermod -aG docker ubuntu || true
sudo systemctl enable docker
sudo systemctl start docker
# Install AWS CLI v2
if ! command -v aws >/dev/null 2>&1; then
  curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
  unzip -q awscliv2.zip
  sudo ./aws/install
fi
