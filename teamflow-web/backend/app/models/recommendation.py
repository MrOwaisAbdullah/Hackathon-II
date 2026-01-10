"""Recommendation acceptance tracking model (A1 - Specification Analysis Finding).

This module provides database models for tracking AI recommendation acceptance/rejection.
Used to calculate SC-005: 70% acceptance rate target (T066, T069).
"""
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Column, JSON


class RecommendationAcceptanceLog(SQLModel, table=True):
    """Database model for tracking recommendation acceptance (T066, SC-005).

    Tracks when users accept or reject AI-suggested actions:
    - Task assignments (suggest_assignee tool)
    - Task creations from natural language
    - Priority recommendations
    - Other AI-driven suggestions

    This data is used to calculate recommendation acceptance rate (SC-005: 70% target).
    """

    __tablename__ = "recommendation_acceptance_log"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True, description="User who received the recommendation")
    recommendation_type: str = Field(nullable=False, index=True, description="Type: 'assignee', 'task_creation', 'priority', etc.")
    recommendation_id: str = Field(nullable=False, description="Unique identifier for the recommendation")
    action: str = Field(nullable=False, description="User action: 'accepted' or 'rejected'")
    reasoning: Optional[str] = Field(default=None, description="AI reasoning that was shown to user")
    context: Optional[dict] = Field(default=None, column_type=JSON, description="Additional context (task_id, project_id, etc.)")
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True, description="When the user acted on the recommendation")
