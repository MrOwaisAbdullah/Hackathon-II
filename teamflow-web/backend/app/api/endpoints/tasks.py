"""Tasks API endpoints."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.core.deps import CurrentUser, SessionDep
from app.models.task import Task, TaskCreate, TaskRead, TaskStatus, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])
task_service = TaskService()


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    current_user: CurrentUser,
    session: SessionDep,
) -> Task:
    """Create a new task for the current agency."""
    try:
        return task_service.create_task(task_data, current_user.agency_id, session)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("", response_model=list[TaskRead])
def list_tasks(
    current_user: CurrentUser,
    session: SessionDep,
    status: Optional[TaskStatus] = None,
    project_id: Optional[UUID] = None,
    assignee_id: Optional[UUID] = None,
) -> list[TaskRead]:
    """List all tasks for the current agency with optional filters."""
    return task_service.list_tasks(
        current_user.agency_id,
        session,
        status=status,
        project_id=project_id,
        assignee_id=assignee_id,
    )


@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: UUID,
    current_user: CurrentUser,
    session: SessionDep,
) -> Task:
    """Get a task by ID."""
    task = task_service.get_task(task_id, current_user.agency_id, session)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    current_user: CurrentUser,
    session: SessionDep,
) -> Task:
    """Update a task."""
    try:
        task = task_service.update_task(task_id, task_data, current_user.agency_id, session)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
        return task
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: UUID,
    current_user: CurrentUser,
    session: SessionDep,
) -> None:
    """Delete a task."""
    if not task_service.delete_task(task_id, current_user.agency_id, session):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
