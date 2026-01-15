"""MCP tools for TeamFlow (T018-T020).

These tools expose service layer methods as MCP tools for AI agents.
Tool categories:
- Knowledge Base: search_knowledge_base (RAG)
- Task Management: add_task, list_tasks, assign_task, complete_task
- Analytics: get_profitability, workload_summary
- Recommendations: suggest_assignee

Phase 7 (T092): RBAC role constant mapping for MCP tools.
Defines which roles can execute each tool (admin, manager, member, viewer).
"""
from typing import Optional, List, Set
from uuid import UUID
from datetime import datetime
from enum import Enum

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from app.services.task_service import TaskService
from app.services.analytics_service import AnalyticsService


# T092: RBAC Role Constants


class UserRole(str, Enum):
    """User roles for RBAC (T092)."""

    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"
    VIEWER = "viewer"


# T092: Tool-to-Role mapping
# Defines which roles can execute each MCP tool
TOOL_ROLE_PERMISSIONS = {
    # Knowledge Base Tools - Available to all roles
    "search_knowledge_base": {UserRole.ADMIN, UserRole.MANAGER, UserRole.MEMBER, UserRole.VIEWER},

    # Task Management Tools
    "add_task": {UserRole.ADMIN, UserRole.MANAGER, UserRole.MEMBER},
    "list_tasks": {UserRole.ADMIN, UserRole.MANAGER, UserRole.MEMBER, UserRole.VIEWER},
    "assign_task": {UserRole.ADMIN, UserRole.MANAGER},
    "complete_task": {UserRole.ADMIN, UserRole.MANAGER, UserRole.MEMBER},
    "complete_task_by_title": {UserRole.ADMIN, UserRole.MANAGER, UserRole.MEMBER},
    "delete_task": {UserRole.ADMIN, UserRole.MANAGER},
    "delete_task_by_title": {UserRole.ADMIN, UserRole.MANAGER},
    "archive_task": {UserRole.ADMIN, UserRole.MANAGER, UserRole.MEMBER},
    "archive_task_by_title": {UserRole.ADMIN, UserRole.MANAGER, UserRole.MEMBER},

    # Analytics Tools - Manager and Admin only
    "get_profitability": {UserRole.ADMIN, UserRole.MANAGER},
    "workload_summary": {UserRole.ADMIN, UserRole.MANAGER, UserRole.MEMBER},

    # Recommendation Tools - All roles can view recommendations
    "suggest_assignee": {UserRole.ADMIN, UserRole.MANAGER, UserRole.MEMBER},
}


def check_tool_permission(tool_name: str, user_role: UserRole) -> bool:
    """Check if user role has permission to execute a tool (T092).

    Args:
        tool_name: Name of the MCP tool
        user_role: User's role (admin, manager, member, viewer)

    Returns:
        True if user has permission, False otherwise

    Example:
        >>> check_tool_permission("add_task", UserRole.MEMBER)
        True
        >>> check_tool_permission("assign_task", UserRole.VIEWER)
        False
    """
    allowed_roles = TOOL_ROLE_PERMISSIONS.get(tool_name, set())
    return user_role in allowed_roles


def get_allowed_roles(tool_name: str) -> Set[UserRole]:
    """Get set of roles allowed to execute a tool (T092).

    Args:
        tool_name: Name of the MCP tool

    Returns:
        Set of allowed roles

    Example:
        >>> get_allowed_roles("assign_task")
        {UserRole.ADMIN, UserRole.MANAGER}
    """
    return TOOL_ROLE_PERMISSIONS.get(tool_name, set())


# Input schemas for tools


class SearchKnowledgeBaseInput(BaseModel):
    """Input schema for search_knowledge_base tool."""

    query: str = Field(..., description="Natural language query to search knowledge base")
    limit: int = Field(5, description="Maximum results to return (default: 5)")


class AddTaskInput(BaseModel):
    """Input schema for add_task tool."""

    title: str = Field(..., description="Task title (e.g., 'Fix navbar bug')")
    description: Optional[str] = Field(None, description="Task description")
    project_id: Optional[UUID] = Field(None, description="Project ID (optional)")
    assignee_id: Optional[UUID] = Field(None, description="User ID to assign task to")
    priority: Optional[str] = Field(None, description="Priority: LOW, MEDIUM, or HIGH")
    status: Optional[str] = Field(None, description="Status: TODO, IN_PROGRESS, BLOCKED, or DONE")
    due_date: Optional[datetime] = Field(None, description="Due date for the task")


class ListTasksInput(BaseModel):
    """Input schema for list_tasks tool."""

    project_id: Optional[UUID] = Field(None, description="Filter by project ID")
    assignee_id: Optional[UUID] = Field(None, description="Filter by assignee ID")
    status: Optional[str] = Field(None, description="Filter by status")
    limit: int = Field(50, description="Maximum number of tasks to return")


class AssignTaskInput(BaseModel):
    """Input schema for assign_task tool."""

    task_id: UUID = Field(..., description="Task ID to reassign")
    assignee_id: UUID = Field(..., description="User ID to assign task to")


class CompleteTaskInput(BaseModel):
    """Input schema for complete_task tool."""

    task_id: UUID = Field(..., description="Task ID to complete")


class GetProfitabilityInput(BaseModel):
    """Input schema for get_profitability tool."""

    project_id: UUID = Field(..., description="Project ID to analyze")


class WorkloadSummaryInput(BaseModel):
    """Input schema for workload_summary tool."""

    agency_id: UUID = Field(..., description="Agency ID to analyze")


class SuggestAssigneeInput(BaseModel):
    """Input schema for suggest_assignee tool."""

    task_id: UUID = Field(..., description="Task ID to find best assignee for")


# Knowledge Base Tools (RAG)


def register_knowledge_base_tools(mcp: FastMCP):
    """Register knowledge base RAG tools with MCP server."""

    @mcp.tool()
    def search_knowledge_base(query: str, limit: int = 5) -> str:
        """Search the TeamFlow knowledge base for relevant information.

        Use this tool when users ask about:
        - TeamFlow features and functionality
        - How to perform specific tasks
        - Documentation and API references
        - Troubleshooting and error messages
        - Best practices and workflows

        Args:
            query: Natural language question about TeamFlow
            limit: Maximum results to return (default: 5)

        Returns:
            Relevant knowledge base excerpts with sources
        """
        from app.services.rag_service import rag_service

        try:
            results = rag_service.search_knowledge_base(
                query=query,
                limit=limit,
                score_threshold=0.7,
            )

            if not results:
                return f"No relevant information found in knowledge base for query: {query}"

            # Format results for agent
            formatted = []
            for r in results:
                formatted.append(
                    f"Source: {r.source}\n"
                    f"Title: {r.title}\n"
                    f"Relevance: {r.score:.2f}\n"
                    f"Content: {r.text}\n"
                )

            return "\n---\n".join(formatted)

        except Exception as e:
            return f"Error searching knowledge base: {str(e)}"


