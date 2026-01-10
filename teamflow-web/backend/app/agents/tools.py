"""OpenAI Agents SDK tools for TeamFlow.

These tools are compatible with OpenAI Agents SDK using @function_tool decorator.
They mirror the MCP tool functionality but work natively with the Agents SDK.

Tool categories:
- Knowledge Base: search_knowledge_base (RAG)
- Task Management: add_task, list_tasks, assign_task, complete_task
- Analytics: get_profitability, workload_summary
- Recommendations: suggest_assignee
"""
from typing import Optional
from agents import function_tool, RunContextWrapper
from uuid import UUID

# Knowledge Base Tools (RAG)


@function_tool
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


# Task Management Tools


@function_tool
def add_task(
    ctx: RunContextWrapper,
    title: str,
    description: Optional[str] = None,
    project_name: Optional[str] = None,
    assignee_name: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    due_date: Optional[str] = None,
) -> str:
    """Create a new task in TeamFlow.

    All parameters except title are OPTIONAL with sensible defaults:
    - No description? Task created without description
    - No project? Task created without project
    - No assignee? Task created UNASSIGNED
    - No priority? Defaults to MEDIUM
    - No status? Defaults to TODO
    - No due_date? No deadline set

    Args:
        ctx: Agent execution context (automatically injected)
        title: Task title (required)
        description: Task description (optional)
        project_name: Name of the project - searches by partial match (optional)
        assignee_name: Name of the user to assign task to - if not provided, task is UNASSIGNED (optional)
        priority: Priority level - LOW, MEDIUM, HIGH, or URGENT (default: MEDIUM)
        status: Task status - TODO, IN_PROGRESS, BLOCKED, or DONE (default: TODO)
        due_date: Due date in YYYY-MM-DD format (e.g., "2026-01-10") (optional)

    Returns:
        Confirmation message with task details

    Example:
        >>> add_task(title="Review FB ads", description="Review Facebook ad campaign")
        Creates unassigned task with medium priority, todo status

        >>> add_task(title="Fix bug", assignee_name="Owais", priority="high", due_date="2026-01-15")
        Creates high-priority task assigned to Owais with due date
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"[add_task] Called with title={title}, project_name={project_name}, description={description}")
    try:
        from app.services.task_service import TaskService
        from app.services.project_service import ProjectService
        from app.models.task import TaskPriority, TaskStatus, TaskCreate
        from app.db.session import engine
        from sqlmodel import Session, select
        from app.models.project import Project

        # Get agency_id from context
        # ctx.context can be an AgentContext object (from ChatKit) or a dict (from orchestrator)
        context_obj = ctx.context
        if context_obj is None:
            logger.error(f"[add_task] No context available")
            return "Error: No context available. Please ensure you are logged in."

        # Handle AgentContext object from ChatKit
        if hasattr(context_obj, 'request_context'):
            context_dict = context_obj.request_context
        elif isinstance(context_obj, dict):
            context_dict = context_obj
        else:
            logger.error(f"[add_task] Unexpected context type: {type(context_obj)}")
            return "Error: Unexpected context type."

        agency_id_str = context_dict.get("agency_id") if context_dict else None
        if not agency_id_str:
            logger.error(f"[add_task] No agency_id in context_dict: {context_dict}")
            return "Error: Could not determine agency_id from request context. Please ensure you are logged in."

        agency_id = UUID(agency_id_str)
        logger.info(f"[add_task] Using agency_id: {agency_id}")

        # Map priority string to enum (TaskPriority uses UPPERCASE)
        priority_map = {
            "low": TaskPriority.LOW,
            "medium": TaskPriority.MEDIUM,
            "high": TaskPriority.HIGH,
            "urgent": TaskPriority.HIGH,
        }

        # Map status string to enum (TaskStatus uses UPPERCASE)
        status_map = {
            "todo": TaskStatus.TODO,
            "in_progress": TaskStatus.DOING,
            "doing": TaskStatus.DOING,
            "blocked": TaskStatus.REVIEW,  # Map blocked to REVIEW as closest equivalent
            "review": TaskStatus.REVIEW,
            "done": TaskStatus.DONE,
        }

        # Create database session with proper context manager
        with Session(engine) as db:
            task_service = TaskService()

            # Handle project_name - find project by name if provided
            project_id = None
            if project_name:
                logger.info(f"[add_task] Searching for project with name: {project_name}")
                # Search for project by name (case-insensitive)
                project = db.exec(
                    select(Project).where(
                        Project.agency_id == agency_id,
                        Project.name.ilike(f"%{project_name}%")
                    )
                ).first()

                if project:
                    project_id = project.id
                    logger.info(f"[add_task] Found project: {project.name} (ID: {project.id})")
                else:
                    logger.warning(f"[add_task] No project found matching: {project_name}, will create task without project")
                # else: Project not found - don't fail, just create without project

            # Handle assignee_name - find user by name if provided
            assignee_id = None
            if assignee_name:
                logger.info(f"[add_task] Searching for assignee with name: {assignee_name}")
                from app.models.user import User
                # Search for user by name (case-insensitive)
                user = db.exec(
                    select(User).where(
                        User.agency_id == agency_id,
                        User.name.ilike(f"%{assignee_name}%")
                    )
                ).first()

                if user:
                    assignee_id = user.id
                    logger.info(f"[add_task] Found assignee: {user.name} (ID: {user.id})")
                else:
                    logger.warning(f"[add_task] No user found matching: {assignee_name}, will create task without assignee")

            # Handle due_date - parse YYYY-MM-DD format
            parsed_due_date = None
            if due_date:
                try:
                    from datetime import datetime
                    parsed_due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
                    logger.info(f"[add_task] Parsed due_date: {parsed_due_date}")
                except ValueError as e:
                    logger.warning(f"[add_task] Failed to parse due_date '{due_date}': {e}")

            # Prepare task data
            task_data_dict = {
                "title": title,
                "description": description,
                "priority": priority_map.get(priority.lower() if priority else "medium", TaskPriority.MEDIUM),
                "status": status_map.get(status.lower() if status else "todo", TaskStatus.TODO),
            }

            # Only add project_id if we found one
            if project_id:
                task_data_dict["project_id"] = project_id

            # Only add assignee_id if we found one
            if assignee_id:
                task_data_dict["assignee_id"] = assignee_id

            # Only add due_date if we parsed it successfully
            if parsed_due_date:
                task_data_dict["due_date"] = parsed_due_date

            task_data = TaskCreate(**task_data_dict)

            # Create the task
            created_task = task_service.create_task(task_data, agency_id, db)
            logger.info(f"[add_task] Task created successfully: {created_task.id}")

            # Format response with complete details
            details = []
            if created_task.description:
                desc_preview = created_task.description[:50] + "..." if len(created_task.description) > 50 else created_task.description
                details.append(f"description: {desc_preview}")
            if created_task.project_id:
                # Get actual project name
                if project:
                    details.append(f"project: {project.name}")
                else:
                    details.append(f"project_id: {created_task.project_id}")
            else:
                details.append("project: none")
            if created_task.assignee_id:
                # Get actual assignee name
                if assignee_name:
                    details.append(f"assignee: {assignee_name}")
                else:
                    details.append(f"assignee_id: {created_task.assignee_id}")
            else:
                details.append("assignee: none")
            if created_task.priority:
                details.append(f"priority: {created_task.priority}")
            if created_task.status:
                details.append(f"status: {created_task.status}")
            if created_task.due_date:
                details.append(f"due_date: {created_task.due_date}")

            details_str = ", ".join(details) if details else "no additional details"
            return f"✓ Task '{title}' created successfully with ID: {created_task.id}\n  Details: {details_str}"

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error creating task: {str(e)}"


@function_tool
def list_tasks(
    ctx: RunContextWrapper,
    project_name: Optional[str] = None,
    assignee_name: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
) -> str:
    """List tasks in TeamFlow with optional filters.

    Args:
        ctx: Agent execution context (automatically injected)
        project_name: Filter by project name (partial match, optional)
        assignee_name: Filter by assignee name (partial match, optional)
        status: Filter by status (TODO, IN_PROGRESS, DOING, BLOCKED, REVIEW, DONE, ARCHIVED)
        limit: Maximum number of tasks to return (default: 50)

    Returns:
        List of tasks with their details

    Example:
        >>> list_tasks(project_name="justglow")  # List all tasks in justglow project
        >>> list_tasks(assignee_name="Owais")  # List all tasks assigned to Owais
        >>> list_tasks(status="TODO")  # List all TODO tasks
        >>> list_tasks()  # List all non-archived tasks
    """
    import logging
    logger = logging.getLogger(__name__)
    try:
        from app.services.task_service import TaskService
        from app.models.task import TaskStatus
        from app.db.session import engine
        from sqlmodel import Session, select
        from app.models.project import Project
        from app.models.user import User

        # Get agency_id from context
        context_obj = ctx.context
        if context_obj is None:
            return "Error: No context available. Please ensure you are logged in."

        # Handle AgentContext object from ChatKit
        if hasattr(context_obj, 'request_context'):
            context_dict = context_obj.request_context
        elif isinstance(context_obj, dict):
            context_dict = context_obj
        else:
            return "Error: Unexpected context type."

        agency_id_str = context_dict.get("agency_id") if context_dict else None
        if not agency_id_str:
            return "Error: Could not determine agency_id from request context. Please ensure you are logged in."

        agency_id = UUID(agency_id_str)

        # Map status string to enum
        status_map = {
            "todo": TaskStatus.TODO,
            "in_progress": TaskStatus.DOING,
            "doing": TaskStatus.DOING,
            "blocked": TaskStatus.REVIEW,
            "review": TaskStatus.REVIEW,
            "done": TaskStatus.DONE,
            "archived": TaskStatus.ARCHIVED,
        }

        # Parse status filter
        status_filter = None
        if status:
            status_lower = status.lower()
            status_filter = status_map.get(status_lower)
            if not status_filter:
                return f"Invalid status: {status}. Valid options: TODO, IN_PROGRESS, DOING, BLOCKED, REVIEW, DONE, ARCHIVED"

        with Session(engine) as db:
            task_service = TaskService()

            # Resolve project_id from project_name if provided
            project_id = None
            if project_name:
                project = db.exec(
                    select(Project).where(
                        Project.agency_id == agency_id,
                        Project.name.ilike(f"%{project_name}%")
                    )
                ).first()
                if project:
                    project_id = project.id
                    logger.info(f"[list_tasks] Found project: {project.name} (ID: {project.id})")
                else:
                    return f"No project found matching: {project_name}"

            # Resolve assignee_id from assignee_name if provided
            assignee_id = None
            if assignee_name:
                user = db.exec(
                    select(User).where(
                        User.agency_id == agency_id,
                        User.name.ilike(f"%{assignee_name}%")
                    )
                ).first()
                if user:
                    assignee_id = user.id
                    logger.info(f"[list_tasks] Found assignee: {user.name} (ID: {user.id})")
                else:
                    return f"No user found matching: {assignee_name}"

            # List tasks using TaskService
            include_archived = status_filter == TaskStatus.ARCHIVED
            tasks = task_service.list_tasks(
                agency_id=agency_id,
                session=db,
                status=status_filter,
                project_id=project_id,
                assignee_id=assignee_id,
                include_archived=include_archived,
            )

            # Apply limit
            tasks = tasks[:limit]

            if not tasks:
                filters = []
                if project_name:
                    filters.append(f"project={project_name}")
                if assignee_name:
                    filters.append(f"assignee={assignee_name}")
                if status:
                    filters.append(f"status={status}")
                filter_str = ", ".join(filters) if filters else "no filters"
                return f"Found 0 tasks with {filter_str}."

            # Format tasks for display
            formatted_tasks = []
            for task in tasks:
                task_info = [
                    f"ID: {task.id}",
                    f"Title: {task.title}",
                    f"Status: {task.status}",
                    f"Priority: {task.priority or 'Not set'}",
                ]

                if task.description:
                    desc_preview = task.description[:50] + "..." if len(task.description) > 50 else task.description
                    task_info.append(f"Description: {desc_preview}")

                if task.assignee:
                    task_info.append(f"Assignee: {task.assignee.name}")
                else:
                    task_info.append("Assignee: Unassigned")

                if task.project_id:
                    # Fetch project name
                    project = db.get(Project, task.project_id)
                    if project:
                        task_info.append(f"Project: {project.name}")

                if task.due_date:
                    task_info.append(f"Due: {task.due_date}")

                formatted_tasks.append(" | ".join(task_info))

            header = f"Found {len(tasks)} task(s):\n"
            return header + "\n".join(formatted_tasks)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error listing tasks: {str(e)}"


@function_tool
def assign_task(
    ctx: RunContextWrapper,
    task_id: str,
    assignee_name: Optional[str] = None,
) -> str:
    """Assign or reassign a task to a user.

    Args:
        ctx: Agent execution context (automatically injected)
        task_id: Task ID to reassign
        assignee_name: Name of the user to assign task to (if None, task will be unassigned)

    Returns:
        Confirmation message with new assignment

    Example:
        >>> assign_task(task_id="123e4567-e89b-12d3-a456-426614174000", assignee_name="Owais")
        Assigns task to Owais
    """
    import logging
    logger = logging.getLogger(__name__)
    try:
        from app.services.task_service import TaskService
        from app.db.session import engine
        from sqlmodel import Session, select
        from app.models.user import User

        # Get agency_id from context
        context_obj = ctx.context
        if context_obj is None:
            return "Error: No context available. Please ensure you are logged in."

        if hasattr(context_obj, 'request_context'):
            context_dict = context_obj.request_context
        elif isinstance(context_obj, dict):
            context_dict = context_obj
        else:
            return "Error: Unexpected context type."

        agency_id_str = context_dict.get("agency_id") if context_dict else None
        if not agency_id_str:
            return "Error: Could not determine agency_id from request context. Please ensure you are logged in."

        agency_id = UUID(agency_id_str)

        with Session(engine) as db:
            task_service = TaskService()

            # Resolve assignee_id from assignee_name
            assignee_id = None
            if assignee_name:
                user = db.exec(
                    select(User).where(
                        User.agency_id == agency_id,
                        User.name.ilike(f"%{assignee_name}%")
                    )
                ).first()
                if user:
                    assignee_id = user.id
                    logger.info(f"[assign_task] Found assignee: {user.name} (ID: {user.id})")
                else:
                    return f"No user found matching: {assignee_name}"

            # Assign task using TaskService
            task = task_service.assign_task(
                task_id=UUID(task_id),
                assignee_id=assignee_id,
                agency_id=agency_id,
                session=db,
            )

            if not task:
                return f"Task not found with ID: {task_id}"

            if assignee_id:
                return f"✓ Task '{task.title}' (ID: {task_id}) assigned to {assignee_name or 'user'}"
            else:
                return f"✓ Task '{task.title}' (ID: {task_id}) unassigned"

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error assigning task: {str(e)}"


@function_tool
def complete_task(
    ctx: RunContextWrapper,
    task_id: str,
) -> str:
    """Mark a task as complete (status = DONE).

    Args:
        ctx: Agent execution context (automatically injected)
        task_id: Task ID to complete

    Returns:
        Confirmation message

    Example:
        >>> complete_task(task_id="123e4567-e89b-12d3-a456-426614174000")
        Marks task as complete
    """
    import logging
    logger = logging.getLogger(__name__)
    try:
        from app.services.task_service import TaskService
        from app.models.task import TaskUpdate, TaskStatus
        from app.db.session import engine
        from sqlmodel import Session

        # Get agency_id from context
        context_obj = ctx.context
        if context_obj is None:
            return "Error: No context available. Please ensure you are logged in."

        if hasattr(context_obj, 'request_context'):
            context_dict = context_obj.request_context
        elif isinstance(context_obj, dict):
            context_dict = context_obj
        else:
            return "Error: Unexpected context type."

        agency_id_str = context_dict.get("agency_id") if context_dict else None
        if not agency_id_str:
            return "Error: Could not determine agency_id from request context. Please ensure you are logged in."

        agency_id = UUID(agency_id_str)

        with Session(engine) as db:
            task_service = TaskService()

            # Create update with status=DONE
            task_update = TaskUpdate(status=TaskStatus.DONE)

            # Update task using TaskService
            task = task_service.update_task(
                task_id=UUID(task_id),
                task_data=task_update,
                agency_id=agency_id,
                session=db,
            )

            if not task:
                return f"Task not found with ID: {task_id}"

            logger.info(f"[complete_task] Task marked as complete: {task_id}")
            return f"✓ Task '{task.title}' (ID: {task_id}) marked as complete"

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error completing task: {str(e)}"


@function_tool
def delete_task(
    ctx: RunContextWrapper,
    task_title: Optional[str] = None,
) -> str:
    """Delete a task permanently.

    WARNING: This is a destructive action that cannot be easily undone.
    Consider using archive_task if you want to hide the task but keep it for reference.

    Note: Tasks with time entries cannot be deleted due to data integrity. Use archive instead.

    Args:
        ctx: Agent execution context (automatically injected)
        task_title: Title of the task to delete (partial match). If not provided, agent will ask for clarification.

    Returns:
        Confirmation message or error with alternative suggestion

    Example:
        >>> delete_task(task_title="new render")
        Permanently deletes the task (or suggests archive if not possible)
    """
    import logging
    logger = logging.getLogger(__name__)
    try:
        from app.services.task_service import TaskService
        from app.db.session import engine
        from sqlmodel import Session, select
        from app.models.task import Task
        from sqlalchemy.exc import IntegrityError

        # Get agency_id from context
        context_obj = ctx.context
        if context_obj is None:
            return "Error: No context available. Please ensure you are logged in."

        if hasattr(context_obj, 'request_context'):
            context_dict = context_obj.request_context
        elif isinstance(context_obj, dict):
            context_dict = context_obj
        else:
            return "Error: Unexpected context type."

        agency_id_str = context_dict.get("agency_id") if context_dict else None
        if not agency_id_str:
            return "Error: Could not determine agency_id from request context. Please ensure you are logged in."

        agency_id = UUID(agency_id_str)

        # Require task_title for safety
        if not task_title:
            return "To delete a task, please specify the task title. For example: 'delete the task named new render'"

        with Session(engine) as db:
            task_service = TaskService()

            # Search for task by title (case-insensitive)
            task = db.exec(
                select(Task).where(
                    Task.agency_id == agency_id,
                    Task.title.ilike(f"%{task_title}%")
                )
            ).first()

            if not task:
                return f"No task found matching: {task_title}"

            # Try to delete the task using TaskService
            try:
                deleted = task_service.delete_task(
                    task_id=task.id,
                    agency_id=agency_id,
                    session=db,
                )

                if not deleted:
                    return f"Task not found with ID: {task.id}"

                logger.info(f"[delete_task] Task deleted: {task.id}")
                return f"✓ Task '{task.title}' (ID: {task.id}) has been permanently deleted"

            except IntegrityError as ie:
                # Foreign key constraint - task has time entries or other dependencies
                logger.warning(f"[delete_task] Cannot delete task '{task.title}' due to foreign key constraints: {ie}")
                return f"""⚠️ Cannot delete task '{task.title}' because it has associated data (time entries or other references).

