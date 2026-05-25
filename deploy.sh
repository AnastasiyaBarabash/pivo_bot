#!/bin/bash
set -e

source .env

echo "Собираю..."
docker build -t bar-backend:latest ./backend
docker build -t bar-frontend:latest ./frontend
docker build -t bar-bot:latest ./bot

echo "Деплой в Kubernetes..."
kubectl apply -f k8s/namespace.yaml

kubectl create secret generic bar-bot-secret \
  --namespace=party-hard \
  --from-literal=telegram-token="$TELEGRAM_TOKEN" \
  --dry-run=client -o yaml | kubectl apply -f -
 
echo "Взлетаем!..."
kubectl apply -f k8s/
 
echo "Можно идти пить! Интерфейс бармена: http://<NODE_IP>:30080"