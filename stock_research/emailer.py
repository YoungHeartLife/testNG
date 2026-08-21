"""Email delivery for generated reports."""

from __future__ import annotations

import smtplib
from email.message import EmailMessage

from .config import Settings


def send_report(settings: Settings, subject: str, markdown: str, html: str) -> None:
    if not settings.email_enabled:
        return
    missing = [name for name, value in {
        "EMAIL_TO": settings.email_to,
        "EMAIL_FROM": settings.email_from,
        "SMTP_HOST": settings.smtp_host,
        "SMTP_USERNAME": settings.smtp_username,
        "SMTP_PASSWORD": settings.smtp_password,
    }.items() if not value]
    if missing:
        raise RuntimeError(f"Email enabled but missing settings: {', '.join(missing)}")
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.email_from
    message["To"] = settings.email_to
    message.set_content(markdown)
    message.add_alternative(html, subtype="html")
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30) as smtp:
        smtp.starttls()
        smtp.login(settings.smtp_username, settings.smtp_password)
        smtp.send_message(message)
