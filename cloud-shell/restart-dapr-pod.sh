#!/bin/bash
# Restart backend pod to reload Dapr components

echo "=== Restarting backend deployment ==="
kubectl rollout restart deployment/teamflow-backend -n teamflow

echo ""
echo "=== Waiting for rollout to complete ==="
kubectl rollout status deployment/teamflow-backend -n teamflow

echo ""
echo "=== New pods after restart ==="
kubectl get pods -n teamflow -l app=teamflow-backend

echo ""
echo "=== Waiting 10 seconds for Dapr to fully start ==="
sleep 10

echo ""
echo "=== Checking Dapr metadata (should show 3 components) ==="
kubectl exec -it deployment/teamflow-backend -n teamflow -- curl -s http://localhost:3500/v1.0/metadata | jq .

echo ""
echo "=== Checking Dapr sidecar logs for loaded components ==="
kubectl logs -l app=teamflow-backend -n teamflow -c daprd --tail=30 | grep -i "component\|loaded"

echo ""
echo "=== Testing Dapr event publishing ==="
kubectl exec -it deployment/teamflow-backend -n teamflow -- curl -X POST "http://localhost:3500/v1.0/publish/kafka-pubsub/task-events" \
  -H "Content-Type: application/cloudevents+json" \
  -d '{"specversion":"1.0","type":"teamflow.task.test","source":"teamflow-backend","id":"test-001","time":"2026-02-08T12:00:00Z","datacontenttype":"application/json","data":{"task_id":"test-task-001","project_id":"test-project-001","user_id":"test-user-001","title":"Test Task from Dapr","status":"TODO"}}'
