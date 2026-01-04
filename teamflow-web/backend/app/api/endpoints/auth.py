"""Authentication endpoints - signup, login, logout."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.db.session import SessionDep, get_session
from app.models.agency import AgencyCreate, AgencyRead
from app.models.user import (
    UserCreate,
    UserLogin,
    UserRead,
    UserRole,
)
from app.services.auth_service import AuthService
from app.core.rate_limit import check_rate_limit
from app.core.logging import get_logger, log_api_call

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Service instance
auth_service = AuthService()
logger = get_logger("api.auth")


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
def register(
    agency_data: AgencyCreate,
    user_data: UserCreate,
    session: SessionDep,
    request: Request,
) -> dict:
    """
    Register a new agency with admin user.

    This endpoint creates both an agency and the first admin user for that agency.
    """
    # T163: Rate limiting check (3 registrations per hour per IP)
    check_rate_limit(request, "auth_register")

    # Create agency
    agency = auth_service.register_agency(agency_data, session)

    # Create admin user for the agency
    user = auth_service.register_user(
        user_data,
        agency_id=agency.id,
        session=session,
        role=UserRole.admin,
    )

    # Generate JWT token
    from app.core.security import create_access_token

    token = create_access_token(
        data={
            "sub": str(user.id),
            "agency_id": str(user.agency_id),
            "email": user.email,
            "role": user.role.value,
        }
    )

    return {
        "agency": AgencyRead.model_validate(agency).model_dump(),
        "user": UserRead.model_validate(user).model_dump(),
        "access_token": token,
        "token_type": "bearer",
    }


@router.post("/login", response_model=dict)
def login(
    credentials: UserLogin,
    session: SessionDep,
    request: Request,
) -> dict:
    """Authenticate user and return JWT token."""
    # T163: Rate limiting check (5 login attempts per minute per IP)
    check_rate_limit(request, "auth_login")

    try:
        user, token = auth_service.login(credentials, session)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": UserRead.model_validate(user).model_dump(),
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/logout")
def logout() -> dict[str, str]:
    """
    Logout user.

    JWT tokens are stateless - logout is handled client-side by removing the token.
    This endpoint exists for API completeness and future token blacklisting.
    """
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserRead)
def get_current_user(
    request: Request,
    session: SessionDep,
) -> UserRead:
    """
    Get current authenticated user.

    Requires valid JWT token. User info is extracted from token by middleware.
    """
    # Get user_id from request state (set by JWT middleware)
    user_id = getattr(request.state, "user_id", None)
    agency_id = getattr(request.state, "agency_id", None)

    if not user_id or not agency_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    # Get user from database (scoped to agency for multi-tenant isolation)
    user = auth_service.get_user_by_id(UUID(user_id), UUID(agency_id), session)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserRead.model_validate(user)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_account(
    request: Request,
    session: SessionDep,
) -> None:
    """
    Delete the current user's account.

    This performs a soft delete (sets active=False).
    All tasks assigned to the user will become unassigned.
    The user will be logged out immediately.

    Security: User can only delete their own account.
    """
    # Get user_id from request state (set by JWT middleware)
    user_id = getattr(request.state, "user_id", None)
    agency_id = getattr(request.state, "agency_id", None)

    if not user_id or not agency_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    # Rate limiting check (1 account deletion per hour per user)
    check_rate_limit(request, "auth_delete_me")

    # Get user info before deletion for audit log
    from app.models.user import User
    target_user = session.get(User, UUID(user_id))

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Perform soft delete using user service
    from app.services.user_service import UserService
    user_service = UserService()

    user_service.delete_user(
        user_id,
        agency_id,
        session,
        target_user,  # Pass current user as context
    )

    # Audit log: Self-account deletion
    log_api_call(
        logger,
        endpoint="DELETE /api/v1/auth/me",
        action="delete_my_account",
        user_id=user_id,
        agency_id=agency_id,
        target_user_id=user_id,
        target_user_email=target_user.email,
    )


@router.get("/me/export")
def export_my_data(
    request: Request,
    session: SessionDep,
) -> JSONResponse:
    """
    Export all data associated with the current user's account.

    Returns a JSON file containing:
    - User profile information
    - All tasks created or assigned to the user
    - All projects the user is associated with
    - All time entries logged by the user

    Security: User can only export their own data.
    """
    # Get user_id from request state (set by JWT middleware)
    user_id = getattr(request.state, "user_id", None)
    agency_id = getattr(request.state, "agency_id", None)

    if not user_id or not agency_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    # Rate limiting check (5 exports per hour per user)
    check_rate_limit(request, "auth_export_me")

    from app.models.user import User
    from app.models.task import Task
    from app.models.project import Project
    from sqlmodel import select

    # Get user
    user = session.get(User, UUID(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Get all tasks for this agency (filter by created_by or assignee)
    tasks = session.exec(
        select(Task).where(
            (Task.agency_id == UUID(agency_id)) &
            ((Task.created_by == UUID(user_id)) | (Task.assignee_id == UUID(user_id)))
        )
    ).all()

    # Get all projects for this agency
    projects = session.exec(
        select(Project).where(Project.agency_id == UUID(agency_id))
    ).all()

    # Get time entries (if model exists)
    time_entries = []
    try:
        from app.models.time_entry import TimeEntry
        time_entries = session.exec(
            select(TimeEntry).where(
                (TimeEntry.agency_id == UUID(agency_id)) &
                (TimeEntry.user_id == UUID(user_id))
            )
        ).all()
    except ImportError:
        pass

    # Build export data
    export_data = {
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role.value,
            "is_project_manager": user.is_project_manager,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        },
        "tasks": [
            {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "status": task.status.value if task.status else None,
                "priority": task.priority.value if task.priority else None,
                "project_id": str(task.project_id) if task.project_id else None,
                "assignee_id": str(task.assignee_id) if task.assignee_id else None,
                "created_by": str(task.created_by) if task.created_by else None,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None,
                "due_date": task.due_date.isoformat() if task.due_date else None,
            }
            for task in tasks
        ],
        "projects": [
            {
                "id": str(project.id),
                "name": project.name,
                "description": project.description,
                "status": project.status.value if hasattr(project, 'status') and project.status else None,
                "created_at": project.created_at.isoformat() if project.created_at else None,
                "updated_at": project.updated_at.isoformat() if project.updated_at else None,
            }
            for project in projects
        ],
        "time_entries": [
            {
                "id": str(entry.id),
                "task_id": str(entry.task_id) if entry.task_id else None,
                "duration_minutes": entry.duration_minutes,
                "note": entry.note,
                "entry_date": entry.entry_date.isoformat() if entry.entry_date else None,
                "created_at": entry.created_at.isoformat() if entry.created_at else None,
            }
            for entry in time_entries
        ],
        "exported_at": str(request.state.user_id if hasattr(request.state, 'user_id') else user_id),
        "export_date": __import__('datetime').datetime.utcnow().isoformat(),
    }

    # Audit log: Data export
    log_api_call(
        logger,
        endpoint="GET /api/v1/auth/me/export",
        action="export_my_data",
        user_id=user_id,
        agency_id=agency_id,
        task_count=len(tasks),
        project_count=len(projects),
        time_entry_count=len(time_entries),
    )

    return JSONResponse(
        content=export_data,
        headers={
            "Content-Disposition": 'attachment; filename="teamflow-export.json"',
        },
    )
