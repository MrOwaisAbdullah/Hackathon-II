#!/bin/bash
helm install teamflow ./helm/teamflow \
  --namespace teamflow \
  --set frontend.image.repository=mrowaisabdullah/teamflow-frontend \
  --set frontend.image.tag=latest \
  --set backend.image.repository=mrowaisabdullah/teamflow-backend \
  --set backend.image.tag=latest \
  --set backend.dapr.enabled=true \
  --set frontend.dapr.enabled=false \
  --set secrets.existingSecret=teamflow-secrets \
  --set ingress.enabled=false \
  --wait --timeout 10m
