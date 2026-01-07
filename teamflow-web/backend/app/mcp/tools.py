"""MCP tools for TeamFlow (T018-T020).

These tools expose service layer methods as MCP tools for AI agents.
Tool categories:
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
        # This is a placeholder - actual implementation would use TaskService
        # For now, return a structured response
        return f"Task '{title}' created successfully. (Tool implementation pending service integration)"

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
        return f"Tasks filtered by project={project_id}, assignee={assignee_id}, status={status}. (Tool implementation pending service integration)"

    @mcp.tool()
    def assign_task(task_id: str, assignee_id: str) -> str:
        """Assign a task to a user.

        Args:
            task_id: Task ID to reassign
            assignee_id: User ID to assign task to

        Returns:
            Confirmation message with new assignment
        """
        return f"Task {task_id} assigned to user {assignee_id}. (Tool implementation pending service integration)"

    @mcp.tool()
    def complete_task(task_id: str) -> str:
        """Mark a task as complete.

        Args:
            task_id: Task ID to complete

        Returns:
            Confirmation message
        """
        return f"Task {task_id} marked as complete. (Tool implementation pending service integration)"


# Analytics Tools (T019)


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
        return f"Profitability analysis for project {project_id}. (Tool implementation pending service integration)"

    @mcp.tool()
    def workload_summary(agency_id: str) -> str:
        """Get workload summary for an agency.

        Args:
            agency_id: Agency ID to analyze

        Returns:
            Workload summary showing team member utilization
        """
        return f"Workload summary for agency {agency_id}. (Tool implementation pending service integration)"


# AI Recommendation Tools (T020)


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
        return f"Assignee suggestion for task {task_id}. (Tool implementation pending service integration)"
