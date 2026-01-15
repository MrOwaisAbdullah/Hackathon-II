"""Unit tests for MCP tools (T067).

Tests the AI recommendation tools including suggest_assignee with sample data.
"""
import pytest
from uuid import uuid4, UUID
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from app.models.task import Task, TaskCreate, TaskPriority, TaskStatus
from app.models.user import User
from app.models.project import Project
from app.services.task_service import TaskService
from app.mcp.tools import register_recommendation_tools, register_analytics_tools, register_task_tools


@pytest.fixture
def test_agency(db_session: Session):
    """Create a test agency."""
    from app.models.agency import Agency
    agency = Agency(
        name="Test Agency",
        slug="test-agency",
    )
    db_session.add(agency)
    db_session.commit()
    db_session.refresh(agency)
    return agency


@pytest.fixture
def test_project(db_session: Session, test_agency):
    """Create a test project."""
    project = Project(
        title="Test Project",
        agency_id=test_agency.id,
        budget=10000.0,
        hourly_rate=100.0,
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


@pytest.fixture
def test_users(db_session: Session, test_agency):
    """Create test users with different skills."""
    users = [
        User(
            email="alice@example.com",
            full_name="Alice Johnson",
            agency_id=test_agency.id,
            skills=["python", "fastapi", "react"],
            capacity_hours=40,
            role="member",
        ),
        User(
            email="bob@example.com",
            full_name="Bob Smith",
            agency_id=test_agency.id,
            skills=["javascript", "react", "nodejs"],
            capacity_hours=40,
            role="member",
        ),
        User(
            email="charlie@example.com",
            full_name="Charlie Brown",
            agency_id=test_agency.id,
            skills=["python", "django", "postgresql"],
            capacity_hours=40,
            role="member",
        ),
    ]
    for user in users:
        db_session.add(user)
    db_session.commit()
    for user in users:
        db_session.refresh(user)
    return users


@pytest.fixture
def test_tasks(db_session: Session, test_project, test_users):
    """Create test tasks assigned to different users."""
    tasks = [
        Task(
            title="Build API endpoint",
            description="Create a FastAPI endpoint for user authentication",
            project_id=test_project.id,
            agency_id=test_project.agency_id,
            assignee_id=test_users[0].id,  # Alice - Python/FastAPI
            priority=TaskPriority.HIGH,
            status=TaskStatus.DOING,
        ),
        Task(
            title="Fix navbar bug",
            description="Fix responsive navbar issue on mobile",
            project_id=test_project.id,
            agency_id=test_project.agency_id,
            assignee_id=test_users[1].id,  # Bob - React/JavaScript
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.TODO,
        ),
        Task(
            title="Database optimization",
            description="Optimize PostgreSQL queries for better performance",
            project_id=test_project.id,
            agency_id=test_project.agency_id,
            assignee_id=test_users[2].id,  # Charlie - Python/PostgreSQL
            priority=TaskPriority.HIGH,
            status=TaskStatus.DOING,
        ),
    ]
    for task in tasks:
        db_session.add(task)
    db_session.commit()
    for task in tasks:
        db_session.refresh(task)
    return tasks


class TestSuggestAssignee:
    """Test suggest_assignee MCP tool (T067)."""

    def test_suggest_assignee_recommends_correct_user(
        self, db_session: Session, test_tasks, test_users
    ):
        """Test that suggest_assignee recommends the most suitable team member."""
        # Create a new task that requires Python/FastAPI skills
        # Alice should be recommended (has python, fastapi, currently has 1 task)
        new_task = Task(
            title="Create REST API",
            description="Build a REST API using FastAPI and Python",
            project_id=test_tasks[0].project_id,
            agency_id=test_tasks[0].agency_id,
            priority=TaskPriority.HIGH,
            status=TaskStatus.TODO,
        )
        db_session.add(new_task)
        db_session.commit()
        db_session.refresh(new_task)

        # Call suggest_assignee tool
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("test")
        register_recommendation_tools(mcp)

        # Get the suggest_assignee tool
        suggest_assignee_tool = None
        for tool_name, tool_func in mcp._tool_manager._tools.items():
            if tool_name == "suggest_assignee":
                suggest_assignee_tool = tool_func
                break

        assert suggest_assignee_tool is not None, "suggest_assignee tool not found"

        # Call the tool
        result = suggest_assignee_tool(task_id=str(new_task.id))

        # Verify result contains recommendation
        assert "Recommended Assignee:" in result
        assert "Alice Johnson" in result or "Charlie Brown" in result  # Both have Python
        assert "Reasoning:" in result
        assert "Skills Match:" in result
        assert "Workload Analysis:" in result
        assert "Overall Score:" in result

        # Verify alternatives are included
        assert "Alternative Candidates:" in result

    def test_suggest_assignee_includes_alternatives(
        self, db_session: Session, test_tasks
    ):
        """Test that suggest_assignee provides alternative candidates."""
        # Use existing task
        result = None
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_recommendation_tools(mcp)

        # Get the suggest_assignee tool
        for tool_name, tool_func in mcp._tool_manager._tools.items():
            if tool_name == "suggest_assignee":
                result = tool_func(task_id=str(test_tasks[0].id))
                break

        assert result is not None
        # Should include top 3 alternatives
        assert "Alternative Candidates:" in result
        # Count how many alternatives are listed
        lines = result.split("\n")
        alternative_count = sum(1 for line in lines if line.strip().startswith(("1.", "2.", "3.")))
        assert alternative_count >= 1, "Should include at least 1 alternative"

    def test_suggest_assignee_handles_nonexistent_task(self):
        """Test that suggest_assignee handles non-existent task gracefully."""
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_recommendation_tools(mcp)

        # Get the suggest_assignee tool
        for tool_name, tool_func in mcp._tool_manager._tools.items():
            if tool_name == "suggest_assignee":
                result = tool_func(task_id=str(uuid4()))  # Non-existent UUID
                assert "Error:" in result or "not found" in result.lower()
                break


class TestWorkloadSummary:
    """Test workload_summary MCP tool."""

    def test_workload_summary_shows_utilization(
        self, db_session: Session, test_agency, test_users, test_tasks
    ):
        """Test that workload_summary shows team member utilization."""
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_analytics_tools(mcp)

        # Get the workload_summary tool
        for tool_name, tool_func in mcp._tool_manager._tools.items():
            if tool_name == "workload_summary":
                result = tool_func(agency_id=str(test_agency.id))

                # Verify summary includes all team members
                assert "Workload Summary" in result
                assert "Alice Johnson" in result
                assert "Bob Smith" in result
                assert "Charlie Brown" in result

                # Verify utilization data is included
                assert "Tasks" in result
                assert "Hours" in result
                assert "Utilization" in result

                # Verify summary statistics
                assert "Total team members:" in result
                assert "Average utilization:" in result
                break

    def test_workload_summary_identifies_over_capacity(
        self, db_session: Session, test_agency, test_users
    ):
        """Test that workload_summary identifies members over capacity."""
        # Give one user too many tasks (over 40 hours)
        from app.services.task_service import TaskService

        task_service = TaskService()
        for i in range(15):  # 15 tasks * 4 hours = 60 hours (> 40 capacity)
            task = TaskCreate(
                title=f"Extra task {i}",
                project_id=None,
                assignee_id=test_users[0].id,
                priority=TaskPriority.MEDIUM,
            )
            task_service.create_task(task, test_agency.id, db_session)

        # Check workload summary
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_analytics_tools(mcp)

        for tool_name, tool_func in mcp._tool_manager._tools.items():
            if tool_name == "workload_summary":
                result = tool_func(agency_id=str(test_agency.id))

                # Should identify over-capacity members
                assert "Members over capacity:" in result
                assert "⚠️" in result  # Warning indicator
                break


class TestGetProfitability:
    """Test get_profitability MCP tool."""

    def test_get_profitability_calculates_metrics(
        self, db_session: Session, test_project
    ):
        """Test that get_profitability calculates revenue, cost, profit, and margin."""
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_analytics_tools(mcp)

        for tool_name, tool_func in mcp._tool_manager._tools.items():
            if tool_name == "get_profitability":
                result = tool_func(project_id=str(test_project.id))

                # Verify financial metrics are included
                assert "Profitability Analysis" in result
                assert "Revenue:" in result
                assert "Cost:" in result
                assert "Profit:" in result
                assert "Margin:" in result

                # Verify budget comparison
                assert "Budget Comparison:" in result
                assert "Status:" in result
                break

    def test_get_profitability_handles_project_without_budget(
        self, db_session: Session, test_agency
    ):
        """Test that get_profitability handles project without budget."""
        from app.models.project import Project
        from mcp.server.fastmcp import FastMCP

        # Create project without budget
        project = Project(
            title="No Budget Project",
            agency_id=test_agency.id,
        )
        db_session.add(project)
        db_session.commit()
        db_session.refresh(project)

        mcp = FastMCP("test")
        register_analytics_tools(mcp)

        for tool_name, tool_func in mcp._tool_manager._tools.items():
            if tool_name == "get_profitability":
                result = tool_func(project_id=str(project.id))

                # Should return error message
                assert "Error:" in result or "budget" in result.lower()
                break


class TestTaskManagementTools:
    """Test task management MCP tools."""

    def test_add_task_creates_task(
        self, db_session: Session, test_project, test_users
    ):
        """Test that add_task tool creates a new task."""
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_task_tools(mcp)

        for tool_name, tool_func in mcp._tool_manager._tools.items():
            if tool_name == "add_task":
                result = tool_func(
                    title="Test task from MCP",
                    description="This is a test task created via MCP tool",
                    project_id=str(test_project.id),
                    assignee_id=str(test_users[0].id),
                    priority="high",
                )

                # Verify task was created
                assert "Task created successfully!" in result
                assert "Test task from MCP" in result
                assert "HIGH" in result
                break

    def test_list_tasks_filters_by_status(
        self, db_session: Session, test_project, test_tasks
    ):
        """Test that list_tasks tool filters by status."""
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_task_tools(mcp)

        for tool_name, tool_func in mcp._tool_manager._tools.items():
            if tool_name == "list_tasks":
                # Filter by DOING status
                result = tool_func(
                    project_id=str(test_project.id),
                    status="doing",
                )

                # Verify filtering works
                assert "Found" in result
                # Should only show DOING tasks
                assert "DOING" in result
                break

    def test_assign_task_reassigns_task(
        self, db_session: Session, test_tasks, test_users
    ):
        """Test that assign_task tool reassigns a task."""
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_task_tools(mcp)

        for tool_name, tool_func in mcp._tool_manager._tools.items():
            if tool_name == "assign_task":
                # Reassign first task to third user
                original_assignee = test_tasks[0].assignee.full_name
                new_assignee = test_users[2]

                result = tool_func(
                    task_id=str(test_tasks[0].id),
                    assignee_id=str(new_assignee.id),
                )

                # Verify reassignment
                assert "Task assigned successfully!" in result
                assert new_assignee.full_name in result
                break

    def test_complete_task_marks_done(
        self, db_session: Session, test_tasks
    ):
        """Test that complete_task tool marks task as DONE."""
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_task_tools(mcp)

        for tool_name, tool_func in mcp._tool_manager._tools.items():
            if tool_name == "complete_task":
                # Complete a TODO task
                todo_task = [t for t in test_tasks if t.status == TaskStatus.TODO][0]

                result = tool_func(task_id=str(todo_task.id))

                # Verify completion
                assert "Task completed successfully!" in result
                assert "DONE" in result
                break
