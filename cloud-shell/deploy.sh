#!/bin/bash
# TeamFlow Oracle OKE Deployment Script
# Run this in Oracle Cloud Shell

echo "=== Deploying TeamFlow Backend ==="
kubectl apply -f backend-deployment.yaml

echo ""
echo "=== Deploying TeamFlow Frontend ==="
kubectl apply -f frontend-deployment.yaml

echo ""
echo "=== Waiting for pods to be ready ==="
kubectl wait --for=condition=ready pod -l app=teamflow-backend -n teamflow --timeout=300s
kubectl wait --for=condition=ready pod -l app=teamflow-frontend -n teamflow --timeout=300s

echo ""
echo "=== Deployment Complete! ==="
echo ""
echo "Checking pods..."
kubectl get pods -n teamflow

echo ""
echo "Checking services..."
kubectl get svc -n teamflow

echo ""
echo "To access the application:"
echo "  kubectl port-forward -n teamflow svc/teamflow-frontend 3000:3000"
echo ""
echo "Then open: http://localhost:3000"
