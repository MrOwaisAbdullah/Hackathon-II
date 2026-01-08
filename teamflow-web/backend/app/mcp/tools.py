"""MCP tools for TeamFlow (T018-T020).

These tools expose service layer methods as MCP tools for AI agents.
Tool categories:
- Knowledge Base: search_knowledge_base (RAG)
- Task Management: add_task, list_tasks, assign_task, complete_task
- Analytics: get_profitability, workload_summary
- Recommendations: suggest_assignee
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from app.services.task_service import TaskService
from app.services.analytics_service import AnalyticsService


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
                return f"Project {project.title} has no budget or hourly rate set. Cannot calculate profitability."

            # Calculate profit and margin
            profit = revenue - total_cost
            margin = (profit / revenue * 100) if revenue > 0 else 0

            # Format response
            response = [
                f"Profitability Analysis for Project: {project.title}",
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