Suggested alternatives:
1. Archive the task instead: 'archive task named {task_title}' (hides it from views but preserves history)
2. Complete the task: 'complete task named {task_title}' (marks as DONE)

Would you like me to archive it instead? Say 'yes' to archive '{task.title}'."""

    except IntegrityError as ie:
        import traceback
        traceback.print_exc()
        return f"Cannot delete task due to data integrity constraints: {str(ie)}\n\nSuggestion: Try archiving the task instead with 'archive task named {task_title}'"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error deleting task: {str(e)}"


@function_tool
def archive_task(
    ctx: RunContextWrapper,
    task_title: Optional[str] = None,
) -> str:
    """Archive a task by setting its status to ARCHIVED.

    Archiving hides the task from normal views but keeps it for historical reference.
    This is safer than deleting.

    Args:
        ctx: Agent execution context (automatically injected)
        task_title: Title of the task to archive (partial match). If not provided, agent will ask for clarification.

    Returns:
        Confirmation message

    Example:
        >>> archive_task(task_title="old campaign")
        Archives the task (sets status to ARCHIVED)
    """
    import logging
    logger = logging.getLogger(__name__)
    try:
        from app.services.task_service import TaskService
        from app.db.session import engine
        from sqlmodel import Session, select
        from app.models.task import Task

        # Get agency_id from context
        context_obj = ctx.context
        if context_obj is None:
            return "Error: No context available. Please ensure you are logged in."

        if hasattr(context_obj, 'request_context'):
            context_dict = context_obj.request_context
        elif isinstance(context_obj, dict):
            context_dict = context_obj
        else:
            return "Error: Unexpected context type."

        agency_id_str = context_dict.get("agency_id") if context_dict else None
        if not agency_id_str:
            return "Error: Could not determine agency_id from request context. Please ensure you are logged in."

        agency_id = UUID(agency_id_str)

        # Require task_title for safety
        if not task_title:
            return "To archive a task, please specify the task title. For example: 'archive the task named old campaign'"

        with Session(engine) as db:
            task_service = TaskService()

            # Search for task by title (case-insensitive)
            task = db.exec(
                select(Task).where(
                    Task.agency_id == agency_id,
                    Task.title.ilike(f"%{task_title}%")
                )
            ).first()

            if not task:
                return f"No task found matching: {task_title}"

            # Archive the task using TaskService
            archived_task = task_service.archive_task(
                task_id=task.id,
                agency_id=agency_id,
                session=db,
            )

            if not archived_task:
                return f"Task not found with ID: {task.id}"

            logger.info(f"[archive_task] Task archived: {task.id}")
            return f"✓ Task '{task.title}' (ID: {task.id}) has been archived (hidden from normal views)"

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error archiving task: {str(e)}"


@function_tool
def update_task_priority(
    ctx: RunContextWrapper,
    task_title: str,
    priority: str,
) -> str:
    """Update the priority of an existing task.

    Args:
        ctx: Agent execution context (automatically injected)
        task_title: Title of the task to update (partial match)
        priority: New priority level - LOW, MEDIUM, HIGH, or URGENT

    Returns:
        Confirmation message

    Example:
        >>> update_task_priority(task_title="fix navbar", priority="high")
        Updates task priority to HIGH
    """
    import logging
    logger = logging.getLogger(__name__)
    try:
        from app.services.task_service import TaskService
        from app.models.task import TaskUpdate, TaskPriority
        from app.db.session import engine
        from sqlmodel import Session, select
        from app.models.task import Task

        # Get agency_id from context
        context_obj = ctx.context
        if context_obj is None:
            return "Error: No context available. Please ensure you are logged in."

        if hasattr(context_obj, 'request_context'):
            context_dict = context_obj.request_context
        elif isinstance(context_obj, dict):
            context_dict = context_obj
        else:
            return "Error: Unexpected context type."

        agency_id_str = context_dict.get("agency_id") if context_dict else None
        if not agency_id_str:
            return "Error: Could not determine agency_id from request context. Please ensure you are logged in."

        agency_id = UUID(agency_id_str)

        # Map priority string to enum
        priority_map = {
            "low": TaskPriority.LOW,
            "medium": TaskPriority.MEDIUM,
            "high": TaskPriority.HIGH,
            "urgent": TaskPriority.HIGH,
        }

        priority_lower = priority.lower()
        mapped_priority = priority_map.get(priority_lower)
        if not mapped_priority:
            return f"Invalid priority: {priority}. Valid options: LOW, MEDIUM, HIGH, URGENT"

        with Session(engine) as db:
            task_service = TaskService()

            # Search for task by title (case-insensitive)
            task = db.exec(
                select(Task).where(
                    Task.agency_id == agency_id,
                    Task.title.ilike(f"%{task_title}%")
                )
            ).first()

            if not task:
                return f"No task found matching: {task_title}"

            # Create update with new priority
            task_update = TaskUpdate(priority=mapped_priority)

            # Update task using TaskService
            updated_task = task_service.update_task(
                task_id=task.id,
                task_data=task_update,
                agency_id=agency_id,
                session=db,
            )

            if not updated_task:
                return f"Task not found with ID: {task.id}"

            logger.info(f"[update_task_priority] Task priority updated: {task.id}")
            return f"✓ Task '{task.title}' (ID: {task.id}) priority updated to {priority.upper()}"

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error updating task priority: {str(e)}"


@function_tool
def update_task_due_date(
    ctx: RunContextWrapper,
    task_title: str,
    due_date: str,
) -> str:
    """Update the due date of an existing task.

    Args:
        ctx: Agent execution context (automatically injected)
        task_title: Title of the task to update (partial match)
        due_date: New due date in YYYY-MM-DD format (e.g., "2026-01-15")

    Returns:
        Confirmation message

    Example:
        >>> update_task_due_date(task_title="fix navbar", due_date="2026-01-15")
        Updates task due date to January 15, 2026
    """
    import logging
    logger = logging.getLogger(__name__)
    try:
        from app.services.task_service import TaskService
        from app.models.task import TaskUpdate
        from app.db.session import engine
        from sqlmodel import Session, select
        from app.models.task import Task

        # Get agency_id from context
        context_obj = ctx.context
        if context_obj is None:
            return "Error: No context available. Please ensure you are logged in."

        if hasattr(context_obj, 'request_context'):
            context_dict = context_obj.request_context
        elif isinstance(context_obj, dict):
            context_dict = context_obj
        else:
            return "Error: Unexpected context type."

        agency_id_str = context_dict.get("agency_id") if context_dict else None
        if not agency_id_str:
            return "Error: Could not determine agency_id from request context. Please ensure you are logged in."

        agency_id = UUID(agency_id_str)

        # Parse due_date
        try:
            from datetime import datetime
            parsed_due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
        except ValueError:
            return f"Invalid due date format: {due_date}. Please use YYYY-MM-DD format (e.g., '2026-01-15')"

        with Session(engine) as db:
            task_service = TaskService()

            # Search for task by title (case-insensitive)
            task = db.exec(
                select(Task).where(
                    Task.agency_id == agency_id,
                    Task.title.ilike(f"%{task_title}%")
                )
            ).first()

            if not task:
                return f"No task found matching: {task_title}"

            # Create update with new due_date
            task_update = TaskUpdate(due_date=parsed_due_date)

            # Update task using TaskService
            updated_task = task_service.update_task(
                task_id=task.id,
                task_data=task_update,
                agency_id=agency_id,
                session=db,
            )

            if not updated_task:
                return f"Task not found with ID: {task.id}"

            logger.info(f"[update_task_due_date] Task due date updated: {task.id}")
            return f"✓ Task '{task.title}' (ID: {task.id}) due date updated to {due_date}"

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error updating task due date: {str(e)}"


@function_tool
def update_task_status(
    ctx: RunContextWrapper,
    task_title: str,
    status: str,
) -> str:
    """Update the status of an existing task.

    Args:
        ctx: Agent execution context (automatically injected)
        task_title: Title of the task to update (partial match)
        status: New status - TODO, IN_PROGRESS, BLOCKED, REVIEW, or DONE

    Returns:
        Confirmation message

    Example:
        >>> update_task_status(task_title="fix navbar", status="in_progress")
        Updates task status to IN_PROGRESS (DOING)
    """
    import logging
    logger = logging.getLogger(__name__)
    try:
        from app.services.task_service import TaskService
        from app.models.task import TaskUpdate, TaskStatus
        from app.db.session import engine
        from sqlmodel import Session, select
        from app.models.task import Task

        # Get agency_id from context
        context_obj = ctx.context
        if context_obj is None:
            return "Error: No context available. Please ensure you are logged in."

        if hasattr(context_obj, 'request_context'):
            context_dict = context_obj.request_context
        elif isinstance(context_obj, dict):
            context_dict = context_obj
        else:
            return "Error: Unexpected context type."

        agency_id_str = context_dict.get("agency_id") if context_dict else None
        if not agency_id_str:
            return "Error: Could not determine agency_id from request context. Please ensure you are logged in."

        agency_id = UUID(agency_id_str)

        # Map status string to enum
        status_map = {
            "todo": TaskStatus.TODO,
            "in_progress": TaskStatus.DOING,
            "doing": TaskStatus.DOING,
            "blocked": TaskStatus.REVIEW,
            "review": TaskStatus.REVIEW,
            "done": TaskStatus.DONE,
        }

        status_lower = status.lower()
        mapped_status = status_map.get(status_lower)
        if not mapped_status:
            return f"Invalid status: {status}. Valid options: TODO, IN_PROGRESS, DOING, BLOCKED, REVIEW, DONE"

        with Session(engine) as db:
            task_service = TaskService()

            # Search for task by title (case-insensitive)
            task = db.exec(
                select(Task).where(
                    Task.agency_id == agency_id,
                    Task.title.ilike(f"%{task_title}%")
                )
            ).first()

            if not task:
                return f"No task found matching: {task_title}"

            # Create update with new status
            task_update = TaskUpdate(status=mapped_status)

            # Update task using TaskService
            updated_task = task_service.update_task(
                task_id=task.id,
                task_data=task_update,
                agency_id=agency_id,
                session=db,
            )

            if not updated_task:
                return f"Task not found with ID: {task.id}"

            logger.info(f"[update_task_status] Task status updated: {task.id}")
            return f"✓ Task '{task.title}' (ID: {task.id}) status updated to {status.upper()}"

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error updating task status: {str(e)}"


# Project Management Tools


@function_tool
def list_projects(
    ctx: RunContextWrapper,
    limit: int = 50,
) -> str:
    """List all projects for the user's agency.

    Args:
        ctx: Agent execution context (automatically injected)
        limit: Maximum number of projects to return (default: 50)

    Returns:
        List of projects with their details

    Example:
        >>> list_projects()
        Shows all projects in the agency
    """
    import logging
    logger = logging.getLogger(__name__)
    try:
        from app.services.project_service import ProjectService
        from app.db.session import engine
        from sqlmodel import Session

        # Get agency_id from context
        context_obj = ctx.context
        if context_obj is None:
            return "Error: No context available. Please ensure you are logged in."

        if hasattr(context_obj, 'request_context'):
            context_dict = context_obj.request_context
        elif isinstance(context_obj, dict):
            context_dict = context_obj
        else:
            return "Error: Unexpected context type."

        agency_id_str = context_dict.get("agency_id") if context_dict else None
        if not agency_id_str:
            return "Error: Could not determine agency_id from request context. Please ensure you are logged in."

        agency_id = UUID(agency_id_str)

        with Session(engine) as db:
            project_service = ProjectService()

            # List projects using ProjectService
            projects = project_service.list_projects(
                agency_id=agency_id,
                session=db,
            )

            # Apply limit
            projects = projects[:limit]

            if not projects:
                return "Found 0 projects. You can create a new project by saying 'Create a project named <name>'."

            # Format projects for display
            formatted_projects = []
            for project in projects:
                project_info = [
                    f"ID: {project.id}",
                    f"Name: {project.name}",
                ]

                if project.description:
                    desc_preview = project.description[:50] + "..." if len(project.description) > 50 else project.description
                    project_info.append(f"Description: {desc_preview}")

                if project.status:
                    project_info.append(f"Status: {project.status}")

                # Add task count if available
                from app.models.task import Task
                from sqlmodel import select, func
                task_count = db.exec(
                    select(func.count(Task.id)).where(Task.project_id == project.id)
                ).one()
                project_info.append(f"Tasks: {task_count}")

                formatted_projects.append(" | ".join(project_info))

            header = f"Found {len(projects)} project(s):\n"
            return header + "\n".join(formatted_projects)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error listing projects: {str(e)}"


@function_tool
def create_project(
    ctx: RunContextWrapper,
    name: str,
    client_name: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
) -> str:
    """Create a new project in TeamFlow.

    Args:
        ctx: Agent execution context (automatically injected)
        name: Project name (required)
        client_name: Name of the client for this project (optional)
        description: Project description (optional)
        status: Project status (e.g., LEAD, ACTIVE, ON_HOLD, COMPLETED) (optional)

    Returns:
        Confirmation message with project details

    Example:
        >>> create_project(name="Acme Website", client_name="Acme Corp", description="E-commerce website")
        Creates a new project
    """
    import logging
    logger = logging.getLogger(__name__)
    try:
        from app.services.project_service import ProjectService
        from app.models.project import ProjectCreate, ProjectStatus
        from app.db.session import engine
        from sqlmodel import Session

        # Get agency_id from context
        context_obj = ctx.context
        if context_obj is None:
            return "Error: No context available. Please ensure you are logged in."

        if hasattr(context_obj, 'request_context'):
            context_dict = context_obj.request_context
        elif isinstance(context_obj, dict):
            context_dict = context_obj
        else:
            return "Error: Unexpected context type."

        agency_id_str = context_dict.get("agency_id") if context_dict else None
        if not agency_id_str:
            return "Error: Could not determine agency_id from request context. Please ensure you are logged in."

        agency_id = UUID(agency_id_str)
        logger.info(f"[create_project] Using agency_id: {agency_id}")

        # Map status string to enum
        status_map = {
            "lead": ProjectStatus.LEAD,
            "active": ProjectStatus.ACTIVE,
            "on_hold": ProjectStatus.ON_HOLD,
            "completed": ProjectStatus.COMPLETED,
            "archived": ProjectStatus.ARCHIVED,
        }

        # Prepare project data
        project_data_dict = {"name": name}

        if client_name:
            project_data_dict["client_name"] = client_name
        if description:
            project_data_dict["description"] = description
        if status:
            status_lower = status.lower()
            mapped_status = status_map.get(status_lower)
            if mapped_status:
                project_data_dict["status"] = mapped_status

        project_data = ProjectCreate(**project_data_dict)

        with Session(engine) as db:
            project_service = ProjectService()

            # Create the project
            created_project = project_service.create_project(
                project_data=project_data,
                agency_id=agency_id,
                session=db,
            )
            logger.info(f"[create_project] Project created successfully: {created_project.id}")

            # Format response with complete details
            details = [f"ID: {created_project.id}"]
            if created_project.description:
                desc_preview = created_project.description[:50] + "..." if len(created_project.description) > 50 else created_project.description
                details.append(f"description: {desc_preview}")
            else:
                details.append("description: none")
            if created_project.client_name:
                details.append(f"client: {created_project.client_name}")
            else:
                details.append("client: none")
            if created_project.status:
                details.append(f"status: {created_project.status}")

            details_str = ", ".join(details)
            return f"✓ Project '{name}' created successfully with {details_str}"

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error creating project: {str(e)}"


@function_tool
def get_project_details(
    ctx: RunContextWrapper,
    project_name: str,
) -> str:
    """Get detailed information about a specific project.

    Args:
        ctx: Agent execution context (automatically injected)
        project_name: Name of the project to look up (partial match)

    Returns:
        Project details including task count, status, and other information

    Example:
        >>> get_project_details(project_name="Acme")
        Shows details for Acme project
    """
    import logging
    logger = logging.getLogger(__name__)
    try:
        from app.db.session import engine
        from sqlmodel import Session, select
        from app.models.project import Project
        from app.models.task import Task
        from sqlmodel import func

        # Get agency_id from context
        context_obj = ctx.context
        if context_obj is None:
            return "Error: No context available. Please ensure you are logged in."

        if hasattr(context_obj, 'request_context'):
            context_dict = context_obj.request_context
        elif isinstance(context_obj, dict):
            context_dict = context_obj
        else:
            return "Error: Unexpected context type."

        agency_id_str = context_dict.get("agency_id") if context_dict else None
        if not agency_id_str:
            return "Error: Could not determine agency_id from request context. Please ensure you are logged in."

        agency_id = UUID(agency_id_str)

        with Session(engine) as db:
            # Search for project by name (case-insensitive)
            project = db.exec(
                select(Project).where(
                    Project.agency_id == agency_id,
                    Project.name.ilike(f"%{project_name}%")
                )
            ).first()

            if not project:
                return f"No project found matching: {project_name}"

            # Gather project details
            details = [
                f"ID: {project.id}",
                f"Name: {project.name}",
                f"Status: {project.status}",
            ]

            if project.description:
                details.append(f"Description: {project.description}")
            if project.client_name:
                details.append(f"Client: {project.client_name}")
            if project.start_date:
                details.append(f"Start Date: {project.start_date}")
            if project.end_date:
                details.append(f"End Date: {project.end_date}")

            # Get task statistics
            total_tasks = db.exec(
                select(func.count(Task.id)).where(Task.project_id == project.id)
            ).one()

            tasks_by_status = db.exec(
                select(Task.status, func.count(Task.id))
                .where(Task.project_id == project.id)
                .group_by(Task.status)
            ).all()

            details.append(f"Total Tasks: {total_tasks}")

            task_status_str = ", ".join([f"{status}: {count}" for status, count in tasks_by_status])
            if task_status_str:
                details.append(f"Tasks by Status: {task_status_str}")

            return "\n".join(details)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error getting project details: {str(e)}"


# Analytics Tools


@function_tool
def get_profitability(
    ctx: RunContextWrapper,
    project_name: str,
) -> str:
    """Get profitability analysis for a project.

    Calculates profitability based on:
    - Revenue: Time entries × project hourly rate
    - Cost: Time entries × user hourly rates (if available) or agency average
    - Profit: Revenue - Cost
    - Margin: (Profit / Revenue) × 100%

    Args:
        ctx: Agent execution context (automatically injected)
        project_name: Name of the project to analyze (partial match)

    Returns:
        Profitability metrics including revenue, cost, profit, and margin

    Example:
        >>> get_profitability(project_name="Acme")
        Shows profitability for Acme project
    """
    import logging
    logger = logging.getLogger(__name__)
    try:
        from app.db.session import engine
        from sqlmodel import Session, select
        from app.models.project import Project
        from app.models.task import Task
        from app.models.time_entry import TimeEntry
        from app.models.user import User
        from sqlmodel import func as sql_func
        from decimal import Decimal

        # Get agency_id from context
        context_obj = ctx.context
        if context_obj is None:
            return "Error: No context available. Please ensure you are logged in."

        if hasattr(context_obj, 'request_context'):
            context_dict = context_obj.request_context
        elif isinstance(context_obj, dict):
            context_dict = context_obj
        else:
            return "Error: Unexpected context type."

        agency_id_str = context_dict.get("agency_id") if context_dict else None
        if not agency_id_str:
            return "Error: Could not determine agency_id from request context. Please ensure you are logged in."

        agency_id = UUID(agency_id_str)

        with Session(engine) as db:
            # Find project by name
            project = db.exec(
                select(Project).where(
                    Project.agency_id == agency_id,
                    Project.name.ilike(f"%{project_name}%")
                )
            ).first()

            if not project:
                return f"No project found matching: {project_name}"

            # Get all tasks for this project
            project_tasks = db.exec(
                select(Task.id).where(Task.project_id == project.id)
            ).all()

            if not project_tasks:
                return f"Project '{project.name}' has no tasks yet. No profitability data available."

            task_ids = [t[0] for t in project_tasks]

            # Get all time entries for these tasks
            time_entries = db.exec(
                select(TimeEntry).where(TimeEntry.task_id.in_(task_ids))
            ).all()

            if not time_entries:
                return f"Project '{project.name}' has {len(project_tasks)} tasks but no time entries yet. No profitability data available."

            # Calculate total hours logged
            total_minutes = sum(te.duration_minutes for te in time_entries)
            total_hours = total_minutes / 60

            # Calculate revenue (hours × project hourly rate)
            project_hourly_rate = project.hourly_rate or 50  # Default $50/hr
            revenue = total_hours * project_hourly_rate

            # For cost, we'd need user hourly rates. Since that's not in the User model,
            # we'll estimate cost as 60% of revenue (typical agency markup)
            # This can be refined when user hourly rates are added to the schema
            estimated_cost_percent = 0.6
            cost = revenue * estimated_cost_percent

            # Calculate profit and margin
            profit = revenue - cost
            margin = (profit / revenue * 100) if revenue > 0 else 0

            # Format the response
            return f"""Profitability Analysis for '{project.name}':

