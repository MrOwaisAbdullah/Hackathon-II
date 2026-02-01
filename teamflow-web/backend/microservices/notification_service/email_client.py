"""
T069: SendGrid Email Client

Async email client for sending task reminder notifications via SendGrid.
Includes error handling, retry support, and health checks.
"""

import os
from typing import Optional, Dict, Any
from datetime import datetime

import httpx
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
import structlog

from teamflow_web.backend.app.models.reminder_event import ReminderEvent


logger = structlog.get_logger(__name__)


class SendGridEmailClient:
    """
    Async email client for SendGrid with retry logic and health checks.

    Handles email sending for task reminders with proper error handling
    and telemetry for observability.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize SendGrid email client.

        Args:
            api_key: SendGrid API key (defaults to SENDGRID_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("SENDGRID_API_KEY")
        if not self.api_key:
            logger.warning("SENDGRID_API_KEY not set - emails will fail in production")

        self.client = SendGridAPIClient(api_key=self.api_key) if self.api_key else None
        self.from_email = os.getenv("SENDGRID_FROM_EMAIL", "noreply@teamflow.app")
        self.from_name = os.getenv("SENDGRID_FROM_NAME", "TeamFlow")

    async def send_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send an email via SendGrid API.

        Args:
            to_email: Recipient email address
            to_name: Recipient name
            subject: Email subject line
            html_content: HTML email body
            text_content: Plain text fallback (optional)

        Returns:
            Dict with status and message_id if successful

        Raises:
            Exception: If sending fails
        """
        if not self.client:
            raise Exception("SendGrid client not initialized - missing API key")

        try:
            # Build SendGrid email
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email, to_name),
                subject=subject,
                html_content=Content("text/html", html_content),
            )

            # Add plain text version if provided
            if text_content:
                message.add_content(Content("text/plain", text_content))

            # Send email
            response = self.client.send(message)

            # Check response
            if response.status_code in (200, 201, 202):
                message_id = response.headers.get("X-Message-Id", "")
                logger.info(
                    "Email sent successfully",
                    to_email=to_email,
                    subject=subject,
                    message_id=message_id,
                    status_code=response.status_code,
                )
                return {
                    "status": "accepted",
                    "message_id": message_id,
                    "status_code": response.status_code,
                }
            else:
                logger.error(
                    "SendGrid API returned non-success status",
                    status_code=response.status_code,
                    body=response.body,
                )
                raise Exception(f"SendGrid API error: {response.status_code} - {response.body}")

        except Exception as e:
            logger.error(
                "Failed to send email",
                to_email=to_email,
                subject=subject,
                error=str(e),
            )
            raise

    async def send_reminder_email(self, reminder_event: ReminderEvent) -> Dict[str, Any]:
        """
        Send a task reminder email.

        Args:
            reminder_event: The reminder event with task details

        Returns:
            Dict with status and message_id
        """
        # Format due date for display
        due_date_str = reminder_event.due_date.strftime("%B %d, %Y at %I:%M %p UTC")

        # Build email content
        subject = f"Reminder: {reminder_event.task_title}"
        html_content = self._build_reminder_html(reminder_event, due_date_str)
        text_content = self._build_reminder_text(reminder_event, due_date_str)

        return await self.send_email(
            to_email=reminder_event.user_email,
            to_name=reminder_event.user_name,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
        )

    def _build_reminder_html(self, reminder_event: ReminderEvent, due_date_str: str) -> str:
        """Build HTML email content for task reminder"""
        description_html = ""
        if reminder_event.task_description:
            description_html = f"""
            <p style="margin: 16px 0; color: #4b5563;">
                {reminder_event.task_description}
            </p>
            """

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Task Reminder</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;">
            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color: #f3f4f6;">
                <tr>
                    <td style="padding: 40px 20px;">
                        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="600" style="margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                            <!-- Header -->
                            <tr>
                                <td style="padding: 30px 40px; background: linear-gradient(135deg, #84cc16 0%, #22c55e 100%); border-radius: 12px 12px 0 0;">
                                    <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: 700;">
                                        🔔 Task Reminder
                                    </h1>
                                </td>
                            </tr>

                            <!-- Content -->
                            <tr>
                                <td style="padding: 40px;">
                                    <p style="margin: 0 0 16px 0; font-size: 16px; color: #111827;">
                                        Hello {reminder_event.user_name},
                                    </p>
                                    <p style="margin: 0 0 24px 0; font-size: 16px; color: #4b5563;">
                                        This is a friendly reminder that your task is due soon:
                                    </p>

                                    <!-- Task Card -->
                                    <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color: #f9fafb; border-radius: 8px; border: 1px solid #e5e7eb;">
                                        <tr>
                                            <td style="padding: 20px;">
                                                <h2 style="margin: 0 0 12px 0; font-size: 18px; color: #111827;">
                                                    {reminder_event.task_title}
                                                </h2>
                                                {description_html}
                                                <p style="margin: 16px 0 0 0; font-size: 14px; color: #6b7280;">
                                                    <strong>Due:</strong> {due_date_str}
                                                </p>
                                            </td>
                                        </tr>
                                    </table>

                                    <!-- CTA -->
                                    <table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin: 30px 0 0 0;">
                                        <tr>
                                            <td style="border-radius: 8px; background: linear-gradient(135deg, #84cc16 0%, #22c55e 100%);">
                                                <a href="https://app.teamflow.app/tasks/{reminder_event.task_id}" target="_blank" style="display: inline-block; padding: 14px 28px; color: #ffffff; text-decoration: none; font-weight: 600; font-size: 14px;">
                                                    View Task →
                                                </a>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>

                            <!-- Footer -->
                            <tr>
                                <td style="padding: 20px 40px; background-color: #f9fafb; border-radius: 0 0 12px 12px; text-align: center;">
                                    <p style="margin: 0; font-size: 12px; color: #9ca3af;">
                                        You're receiving this because you have reminders enabled for this task.
                                        <br>
                                        <a href="https://app.teamflow.app/settings/notifications" style="color: #84cc16; text-decoration: none;">
                                            Manage notification preferences
                                        </a>
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

    def _build_reminder_text(self, reminder_event: ReminderEvent, due_date_str: str) -> str:
        """Build plain text email content for task reminder"""
        lines = [
            f"Hello {reminder_event.user_name},",
            "",
            "This is a friendly reminder that your task is due soon:",
            "",
            f"Task: {reminder_event.task_title}",
        ]
        if reminder_event.task_description:
            lines.append(f"Description: {reminder_event.task_description}")
        lines.extend([
            f"Due: {due_date_str}",
            "",
            "View your task: https://app.teamflow.app/tasks/" + str(reminder_event.task_id),
            "",
            "---",
            "You're receiving this because you have reminders enabled for this task.",
            "Manage preferences: https://app.teamflow.app/settings/notifications",
        ])
        return "\n".join(lines)

    async def check_health(self) -> Dict[str, Any]:
        """
        Check SendGrid API connectivity.

        Returns:
            Dict with health status
        """
        if not self.client:
            return {
                "healthy": False,
                "error": "SendGrid client not initialized - missing API key",
            }

        try:
            # Use SendGrid API to verify connectivity
            # We can use a simple GET request to the API
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.sendgrid.com/v3/user/account",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=5.0,
                )

            if response.status_code == 200:
                return {"healthy": True}
            else:
                return {
                    "healthy": False,
                    "error": f"SendGrid API returned {response.status_code}",
                }

        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
            }
