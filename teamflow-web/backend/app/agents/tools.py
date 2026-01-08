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
from agents import function_tool

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
        Confirmation message with task details
    """
    # TODO: Integrate with TaskService when implemented
    details = []
    if description:
        details.append(f"description: {description}")
    if project_id:
        details.append(f"project: {project_id}")
    if assignee_id:
        details.append(f"assignee: {assignee_id}")
    if priority:
        details.append(f"priority: {priority}")

    details_str = ", ".join(details) if details else "no additional details"
    return f"Task '{title}' created successfully with {details_str}. (Integration with TaskService pending)"


@function_tool
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
        status: Filter by status (TODO, IN_PROGRESS, BLOCKED, DONE)
        limit: Maximum number of tasks to return (default: 50)

    Returns:
        List of tasks with their details
    """
    # TODO: Integrate with TaskService when implemented
    filters = []
    if project_id:
        filters.append(f"project={project_id}")
    if assignee_id:
        filters.append(f"assignee={assignee_id}")
    if status:
        filters.append(f"status={status}")

    filter_str = ", ".join(filters) if filters else "no filters"
    return f"Found 0 tasks with {filter_str}. (Integration with TaskService pending)"


@function_tool
def assign_task(task_id: str, assignee_id: str) -> str:
    """Assign a task to a user.

    Args:
        task_id: Task ID to reassign
        assignee_id: User ID to assign task to

    Returns:
        Confirmation message with new assignment
    """
    # TODO: Integrate with TaskService when implemented
    return f"Task {task_id} assigned to user {assignee_id}. (Integration with TaskService pending)"


@function_tool
def complete_task(task_id: str) -> str:
    """Mark a task as complete.

    Args:
        task_id: Task ID to complete

    Returns:
        Confirmation message
    """
    # TODO: Integrate with TaskService when implemented
    return f"Task {task_id} marked as complete. (Integration with TaskService pending)"


# Analytics Tools


@function_tool
def get_profitability(project_id: str) -> str:
    """Get profitability analysis for a project.

    Args:
        project_id: Project ID to analyze

    Returns:
        Profitability metrics including revenue, cost, profit, and margin
    """
    # TODO: Integrate with AnalyticsService when implemented
    return f"Profitability analysis for project {project_id}: revenue $0, cost $0, profit $0, margin 0%. (Integration with AnalyticsService pending)"


@function_tool
def workload_summary(agency_id: str) -> str:
    """Get workload summary for an agency.

    Args:
        agency_id: Agency ID to analyze

    Returns:
        Workload summary showing team member utilization
    """
    # TODO: Integrate with AnalyticsService when implemented
    return f"Workload summary for agency {agency_id}: 0 team members, 0% utilization. (Integration with AnalyticsService pending)"


# AI Recommendation Tools


@function_tool
def suggest_assignee(task_id: str) -> str:
    """Suggest the best assignee for a task using AI reasoning.

    Analyzes team member skills, current workload, and availability to recommend
    the most suitable person for a task.

    Args:
        task_id: Task ID to find assignee for

    Returns:
        Recommended assignee with reasoning (skills match, workload score, alternatives)
    """
    # TODO: Integrate with recommendation engine when implemented
    return f"Assignee suggestion for task {task_id}: No suitable assignee found. (Integration with recommendation engine pending)"


# Export all tools for use with Agent
TEAMFLOW_TOOLS = [
    search_knowledge_base,  # RAG tool
    add_task,
    list_tasks,
    assign_task,
    complete_task,
    get_profitability,
    workload_summary,
    suggest_assignee,
]
