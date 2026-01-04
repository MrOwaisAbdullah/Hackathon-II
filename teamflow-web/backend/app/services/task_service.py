"""Task service for task CRUD operations."""
from typing import Optional
from uuid import UUID

from sqlmodel import Session, col, select
from sqlalchemy.orm import selectinload

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
        # Load assignee relationship for response
        task_with_assignee = session.exec(
            select(Task)
            .options(selectinload(Task.assignee))
            .where(Task.id == task.id)
        ).first()
        return task_with_assignee or task

    def get_task(
        self,
        task_id: UUID,
        agency_id: UUID,
        session: Session,
    ) -> Optional[Task]:
        """Get a task by ID (scoped to agency)."""
        return session.exec(
            select(Task)
            .options(selectinload(Task.assignee))
            .where(
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
        include_archived: bool = False,
    ) -> list[Task]:
        """List tasks for an agency with optional filters."""
        query = select(Task).options(selectinload(Task.assignee)).where(Task.agency_id == agency_id)

        if status:
            query = query.where(Task.status == status)
        if project_id:
            query = query.where(Task.project_id == project_id)
        if assignee_id:
            query = query.where(Task.assignee_id == assignee_id)

        # Exclude archived tasks by default unless include_archived=True
        if not include_archived:
            query = query.where(Task.status != TaskStatus.ARCHIVED)

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
        # Return task with assignee relationship loaded
        return self.get_task(task_id, agency_id, session)

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

    def assign_task(
        self,
        task_id: UUID,
        assignee_id: UUID,
        agency_id: UUID,
        session: Session,
    ) -> Optional[Task]:
        """Assign a task to a user.

        Args:
            task_id: ID of the task to assign
            assignee_id: ID of the user to assign the task to (or None to unassign)
            agency_id: Agency ID for multi-tenant isolation
            session: Database session

        Returns:
            The updated task, or None if task not found

        Raises:
            ValueError: If assignee doesn't exist or doesn't belong to the agency
        """
        task = self.get_task(task_id, agency_id, session)
        if not task:
            return None

        # If assignee_id is None, unassign the task
        if assignee_id is None:
            task.assignee_id = None
            session.add(task)
            session.commit()
            session.refresh(task)
            # Load with assignee relationship (will be None)
            return self.get_task(task_id, agency_id, session)

        # Verify assignee exists and belongs to the same agency
        assignee = session.get(User, assignee_id)
        if not assignee:
            raise ValueError("Assignee not found")
        if assignee.agency_id != agency_id:
            raise ValueError("Assignee does not belong to the same agency")

        # Update the task's assignee
        task.assignee_id = assignee_id
        session.add(task)
        session.commit()
        session.refresh(task)
        # Return task with assignee relationship loaded
        return self.get_task(task_id, agency_id, session)

    def archive_task(
        self,
        task_id: UUID,
        agency_id: UUID,
        session: Session,
    ) -> Optional[Task]:
        """Archive a task by setting status to ARCHIVED.

        Args:
            task_id: ID of the task to archive
            agency_id: Agency ID for multi-tenant isolation
            session: Database session

        Returns:
            The archived task, or None if task not found
        """
        task = self.get_task(task_id, agency_id, session)
        if not task:
            return None

        task.status = TaskStatus.ARCHIVED
        session.add(task)
        session.commit()
        session.refresh(task)
        # Return task with assignee relationship loaded
        return self.get_task(task_id, agency_id, session)

    def restore_task(
        self,
        task_id: UUID,
        agency_id: UUID,
        session: Session,
        restore_status: TaskStatus = TaskStatus.DONE,
    ) -> Optional[Task]:
        """Restore an archived task to a specified status.

        Args:
            task_id: ID of the task to restore
            agency_id: Agency ID for multi-tenant isolation
            session: Database session
            restore_status: Status to restore the task to (default: DONE)

        Returns:
            The restored task, or None if task not found
        """
        task = self.get_task(task_id, agency_id, session)
        if not task:
            return None

        # Only allow restoring archived tasks
        if task.status != TaskStatus.ARCHIVED:
            raise ValueError("Task is not archived")

        task.status = restore_status
        session.add(task)
        session.commit()
        session.refresh(task)
        # Return task with assignee relationship loaded
        return self.get_task(task_id, agency_id, session)
