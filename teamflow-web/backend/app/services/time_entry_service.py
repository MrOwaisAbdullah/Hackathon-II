"""Time Entry service for time tracking operations."""
from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, col, select, and_, func
from sqlalchemy import case

from app.models.time_entry import TimeEntry, TimeEntryCreate, TimeEntryUpdate
from app.models.task import Task
from app.models.user import User
from app.models.project import Project


class TimeEntryService:
    """Service for time entry operations."""

    def create_time_entry(
        self,
        entry_data: TimeEntryCreate,
        user_id: UUID,
        agency_id: UUID,
        session: Session,
    ) -> TimeEntry:
        """Create a new time entry.

        Args:
            entry_data: Time entry creation data
            user_id: ID of the user creating the entry
            agency_id: Agency ID for multi-tenant isolation
            session: Database session

        Returns:
            The created time entry

        Raises:
            ValueError: If task doesn't exist or doesn't belong to the agency
        """
        # Verify task exists and belongs to agency
        task = session.exec(
            select(Task).where(
                and_(
                    Task.id == entry_data.task_id,
                    Task.agency_id == agency_id,
                )
            )
        ).first()

        if not task:
            raise ValueError("Task not found")

        # Default entry_date to today if not provided
        entry_date = entry_data.entry_date or date.today()

        time_entry = TimeEntry(
            task_id=entry_data.task_id,
            user_id=user_id,
            agency_id=agency_id,
            duration_minutes=entry_data.duration_minutes,
            note=entry_data.note,
            entry_date=entry_date,
        )

        session.add(time_entry)
        session.commit()
        session.refresh(time_entry)
        return time_entry

    def get_time_entry(
        self,
        entry_id: UUID,
        agency_id: UUID,
        session: Session,
    ) -> Optional[TimeEntry]:
        """Get a time entry by ID (scoped to agency)."""
        return session.exec(
            select(TimeEntry).where(
                and_(
                    TimeEntry.id == entry_id,
                    TimeEntry.agency_id == agency_id,
                )
            )
        ).first()

    def list_time_entries(
        self,
        agency_id: UUID,
        session: Session,
        task_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[TimeEntry]:
        """List time entries for an agency with optional filters.

        Args:
            agency_id: Agency ID for multi-tenant isolation
            session: Database session
            task_id: Filter by task ID
            user_id: Filter by user ID
            start_date: Filter by entry date start (inclusive)
            end_date: Filter by entry date end (inclusive)

        Returns:
            List of time entries matching filters
        """
        query = select(TimeEntry).where(TimeEntry.agency_id == agency_id)

        if task_id:
            query = query.where(TimeEntry.task_id == task_id)
        if user_id:
            query = query.where(TimeEntry.user_id == user_id)
        if start_date:
            query = query.where(TimeEntry.entry_date >= start_date)
        if end_date:
            query = query.where(TimeEntry.entry_date <= end_date)

        # Order by entry_date descending, then created_at descending
        query = query.order_by(
            col(TimeEntry.entry_date).desc(),
            col(TimeEntry.created_at).desc()
        )

        return session.exec(query).all()

    def update_time_entry(
        self,
        entry_id: UUID,
        entry_data: TimeEntryUpdate,
        agency_id: UUID,
        session: Session,
    ) -> Optional[TimeEntry]:
        """Update a time entry."""
        time_entry = self.get_time_entry(entry_id, agency_id, session)
        if not time_entry:
            return None

        entry_data_dict = entry_data.model_dump(exclude_unset=True)
        for field, value in entry_data_dict.items():
            setattr(time_entry, field, value)

        session.add(time_entry)
        session.commit()
        session.refresh(time_entry)
        return time_entry

    def delete_time_entry(
        self,
        entry_id: UUID,
        agency_id: UUID,
        session: Session,
    ) -> bool:
        """Delete a time entry."""
        time_entry = self.get_time_entry(entry_id, agency_id, session)
        if not time_entry:
            return False

        session.delete(time_entry)
        session.commit()
        return True

    def get_total_time_for_task(
        self,
        task_id: UUID,
        agency_id: UUID,
        session: Session,
    ) -> int:
        """Get total minutes logged for a task.

        Args:
            task_id: Task ID
            agency_id: Agency ID for multi-tenant isolation
            session: Database session

        Returns:
            Total duration in minutes
        """
        result = session.exec(
            select(
                func.coalesce(func.sum(TimeEntry.duration_minutes), 0)
            ).where(
                and_(
                    TimeEntry.task_id == task_id,
                    TimeEntry.agency_id == agency_id,
                )
            )
        ).one()

        return int(result)

    def get_profitability_for_project(
        self,
        project_id: UUID,
        agency_id: UUID,
        session: Session,
    ) -> dict:
        """Calculate profitability metrics for a project.

        Args:
            project_id: Project ID
            agency_id: Agency ID for multi-tenant isolation
            session: Database session

        Returns:
            Dictionary with profitability data
        """
        # Get project
        project = session.get(Project, project_id)
        if not project or project.agency_id != agency_id:
            raise ValueError("Project not found")

        # Get all tasks for project
        tasks = session.exec(
            select(Task).where(
                and_(
                    Task.project_id == project_id,
                    Task.agency_id == agency_id,
                )
            )
        ).all()

        task_ids = [t.id for t in tasks]

        if not task_ids:
            return {
                "project_id": str(project_id),
                "project_name": project.name,
                "total_tasks": 0,
                "completed_tasks": 0,
                "completion_percentage": 0.0,
                "total_hours": 0,
                "total_cost": 0.0,
                "total_revenue": 0.0,
                "profit": 0.0,
                "profit_margin": 0.0,
            }

        # Get total time for all tasks in project
        total_minutes_result = session.exec(
            select(
                func.sum(TimeEntry.duration_minutes)
            ).where(
                and_(
                    TimeEntry.task_id.in_(task_ids),
                    TimeEntry.agency_id == agency_id,
                )
            )
        ).one()

        total_minutes = total_minutes_result or 0
        total_hours = total_minutes / 60.0

        # Count completed tasks
        completed_tasks = sum(1 for t in tasks if t.status.value == "DONE")
        total_tasks = len(tasks)
        completion_pct = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0

        # Calculate cost (using project hourly_rate if set)
        hourly_rate = float(project.hourly_rate or 0)
        total_cost = total_hours * hourly_rate

        # Revenue is calculated from completed tasks * hourly_rate
        # This is a simplified calculation
        total_revenue = completed_tasks * hourly_rate * 8  # Assuming 8 hours per task

        profit = total_revenue - total_cost
        profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else 0.0

        return {
            "project_id": str(project_id),
            "project_name": project.name,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_percentage": round(completion_pct, 1),
            "total_hours": round(total_hours, 1),
            "total_cost": round(total_cost, 2),
            "total_revenue": round(total_revenue, 2),
            "profit": round(profit, 2),
            "profit_margin": round(profit_margin, 2),
        }
