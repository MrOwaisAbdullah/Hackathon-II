"""Tasks API endpoints."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.core.deps import CurrentUser, SessionDep
from app.core.logging import get_logger, log_api_call
from app.models.task import Task, TaskAssign, TaskCreate, TaskRead, TaskStatus, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])
task_service = TaskService()
# T155: Structured logger for tasks endpoint
logger = get_logger("api.tasks")


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    current_user: CurrentUser,
    session: SessionDep,
) -> Task:
    """Create a new task for the current agency."""
    try:
        task = task_service.create_task(task_data, current_user.agency_id, session)
        # T155: Log task creation
        log_api_call(
            logger,
            endpoint="POST /api/v1/tasks",
            action="create_task",
            user_id=current_user.id,
            agency_id=current_user.agency_id,
            task_id=str(task.id),
            task_title=task.title,
            task_status=task.status,
        )
        return task
    except ValueError as e:
        logger.warning(
            f"Failed to create task: {str(e)}",
            user_id=current_user.id,
            agency_id=current_user.agency_id,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("", response_model=dict[str, list[TaskRead]])
def list_tasks(
    current_user: CurrentUser,
    session: SessionDep,
    status: Optional[TaskStatus] = None,
    project_id: Optional[UUID] = None,
    assignee_id: Optional[UUID] = None,
    include: Optional[str] = Query(None, description="Include additional data (e.g., 'archived')"),
) -> dict[str, list[TaskRead]]:
    """List all tasks for the current agency with optional filters.

    Args:
        status: Filter by task status
        project_id: Filter by project ID
        assignee_id: Filter by assignee ID
        include: Include archived tasks ('archived') or other special data
    """
    include_archived = include == "archived"
    tasks = task_service.list_tasks(
        current_user.agency_id,
        session,
        status=status,
        project_id=project_id,
        assignee_id=assignee_id,
        include_archived=include_archived,
    )
    return {"tasks": tasks}


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
            logger.warning(
                f"Task not found for update: {task_id}",
                user_id=current_user.id,
                agency_id=current_user.agency_id,
                task_id=str(task_id),
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
        # T155: Log task update
        log_api_call(
            logger,
            endpoint="PATCH /api/v1/tasks/{id}",
            action="update_task",
            user_id=current_user.id,
            agency_id=current_user.agency_id,
            task_id=str(task_id),
            updated_fields=list(task_data.model_fields_set or []),
        )
        return task
    except ValueError as e:
        logger.warning(
            f"Failed to update task: {str(e)}",
            user_id=current_user.id,
            agency_id=current_user.agency_id,
            task_id=str(task_id),
        )
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


@router.post("/{task_id}/assign", response_model=TaskRead)
def assign_task(
    task_id: UUID,
    assignment: TaskAssign,
    current_user: CurrentUser,
    session: SessionDep,
) -> Task:
    """Assign a task to a user."""
    try:
        task = task_service.assign_task(
            task_id,
            assignment.assignee_id,
            current_user.agency_id,
            session,
        )
        if not task:
            logger.warning(
                f"Task not found for assignment: {task_id}",
                user_id=current_user.id,
                agency_id=current_user.agency_id,
                task_id=str(task_id),
                assignee_id=str(assignment.assignee_id) if assignment.assignee_id else None,
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
        # T155: Log task assignment
        log_api_call(
            logger,
            endpoint="POST /api/v1/tasks/{id}/assign",
            action="assign_task",
            user_id=current_user.id,
            agency_id=current_user.agency_id,
            task_id=str(task_id),
            assigned_to=str(assignment.assignee_id) if assignment.assignee_id else None,
            previous_assignee=str(task.assignee_id) if task.assignee_id else None,
        )
        return task
    except ValueError as e:
        logger.warning(
            f"Failed to assign task: {str(e)}",
            user_id=current_user.id,
            agency_id=current_user.agency_id,
            task_id=str(task_id),
            assignee_id=str(assignment.assignee_id) if assignment.assignee_id else None,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{task_id}/archive", response_model=TaskRead)
def archive_task(
    task_id: UUID,
    current_user: CurrentUser,
    session: SessionDep,
) -> Task:
    """Archive a task by setting its status to ARCHIVED.

    Archived tasks are soft-deleted and can be restored later.
    They are excluded from default task listings.
    """
    task = task_service.archive_task(task_id, current_user.agency_id, session)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


@router.post("/{task_id}/restore", response_model=TaskRead)
def restore_task(
    task_id: UUID,
    current_user: CurrentUser,
    session: SessionDep,
) -> Task:
    """Restore an archived task to active status.

    Restores the task to DONE status by default.
    """
    try:
        task = task_service.restore_task(task_id, current_user.agency_id, session)
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
