#!/bin/bash
# Fix ImagePullBackOff by adding Docker Hub credentials

echo "Step 1: Login to Docker Hub"
echo "When prompted, enter your Docker Hub username and password"
docker login

echo ""
echo "Step 2: Create Kubernetes secret for Docker Hub"
echo "Replace YOUR_DOCKER_HUB_PASSWORD with your actual password"
kubectl create secret docker-registry docker-hub-secret \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=mrowaisabdullah \
  --docker-password=YOUR_DOCKER_HUB_PASSWORD \
  --namespace teamflow \
  --dry-run=client -o yaml | kubectl apply -f -

echo ""
echo "Step 3: Patch deployments to use the secret"
kubectl patch deployment teamflow-backend -n teamflow -p '{"spec":{"template":{"spec":{"imagePullSecrets":[{"name":"docker-hub-secret"}]}}}}'

kubectl patch deployment teamflow-frontend -n teamflow -p '{"spec":{"template":{"spec":{"imagePullSecrets":[{"name":"docker-hub-secret"}]}}}}'

echo ""
echo "Step 4: Delete old pods so new ones can be created with the secret"
kubectl delete pod teamflow-backend-78b99499bd-xfj6k -n teamflow
kubectl delete pod teamflow-frontend-6996d9b696-5l2l7 -n teamflow

echo ""
echo "Step 5: Watch new pods starting"
kubectl get pods -n teamflow -w