Time Tracking:
- Total Tasks: {len(project_tasks)}
- Total Hours Logged: {total_hours:.1f} hours
- Time Entries: {len(time_entries)}

Financials:
- Hourly Rate: ${project_hourly_rate}/hr
- Revenue: ${revenue:,.2f}
- Estimated Cost: ${cost:,.2f} (based on {estimated_cost_percent*100:.0f}% of revenue)
- Profit: ${profit:,.2f}
- Profit Margin: {margin:.1f}%

Note: Cost calculation uses estimated agency rates. Add user-specific hourly rates for accurate cost tracking."""

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error calculating profitability: {str(e)}"


@function_tool
def workload_summary(
    ctx: RunContextWrapper,
) -> str:
    """Get workload summary for the agency.

    Shows team member utilization based on active task assignments.
    Identifies who is over capacity and who has availability.

    Args:
        ctx: Agent execution context (automatically injected)

    Returns:
        Workload summary showing team member utilization

    Example:
        >>> workload_summary()
        Shows all team members and their task counts
    """
    import logging
    logger = logging.getLogger(__name__)
    try:
        from app.db.session import engine
        from sqlmodel import Session, select
        from app.models.user import User
        from app.models.task import Task
        from sqlmodel import func as sql_func

        # Get agency_id from context
        context_obj = ctx.context
        if context_obj is None:
            return "Error: No context available. Please ensure you are logged in."

        if hasattr(context_obj, 'request_context'):
            context_dict = context_obj.request_context
        elif isinstance(context_obj, dict):
            context_dict = context_obj
        else:
            return "Error: Unexpected context type."

        agency_id_str = context_dict.get("agency_id") if context_dict else None
        if not agency_id_str:
            return "Error: Could not determine agency_id from request context. Please ensure you are logged in."

        agency_id = UUID(agency_id_str)

        with Session(engine) as db:
            # Get all users in the agency
            users = db.exec(
                select(User).where(User.agency_id == agency_id)
            ).all()

            if not users:
                return "No team members found in this agency."

            # Calculate workload for each user
            workload_data = []
            total_active_tasks = 0
            over_capacity_members = []

            for user in users:
                # Count active tasks (TODO, DOING, REVIEW)
                active_tasks = db.exec(
                    select(sql_func.count(Task.id)).where(
                        Task.assignee_id == user.id,
                        Task.status.in_(["TODO", "DOING", "REVIEW"])
                    )
                ).one()

                total_active_tasks += active_tasks

                # Define capacity (typically 3-5 active tasks is healthy)
                capacity_threshold = 5
                utilization_status = "OK"
                if active_tasks > capacity_threshold:
                    utilization_status = "OVER CAPACITY"
                    over_capacity_members.append(user.name)
                elif active_tasks == 0:
                    utilization_status = "AVAILABLE"

                workload_data.append({
                    "name": user.name,
                    "active_tasks": active_tasks,
                    "status": utilization_status,
                })

            # Build summary
            summary_lines = [
                f"Workload Summary for Agency:",
                f"",
                f"Team Size: {len(users)} members",
                f"Total Active Tasks: {total_active_tasks}",
                f"Average Tasks per Member: {total_active_tasks / len(users):.1f}",
                f"",
                f"Team Member Workload:",
                f"{'-' * 60}",
            ]

            # Sort by task count (descending)
            workload_data.sort(key=lambda x: x["active_tasks"], reverse=True)

            for data in workload_data:
                status_indicator = ""
                if data["status"] == "OVER CAPACITY":
                    status_indicator = " ⚠️ OVER CAPACITY"
                elif data["status"] == "AVAILABLE":
                    status_indicator = " ✅ AVAILABLE"

                summary_lines.append(
                    f"• {data['name']}: {data['active_tasks']} active task(s){status_indicator}"
                )

            # Add over capacity alert if any
            if over_capacity_members:
                summary_lines.extend([
                    f"",
                    f"⚠️ Over Capacity: {', '.join(over_capacity_members)}",
                    f"   Consider reassigning tasks or redistributing workload."
                ])

            return "\n".join(summary_lines)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error calculating workload summary: {str(e)}"


# AI Recommendation Tools


@function_tool
def suggest_assignee(
    ctx: RunContextWrapper,
    task_title: Optional[str] = None,
) -> str:
    """Suggest the best assignee for a task using AI reasoning.

    Analyzes team member current workload, role, and availability to recommend
    the most suitable person for a task.

    The recommendation engine considers:
