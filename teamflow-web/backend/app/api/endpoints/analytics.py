"""Analytics API endpoints.

Provides endpoints for dashboard statistics and analytics.
"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.core.deps import CurrentUser, SessionDep
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])
analytics_service = AnalyticsService()


@router.get("/stats")
def get_dashboard_stats(
    current_user: CurrentUser,
    session: SessionDep,
):
    """Get dashboard statistics for the current agency.

    Returns:
        Dictionary with active projects, completed tasks, team utilization, revenue, and trends
    """
    stats = analytics_service.get_dashboard_stats(
        current_user.agency_id,
        session,
    )
    return stats


@router.get("/tasks-by-status")
def get_tasks_by_status(
    current_user: CurrentUser,
    session: SessionDep,
):
    """Get task counts grouped by status.

    Returns:
        List of status counts with labels and colors for visualization
    """
    tasks_by_status = analytics_service.get_tasks_by_status(
        current_user.agency_id,
        session,
    )
    return tasks_by_status


@router.get("/profitability")
def get_project_profitability(
    current_user: CurrentUser,
    session: SessionDep,
):
    """Get profitability data for all projects.

    Returns:
        List of project profitability metrics including revenue, cost, and profit
    """
    profitability = analytics_service.get_project_profitability(
        current_user.agency_id,
        session,
    )
    return profitability


@router.get("/profitability/project/{project_id}")
def get_project_profitability_by_id(
    project_id: UUID,
    current_user: CurrentUser,
    session: SessionDep,
):
    """Get profitability data for a specific project.

    Args:
        project_id: Project UUID
        current_user: Authenticated user
        session: Database session

    Returns:
        Project profitability metrics with actual time-based costs

    Raises:
        404: If project not found
    """
    try:
        profitability = analytics_service.get_project_profitability_by_id(
            project_id,
            current_user.agency_id,
            session,
        )
        return profitability
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
