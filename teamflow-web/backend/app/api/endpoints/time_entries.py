"""Time Entries API endpoints."""
from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.core.deps import CurrentUser, SessionDep
from app.models.time_entry import TimeEntry, TimeEntryCreate, TimeEntryRead, TimeEntryUpdate
from app.services.time_entry_service import TimeEntryService

router = APIRouter(prefix="/time-entries", tags=["time-entries"])
time_entry_service = TimeEntryService()


@router.post("", response_model=TimeEntryRead, status_code=status.HTTP_201_CREATED)
def create_time_entry(
    entry_data: TimeEntryCreate,
    current_user: CurrentUser,
    session: SessionDep,
) -> TimeEntry:
    """Create a new time entry for the current user.

    Args:
        entry_data: Time entry creation data including task_id and duration_minutes
        current_user: Authenticated user
        session: Database session

    Returns:
        The created time entry

    Raises:
        400: If task doesn't exist or doesn't belong to the agency
    """
    try:
        return time_entry_service.create_time_entry(
            entry_data,
            current_user.id,
            current_user.agency_id,
            session,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("", response_model=dict[str, list[TimeEntryRead]])
def list_time_entries(
    current_user: CurrentUser,
    session: SessionDep,
    task_id: Optional[UUID] = None,
    user_id: Optional[UUID] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> dict[str, list[TimeEntryRead]]:
    """List time entries for the current agency with optional filters.

    Args:
        task_id: Filter by task ID
        user_id: Filter by user ID (requires admin or own entries)
        start_date: Filter by entry date start (inclusive)
        end_date: Filter by entry date end (inclusive)

    Returns:
        Dictionary with list of time entries matching filters
    """
    # Non-admin users can only see their own entries
    if current_user.role.value != "admin" and user_id and user_id != current_user.id:
        user_id = current_user.id

    entries = time_entry_service.list_time_entries(
        current_user.agency_id,
        session,
        task_id=task_id,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
    )
    return {"time_entries": entries}


@router.get("/{entry_id}", response_model=TimeEntryRead)
def get_time_entry(
    entry_id: UUID,
    current_user: CurrentUser,
    session: SessionDep,
) -> TimeEntry:
    """Get a time entry by ID.

    Args:
        entry_id: Time entry UUID
        current_user: Authenticated user
        session: Database session

    Returns:
        The time entry

    Raises:
        404: If time entry not found
    """
    entry = time_entry_service.get_time_entry(entry_id, current_user.agency_id, session)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry not found",
        )
    return entry


@router.patch("/{entry_id}", response_model=TimeEntryRead)
def update_time_entry(
    entry_id: UUID,
    entry_data: TimeEntryUpdate,
    current_user: CurrentUser,
    session: SessionDep,
) -> TimeEntry:
    """Update a time entry.

    Args:
        entry_id: Time entry UUID
        entry_data: Time entry update data
        current_user: Authenticated user
        session: Database session

    Returns:
        The updated time entry

    Raises:
        404: If time entry not found
    """
    entry = time_entry_service.update_time_entry(
        entry_id,
        entry_data,
        current_user.agency_id,
        session,
    )
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry not found",
        )
    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_time_entry(
    entry_id: UUID,
    current_user: CurrentUser,
    session: SessionDep,
) -> None:
    """Delete a time entry.

    Args:
        entry_id: Time entry UUID
        current_user: Authenticated user
        session: Database session

    Raises:
        404: If time entry not found
    """
    if not time_entry_service.delete_time_entry(entry_id, current_user.agency_id, session):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry not found",
        )


@router.get("/task/{task_id}/total", response_model=dict[str, int])
def get_total_time_for_task(
    task_id: UUID,
    current_user: CurrentUser,
    session: SessionDep,
) -> dict[str, int]:
    """Get total time logged for a task in minutes.

    Args:
        task_id: Task UUID
        current_user: Authenticated user
        session: Database session

    Returns:
        Dictionary with total_minutes key
    """
    total_minutes = time_entry_service.get_total_time_for_task(
        task_id,
        current_user.agency_id,
        session,
    )
    return {"total_minutes": total_minutes}