- **Workload Score**: Users with fewer active tasks are preferred
- **Role Preference**: Members are preferred over Admins/Viewers for task execution
- **Availability**: Users with 0 active tasks are highly available

    Args:
        ctx: Agent execution context (automatically injected)
        task_title: Optional task title for context (helps with keyword matching if skills were available)

    Returns:
        Recommended assignee with reasoning (workload score, availability, alternatives)

    Example:
        >>> suggest_assignee(task_title="Fix navbar bug")
        Suggests the best person based on workload and availability
    """
    import logging
    logger = logging.getLogger(__name__)
    try:
        from app.db.session import engine
        from sqlmodel import Session, select
        from app.models.user import User, UserRole
        from app.models.task import Task
        from sqlmodel import func as sql_func

        # Get agency_id from context
        context_obj = ctx.context
        if context_obj is None:
            return "Error: No context available. Please ensure you are logged in."

        if hasattr(context_obj, 'request_context'):
            context_dict = context_obj.request_context
        elif isinstance(context_obj, dict):
            context_dict = context_obj
        else:
            return "Error: Unexpected context type."

        agency_id_str = context_dict.get("agency_id") if context_dict else None
        if not agency_id_str:
            return "Error: Could not determine agency_id from request context. Please ensure you are logged in."

        agency_id = UUID(agency_id_str)

        with Session(engine) as db:
            # Get all members (exclude admins and viewers for task assignments)
            users = db.exec(
                select(User).where(
                    User.agency_id == agency_id,
                    User.role.in_([UserRole.member, UserRole.manager])
                )
            ).all()

            if not users:
                return "No team members available for task assignment in this agency."

            # Calculate workload and availability score for each user
            user_scores = []
            for user in users:
                # Count active tasks (TODO, DOING, REVIEW)
                active_tasks = db.exec(
                    select(sql_func.count(Task.id)).where(
                        Task.assignee_id == user.id,
                        Task.status.in_(["TODO", "DOING", "REVIEW"])
                    )
                ).one()

                # Calculate availability score (lower active tasks = higher score)
                # Score = 100 - (active_tasks × 20), minimum 0
                availability_score = max(0, 100 - (active_tasks * 20))

                # Role preference score (managers slightly preferred for complex tasks)
                role_score = 10 if user.role == UserRole.manager else 5

                # Total score
                total_score = availability_score + role_score

                user_scores.append({
                    "user": user,
                    "active_tasks": active_tasks,
                    "availability_score": availability_score,
                    "role_score": role_score,
                    "total_score": total_score,
                })

            # Sort by total score (descending)
            user_scores.sort(key=lambda x: x["total_score"], reverse=True)

            # Get top recommendation and alternatives
            if not user_scores:
                return "No suitable assignees found."

            top_choice = user_scores[0]
            alternatives = user_scores[1:4]  # Top 3 alternatives

            # Build recommendation response
            response_lines = [
                f"💡 Recommended Assignee: {top_choice['user'].name}",
                f"",
                f"Reasoning:",
                f"• Current Workload: {top_choice['active_tasks']} active task(s)",
                f"• Availability Score: {top_choice['availability_score']}/100",
            ]

            if top_choice['active_tasks'] == 0:
                response_lines.append("• Status: ✅ Fully Available - no active tasks")
            elif top_choice['active_tasks'] <= 3:
                response_lines.append("• Status: ✅ Good Availability - light workload")
            elif top_choice['active_tasks'] <= 5:
                response_lines.append("• Status: ⚠️ Moderate Availability - moderate workload")
            else:
                response_lines.append("• Status: ⚠️ Limited Availability - heavy workload")

            # Add role context
            response_lines.append(f"• Role: {top_choice['user'].role.value}")

            # Add alternatives if available
            if alternatives:
                response_lines.extend([
                    f"",
                    f"Alternative Options:",
                ])
                for i, alt in enumerate(alternatives, 1):
                    status = "✅ Available" if alt['active_tasks'] == 0 else f"{alt['active_tasks']} tasks"
                    response_lines.append(
                        f"  {i}. {alt['user'].name} ({status}) - Score: {alt['total_score']}"
                    )

            return "\n".join(response_lines)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error suggesting assignee: {str(e)}"


# Time Entry Tools


@function_tool
def add_time_entry(
    ctx: RunContextWrapper,
    task_title: str,
    duration_minutes: int,
    note: Optional[str] = None,
    entry_date: Optional[str] = None,
) -> str:
    """Log time worked on a task.

    Args:
        ctx: Agent execution context (automatically injected)
        task_title: Title of the task to log time against (partial match)
        duration_minutes: Duration in minutes (e.g., 60 for 1 hour, 30 for 30 minutes)
        note: Optional notes about the work done
        entry_date: Optional date in YYYY-MM-DD format (defaults to today)

    Returns:
        Confirmation message with time entry details

    Example:
        >>> add_time_entry(task_title="fix navbar", duration_minutes=60, note="Fixed responsive issue")
        Logs 1 hour to the task
    """
    import logging
    logger = logging.getLogger(__name__)
    try:
        from app.services.time_entry_service import TimeEntryService
        from app.models.time_entry import TimeEntryCreate
        from app.db.session import engine
        from sqlmodel import Session, select
        from app.models.task import Task
        from datetime import date

        # Get agency_id from context
        context_obj = ctx.context
        if context_obj is None:
            return "Error: No context available. Please ensure you are logged in."

        if hasattr(context_obj, 'request_context'):
            context_dict = context_obj.request_context
        elif isinstance(context_obj, dict):
            context_dict = context_obj
        else:
            return "Error: Unexpected context type."

        agency_id_str = context_dict.get("agency_id") if context_dict else None
        if not agency_id_str:
            return "Error: Could not determine agency_id from request context. Please ensure you are logged in."

        # Get user_id from context
        user_id_str = context_dict.get("user_id") if context_dict else None
        if not user_id_str:
            return "Error: Could not determine user_id from request context. Please ensure you are logged in."

        agency_id = UUID(agency_id_str)
        user_id = UUID(user_id_str)

        with Session(engine) as db:
            # Search for task by title (case-insensitive)
            task = db.exec(
                select(Task).where(
                    Task.agency_id == agency_id,
                    Task.title.ilike(f"%{task_title}%")
                )
            ).first()

            if not task:
                return f"No task found matching: {task_title}"

            # Parse entry_date if provided
            parsed_date = None
            if entry_date:
                try:
                    parsed_date = date.fromisoformat(entry_date)
                except ValueError:
                    return f"Invalid date format: {entry_date}. Use YYYY-MM-DD format (e.g., 2026-01-10)"

            # Create time entry data
            entry_data = TimeEntryCreate(
                task_id=task.id,
                duration_minutes=duration_minutes,
                note=note,
                entry_date=parsed_date,
            )

            # Create time entry using TimeEntryService
            time_entry_service = TimeEntryService()
            created_entry = time_entry_service.create_time_entry(
                entry_data=entry_data,
                user_id=user_id,
                agency_id=agency_id,
                session=db,
            )

            logger.info(f"[add_time_entry] Time entry created: {created_entry.id}")

            # Format duration for display
            hours = duration_minutes // 60
            minutes = duration_minutes % 60
            duration_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

            details = [f"✓ Logged {duration_str} to task '{task.title}'"]
            if note:
                details.append(f"  Note: {note}")
            if parsed_date:
                details.append(f"  Date: {parsed_date}")
            else:
                details.append(f"  Date: today")

            return "\n".join(details)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error adding time entry: {str(e)}"


@function_tool
def list_time_entries(
    ctx: RunContextWrapper,
    task_title: Optional[str] = None,
    user_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 50,
) -> str:
    """List time entries with optional filters.

    Args:
        ctx: Agent execution context (automatically injected)
        task_title: Optional filter by task title (partial match)
        user_name: Optional filter by user name (partial match)
        start_date: Optional filter by start date (YYYY-MM-DD format)
        end_date: Optional filter by end date (YYYY-MM-DD format)
        limit: Maximum number of entries to return (default: 50)

    Returns:
        List of time entries matching the filters

    Example:
        >>> list_time_entries(task_title="fix navbar")
        Shows all time entries for the fix navbar task
    """
    import logging
    logger = logging.getLogger(__name__)
    try:
        from app.services.time_entry_service import TimeEntryService
        from app.db.session import engine
        from sqlmodel import Session, select
        from app.models.time_entry import TimeEntry
        from app.models.task import Task
        from app.models.user import User
        from datetime import date

        # Get agency_id from context
        context_obj = ctx.context
        if context_obj is None:
            return "Error: No context available. Please ensure you are logged in."

        if hasattr(context_obj, 'request_context'):
            context_dict = context_obj.request_context
        elif isinstance(context_obj, dict):
            context_dict = context_obj
        else:
            return "Error: Unexpected context type."

        agency_id_str = context_dict.get("agency_id") if context_dict else None
        if not agency_id_str:
            return "Error: Could not determine agency_id from request context. Please ensure you are logged in."

        agency_id = UUID(agency_id_str)

        with Session(engine) as db:
            time_entry_service = TimeEntryService()

            # Parse filters
            task_id = None
            if task_title:
                task = db.exec(
                    select(Task).where(
                        Task.agency_id == agency_id,
                        Task.title.ilike(f"%{task_title}%")
                    )
                ).first()
                if not task:
                    return f"No task found matching: {task_title}"
                task_id = task.id

            user_id = None
            if user_name:
                user = db.exec(
                    select(User).where(
                        User.agency_id == agency_id,
                        User.name.ilike(f"%{user_name}%")
                    )
                ).first()
                if not user:
                    return f"No user found matching: {user_name}"
                user_id = user.id

            # Parse date filters
            parsed_start_date = None
            parsed_end_date = None
            if start_date:
                try:
                    parsed_start_date = date.fromisoformat(start_date)
                except ValueError:
                    return f"Invalid start_date format: {start_date}. Use YYYY-MM-DD format."
            if end_date:
                try:
                    parsed_end_date = date.fromisoformat(end_date)
                except ValueError:
                    return f"Invalid end_date format: {end_date}. Use YYYY-MM-DD format."

            # List time entries using TimeEntryService
            entries = time_entry_service.list_time_entries(
                agency_id=agency_id,
                session=db,
                task_id=task_id,
                user_id=user_id,
                start_date=parsed_start_date,
                end_date=parsed_end_date,
            )

            # Apply limit
            entries = entries[:limit]

            if not entries:
                return "No time entries found matching the specified filters."

            # Format entries for display
            formatted_entries = []
            for entry in entries:
                # Get task title
                task = db.get(Task, entry.task_id)
                task_title_str = task.title if task else "Unknown Task"

                # Get user name
                user = db.get(User, entry.user_id)
                user_name_str = user.name if user else "Unknown User"

                # Format duration
                hours = entry.duration_minutes // 60
                minutes = entry.duration_minutes % 60
                duration_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

                entry_parts = [
                    f"Task: {task_title_str}",
                    f"User: {user_name_str}",
                    f"Duration: {duration_str}",
                ]

                if entry.entry_date:
                    entry_parts.append(f"Date: {entry.entry_date}")
                if entry.note:
                    entry_parts.append(f"Note: {entry.note}")

                formatted_entries.append(" | ".join(entry_parts))

            header = f"Found {len(entries)} time entry(s):\n"
            return header + "\n".join(formatted_entries)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error listing time entries: {str(e)}"


@function_tool
def get_time_for_task(
    ctx: RunContextWrapper,
    task_title: str,
) -> str:
    """Get total time logged for a specific task.

    Args:
        ctx: Agent execution context (automatically injected)
        task_title: Title of the task (partial match)

    Returns:
        Total time logged with breakdown

    Example:
        >>> get_time_for_task(task_title="fix navbar")
        Shows total hours and entries for the task
    """
    import logging
    logger = logging.getLogger(__name__)
    try:
        from app.services.time_entry_service import TimeEntryService
        from app.db.session import engine
        from sqlmodel import Session, select
        from app.models.task import Task
        from app.models.time_entry import TimeEntry

        # Get agency_id from context
        context_obj = ctx.context
        if context_obj is None:
            return "Error: No context available. Please ensure you are logged in."

        if hasattr(context_obj, 'request_context'):
            context_dict = context_obj.request_context
        elif isinstance(context_obj, dict):
            context_dict = context_obj
        else:
            return "Error: Unexpected context type."

        agency_id_str = context_dict.get("agency_id") if context_dict else None
        if not agency_id_str:
            return "Error: Could not determine agency_id from request context. Please ensure you are logged in."

        agency_id = UUID(agency_id_str)

        with Session(engine) as db:
            # Search for task by title (case-insensitive)
            task = db.exec(
                select(Task).where(
                    Task.agency_id == agency_id,
                    Task.title.ilike(f"%{task_title}%")
                )
            ).first()

            if not task:
                return f"No task found matching: {task_title}"

            # Get total time using TimeEntryService
            time_entry_service = TimeEntryService()
            total_minutes = time_entry_service.get_total_time_for_task(
                task_id=task.id,
                agency_id=agency_id,
                session=db,
            )

            # Get individual entries for breakdown
            entries = db.exec(
                select(TimeEntry).where(
                    TimeEntry.task_id == task.id,
                    TimeEntry.agency_id == agency_id,
                )
            ).all()

            # Format total time
            total_hours = total_minutes / 60
            hours_int = int(total_hours)
            minutes_int = int(total_minutes % 60)
            total_str = f"{hours_int}h {minutes_int}m" if hours_int > 0 else f"{minutes_int}m"

            response_lines = [
                f"Time logged for task '{task.title}':",
                f"Total: {total_str} ({total_hours:.2f} hours)",
                f"Entries: {len(entries)}",
            ]

            if entries:
                response_lines.append("\nBreakdown:")
                for entry in entries:
                    hours = entry.duration_minutes // 60
                    minutes = entry.duration_minutes % 60
                    duration_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

                    entry_str = f"  • {duration_str}"
                    if entry.entry_date:
                        entry_str += f" on {entry.entry_date}"
                    if entry.note:
                        entry_str += f" - {entry.note}"

                    response_lines.append(entry_str)

            return "\n".join(response_lines)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error getting time for task: {str(e)}"


@function_tool
def update_time_entry(
    ctx: RunContextWrapper,
    task_title: str,
    entry_date: str,
    new_duration: Optional[int] = None,
    new_note: Optional[str] = None,
) -> str:
    """Update an existing time entry.

    Args:
        ctx: Agent execution context (automatically injected)
        task_title: Title of the task (to find the entry)
        entry_date: Date of the entry to update (YYYY-MM-DD format)
        new_duration: New duration in minutes (optional)
        new_note: New note text (optional)

    Returns:
        Confirmation message

    Example:
        >>> update_time_entry(task_title="fix navbar", entry_date="2026-01-10", new_duration=120)
        Updates the time entry to 2 hours
    """
    import logging
    logger = logging.getLogger(__name__)
    try:
        from app.services.time_entry_service import TimeEntryService
        from app.models.time_entry import TimeEntryUpdate
        from app.db.session import engine
        from sqlmodel import Session, select
        from app.models.task import Task
        from app.models.time_entry import TimeEntry
        from datetime import date

        # Get agency_id from context
        context_obj = ctx.context
        if context_obj is None:
            return "Error: No context available. Please ensure you are logged in."

        if hasattr(context_obj, 'request_context'):
            context_dict = context_obj.request_context
        elif isinstance(context_obj, dict):
            context_dict = context_obj
        else:
            return "Error: Unexpected context type."

        agency_id_str = context_dict.get("agency_id") if context_dict else None
        if not agency_id_str:
            return "Error: Could not determine agency_id from request context. Please ensure you are logged in."

        agency_id = UUID(agency_id_str)

        # Parse entry date
        try:
            parsed_date = date.fromisoformat(entry_date)
        except ValueError:
            return f"Invalid date format: {entry_date}. Use YYYY-MM-DD format (e.g., 2026-01-10)"

        with Session(engine) as db:
            # Find task by title
            task = db.exec(
                select(Task).where(
                    Task.agency_id == agency_id,
                    Task.title.ilike(f"%{task_title}%")
                )
            ).first()

            if not task:
                return f"No task found matching: {task_title}"

            # Find time entry by task and date
            entry = db.exec(
                select(TimeEntry).where(
                    TimeEntry.task_id == task.id,
                    TimeEntry.agency_id == agency_id,
                    TimeEntry.entry_date == parsed_date,
                )
            ).first()

            if not entry:
                return f"No time entry found for task '{task.title}' on {entry_date}"

            # Build update data
            update_data = {}
            if new_duration is not None:
                update_data["duration_minutes"] = new_duration
            if new_note is not None:
                update_data["note"] = new_note

            if not update_data:
                return "No updates provided. Please specify new_duration or new_note."

            entry_update = TimeEntryUpdate(**update_data)

            # Update using TimeEntryService
            time_entry_service = TimeEntryService()
            updated_entry = time_entry_service.update_time_entry(
                entry_id=entry.id,
                entry_data=entry_update,
                agency_id=agency_id,
                session=db,
            )

            if not updated_entry:
                return f"Failed to update time entry with ID: {entry.id}"

            logger.info(f"[update_time_entry] Time entry updated: {entry.id}")

            # Format response
            response_parts = [f"✓ Time entry updated for task '{task.title}' on {entry_date}"]
            if new_duration:
                hours = new_duration // 60
                minutes = new_duration % 60
                duration_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                response_parts.append(f"  New duration: {duration_str}")
            if new_note is not None:
                response_parts.append(f"  New note: {new_note}")

            return "\n".join(response_parts)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error updating time entry: {str(e)}"


@function_tool
def delete_time_entry(
    ctx: RunContextWrapper,
    task_title: str,
    entry_date: str,
) -> str:
    """Delete a time entry permanently.

    Args:
        ctx: Agent execution context (automatically injected)
        task_title: Title of the task (to find the entry)
        entry_date: Date of the entry to delete (YYYY-MM-DD format)

    Returns:
        Confirmation message

    Example:
        >>> delete_time_entry(task_title="fix navbar", entry_date="2026-01-10")
        Deletes the time entry for that date
    """
    import logging
    logger = logging.getLogger(__name__)
    try:
        from app.services.time_entry_service import TimeEntryService
        from app.db.session import engine
        from sqlmodel import Session, select
        from app.models.task import Task
        from app.models.time_entry import TimeEntry
        from datetime import date

        # Get agency_id from context
        context_obj = ctx.context
        if context_obj is None:
            return "Error: No context available. Please ensure you are logged in."

        if hasattr(context_obj, 'request_context'):
            context_dict = context_obj.request_context
        elif isinstance(context_obj, dict):
            context_dict = context_obj
        else:
            return "Error: Unexpected context type."

        agency_id_str = context_dict.get("agency_id") if context_dict else None
        if not agency_id_str:
            return "Error: Could not determine agency_id from request context. Please ensure you are logged in."

        agency_id = UUID(agency_id_str)

        # Parse entry date
        try:
            parsed_date = date.fromisoformat(entry_date)
        except ValueError:
            return f"Invalid date format: {entry_date}. Use YYYY-MM-DD format (e.g., 2026-01-10)"

        with Session(engine) as db:
            # Find task by title
            task = db.exec(
                select(Task).where(
                    Task.agency_id == agency_id,
                    Task.title.ilike(f"%{task_title}%")
                )
            ).first()

            if not task:
                return f"No task found matching: {task_title}"

            # Find time entry by task and date
            entry = db.exec(
                select(TimeEntry).where(
                    TimeEntry.task_id == task.id,
                    TimeEntry.agency_id == agency_id,
                    TimeEntry.entry_date == parsed_date,
                )
            ).first()

            if not entry:
                return f"No time entry found for task '{task.title}' on {entry_date}"

            # Delete using TimeEntryService
            time_entry_service = TimeEntryService()
            deleted = time_entry_service.delete_time_entry(
                entry_id=entry.id,
                agency_id=agency_id,
                session=db,
            )

            if not deleted:
                return f"Failed to delete time entry with ID: {entry.id}"

            logger.info(f"[delete_time_entry] Time entry deleted: {entry.id}")

            return f"✓ Time entry deleted for task '{task.title}' on {entry_date}"

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error deleting time entry: {str(e)}"


# Export all tools for use with Agent
TEAMFLOW_TOOLS = [
    # RAG / Knowledge Base
    search_knowledge_base,
    # Task Management
    add_task,
    list_tasks,
    assign_task,
    complete_task,
    delete_task,
    archive_task,
    update_task_priority,
    update_task_due_date,
    update_task_status,
    # Project Management
    list_projects,
    create_project,
    get_project_details,
    # Analytics
    get_profitability,
    workload_summary,
    # AI Recommendations
    suggest_assignee,
    # Time Entry
    add_time_entry,
    list_time_entries,
    get_time_for_task,
    update_time_entry,
    delete_time_entry,
]
