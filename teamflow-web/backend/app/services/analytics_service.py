"""Analytics Service for calculating dashboard statistics.

This service provides methods for computing various analytics
including task counts, project metrics, and team utilization.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any
from uuid import UUID
from sqlmodel import Session, select, func, and_

from app.models.task import Task, TaskStatus
from app.models.project import Project
from app.models.user import User
from app.services.time_entry_service import TimeEntryService


class AnalyticsService:
    """Service for analytics and statistics calculations."""

    def __init__(self):
        """Initialize analytics service with time entry service."""
        self.time_entry_service = TimeEntryService()

    def get_dashboard_stats(
        self,
        agency_id: str,
        session: Session,
    ) -> Dict[str, Any]:
        """Calculate dashboard statistics for an agency.

        Args:
            agency_id: The agency ID to calculate stats for
            session: Database session

        Returns:
            Dictionary containing dashboard statistics
        """
        # Count active projects
        active_projects = session.exec(
            select(func.count(Project.id))
            .where(Project.agency_id == agency_id)
        ).one()

        # Count completed tasks
        completed_tasks = session.exec(
            select(func.count(Task.id))
            .where(
                and_(
                    Task.agency_id == agency_id,
                    Task.status == TaskStatus.DONE,
                )
            )
        ).one()

        # Count total team members
        team_count = session.exec(
            select(func.count(User.id))
            .where(User.agency_id == agency_id)
        ).one()

        # Calculate team utilization
        # Utilization = (assigned tasks / total team members) * 100
        team_utilization = 0.0
        if team_count > 0:
            assigned_tasks = session.exec(
                select(func.count(Task.id))
                .where(
                    and_(
                        Task.agency_id == agency_id,
                        Task.assignee_id.is_not(None),
                    )
                )
            ).one()
            team_utilization = min(100.0, (assigned_tasks / team_count) * 100)

        # Calculate revenue (simplified - would use hourly_rate in production)
        revenue = 0.0
        projects = session.exec(
            select(Project).where(Project.agency_id == agency_id)
        ).all()
        for project in projects:
            if hasattr(project, "hourly_rate") and project.hourly_rate:
                # Sum up completed tasks for this project
                completed_for_project = session.exec(
                    select(func.count(Task.id))
                    .where(
                        and_(
                            Task.agency_id == agency_id,
                            Task.project_id == project.id,
                            Task.status == TaskStatus.DONE,
                        )
                    )
                ).one()
                # Estimate revenue (simplified calculation)
                revenue += completed_for_project * project.hourly_rate

        # Calculate trends (compare with previous period)
        # For now, using simplified trend calculation
        trends = {
            "activeProjects": self._calculate_trend(session, agency_id, "projects"),
            "tasksCompleted": self._calculate_trend(session, agency_id, "tasks"),
            "teamUtilization": 0.0,  # Would compare with previous period
            "revenue": 0.0,  # Would compare with previous period
        }

        return {
            "activeProjects": active_projects,
            "tasksCompleted": completed_tasks,
            "teamUtilization": round(team_utilization, 1),
            "revenue": round(revenue, 2),
            "trends": trends,
        }

    def get_tasks_by_status(
        self,
        agency_id: str,
        session: Session,
    ) -> List[Dict[str, Any]]:
        """Get task counts grouped by status.

        Args:
            agency_id: The agency ID to get stats for
            session: Database session

        Returns:
            List of dicts with label, value, and color for each status
        """
        status_colors = {
            TaskStatus.TODO: "#6366f1",     # Indigo
            TaskStatus.DOING: "#f59e0b",    # Amber
            TaskStatus.REVIEW: "#8b5cf6",   # Violet
            TaskStatus.DONE: "#10b981",     # Emerald
        }

        status_labels = {
            TaskStatus.TODO: "To Do",
            TaskStatus.DOING: "In Progress",
            TaskStatus.REVIEW: "In Review",
            TaskStatus.DONE: "Done",
        }

        result = []
        for status in TaskStatus:
            count = session.exec(
                select(func.count(Task.id))
                .where(
                    and_(
                        Task.agency_id == agency_id,
                        Task.status == status,
                    )
                )
            ).one()

            result.append({
                "label": status_labels[status],
                "value": count,
                "color": status_colors[status],
            })

        return result

    def get_project_profitability(
        self,
        agency_id: str,
        session: Session,
    ) -> List[Dict[str, Any]]:
        """Calculate profitability for each project using time entry data.

        Args:
            agency_id: The agency ID to get profitability for
            session: Database session

        Returns:
            List of project profitability data with actual time-based costs
        """
        projects = session.exec(
            select(Project).where(Project.agency_id == agency_id)
        ).all()

        profitability_data = []
        for project in projects:
            try:
                # Use TimeEntryService for accurate profitability calculation
                profit_data = self.time_entry_service.get_profitability_for_project(
                    project.id,
                    agency_id,
                    session,
                )
                profitability_data.append(profit_data)
            except ValueError:
                # Skip projects that can't be calculated
                continue

        return profitability_data

    def get_project_profitability_by_id(
        self,
        project_id: UUID,
        agency_id: UUID,
        session: Session,
    ) -> Dict[str, Any]:
        """Get profitability data for a specific project.

        Args:
            project_id: The project ID to get profitability for
            agency_id: The agency ID for multi-tenant isolation
            session: Database session

        Returns:
            Project profitability data with actual time-based costs

        Raises:
            ValueError: If project not found
        """
        return self.time_entry_service.get_profitability_for_project(
            project_id,
            agency_id,
            session,
        )

    def _calculate_trend(
        self,
        session: Session,
        agency_id: str,
        metric_type: str,
    ) -> float:
        """Calculate trend (change from previous period).

        Args:
            session: Database session
            agency_id: The agency ID
            metric_type: Type of metric ('projects' or 'tasks')

        Returns:
            Trend value (percentage change)
        """
        # Simplified trend calculation
        # In production, would compare with data from 30 days ago
        # For now, return 0 as placeholder
        return 0.0
