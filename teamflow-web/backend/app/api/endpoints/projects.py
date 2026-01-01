"""Projects API endpoints."""
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.core.deps import CurrentUser, SessionDep
from app.models.project import (
    Project,
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
)
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])
project_service = ProjectService()


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    current_user: CurrentUser,
    session: SessionDep,
) -> Project:
    """Create a new project for the current agency."""
    try:
        return project_service.create_project(project_data, current_user.agency_id, session)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("", response_model=list[ProjectRead])
def list_projects(
    current_user: CurrentUser,
    session: SessionDep,
) -> list[ProjectRead]:
    """List all projects for the current agency."""
    return project_service.list_projects(current_user.agency_id, session)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: UUID,
    current_user: CurrentUser,
    session: SessionDep,
) -> Project:
    """Get a project by ID."""
    project = project_service.get_project(project_id, current_user.agency_id, session)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    current_user: CurrentUser,
    session: SessionDep,
) -> Project:
    """Update a project."""
    project = project_service.update_project(
        project_id, project_data, current_user.agency_id, session
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: UUID,
    current_user: CurrentUser,
    session: SessionDep,
) -> None:
    """Delete a project."""
    if not project_service.delete_project(project_id, current_user.agency_id, session):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
