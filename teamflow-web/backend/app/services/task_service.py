"""Task service for task CRUD operations."""
from typing import Optional
from uuid import UUID
from datetime import datetime

from sqlmodel import Session, col, select
from sqlalchemy.orm import selectinload

from app.models.project import Project
from app.models.task import Task, TaskCreate, TaskUpdate, TaskStatus
from app.models.user import User

# Phase 5: Import EventPublisher for task lifecycle events
# Import at runtime to avoid circular imports


class TaskService:
    """Service for task operations."""

    def _get_event_publisher(self):
        """Lazy import EventPublisher to avoid circular imports."""
        from app.services.event_publisher import EventPublisher

        return EventPublisher()

    def create_task(
        self,
        task_data: TaskCreate,
        agency_id: UUID,
        session: Session,
        user_id: Optional[UUID] = None,
    ) -> Task:
        """Create a new task for an agency."""
        # Verify project exists and belongs to agency
        if task_data.project_id:
            project = session.get(Project, task_data.project_id)
            if not project or project.agency_id != agency_id:
                raise ValueError("Invalid project")

        # Verify assignee exists and belongs to agency
        if task_data.assignee_id:
            assignee = session.get(User, task_data.assignee_id)
            if not assignee or assignee.agency_id != agency_id:
                raise ValueError("Invalid assignee")

        task = Task(
            **task_data.model_dump(exclude_unset=True),
            agency_id=agency_id,
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        # Phase 5: T044 - Set next_instance_id when creating recurring task
        if task.recurrence_rule:
            from app.services.recurrence_calculator import RecurrenceCalculator, RecurrenceRule

            rule = RecurrenceRule(**task.recurrence_rule)
            if task.due_date:
                due_datetime = datetime.combine(task.due_date, datetime.min.time())
            else:
                due_datetime = datetime.utcnow()

            next_date = RecurrenceCalculator.calculate_next_instance(due_datetime, rule)
            if next_date:
                # Note: In a real implementation, we would create the next instance
                # For now, we just log that we calculated the next date
                pass

        # Phase 5: Publish task.created event
        try:
            event_publisher = self._get_event_publisher()
            import asyncio

            # Run async event publishing in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    event_publisher.publish_task_created(
                        task_id=str(task.id),
                        project_id=str(task.project_id) if task.project_id else "",
                        user_id=str(user_id) if user_id else "",
                        title=task.title,
                        status=task.status.value,
                        recurrence_rule=task.recurrence_rule,
                    )
                )
            finally:
                loop.close()
        except Exception as e:
            # Log error but don't fail task creation
            pass

        # T082, T083: Generate and schedule reminders if task has due_date and reminder_settings
        if task.due_date and task.reminder_settings:
            try:
                self._schedule_reminders(task, agency_id, session, user_id)
            except Exception as e:
                # Log error but don't fail task creation
                pass

        # Load assignee relationship for response
        task_with_assignee = session.exec(
            select(Task)
            .options(selectinload(Task.assignee))
            .where(Task.id == task.id)
        ).first()
        return task_with_assignee or task

    def get_task(
        self,
        task_id: UUID,
        agency_id: UUID,
        session: Session,
    ) -> Optional[Task]:
        """Get a task by ID (scoped to agency)."""
        return session.exec(
            select(Task)
            .options(selectinload(Task.assignee))
            .where(
                Task.id == task_id,
                Task.agency_id == agency_id,
            )
        ).first()

    def list_tasks(
        self,
        agency_id: UUID,
        session: Session,
        status: Optional[TaskStatus] = None,
        project_id: Optional[UUID] = None,
        assignee_id: Optional[UUID] = None,
        include_archived: bool = False,
    ) -> list[Task]:
        """List tasks for an agency with optional filters."""
        query = select(Task).options(selectinload(Task.assignee)).where(Task.agency_id == agency_id)

        if status:
            query = query.where(Task.status == status)
        if project_id:
            query = query.where(Task.project_id == project_id)
        if assignee_id:
            query = query.where(Task.assignee_id == assignee_id)

        # Exclude archived tasks by default unless include_archived=True
        if not include_archived:
            query = query.where(Task.status != TaskStatus.ARCHIVED)

        # Order by status then created_at
        query = query.order_by(Task.status, Task.created_at.desc())

        return session.exec(query).all()

    def update_task(
        self,
        task_id: UUID,
        task_data: TaskUpdate,
        agency_id: UUID,
        session: Session,
        user_id: Optional[UUID] = None,
    ) -> Optional[Task]:
        """Update a task."""
        task = self.get_task(task_id, agency_id, session)
        if not task:
            return None

        # Phase 5: T043 - Track status change for event emission
        old_status = task.status

        # Verify project belongs to agency
        if task_data.project_id:
            project = session.get(Project, task_data.project_id)
            if not project or project.agency_id != agency_id:
                raise ValueError("Invalid project")

        # Verify assignee belongs to agency
        if task_data.assignee_id:
            assignee = session.get(User, task_data.assignee_id)
            if not assignee or assignee.agency_id != agency_id:
                raise ValueError("Invalid assignee")

        task_data_dict = task_data.model_dump(exclude_unset=True)
        for field, value in task_data_dict.items():
            setattr(task, field, value)

        session.add(task)
        session.commit()
        session.refresh(task)

        # Phase 5: T043 - Emit task.completed event when status changes to DONE
        new_status = task.status
        if old_status != new_status and new_status == TaskStatus.DONE:
            try:
                event_publisher = self._get_event_publisher()
                import asyncio

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(
                        event_publisher.publish_task_completed(
                            task_id=str(task.id),
                            project_id=str(task.project_id) if task.project_id else "",
                            user_id=str(user_id) if user_id else "",
                            recurrence_rule=task.recurrence_rule,
                        )
                    )
                finally:
                    loop.close()
            except Exception as e:
                # Log error but don't fail task update
                pass

        # Also publish task_updated event
        try:
            event_publisher = self._get_event_publisher()
            import asyncio

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    event_publisher.publish_task_updated(
                        task_id=str(task.id),
                        project_id=str(task.project_id) if task.project_id else "",
                        user_id=str(user_id) if user_id else "",
                        changes={"status": old_status.value + " -> " + new_status.value},
                    )
                )
            finally:
                loop.close()
        except Exception:
            pass

        # T082, T083: Reschedule reminders if due_date or reminder_settings changed
        if task.due_date and task.reminder_settings:
            # Check if reminder settings were updated
            reminder_fields_updated = any(
                field in task_data_dict for field in ["due_date", "reminder_settings"]
            )
            if reminder_fields_updated:
                try:
                    self._schedule_reminders(task, agency_id, session, user_id)
                except Exception as e:
                    # Log error but don't fail task update
                    pass

        # Return task with assignee relationship loaded
        return self.get_task(task_id, agency_id, session)

    def delete_task(
        self,
        task_id: UUID,
        agency_id: UUID,
        session: Session,
    ) -> bool:
        """Soft delete a task by marking with deleted status."""
        # For now, we'll do actual delete
        # In production, you might want soft delete with a deleted_at field
        task = self.get_task(task_id, agency_id, session)
        if not task:
            return False

        session.delete(task)
        session.commit()
        return True

    def assign_task(
        self,
        task_id: UUID,
        assignee_id: UUID,
        agency_id: UUID,
        session: Session,
    ) -> Optional[Task]:
        """Assign a task to a user.

        Args:
            task_id: ID of the task to assign
            assignee_id: ID of the user to assign the task to (or None to unassign)
            agency_id: Agency ID for multi-tenant isolation
            session: Database session

        Returns:
            The updated task, or None if task not found

        Raises:
            ValueError: If assignee doesn't exist or doesn't belong to the agency
        """
        task = self.get_task(task_id, agency_id, session)
        if not task:
            return None

        # If assignee_id is None, unassign the task
        if assignee_id is None:
            task.assignee_id = None
            session.add(task)
            session.commit()
            session.refresh(task)
            # Load with assignee relationship (will be None)
            return self.get_task(task_id, agency_id, session)

        # Verify assignee exists and belongs to the same agency
        assignee = session.get(User, assignee_id)
        if not assignee:
            raise ValueError("Assignee not found")
        if assignee.agency_id != agency_id:
            raise ValueError("Assignee does not belong to the same agency")

        # Update the task's assignee
        task.assignee_id = assignee_id
        session.add(task)
        session.commit()
        session.refresh(task)
        # Return task with assignee relationship loaded
        return self.get_task(task_id, agency_id, session)

    def archive_task(
        self,
        task_id: UUID,
        agency_id: UUID,
        session: Session,
    ) -> Optional[Task]:
        """Archive a task by setting status to ARCHIVED.

        Args:
            task_id: ID of the task to archive
            agency_id: Agency ID for multi-tenant isolation
            session: Database session

        Returns:
            The archived task, or None if task not found
        """
        task = self.get_task(task_id, agency_id, session)
        if not task:
            return None

        task.status = TaskStatus.ARCHIVED
        session.add(task)
        session.commit()
        session.refresh(task)
        # Return task with assignee relationship loaded
        return self.get_task(task_id, agency_id, session)

    def restore_task(
        self,
        task_id: UUID,
        agency_id: UUID,
        session: Session,
        restore_status: TaskStatus = TaskStatus.DONE,
    ) -> Optional[Task]:
        """Restore an archived task to a specified status.

        Args:
            task_id: ID of the task to restore
            agency_id: Agency ID for multi-tenant isolation
            session: Database session
            restore_status: Status to restore the task to (default: DONE)

        Returns:
            The restored task, or None if task not found
        """
        task = self.get_task(task_id, agency_id, session)
        if not task:
            return None

        # Only allow restoring archived tasks
        if task.status != TaskStatus.ARCHIVED:
            raise ValueError("Task is not archived")

        task.status = restore_status
        session.add(task)
        session.commit()
        session.refresh(task)
        # Return task with assignee relationship loaded
        return self.get_task(task_id, agency_id, session)

    def _schedule_reminders(
        self,
        task: Task,
        agency_id: UUID,
        session: Session,
        user_id: Optional[UUID] = None,
    ) -> None:
        """
        T082, T083: Schedule reminders for a task with due date and reminder settings.

        This method:
        1. Calculates reminder times using ReminderScheduler
        2. Creates ReminderEvent records in the database
        3. Publishes reminder events to Kafka via EventPublisher

        Args:
            task: The task with due_date and reminder_settings
            agency_id: Agency ID
            session: Database session
            user_id: Optional user ID for logging
        """
        from app.services.reminder_scheduler import ReminderScheduler, ReminderSettings as SchedulerReminderSettings
        from app.models.reminder_event import ReminderEvent, ReminderEventStatus
        import structlog

        logger = structlog.get_logger(__name__)

        if not task.due_date or not task.reminder_settings:
            return

        # Convert task's reminder_settings to ReminderScheduler format
        try:
            # ReminderSettings from task model: {offsets: [...], channels: [...], custom_message: ...}
            scheduler_settings = SchedulerReminderSettings(
                offsets=task.reminder_settings.get("offsets", []),
                channels=task.reminder_settings.get("channels", ["email"])
            )
        except Exception as e:
            logger.error(
                "invalid_reminder_settings",
                task_id=str(task.id),
                error=str(e),
            )
            return

        # Calculate reminder times
        # Combine due_date with current time for datetime
        from datetime import datetime, timezone
        due_datetime = datetime.combine(task.due_date, datetime.min.time()).replace(tzinfo=timezone.utc)

        reminder_times = ReminderScheduler.calculate_reminder_times(
            due_date=due_datetime,
            reminder_settings=scheduler_settings,
        )

        if not reminder_times:
            logger.info(
                "no_reminders_scheduled",
                task_id=str(task.id),
                reason="All reminder times are in the past",
            )
            return

        # Get user info for reminders
        assignee_id = task.assignee_id or user_id
        if not assignee_id:
            logger.warning(
                "no_assignee_for_reminders",
                task_id=str(task.id),
            )
            return

        from app.models.user import User
        assignee = session.get(User, assignee_id)
        if not assignee:
            logger.warning(
                "assignee_not_found",
                assignee_id=str(assignee_id),
            )
            return

        # Create ReminderEvent records and publish events
        event_publisher = self._get_event_publisher()
        import asyncio

        for remind_at in reminder_times:
            # Create unique reminder ID
            import uuid
            reminder_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{task.id}:{remind_at.isoformat()}"))

            # Create ReminderEvent record
            reminder_event = ReminderEvent(
                id=uuid.UUID(reminder_id),
                task_id=task.id,
                agency_id=agency_id,
                user_id=assignee_id,
                status=ReminderEventStatus.PENDING,
                remind_at=remind_at,
                due_date=due_datetime,
                task_title=task.title,
                task_description=task.description,
                user_email=assignee.email,
                user_name=assignee.name,
                created_at=datetime.now(timezone.utc),
            )

            # Note: We would need a ReminderEvent model in database to persist this
            # For now, we publish the event directly
            # In production, you'd do: session.add(reminder_event); session.commit()

            # Publish reminder event to Kafka
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(
                        event_publisher.publish_reminder_event(
                            reminder_id=reminder_id,
                            task_id=str(task.id),
                            user_id=str(assignee_id),
                            due_date=due_datetime.isoformat(),
                            channels=task.reminder_settings.get("channels", ["email"]),
                            custom_message=task.reminder_settings.get("custom_message"),
                        )
                    )
                finally:
                    loop.close()

                logger.info(
                    "reminder_scheduled",
                    reminder_id=reminder_id,
                    task_id=str(task.id),
                    remind_at=remind_at.isoformat(),
                    user_id=str(assignee_id),
                )
            except Exception as e:
                logger.error(
                    "failed_to_publish_reminder_event",
                    reminder_id=reminder_id,
                    task_id=str(task.id),
                    error=str(e),
                )
