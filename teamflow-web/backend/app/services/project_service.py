"""Project service for project CRUD operations."""
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from app.models.agency import Agency
from app.models.project import Project, ProjectCreate, ProjectUpdate


class ProjectService:
    """Service for project operations."""

    def create_project(
        self,
        project_data: ProjectCreate,
        agency_id: UUID,
        session: Session,
    ) -> Project:
        """Create a new project for an agency."""
        # Verify agency exists
        agency = session.get(Agency, agency_id)
        if not agency:
            raise ValueError("Agency not found")

        project = Project(
            **project_data.model_dump(exclude_unset=True),
            agency_id=agency_id,
        )
        session.add(project)
        session.commit()
        session.refresh(project)
        return project

    def get_project(
        self,
        project_id: UUID,
        agency_id: UUID,
        session: Session,
    ) -> Optional[Project]:
        """Get a project by ID (scoped to agency)."""
        return session.exec(
            select(Project).where(
                Project.id == project_id,
                Project.agency_id == agency_id,
            )
        ).first()

    def list_projects(
        self,
        agency_id: UUID,
        session: Session,
    ) -> List[Project]:
        """List all projects for an agency."""
        return session.exec(
            select(Project)
            .where(Project.agency_id == agency_id)
            .order_by(Project.created_at.desc())
        ).all()

    def update_project(
        self,
        project_id: UUID,
        project_data: ProjectUpdate,
        agency_id: UUID,
        session: Session,
    ) -> Optional[Project]:
        """Update a project."""
        project = self.get_project(project_id, agency_id, session)
        if not project:
            return None

        project_data_dict = project_data.model_dump(exclude_unset=True)
        for field, value in project_data_dict.items():
            setattr(project, field, value)

        session.add(project)
        session.commit()
        session.refresh(project)
        return project

    def delete_project(
        self,
        project_id: UUID,
        agency_id: UUID,
        session: Session,
    ) -> bool:
        """Delete a project."""
        project = self.get_project(project_id, agency_id, session)
        if not project:
            return False

        session.delete(project)
        session.commit()
        return True