# Task Management Tools (T018)


def register_task_tools(mcp: FastMCP):
    """Register task management tools with MCP server."""

    @mcp.tool()
    def add_task(
        title: str,
        description: Optional[str] = None,
        project_id: Optional[str] = None,
        assignee_id: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        """Create a new task in TeamFlow.

        Args:
            title: Task title (e.g., 'Fix navbar bug')
            description: Task description
            project_id: Project ID (optional)
            assignee_id: User ID to assign task to
            priority: Priority: LOW, MEDIUM, or HIGH
            status: Status: TODO, IN_PROGRESS, BLOCKED, or DONE

        Returns:
            Confirmation message with task ID
        """
        from uuid import UUID
        from sqlmodel import Session
        from app.db.session import get_session
        from app.models.task import TaskCreate, TaskPriority, TaskStatus
        from app.services.task_service import TaskService

        try:
            # Get database session
            session_gen = get_session()
            session = next(session_gen)

            # For now, use a default agency ID from the first project or user
            # In production, this would come from user context
            if project_id:
                from app.models.project import Project
                project = session.get(Project, UUID(project_id))
                if not project:
                    return f"Error: Project {project_id} not found"
                agency_id = project.agency_id
            else:
                # Use default agency - in production this comes from user context
                from app.models.user import User
                first_user = session.exec(select(User).limit(1)).first()
                if not first_user:
                    return "Error: No users found. Cannot determine agency."
                agency_id = first_user.agency_id

            # Map string priorities to enum
            priority_map = {
                'low': TaskPriority.LOW,
                'medium': TaskPriority.MEDIUM,
                'high': TaskPriority.HIGH,
            }

            # Map string statuses to enum
            status_map = {
                'todo': TaskStatus.TODO,
                'in_progress': TaskStatus.IN_PROGRESS,
                'blocked': TaskStatus.BLOCKED,
                'done': TaskStatus.DONE,
            }

            # Create TaskCreate object
            task_data = TaskCreate(
                title=title,
                description=description,
                project_id=UUID(project_id) if project_id else None,
                assignee_id=UUID(assignee_id) if assignee_id else None,
                priority=priority_map.get(priority.lower(), TaskPriority.MEDIUM) if priority else TaskPriority.MEDIUM,
                status=status_map.get(status.lower(), TaskStatus.TODO) if status else TaskStatus.TODO,
            )

            # Create task using service
            task_service = TaskService()
            task = task_service.create_task(task_data, agency_id, session)

            return (
                f"Task created successfully!\n"
                f"- ID: {task.id}\n"
                f"- Title: {task.title}\n"
                f"- Priority: {task.priority}\n"
                f"- Status: {task.status}\n"
                f"- Assigned to: {task.assignee.full_name if task.assignee else 'Unassigned'}"
            )

        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error creating task: {str(e)}"

    @mcp.tool()
    def list_tasks(
        project_id: Optional[str] = None,
        assignee_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> str:
        """List tasks in TeamFlow with optional filters.

        Args:
            project_id: Filter by project ID
            assignee_id: Filter by assignee ID
            status: Filter by status
            limit: Maximum number of tasks to return (default: 50)

        Returns:
            List of tasks with their details
        """
        from uuid import UUID
        from sqlmodel import Session, select
        from app.db.session import get_session
        from app.models.task import TaskStatus
        from app.models.user import User
        from app.services.task_service import TaskService

        try:
            # Get database session
            session_gen = get_session()
            session = next(session_gen)

            # Determine agency_id from context
            # In production, this would come from user context
            if assignee_id:
                from app.models.user import User
                assignee = session.get(User, UUID(assignee_id))
                if not assignee:
                    return f"Error: Assignee {assignee_id} not found"
                agency_id = assignee.agency_id
            elif project_id:
                from app.models.project import Project
                project = session.get(Project, UUID(project_id))
                if not project:
                    return f"Error: Project {project_id} not found"
                agency_id = project.agency_id
            else:
                # Use default agency
                first_user = session.exec(select(User).limit(1)).first()
                if not first_user:
                    return "Error: No users found. Cannot determine agency."
                agency_id = first_user.agency_id

            # Map status string to enum
            status_map = {
                'todo': TaskStatus.TODO,
                'in_progress': TaskStatus.IN_PROGRESS,
                'blocked': TaskStatus.BLOCKED,
                'done': TaskStatus.DONE,
            }
            task_status = status_map.get(status.lower()) if status else None

            # List tasks using service
            task_service = TaskService()
            tasks = task_service.list_tasks(
                agency_id=agency_id,
                session=session,
                status=task_status,
                project_id=UUID(project_id) if project_id else None,
                assignee_id=UUID(assignee_id) if assignee_id else None,
            )

            if not tasks:
                return "No tasks found matching the specified filters."

            # Format results
            lines = [
                f"Found {len(tasks)} task(s):",
                f"",
            ]

            for i, task in enumerate(tasks[:limit], 1):
                assignee_name = task.assignee.full_name if task.assignee else "Unassigned"
                lines.append(
                    f"{i}. **{task.title}** (ID: {task.id})\n"
                    f"   - Status: {task.status}\n"
                    f"   - Priority: {task.priority}\n"
                    f"   - Assigned to: {assignee_name}\n"
                    f"   - Created: {task.created_at.strftime('%Y-%m-%d') if task.created_at else 'N/A'}"
                )

            return "\n".join(lines)

        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error listing tasks: {str(e)}"

    @mcp.tool()
    def assign_task(task_id: str, assignee_id: str) -> str:
        """Assign a task to a user.

        Args:
            task_id: Task ID to reassign
            assignee_id: User ID to assign task to

        Returns:
            Confirmation message with new assignment
        """
        from uuid import UUID
        from sqlmodel import Session, select
        from app.db.session import get_session
        from app.services.task_service import TaskService
        from app.models.user import User

        try:
            # Get database session
            session_gen = get_session()
            session = next(session_gen)

            # Get task to determine agency_id
            from app.models.task import Task
            task = session.get(Task, UUID(task_id))
            if not task:
                return f"Error: Task {task_id} not found"

            # Verify assignee exists
            assignee = session.get(User, UUID(assignee_id))
            if not assignee:
                return f"Error: User {assignee_id} not found"

            # Assign task using service
            task_service = TaskService()
            updated_task = task_service.assign_task(
                task_id=UUID(task_id),
                assignee_id=UUID(assignee_id),
                agency_id=task.agency_id,
                session=session
            )

            if not updated_task:
                return f"Error: Failed to assign task {task_id}"

            return (
                f"Task assigned successfully!\n"
                f"- Task: {updated_task.title}\n"
                f"- Assigned to: {updated_task.assignee.full_name if updated_task.assignee else 'Unassigned'}\n"
                f"- Status: {updated_task.status}"
            )

        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error assigning task: {str(e)}"

    @mcp.tool()
    def complete_task(task_id: str) -> str:
        """Mark a task as complete.

        Args:
            task_id: Task ID to complete

        Returns:
            Confirmation message
        """
        from uuid import UUID
        from sqlmodel import Session
        from app.db.session import get_session
        from app.models.task import TaskUpdate, TaskStatus
        from app.services.task_service import TaskService

        try:
            # Get database session
            session_gen = get_session()
            session = next(session_gen)

            # Get task to determine agency_id
            from app.models.task import Task
            task = session.get(Task, UUID(task_id))
            if not task:
                return f"Error: Task {task_id} not found"

            # Update task status to DONE
            task_service = TaskService()
            updated_task = task_service.update_task(
                task_id=UUID(task_id),
                task_data=TaskUpdate(status=TaskStatus.DONE),
                agency_id=task.agency_id,
                session=session
            )

            if not updated_task:
                return f"Error: Failed to complete task {task_id}"

            return (
                f"Task completed successfully!\n"
                f"- Task: {updated_task.title}\n"
                f"- Status: {updated_task.status}\n"
                f"- Completed at: {updated_task.updated_at.strftime('%Y-%m-%d %H:%M') if updated_task.updated_at else 'N/A'}"
            )

        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error completing task: {str(e)}"

    @mcp.tool()
    def complete_task_by_title(task_title: str) -> str:
        """Find a task by title and mark it as complete.

        This tool searches for a task by its title (partial matching supported)
        and marks it as complete. Use this when the user provides a task title
        instead of a task ID.

        Args:
            task_title: Title of the task to complete (partial matching supported)

        Returns:
            Confirmation message with task details

        Example:
            >>> complete_task_by_title("landing page redesign")
        """
        from uuid import UUID
        from sqlmodel import Session, select
        from app.db.session import get_session
        from app.models.task import Task, TaskUpdate, TaskStatus
        from app.services.task_service import TaskService

        try:
            # Get database session
            session_gen = get_session()
            session = next(session_gen)

            # Search for task by title (case-insensitive partial match)
            statement = select(Task).where(
                Task.title.ilike(f"%{task_title}%")
            ).order_by(Task.created_at.desc())

            results = session.exec(statement).all()

            if not results:
                return (
                    f"No task found matching title: '{task_title}'\n"
                    f"Tip: Use list_tasks() to see all available tasks"
                )

            # Use the first (most recent) matching task
            task = results[0]

            # If multiple matches found, warn the user
            if len(results) > 1:
                task_titles = [f"- {t.title}" for t in results]
                return (
                    f"Found {len(results)} tasks matching '{task_title}':\n"
                    + "\n".join(task_titles) +
                    f"\n\nPlease be more specific. I'll use the most recent one: '{task.title}'"
                )

            # Update task status to DONE
            task_service = TaskService()
            updated_task = task_service.update_task(
                task_id=task.id,
                task_data=TaskUpdate(status=TaskStatus.DONE),
                agency_id=task.agency_id,
                session=session
            )

            if not updated_task:
                return f"Error: Failed to complete task '{task_title}'"

            return (
                f"Task completed successfully!\n"
                f"- Task: {updated_task.title}\n"
                f"- ID: {updated_task.id}\n"
                f"- Status: {updated_task.status}\n"
                f"- Completed at: {updated_task.updated_at.strftime('%Y-%m-%d %H:%M') if updated_task.updated_at else 'N/A'}"
            )

        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error completing task by title: {str(e)}"


# Analytics Tools (T019, T062-T064)


def register_analytics_tools(mcp: FastMCP):
    """Register analytics tools with MCP server."""

    @mcp.tool()
    def get_profitability(project_id: str) -> str:
        """Get profitability analysis for a project.

        Args:
            project_id: Project ID to analyze

        Returns:
            Profitability metrics including revenue, cost, profit, and margin
        """
        from uuid import UUID
        from sqlmodel import Session, select, func
        from app.db.session import get_session
        from app.models.project import Project
        from app.models.task import Task, TaskStatus
        from app.services.time_entry_service import TimeEntryService

        try:
            project_uuid = UUID(project_id)

            # Get database session
            session_gen = get_session()
            session = next(session_gen)

            # Get project
            project = session.get(Project, project_uuid)
            if not project:
                return f"Error: Project {project_id} not found"

            time_entry_service = TimeEntryService()

            # Get all time entries for this project
            time_entries = time_entry_service.list_time_entries(
                agency_id=str(project.agency_id),
                project_id=project_uuid,
                session=session
            )

            # Calculate actual hours and cost
            total_hours = sum(entry.hours for entry in time_entries if entry.hours)
            total_cost = total_hours * 50  # Assuming $50/hour average cost

            # Calculate revenue (from project budget or hourly rate)
            budget = getattr(project, 'budget', None)
            hourly_rate = getattr(project, 'hourly_rate', None)

            if budget:
                revenue = budget
            elif hourly_rate:
                revenue = total_hours * hourly_rate
            else:
                return f"Project {project.name} has no budget or hourly rate set. Cannot calculate profitability."

            # Calculate profit and margin
            profit = revenue - total_cost
            margin = (profit / revenue * 100) if revenue > 0 else 0

            # Format response
            response = [
                f"Profitability Analysis for Project: {project.name}",
                f"",
                f"**Financial Metrics:**",
                f"- Revenue: ${revenue:,.2f}",
                f"- Cost: ${total_cost:,.2f} (based on {total_hours:.1f} hours @ $50/hr)",
                f"- Profit: ${profit:,.2f}",
                f"- Margin: {margin:.1f}%",
                f"",
            ]

            # Add comparison to budget if available
            if budget:
                budget_used_pct = (revenue / budget * 100) if budget > 0 else 0
                response.extend([
                    f"**Budget Comparison:**",
                    f"- Budget: ${budget:,.2f}",
                    f"- Used: ${revenue:,.2f} ({budget_used_pct:.1f}%)",
                ])

                # Add status message
                if margin < 0:
                    response.append(f"- Status: ⚠️ OVER BUDGET (loss of ${abs(profit):,.2f})")
                elif margin < 20:
                    response.append(f"- Status: ⚠️ Low margin (target: 20%+)")
                else:
                    response.append(f"- Status: ✅ Healthy margin")

            return "\n".join(response)

        except ValueError:
            return f"Error: Invalid project ID format: {project_id}"
        except Exception as e:
            return f"Error calculating profitability: {str(e)}"

    @mcp.tool()
    def workload_summary(agency_id: str) -> str:
        """Get workload summary for an agency.

        Args:
            agency_id: Agency ID to analyze

        Returns:
            Workload summary showing team member utilization
        """
        from uuid import UUID
        from sqlmodel import Session, select
        from app.db.session import get_session
        from app.models.task import Task
        from app.models.user import User

        try:
            agency_uuid = UUID(agency_id)

            # Get database session
            session_gen = get_session()
            session = next(session_gen)

            # Get all team members
            team_members = session.exec(
                select(User).where(User.agency_id == agency_uuid)
            ).all()

            if not team_members:
                return f"No team members found for agency {agency_id}"

            # Build workload summary
            summary_lines = [
                f"Workload Summary for Agency",
                f"",
                f"{'Team Member':<30} {'Tasks':<8} {'Hours':<10} {'Utilization':<12}",
                f"{'-' * 70}",
            ]

            total_tasks = 0
            total_hours = 0
            over_capacity = 0

            for member in team_members:
                name = member.full_name or member.email
                # Limit name length for display
                if len(name) > 28:
                    name = name[:25] + "..."

                # Get active tasks for this member
                active_tasks = session.exec(
                    select(Task).where(
                        Task.assignee_id == member.id,
                        Task.status.in_(['TODO', 'IN_PROGRESS', 'BLOCKED'])
                    )
                ).all()

                task_count = len(active_tasks)

                # Estimate hours (4 hours per task)
                hours_assigned = task_count * 4

                # Get capacity
                capacity = getattr(member, 'capacity_hours', 40)

                # Calculate utilization
                utilization = (hours_assigned / capacity * 100) if capacity > 0 else 0

                # Track totals
                total_tasks += task_count
                total_hours += hours_assigned
                if utilization > 100:
                    over_capacity += 1

                # Format utilization with warning if over capacity
                util_str = f"{utilization:.0f}%"
                if utilization > 100:
                    util_str += " ⚠️"
                elif utilization > 80:
                    util_str += " ~"

                summary_lines.append(f"{name:<30} {task_count:<8} {hours_assigned:<10.1f} {util_str:<12}")

            # Add summary statistics
            avg_utilization = (total_hours / (len(team_members) * 40) * 100) if team_members else 0

            summary_lines.extend([
                f"{'-' * 70}",
                f"{'TOTAL':<30} {total_tasks:<8} {total_hours:<10.1f}",
                f"",
                f"**Summary:**",
                f"- Total team members: {len(team_members)}",
                f"- Average utilization: {avg_utilization:.0f}%",
                f"- Members over capacity: {over_capacity}",
            ])

            if over_capacity > 0:
                summary_lines.append(f"- ⚠️ Consider redistributing tasks from over-capacity members")

            return "\n".join(summary_lines)

        except ValueError:
            return f"Error: Invalid agency ID format: {agency_id}"
        except Exception as e:
            return f"Error generating workload summary: {str(e)}"


# AI Recommendation Tools (T020, T057-T061)


def register_recommendation_tools(mcp: FastMCP):
    """Register AI recommendation tools with MCP server."""

    @mcp.tool()
    def suggest_assignee(task_id: str) -> str:
        """Suggest the best assignee for a task using AI reasoning.

        Analyzes team member skills, current workload, and availability to recommend
        the most suitable person for a task.

        Args:
            task_id: Task ID to find assignee for

        Returns:
            Recommended assignee with reasoning (skills match, workload score, alternatives)
        """
        from uuid import UUID
        from sqlmodel import Session, select
        from app.db.session import get_session
        from app.models.task import Task
        from app.models.user import User
        from app.models.project import Project

        try:
            task_uuid = UUID(task_id)

            # Get database session
            session_gen = get_session()
            session = next(session_gen)

            # Get task with project info
            task = session.get(Task, task_uuid)
            if not task:
                return f"Error: Task {task_id} not found"

            # Get project to determine agency
            project = session.get(Project, task.project_id) if task.project_id else None
            if not project:
                return f"Error: Task {task_id} has no project assigned"

            agency_id = project.agency_id

            # Get all team members for this agency
            team_members = session.exec(
                select(User).where(User.agency_id == agency_id)
            ).all()

            if not team_members:
                return f"Error: No team members found for this project"

            # Analyze each team member
            candidates = []
            for member in team_members:
                # Get member's skills
                skills = getattr(member, 'skills', [])
                skills_list = skills if isinstance(skills, list) else []

                # Calculate current workload
                current_tasks = session.exec(
                    select(Task).where(
                        Task.assignee_id == member.id,
                        Task.status.in_(['TODO', 'IN_PROGRESS', 'BLOCKED'])
                    )
                ).all()
                task_count = len(current_tasks)

                # Estimate hours (assuming 4 hours per task as baseline)
                hours_assigned = task_count * 4

                # Calculate utilization percentage
                capacity = getattr(member, 'capacity_hours', 40)  # Default 40 hours/week
                utilization = (hours_assigned / capacity * 100) if capacity > 0 else 0

                # Calculate availability score (lower utilization = higher availability)
                availability_score = max(0, 100 - utilization)

                # Skills matching (basic keyword matching on task title/description)
                task_text = f"{task.title} {task.description or ''}".lower()
                skills_match = 0
                for skill in skills_list:
                    if skill.lower() in task_text:
                        skills_match += 1

                # Calculate overall score
                # 40% skills match, 30% availability, 30% lower workload
                score = (
                    (skills_match * 10) +  # Skills: up to 50 points
                    (availability_score * 0.3) +  # Availability: up to 30 points
                    (max(0, 100 - utilization) * 0.2)  # Workload: up to 20 points
                )

                candidates.append({
                    'user_id': str(member.id),
                    'name': member.full_name or member.email,
                    'email': member.email,
                    'skills': skills_list,
                    'task_count': task_count,
                    'hours_assigned': hours_assigned,
                    'utilization_percentage': round(utilization, 1),
                    'availability_score': round(availability_score, 1),
                    'skills_match': skills_match,
                    'overall_score': round(score, 1)
                })

            # Sort by overall score
            candidates.sort(key=lambda x: x['overall_score'], reverse=True)

            # Get top recommendation
            if not candidates:
                return f"No suitable assignees found for task {task_id}"

            top_choice = candidates[0]
            alternatives = candidates[1:4]  # Top 3 alternatives

            # Build reasoning
            reasoning_parts = [
                f"Recommended Assignee: {top_choice['name']} ({top_choice['email']})",
                f"",
                f"**Reasoning:**",
                f"",
                f"**Skills Match:** Found {top_choice['skills_match']} relevant skill matches",
                f"- Task requires: {task.title}",
            ]

            if top_choice['skills']:
                reasoning_parts.append(f"- Candidate has: {', '.join(top_choice['skills'])}")

            reasoning_parts.extend([
                f"",
                f"**Workload Analysis:**",
                f"- Current tasks: {top_choice['task_count']}",
                f"- Hours assigned: {top_choice['hours_assigned']}",
                f"- Utilization: {top_choice['utilization_percentage']}%",
                f"- Availability score: {top_choice['availability_score']}/100",
                f"",
                f"**Overall Score:** {top_choice['overall_score']}/100",
            ])

            if alternatives:
                reasoning_parts.append(f"")
                reasoning_parts.append(f"**Alternative Candidates:**")
                for i, alt in enumerate(alternatives, 1):
                    reasoning_parts.append(
                        f"{i}. {alt['name']} - Score: {alt['overall_score']}/100 "
                        f"({alt['task_count']} tasks, {alt['utilization_percentage']}% utilized)"
                    )

            return "\n".join(reasoning_parts)

        except ValueError:
            return f"Error: Invalid task ID format: {task_id}"
        except Exception as e:
            return f"Error suggesting assignee: {str(e)}"


# Project Management Tools


def register_project_tools(mcp: FastMCP):
    """Register project management tools with MCP server."""

    @mcp.tool()
    def list_projects(
        agency_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> str:
        """List projects in TeamFlow with optional filters.

        Args:
            agency_id: Filter by agency ID
            status: Filter by status (ACTIVE, COMPLETED, ON_HOLD)
            limit: Maximum number of projects to return (default: 50)

        Returns:
            List of projects with their details
        """
        from uuid import UUID
        from sqlmodel import Session, select
        from app.db.session import get_session
        from app.models.project import Project, ProjectStatus

        try:
            # Get database session
            session_gen = get_session()
            session = next(session_gen)

            # Build query
            query = select(Project)
            if agency_id:
                query = query.where(Project.agency_id == UUID(agency_id))
            if status:
                status_map = {
                    'active': ProjectStatus.active,
                    'completed': ProjectStatus.completed,
                    'on_hold': ProjectStatus.on_hold,
                }
                project_status = status_map.get(status.lower())
                if project_status:
                    query = query.where(Project.status == project_status)

            query = query.limit(limit)
            projects = session.exec(query).all()

            if not projects:
                return "No projects found matching the specified filters."

            # Format results
            lines = [
                f"Found {len(projects)} project(s):",
                f"",
            ]

            for i, project in enumerate(projects[:limit], 1):
                lines.append(
                    f"{i}. **{project.name}** (ID: {project.id})\n"
                    f"   - Status: {project.status}\n"
                    f"   - Created: {project.created_at.strftime('%Y-%m-%d') if project.created_at else 'N/A'}"
                )

            return "\n".join(lines)

        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error listing projects: {str(e)}"

    @mcp.tool()
    def create_project(
        title: str,
        description: Optional[str] = None,
        agency_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        """Create a new project in TeamFlow.

        Args:
            title: Project title
            description: Project description
            agency_id: Agency ID (optional, will use default if not provided)
            status: Project status (ACTIVE, COMPLETED, ON_HOLD)

        Returns:
            Confirmation message with project ID
        """
        from uuid import UUID
        from sqlmodel import Session, select
        from app.db.session import get_session
        from app.models.project import ProjectCreate, ProjectStatus
        from app.services.project_service import ProjectService
        from app.models.user import User

        try:
            # Get database session
            session_gen = get_session()
            session = next(session_gen)

            # Determine agency_id
            if agency_id:
                agency_uuid = UUID(agency_id)
            else:
                # Use default agency - get from first user
                first_user = session.exec(select(User).limit(1)).first()
                if not first_user:
                    return "Error: No users found. Cannot determine agency."
                agency_uuid = first_user.agency_id

            # Map status string to enum
            status_map = {
                'active': ProjectStatus.active,
                'completed': ProjectStatus.completed,
                'on_hold': ProjectStatus.on_hold,
            }

            # Create ProjectCreate object (model uses 'name' field, not 'title')
            project_data = ProjectCreate(
                name=title,
                description=description,
                status=status_map.get(status.lower(), ProjectStatus.active) if status else ProjectStatus.active,
            )

            # Create project using service
            project_service = ProjectService()
            project = project_service.create_project(project_data, agency_uuid, session)

            return (
                f"Project created successfully!\n"
                f"- ID: {project.id}\n"
                f"- Name: {project.name}\n"
                f"- Status: {project.status}"
            )

        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error creating project: {str(e)}"

    @mcp.tool()
    def get_project_details(project_id: str) -> str:
        """Get detailed information about a project.

        Args:
            project_id: Project ID to get details for

        Returns:
            Project details with task summary
        """
        from uuid import UUID
        from sqlmodel import Session, select, func
        from app.db.session import get_session
        from app.models.project import Project
        from app.models.task import Task, TaskStatus

        try:
            project_uuid = UUID(project_id)

            # Get database session
            session_gen = get_session()
            session = next(session_gen)

            # Get project
            project = session.get(Project, project_uuid)
            if not project:
                return f"Error: Project {project_id} not found"

            # Get task statistics
            total_tasks = session.exec(
                select(func.count(Task.id)).where(Task.project_id == project_uuid)
            ).one()

            completed_tasks = session.exec(
                select(func.count(Task.id)).where(
                    Task.project_id == project_uuid,
                    Task.status == TaskStatus.DONE
                )
            ).one()

            in_progress_tasks = session.exec(
                select(func.count(Task.id)).where(
                    Task.project_id == project_uuid,
                    Task.status == TaskStatus.IN_PROGRESS
                )
            ).one()

            # Format response
            lines = [
                f"Project Details: {project.name}",
                f"",
                f"**Basic Information:**",
                f"- ID: {project.id}",
                f"- Description: {project.description or 'N/A'}",
                f"- Status: {project.status}",
                f"- Created: {project.created_at.strftime('%Y-%m-%d') if project.created_at else 'N/A'}",
                f"",
                f"**Task Summary:**",
                f"- Total tasks: {total_tasks or 0}",
                f"- Completed: {completed_tasks or 0}",
                f"- In Progress: {in_progress_tasks or 0}",
                f"",
            ]

            # Calculate completion percentage
            if total_tasks and total_tasks > 0:
                completion_pct = (completed_tasks / total_tasks * 100) if total_tasks else 0
                lines.append(f"- Completion: {completion_pct:.1f}%")

                # Add status message
                if completion_pct >= 100:
                    lines.append(f"- Status: ✅ Project Complete")
                elif completion_pct >= 75:
                    lines.append(f"- Status: 🟢 Good Progress")
                elif completion_pct >= 50:
                    lines.append(f"- Status: 🟡 In Progress")
                elif completion_pct >= 25:
                    lines.append(f"- Status: 🟠 Just Started")
                else:
                    lines.append(f"- Status: 🔴 Needs Attention")

            return "\n".join(lines)

        except ValueError:
            return f"Error: Invalid project ID format: {project_id}"
        except Exception as e:
            return f"Error getting project details: {str(e)}"


# Task Update Tools


def register_task_update_tools(mcp: FastMCP):
    """Register task update tools with MCP server."""

    @mcp.tool()
    def update_task_priority(task_id: str, priority: str) -> str:
        """Update the priority of a task.

        Args:
            task_id: Task ID to update
            priority: New priority (LOW, MEDIUM, HIGH)

        Returns:
            Confirmation message
        """
        from uuid import UUID
        from sqlmodel import Session
        from app.db.session import get_session
        from app.models.task import TaskUpdate, TaskPriority
        from app.services.task_service import TaskService

        try:
            # Get database session
            session_gen = get_session()
            session = next(session_gen)

            # Get task to determine agency_id
            from app.models.task import Task
            task = session.get(Task, UUID(task_id))
            if not task:
                return f"Error: Task {task_id} not found"

            # Map priority string to enum
            priority_map = {
                'low': TaskPriority.LOW,
                'medium': TaskPriority.MEDIUM,
                'high': TaskPriority.HIGH,
            }

            new_priority = priority_map.get(priority.lower())
            if not new_priority:
                return f"Error: Invalid priority '{priority}'. Use LOW, MEDIUM, or HIGH."

            # Update task using service
            task_service = TaskService()
            updated_task = task_service.update_task(
                task_id=UUID(task_id),
                task_data=TaskUpdate(priority=new_priority),
                agency_id=task.agency_id,
                session=session
            )

            if not updated_task:
                return f"Error: Failed to update task {task_id}"

            return (
                f"Task priority updated successfully!\n"
                f"- Task: {updated_task.title}\n"
                f"- New Priority: {updated_task.priority}"
            )

        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error updating task priority: {str(e)}"

    @mcp.tool()
    def update_task_due_date(task_id: str, due_date: str) -> str:
        """Update the due date of a task.

        Args:
            task_id: Task ID to update
            due_date: New due date (format: YYYY-MM-DD)

        Returns:
            Confirmation message
        """
        from uuid import UUID
        from sqlmodel import Session
        from app.db.session import get_session
        from app.models.task import TaskUpdate
        from app.services.task_service import TaskService
        from datetime import datetime

        try:
            # Parse due date
            parsed_date = datetime.strptime(due_date, "%Y-%m-%d")

            # Get database session
            session_gen = get_session()
            session = next(session_gen)

            # Get task to determine agency_id
            from app.models.task import Task
            task = session.get(Task, UUID(task_id))
            if not task:
                return f"Error: Task {task_id} not found"

            # Update task using service
            task_service = TaskService()
            updated_task = task_service.update_task(
                task_id=UUID(task_id),
                task_data=TaskUpdate(due_date=parsed_date),
                agency_id=task.agency_id,
                session=session
            )

            if not updated_task:
                return f"Error: Failed to update task {task_id}"

            return (
                f"Task due date updated successfully!\n"
                f"- Task: {updated_task.title}\n"
                f"- New Due Date: {updated_task.due_date.strftime('%Y-%m-%d') if updated_task.due_date else 'Not set'}"
            )

        except ValueError:
            return f"Error: Invalid date format. Use YYYY-MM-DD (e.g., 2025-12-31)"
        except Exception as e:
            return f"Error updating task due date: {str(e)}"

    @mcp.tool()
    def update_task_status(task_id: str, status: str) -> str:
        """Update the status of a task.

        Args:
            task_id: Task ID to update
            status: New status (TODO, IN_PROGRESS, BLOCKED, DONE)

        Returns:
            Confirmation message
        """
        from uuid import UUID
        from sqlmodel import Session
        from app.db.session import get_session
        from app.models.task import TaskUpdate, TaskStatus
        from app.services.task_service import TaskService

        try:
            # Get database session
            session_gen = get_session()
            session = next(session_gen)

            # Get task to determine agency_id
            from app.models.task import Task
            task = session.get(Task, UUID(task_id))
            if not task:
                return f"Error: Task {task_id} not found"

            # Map status string to enum
            status_map = {
                'todo': TaskStatus.TODO,
                'in_progress': TaskStatus.IN_PROGRESS,
                'blocked': TaskStatus.BLOCKED,
                'done': TaskStatus.DONE,
            }

            new_status = status_map.get(status.lower())
            if not new_status:
                return f"Error: Invalid status '{status}'. Use TODO, IN_PROGRESS, BLOCKED, or DONE."

            # Update task using service
            task_service = TaskService()
            updated_task = task_service.update_task(
                task_id=UUID(task_id),
                task_data=TaskUpdate(status=new_status),
                agency_id=task.agency_id,
                session=session
            )

            if not updated_task:
                return f"Error: Failed to update task {task_id}"

            return (
                f"Task status updated successfully!\n"
                f"- Task: {updated_task.title}\n"
                f"- New Status: {updated_task.status}"
            )

        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error updating task status: {str(e)}"

    @mcp.tool()
    def archive_task(task_id: str) -> str:
        """Archive a task (mark as completed and hide from active lists).

        Args:
            task_id: Task ID to archive

        Returns:
            Confirmation message
        """
        from uuid import UUID
        from sqlmodel import Session
        from app.db.session import get_session
        from app.models.task import TaskUpdate, TaskStatus
        from app.services.task_service import TaskService

        try:
            # Get database session
            session_gen = get_session()
            session = next(session_gen)

            # Get task to determine agency_id
            from app.models.task import Task
            task = session.get(Task, UUID(task_id))
            if not task:
                return f"Error: Task {task_id} not found"

            # Archive by setting status to DONE
            task_service = TaskService()
            updated_task = task_service.update_task(
                task_id=UUID(task_id),
                task_data=TaskUpdate(status=TaskStatus.DONE),
                agency_id=task.agency_id,
                session=session
            )

            if not updated_task:
                return f"Error: Failed to archive task {task_id}"

            return (
                f"Task archived successfully!\n"
                f"- Task: {updated_task.title}\n"
                f"- Status: {updated_task.status}"
            )

        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error archiving task: {str(e)}"

    @mcp.tool()
    def delete_task(task_id: str) -> str:
        """Delete a task permanently.

        Args:
            task_id: Task ID to delete

        Returns:
            Confirmation message
        """
        from uuid import UUID
        from sqlmodel import Session
        from app.db.session import get_session
        from app.services.task_service import TaskService

        try:
            # Get database session
            session_gen = get_session()
            session = next(session_gen)

            # Get task to determine agency_id
            from app.models.task import Task
            task = session.get(Task, UUID(task_id))
            if not task:
                return f"Error: Task {task_id} not found"

            task_title = task.title

            # Delete task using service
            task_service = TaskService()
            success = task_service.delete_task(
                task_id=UUID(task_id),
                agency_id=task.agency_id,
                session=session
            )

            if not success:
                return f"Error: Failed to delete task {task_id}"

            return (
                f"Task deleted successfully!\n"
                f"- Deleted Task: {task_title}\n"
                f"- ID: {task_id}"
            )

        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error deleting task: {str(e)}"

    @mcp.tool()
    def delete_task_by_title(task_title: str) -> str:
        """Find a task by title and delete it permanently.

        This tool searches for a task by its title (partial matching supported)
        and deletes it permanently. Use this when the user provides a task title
        instead of a task ID.

        WARNING: Deletion is permanent and cannot be undone.

        Args:
            task_title: Title of the task to delete (partial matching supported)

        Returns:
            Confirmation message with task details

        Example:
            >>> delete_task_by_title("old task")
        """
        from uuid import UUID
        from sqlmodel import Session, select
        from app.db.session import get_session
        from app.models.task import Task
        from app.services.task_service import TaskService

        try:
            # Get database session
            session_gen = get_session()
            session = next(session_gen)

            # Search for task by title (case-insensitive partial match)
            statement = select(Task).where(
                Task.title.ilike(f"%{task_title}%")
            ).order_by(Task.created_at.desc())

            results = session.exec(statement).all()

            if not results:
                return (
                    f"No task found matching title: '{task_title}'\n"
                    f"Tip: Use list_tasks() to see all available tasks"
                )

            # Use the first (most recent) matching task
            task = results[0]

            # If multiple matches found, warn the user
            if len(results) > 1:
                task_titles = [f"- {t.title}" for t in results]
                return (
                    f"Found {len(results)} tasks matching '{task_title}':\n"
                    + "\n".join(task_titles) +
                    f"\n\nPlease be more specific. I'll delete the most recent one: '{task.title}'"
                )

            # Delete task using service
            task_service = TaskService()
            success = task_service.delete_task(
                task_id=task.id,
                agency_id=task.agency_id,
                session=session
            )

            if not success:
                return f"Error: Failed to delete task '{task_title}'"

            return (
                f"Task deleted successfully!\n"
                f"- Deleted Task: {task.title}\n"
                f"- ID: {task.id}"
            )

        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error deleting task by title: {str(e)}"

    @mcp.tool()
    def archive_task_by_title(task_title: str) -> str:
        """Find a task by title and archive it (mark as done and hide from active lists).

        This tool searches for a task by its title (partial matching supported)
        and archives it. Archived tasks are marked as done but can be recovered.
        Use this when the user provides a task title instead of a task ID.

        Args:
            task_title: Title of the task to archive (partial matching supported)

        Returns:
            Confirmation message with task details

        Example:
            >>> archive_task_by_title("completed feature")
        """
        from uuid import UUID
        from sqlmodel import Session, select
        from app.db.session import get_session
        from app.models.task import Task, TaskUpdate, TaskStatus
        from app.services.task_service import TaskService

        try:
            # Get database session
            session_gen = get_session()
            session = next(session_gen)

            # Search for task by title (case-insensitive partial match)
            statement = select(Task).where(
                Task.title.ilike(f"%{task_title}%")
            ).order_by(Task.created_at.desc())

            results = session.exec(statement).all()

            if not results:
                return (
                    f"No task found matching title: '{task_title}'\n"
                    f"Tip: Use list_tasks() to see all available tasks"
                )

            # Use the first (most recent) matching task
            task = results[0]

            # If multiple matches found, warn the user
            if len(results) > 1:
                task_titles = [f"- {t.title}" for t in results]
                return (
                    f"Found {len(results)} tasks matching '{task_title}':\n"
                    + "\n".join(task_titles) +
                    f"\n\nPlease be more specific. I'll archive the most recent one: '{task.title}'"
                )

            # Archive by setting status to DONE
            task_service = TaskService()
            updated_task = task_service.update_task(
                task_id=task.id,
                task_data=TaskUpdate(status=TaskStatus.DONE),
                agency_id=task.agency_id,
                session=session
            )

            if not updated_task:
                return f"Error: Failed to archive task '{task_title}'"

            return (
                f"Task archived successfully!\n"
                f"- Task: {updated_task.title}\n"
                f"- ID: {task.id}\n"
                f"- Status: {updated_task.status}"
            )

        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error archiving task by title: {str(e)}"


# Time Entry Tools


def register_time_entry_tools(mcp: FastMCP):
    """Register time entry tools with MCP server."""

    @mcp.tool()
    def add_time_entry(
        task_id: str,
        hours: float,
        description: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> str:
        """Add a time entry to track work on a task.

        Args:
            task_id: Task ID to log time against
            hours: Hours worked (e.g., 2.5 for 2.5 hours)
            description: Description of work done
            user_id: User ID (optional, will use assignee if not provided)

        Returns:
            Confirmation message with time entry ID
        """
        from uuid import UUID
        from sqlmodel import Session, select
        from app.db.session import get_session
        from app.models.time_entry import TimeEntryCreate
        from app.services.time_entry_service import TimeEntryService
        from app.models.task import Task
        from app.models.user import User

        try:
            # Get database session
            session_gen = get_session()
            session = next(session_gen)

            # Get task
            task = session.get(Task, UUID(task_id))
            if not task:
                return f"Error: Task {task_id} not found"

            # Determine user_id
            if user_id:
                user_uuid = UUID(user_id)
            else:
                # Use task assignee
                user_uuid = task.assignee_id

            # Create TimeEntry object
            time_entry_data = TimeEntryCreate(
                task_id=UUID(task_id),
                user_id=user_uuid,
                hours=hours,
                description=description,
            )

            # Create time entry using service
            time_entry_service = TimeEntryService()
            time_entry = time_entry_service.create_time_entry(
                time_entry_data, task.agency_id, session
            )

            return (
                f"Time entry added successfully!\n"
                f"- ID: {time_entry.id}\n"
                f"- Hours: {time_entry.hours}\n"
                f"- Task: {task.title}"
            )

        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error adding time entry: {str(e)}"

    @mcp.tool()
    def list_time_entries(
        task_id: Optional[str] = None,
        user_id: Optional[str] = None,
        agency_id: Optional[str] = None,
        limit: int = 50,
    ) -> str:
        """List time entries with optional filters.

        Args:
            task_id: Filter by task ID
            user_id: Filter by user ID
            agency_id: Filter by agency ID
            limit: Maximum number of time entries to return (default: 50)

        Returns:
            List of time entries with details
        """
        from uuid import UUID
        from sqlmodel import Session
        from app.db.session import get_session
        from app.services.time_entry_service import TimeEntryService

        try:
            # Get database session
            session_gen = get_session()
            session = next(session_gen)

            # Determine agency_id
            if agency_id:
                agency_uuid = UUID(agency_id)
            elif task_id:
                from app.models.task import Task
                task = session.get(Task, UUID(task_id))
                if not task:
                    return f"Error: Task {task_id} not found"
                agency_uuid = task.agency_id
            elif user_id:
                from app.models.user import User
                user = session.get(User, UUID(user_id))
                if not user:
                    return f"Error: User {user_id} not found"
                agency_uuid = user.agency_id
            else:
                return "Error: Must provide at least one of: task_id, user_id, or agency_id"

            # List time entries using service
            time_entry_service = TimeEntryService()
            time_entries = time_entry_service.list_time_entries(
                agency_id=str(agency_uuid),
                session=session,
                task_id=UUID(task_id) if task_id else None,
                user_id=UUID(user_id) if user_id else None,
            )

            if not time_entries:
                return "No time entries found matching the specified filters."

            # Format results
            lines = [
                f"Found {len(time_entries)} time entr(ies):",
                f"",
            ]

            for i, entry in enumerate(time_entries[:limit], 1):
                user_name = entry.user.full_name if entry.user else "Unknown"
                task_title = entry.task.title if entry.task else "Unknown"
                lines.append(
                    f"{i}. **{task_title}** - {entry.hours}h by {user_name}\n"
                    f"   - Date: {entry.created_at.strftime('%Y-%m-%d') if entry.created_at else 'N/A'}\n"
                    f"   - Description: {entry.description or 'No description'}"
                )

            return "\n".join(lines)

        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error listing time entries: {str(e)}"

    @mcp.tool()
    def get_time_for_task(task_id: str) -> str:
        """Get total time tracked for a task.

        Args:
            task_id: Task ID to get time summary for

        Returns:
            Time summary with total hours and entry count
        """
        from uuid import UUID
        from sqlmodel import Session
        from app.db.session import get_session
        from app.services.time_entry_service import TimeEntryService
        from app.models.task import Task

        try:
            # Get database session
            session_gen = get_session()
            session = next(session_gen)

            # Get task
            task = session.get(Task, UUID(task_id))
            if not task:
                return f"Error: Task {task_id} not found"

            # List time entries for this task
            time_entry_service = TimeEntryService()
            time_entries = time_entry_service.list_time_entries(
                agency_id=str(task.agency_id),
                session=session,
                task_id=UUID(task_id),
            )

            # Calculate totals
            total_hours = sum(entry.hours for entry in time_entries if entry.hours)
            entry_count = len(time_entries)

            # Format response
            lines = [
                f"Time Summary for Task: {task.title}",
                f"",
                f"**Total Time Tracked:**",
                f"- Hours: {total_hours:.1f}",
                f"- Entries: {entry_count}",
                f"",
            ]

            # Add breakdown by user if entries exist
            if time_entries:
                user_hours = {}
                for entry in time_entries:
                    user_name = entry.user.full_name if entry.user else "Unknown"
                    user_hours[user_name] = user_hours.get(user_name, 0) + (entry.hours or 0)

                lines.append("**Breakdown by User:**")
                for user_name, hours in sorted(user_hours.items(), key=lambda x: x[1], reverse=True):
                    lines.append(f"- {user_name}: {hours:.1f}h")

            return "\n".join(lines)

        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error getting time for task: {str(e)}"

    @mcp.tool()
    def update_time_entry(
        time_entry_id: str,
        hours: Optional[float] = None,
        description: Optional[str] = None,
    ) -> str:
        """Update an existing time entry.

        Args:
            time_entry_id: Time entry ID to update
            hours: New hours value (optional)
            description: New description (optional)

        Returns:
            Confirmation message
        """
        from uuid import UUID
        from sqlmodel import Session
        from app.db.session import get_session
        from app.models.time_entry import TimeEntryUpdate
        from app.services.time_entry_service import TimeEntryService

        try:
            # Get database session
            session_gen = get_session()
            session = next(session_gen)

            # Get time entry to determine agency_id
            from app.models.time_entry import TimeEntry
            time_entry = session.get(TimeEntry, UUID(time_entry_id))
            if not time_entry:
                return f"Error: Time entry {time_entry_id} not found"

            # Build update data
            update_data = {}
            if hours is not None:
                update_data['hours'] = hours
            if description is not None:
                update_data['description'] = description

            if not update_data:
                return "Error: No updates provided. Provide hours or description."

            # Update time entry using service
            time_entry_service = TimeEntryService()
            updated_entry = time_entry_service.update_time_entry(
                time_entry_id=UUID(time_entry_id),
                time_entry_data=TimeEntryUpdate(**update_data),
                agency_id=time_entry.task.agency_id,
                session=session
            )

            if not updated_entry:
                return f"Error: Failed to update time entry {time_entry_id}"

            return (
                f"Time entry updated successfully!\n"
                f"- Hours: {updated_entry.hours}\n"
                f"- Description: {updated_entry.description or 'No description'}"
            )

        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error updating time entry: {str(e)}"

    @mcp.tool()
    def delete_time_entry(time_entry_id: str) -> str:
        """Delete a time entry.

        Args:
            time_entry_id: Time entry ID to delete

        Returns:
            Confirmation message
        """
        from uuid import UUID
        from sqlmodel import Session
        from app.db.session import get_session
        from app.services.time_entry_service import TimeEntryService

        try:
            # Get database session
            session_gen = get_session()
            session = next(session_gen)

            # Get time entry to determine agency_id
            from app.models.time_entry import TimeEntry
            time_entry = session.get(TimeEntry, UUID(time_entry_id))
            if not time_entry:
                return f"Error: Time entry {time_entry_id} not found"

            # Delete time entry using service
            time_entry_service = TimeEntryService()
            success = time_entry_service.delete_time_entry(
                time_entry_id=UUID(time_entry_id),
                agency_id=time_entry.task.agency_id,
                session=session
            )

            if not success:
                return f"Error: Failed to delete time entry {time_entry_id}"

            return (
                f"Time entry deleted successfully!\n"
                f"- ID: {time_entry_id}"
            )

        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error deleting time entry: {str(e)}"
