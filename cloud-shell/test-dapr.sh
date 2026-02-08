#!/bin/bash
# Test Dapr event publishing to Kafka

curl -X POST "http://localhost:3500/v1.0/publish/kafka-pubsub/task-events" \
  -H "Content-Type: application/cloudevents+json" \
  -d '{"specversion":"1.0","type":"teamflow.task.test","source":"teamflow-backend","id":"test-001","time":"2026-02-08T12:00:00Z","datacontenttype":"application/json","data":{"task_id":"test-task-001","project_id":"test-project-001","user_id":"test-user-001","title":"Test Task from Dapr","status":"TODO"}}'
