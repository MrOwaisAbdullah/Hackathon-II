"""
T045-T050: Recurring Task Service Microservice

This FastAPI microservice handles recurring task automation by:
1. Subscribing to task-events from Kafka via Dapr
2. Filtering for task.completed events
3. Calculating next instance dates using RecurrenceCalculator
4. Creating new task instances via backend API

Event Flow:
Backend (task.completed) → Kafka → Dapr → RecurringTaskService → Backend API (create task)
"""

import asyncio
import structlog
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
import httpx

# Configure structured logging
logger = structlog.get_logger(__name__)

# Configuration
BACKEND_API_URL = "http://teamflow-backend.teamflow.svc.cluster.local:8000"
DAPR_HTTP_PORT = 3500

app = FastAPI(
    title="Recurring Task Service",
    description="Microservice for automatic recurring task instance creation",
    version="1.0.0",
)


# Pydantic models
class TaskCompletedEvent(BaseModel):
    """Task completed event from Kafka."""

    task_id: str
    project_id: str
    user_id: str
    title: str
    status: str
    recurrence_rule: Optional[dict] = Field(default=None)
    timestamp: str


class CreateTaskRequest(BaseModel):
    """Request to create a new task instance."""

    title: str
    description: Optional[str] = None
    status: str = "TODO"
    priority: Optional[str] = "MEDIUM"
    project_id: str
    assignee_id: Optional[str] = None
    due_date: Optional[str] = None
    recurrence_rule: Optional[dict] = None


# T046: Dapr subscription endpoint
@app.get("/dapr/subscribe")
async def dapr_subscribe():
    """
    Dapr subscription endpoint.

    Returns the list of topic subscriptions for this service.
    Dapr calls this on startup to discover which topics to subscribe to.
    """
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/events/task-events",
        }
    ]


# T047: Event handler for task completion events
@app.post("/events/task-events")
async def handle_task_event(request: Request):
    """
    Handle task events from Kafka via Dapr.

    Only processes task.completed events with recurrence_rule.
    Skips non-recurring tasks to avoid unnecessary processing.
    """
    try:
        # Parse CloudEvents envelope from Dapr
        event_data = await request.json()

        # Dapr sends data in format: { data: [ { actual_event } ] }
        if "data" in event_data:
            events = event_data["data"]
        else:
            events = [event_data]

        results = []
        for event in events:
            result = await process_task_completed_event(event)
            results.append(result)

        return {"status": "SUCCESS"}

    except Exception as e:
        logger.error("handle_task_event_failed", error=str(e))
        return {"status": "ERROR", "message": str(e)}


async def process_task_completed_event(event: dict) -> str:
    """
    Process a single task completed event.

    T048: Calculate next instance date using RecurrenceCalculator
    T049: Implement next instance creation via backend API
    """
    try:
        # Parse event data
        task_event = TaskCompletedEvent(**event)

        # Filter: Only process completed tasks with recurrence_rule
        if task_event.status != "DONE" and task_event.status != "completed":
            return "SKIPPED: Not a completed event"

        if not task_event.recurrence_rule:
            return "SKIPPED: Not a recurring task"

        logger.info(
            "processing_recurring_task",
            task_id=task_event.task_id,
            title=task_event.title,
        )

        # T048: Calculate next instance date
        next_due_date = await calculate_next_instance_date(task_event)

        if not next_due_date:
            logger.info("recurrence_ended", task_id=task_event.task_id)
            return "SUCCESS: Recurrence ended"

        # T049: Create next instance via backend API
        new_task_id = await create_next_instance(task_event, next_due_date)

        logger.info(
            "next_instance_created",
            original_task_id=task_event.task_id,
            new_task_id=new_task_id,
            next_due_date=next_due_date,
        )

        return "SUCCESS: Next instance created"

    except Exception as e:
        logger.error("process_task_event_failed", task_id=event.get("task_id"), error=str(e))
        return f"ERROR: {str(e)}"


async def calculate_next_instance_date(task_event: TaskCompletedEvent) -> Optional[str]:
    """
    T048: Calculate next instance date using RecurrenceCalculator.

    Returns ISO 8601 formatted datetime string, or None if recurrence ended.
    """
    try:
        # Import RecurrenceCalculator (may need to load from backend service code)
        # For microservice, we'll need to either:
        # 1. Duplicate the logic (simpler, independent service)
        # 2. Call backend API (adds latency, depends on backend)
        # 3. Share via common package (best for DRY)

        # For this implementation, we'll use option 2 - call backend API
        # This allows the backend to own the recurrence logic

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_API_URL}/api/recurrence/calculate",
                json={
                    "current_date": task_event.timestamp,
                    "recurrence_rule": task_event.recurrence_rule,
                },
                timeout=10.0,
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("next_date")
            else:
                logger.error(
                    "calculate_next_date_failed",
                    status_code=response.status_code,
                    response_text=response.text,
                )
                return None

    except Exception as e:
        logger.error("calculate_next_date_exception", error=str(e))
        return None


async def create_next_instance(task_event: TaskCompletedEvent, due_date: str) -> str:
    """
    T049: Create next task instance via backend API.

    Returns the new task ID.
    """
    try:
        async with httpx.AsyncClient() as client:
            # Create task request with same fields as original
            create_request = CreateTaskRequest(
                title=task_event.title,
                project_id=task_event.project_id,
                assignee_id=task_event.user_id,
                due_date=due_date.split("T")[0] if due_date else None,
                recurrence_rule=task_event.recurrence_rule,
            )

            response = await client.post(
                f"{BACKEND_API_URL}/api/tasks",
                json=create_request.model_dump(exclude_none=True),
                timeout=30.0,
            )

            if response.status_code == 201 or response.status_code == 200:
                result = response.json()
                return result.get("id", "")
            else:
                logger.error(
                    "create_task_failed",
                    status_code=response.status_code,
                    response_text=response.text,
                )
                raise HTTPException(status_code=500, detail="Failed to create task")

    except Exception as e:
        logger.error("create_next_instance_exception", error=str(e))
        raise


# T050: Health and readiness endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes liveness probe."""
    return {"status": "healthy", "service": "recurring-task-service"}


@app.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint for Kubernetes readiness probe.

    Checks if backend API is accessible.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BACKEND_API_URL}/health",
                timeout=5.0,
            )
            if response.status_code == 200:
                return {"status": "ready", "service": "recurring-task-service"}
            else:
                return {"status": "not_ready", "service": "recurring-task-service", "reason": "backend_unavailable"}
    except Exception as e:
        return {"status": "not_ready", "service": "recurring-task-service", "reason": str(e)}


@app.get("/")
async def root():
    """Root endpoint for service information."""
    return {
        "service": "Recurring Task Service",
        "version": "1.0.0",
        "status": "running",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
