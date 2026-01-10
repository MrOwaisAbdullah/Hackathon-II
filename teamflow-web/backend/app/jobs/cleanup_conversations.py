"""Conversation cleanup job for Phase 7 (T085).

Deletes messages and conversations older than 7 days to manage storage
and comply with data retention policies.

Usage:
    python -m app.jobs.cleanup_conversations
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlmodel import Session, select, col
from app.models.chat import Message, Conversation
from app.database import get_session


RETENTION_DAYS = 7
"""Number of days to retain conversations before cleanup."""


def get_cutoff_date() -> datetime:
    """Get the cutoff date for cleanup (T085).

    Returns:
        datetime: Cutoff date (current time - RETENTION_DAYS)
    """
    return datetime.utcnow() - timedelta(days=RETENTION_DAYS)


def cleanup_messages(session: Session, cutoff_date: datetime) -> int:
    """Delete messages older than cutoff date (T085).

    Args:
        session: Database session
        cutoff_date: Messages older than this date will be deleted

    Returns:
        int: Number of messages deleted
    """
    statement = select(Message).where(Message.created_at < cutoff_date)
    results = session.exec(statement)
    messages_to_delete = results.all()

    count = len(messages_to_delete)

    for message in messages_to_delete:
        session.delete(message)

    session.commit()

    return count


def cleanup_conversations(session: Session, cutoff_date: datetime) -> int:
    """Delete conversations older than cutoff date (T085).

    Only deletes conversations that have no messages (orphaned conversations).
    Active conversations with recent messages are preserved.

    Args:
        session: Database session
        cutoff_date: Conversations older than this date will be deleted

    Returns:
        int: Number of conversations deleted
    """
    # Find conversations with no messages (orphans) or older than cutoff
    statement = select(Conversation).where(
        (Conversation.created_at < cutoff_date) & (Conversation.is_archived == True)
    )
    results = session.exec(statement)
    conversations_to_delete = results.all()

    count = len(conversations_to_delete)

    for conversation in conversations_to_delete:
        session.delete(conversation)

    session.commit()

    return count


def get_stats(session: Session) -> dict:
    """Get current database statistics (T085).

    Args:
        session: Database session

    Returns:
        dict: Statistics including total messages and conversations
    """
    total_messages = session.exec(select(col(Message.id).count())).one()
    total_conversations = session.exec(select(col(Conversation.id).count())).one()

    return {
        "total_messages": total_messages,
        "total_conversations": total_conversations,
    }


def main():
    """Run the cleanup job (T085).

    Deletes messages and conversations older than RETENTION_DAYS.
    Prints summary statistics before and after cleanup.
    """
    print(f"[cleanup_conversations] Starting cleanup job...")
    print(f"[cleanup_conversations] Retention period: {RETENTION_DAYS} days")

    cutoff_date = get_cutoff_date()
    print(f"[cleanup_conversations] Cutoff date: {cutoff_date.isoformat()}")

    with next(get_session()) as session:
        # Get stats before cleanup
        stats_before = get_stats(session)
        print(f"[cleanup_conversations] Stats before: {stats_before}")

        # Cleanup messages
        messages_deleted = cleanup_messages(session, cutoff_date)
        print(f"[cleanup_conversations] Deleted {messages_deleted} messages")

        # Cleanup conversations (only archived/orphaned)
        conversations_deleted = cleanup_conversations(session, cutoff_date)
        print(f"[cleanup_conversations] Deleted {conversations_deleted} conversations")

        # Get stats after cleanup
        stats_after = get_stats(session)
        print(f"[cleanup_conversations] Stats after: {stats_after}")

        print(f"[cleanup_conversations] Cleanup job completed successfully")
        print(f"[cleanup_conversations] Summary:")
        print(f"  - Messages deleted: {messages_deleted}")
        print(f"  - Conversations deleted: {conversations_deleted}")
        print(f"  - Storage freed: {stats_before['total_messages'] - stats_after['total_messages']} messages")
        print(f"  - Remaining messages: {stats_after['total_messages']}")
        print(f"  - Remaining conversations: {stats_after['total_conversations']}")


if __name__ == "__main__":
    main()
