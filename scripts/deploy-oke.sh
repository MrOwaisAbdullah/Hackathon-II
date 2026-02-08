#!/bin/bash
# TeamFlow Oracle OKE Deployment Script
# Run this in Oracle Cloud Shell after completing all setup steps

set -e

echo "=== TeamFlow Oracle OKE Deployment ==="
echo ""

# Check if namespace exists
if kubectl get namespace teamflow >/dev/null 2>&1; then
  echo "Namespace 'teamflow' already exists"
else
  echo "Creating namespace 'teamflow'..."
  kubectl create namespace teamflow
fi

# Check if secrets exist
if kubectl get secret teamflow-secrets -n teamflow >/dev/null 2>&1; then
  echo "Secret 'teamflow-secrets' already exists"
else
  echo "ERROR: Secret 'teamflow-secrets' not found!"
  echo "Please create it first using:"
  echo "kubectl create secret generic teamflow-secrets \\"
  echo "  --namespace teamflow \\"
  echo "  --from-literal=database-url='your-db-url' \\"
  echo "  --from-literal=openai-api-key='your-key' \\"
  echo "  --from-literal=jwt-secret='your-secret' \\"
  echo "  --from-literal=better-auth-secret='your-secret'"
  exit 1
fi

# Check if Dapr is installed
if kubectl get namespace dapr-system >/dev/null 2>&1; then
  echo "Dapr is installed"
else
  echo "ERROR: Dapr not found!"
  echo "Please install it first using: dapr init -k --runtime-version 1.14.0"
  exit 1
fi

# Check if Kafka is running
if kubectl get pods -n kafka -l app.kubernetes.io/name=strimzi-kafka-operator >/dev/null 2>&1; then
  echo "Kafka/Strimzi is installed"
else
  echo "WARNING: Kafka not found in 'kafka' namespace"
  echo "Events will not work without Kafka!"
fi

echo ""
echo "=== Deploying TeamFlow with Helm ==="

# Deploy using inline values (since values-oke.yaml may not be in Cloud Shell)
helm install teamflow ./helm/teamflow \
  --namespace teamflow \
  --set frontend.image.repository=mrowaisabdullah/teamflow-frontend \
  --set frontend.image.tag=latest \
  --set frontend.dapr.enabled=false \
  --set frontend.replicaCount=1 \
  --set backend.image.repository=mrowaisabdullah/teamflow-backend \
  --set backend.image.tag=latest \
  --set backend.dapr.enabled=true \
  --set backend.dapr.appId=teamflow-backend \
  --set backend.dapr.appPort=8000 \
  --set backend.replicaCount=1 \
  --set secrets.existingSecret=teamflow-secrets \
  --set ingress.enabled=false \
  --wait --timeout 10m

echo ""
echo "=== Deployment Complete! ==="
echo ""
echo "Checking pods..."
kubectl get pods -n teamflow

echo ""
echo "Checking services..."
kubectl get svc -n teamflow

echo ""
echo "To access the application, use port-forwarding:"
echo "  kubectl port-forward -n teamflow svc/teamflow-frontend 3000:3000"
echo ""
echo "Then open: http://localhost:3000"
