"""Task service for task CRUD operations."""
from typing import Optional
from uuid import UUID

from sqlmodel import Session, col, select

from app.models.project import Project
from app.models.task import Task, TaskCreate, TaskUpdate, TaskStatus
from app.models.user import User


class TaskService:
    """Service for task operations."""

    def create_task(
        self,
        task_data: TaskCreate,
        agency_id: UUID,
        session: Session,
    ) -> Task:
        """Create a new task for an agency."""
        # Verify project exists and belongs to agency
        if task_data.project_id:
            project = session.get(Project, task_data.project_id)
            if not project or project.agency_id != agency_id:
                raise ValueError("Invalid project")

        # Verify assignee exists and belongs to agency
        if task_data.assignee_id:
            assignee = session.get(User, task_data.assignee_id)
            if not assignee or assignee.agency_id != agency_id:
                raise ValueError("Invalid assignee")

        task = Task(
            **task_data.model_dump(exclude_unset=True),
            agency_id=agency_id,
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    def get_task(
        self,
        task_id: UUID,
        agency_id: UUID,
        session: Session,
    ) -> Optional[Task]:
        """Get a task by ID (scoped to agency)."""
        return session.exec(
            select(Task).where(
                Task.id == task_id,
                Task.agency_id == agency_id,
            )
        ).first()

    def list_tasks(
        self,
        agency_id: UUID,
        session: Session,
        status: Optional[TaskStatus] = None,
        project_id: Optional[UUID] = None,
        assignee_id: Optional[UUID] = None,
    ) -> list[Task]:
        """List tasks for an agency with optional filters."""
        query = select(Task).where(Task.agency_id == agency_id)

        if status:
            query = query.where(Task.status == status)
        if project_id:
            query = query.where(Task.project_id == project_id)
        if assignee_id:
            query = query.where(Task.assignee_id == assignee_id)

        # Order by status then created_at
        query = query.order_by(Task.status, Task.created_at.desc())

        return session.exec(query).all()

    def update_task(
        self,
        task_id: UUID,
        task_data: TaskUpdate,
        agency_id: UUID,
        session: Session,
    ) -> Optional[Task]:
        """Update a task."""
        task = self.get_task(task_id, agency_id, session)
        if not task:
            return None

        # Verify project belongs to agency
        if task_data.project_id:
            project = session.get(Project, task_data.project_id)
            if not project or project.agency_id != agency_id:
                raise ValueError("Invalid project")

        # Verify assignee belongs to agency
        if task_data.assignee_id:
            assignee = session.get(User, task_data.assignee_id)
            if not assignee or assignee.agency_id != agency_id:
                raise ValueError("Invalid assignee")

        task_data_dict = task_data.model_dump(exclude_unset=True)
        for field, value in task_data_dict.items():
            setattr(task, field, value)

        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    def delete_task(
        self,
        task_id: UUID,
        agency_id: UUID,
        session: Session,
    ) -> bool:
        """Soft delete a task by marking with deleted status."""
        # For now, we'll do actual delete
        # In production, you might want soft delete with a deleted_at field
        task = self.get_task(task_id, agency_id, session)
        if not task:
            return False

        session.delete(task)
        session.commit()
        return True
