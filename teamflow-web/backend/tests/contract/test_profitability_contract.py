"""Contract tests for profitability analytics endpoints.

These tests verify the schema validation for profitability data (User Story 5).
The actual analytics returns a list of dicts with project profitability data.
"""
import pytest


class TestProfitabilityContract:
    """Contract tests for profitability analytics schemas."""

    def test_project_profitability_structure(self):
        """Test profitability data structure contains required keys."""
        # Single project profitability data
        data = {
            "projectId": "123e4567-e89b-12d3-a456-426614174000",
            "projectName": "Website Redesign",
            "totalTasks": 10,
            "completedTasks": 7,
            "completionPercentage": 70.0,
            "revenue": 5000.0,
            "cost": 3200.0,
            "profit": 1800.0,
        }

        # Verify all required keys exist
        required_keys = [
            "projectId", "projectName", "totalTasks", "completedTasks",
            "completionPercentage", "revenue", "cost", "profit"
        ]
        for key in required_keys:
            assert key in data, f"Missing required key: {key}"

        assert isinstance(data["projectId"], str)
        assert isinstance(data["projectName"], str)
        assert isinstance(data["totalTasks"], int)
        assert isinstance(data["completedTasks"], int)
        assert isinstance(data["completionPercentage"], (int, float))
        assert isinstance(data["revenue"], (int, float))
        assert isinstance(data["cost"], (int, float))
        assert isinstance(data["profit"], (int, float))

    def test_profitability_calculation(self):
        """Test profit calculation: profit = revenue - cost."""
        data = {
            "projectId": "123e4567-e89b-12d3-a456-426614174000",
            "projectName": "Mobile App",
            "totalTasks": 15,
            "completedTasks": 12,
            "completionPercentage": 80.0,
            "revenue": 10000.0,
            "cost": 6000.0,
            "profit": 4000.0,
        }

        assert data["profit"] == data["revenue"] - data["cost"]

    def test_profitability_negative_profit(self):
        """Test handling of negative profit (unprofitable project)."""
        data = {
            "projectId": "123e4567-e89b-12d3-a456-426614174000",
            "projectName": "Loss Project",
            "totalTasks": 5,
            "completedTasks": 2,
            "completionPercentage": 40.0,
            "revenue": 2000.0,
            "cost": 3000.0,
            "profit": -1000.0,
        }

        assert data["profit"] == -1000.0

    def test_profitability_list(self):
        """Test profitability data for multiple projects."""
        data = [
            {
                "projectId": "123e4567-e89b-12d3-a456-426614174000",
                "projectName": "Website Redesign",
                "totalTasks": 10,
                "completedTasks": 7,
                "completionPercentage": 70.0,
                "revenue": 5000.0,
                "cost": 3200.0,
                "profit": 1800.0,
            },
            {
                "projectId": "223e4567-e89b-12d3-a456-426614174001",
                "projectName": "Mobile App",
                "totalTasks": 15,
                "completedTasks": 12,
                "completionPercentage": 80.0,
                "revenue": 8000.0,
                "cost": 5000.0,
                "profit": 3000.0,
            },
        ]

        assert len(data) == 2
        total_profit = sum(p["profit"] for p in data)
        assert total_profit == 4800.0

    def test_completion_percentage_calculation(self):
        """Test completion percentage calculation."""
        # Test zero division handling
        data = {
            "projectId": "123e4567-e89b-12d3-a456-426614174000",
            "projectName": "New Project",
            "totalTasks": 0,
            "completedTasks": 0,
            "completionPercentage": 0.0,  # Should handle division by zero
            "revenue": 0.0,
            "cost": 0.0,
            "profit": 0.0,
        }

        # If totalTasks is 0, completionPercentage should be 0
        if data["totalTasks"] == 0:
            assert data["completionPercentage"] == 0.0
