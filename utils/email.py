from email.message import EmailMessage

import aiosmtplib
from fastapi.templating import Jinja2Templates

from config import settings

templates = Jinja2Templates(directory="templates")


async def send_email(
    to_email: str, subject: str, plain_text: str, html_content: str | None = None
) -> None:
    message = EmailMessage()
    message["From"] = settings.mail_from
    message["To"] = to_email
    message["Subject"] = subject

    message.set_content(plain_text)
    if html_content:
        message.add_alternative(html_content, subtype="html")

    await aiosmtplib.send(
        message,
        hostname=settings.mail_server,
        port=settings.mail_port,
        username=settings.mail_username if settings.mail_username else None,
        password=settings.mail_password.get_secret_value()
        if settings.mail_password
        else None,
        start_tls=settings.mail_use_tls,
    )


async def send_password_reset_email(to_email: str, username: str, token: str) -> None:
    reset_url = f"{settings.frontend_url}/reset-password?token={token}"

    template = templates.env.get_template("password_reset.html")
    html_content = template.render(reset_url=reset_url, username=username)

    plain_text = f"""Hi {username},

You requested to reset your password. Click the link below to set a new password:

{reset_url}

This link will expire in 1 hour.

If you didn't request this, you can safely ignore this email.

Best regards,
The FastAPI Blog Team
"""

    await send_email(
        to_email=to_email,
        subject="Reset Your Password - FastAPI Blog",
        plain_text=plain_text,
        html_content=html_content,
    )


async def send_task_assignment_email(
    to_email: str,
    assignee_name: str,
    assigned_by_name: str,
    task_title: str,
    task_description: str | None,
    project_name: str,
    priority: str,
    status: str,
    task_url: str,
) -> None:
    template = templates.env.get_template("task_assigned.html")
    html_content = template.render(
        assignee_name=assignee_name,
        assigned_by_name=assigned_by_name,
        task_title=task_title,
        task_description=task_description,
        project_name=project_name,
        priority=priority,
        status=status.replace("_", " ").title(),
        task_url=task_url,
    )

    plain_text = f"""Hello {assignee_name},

{assigned_by_name} has assigned you a task in {project_name}:

{task_title}
Priority: {priority} | Status: {status.replace('_', ' ').title()}

View it here: {task_url}
"""

    await send_email(
        to_email=to_email,
        subject=f"Task assigned: {task_title}",
        plain_text=plain_text,
        html_content=html_content,
    )


async def send_invite_email(
    to_email: str,
    token: str,
    role: str,
    workspace_title: str,
    invited_by_username: str,
) -> None:
    invite_link = f"{settings.frontend_url}/invite/{token}"

    template = templates.env.get_template("invite_email.html")
    html_content = template.render(
        invite_link=invite_link,
        workspace_title=workspace_title,
        invited_by_username=invited_by_username,
        role=role,
    )

    plain_text = f"""Hi,

{invited_by_username} has invited you to join the workspace {workspace_title} as a {role}.

Click the link below to accept:
{invite_link}

This invitation expires in 48 hours.

If you weren't expecting this invitation, you can safely ignore this email.
"""

    await send_email(
        to_email=to_email,
        subject=f"You're invited to join {workspace_title}",
        plain_text=plain_text,
        html_content=html_content,
    )
