"""Mail adapter — outbound only, used for vendor deviation notifications
(architecture doc Section 6.2). Fire-and-forget via FastAPI BackgroundTasks
at the call site, not here."""

import smtplib
from email.message import EmailMessage

from app.core.config import settings


async def send_deviation_email(to_address: str, dc_no: str, difference_qty: int) -> None:
    if not settings.smtp_host:
        # No SMTP configured yet (dev/local) — log instead of failing.
        print(f"[mail:mock] Would email {to_address} about DC {dc_no}, diff {difference_qty}")
        return

    message = EmailMessage()
    message["Subject"] = f"Deviation on DC {dc_no}"
    message["From"] = settings.smtp_username or "noreply@ppc-cbe.local"
    message["To"] = to_address
    message.set_content(
        f"DC {dc_no} has been reverted due to a quantity shortfall of {difference_qty}. "
        "Please review and resend a corrected delivery challan."
    )

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        if settings.smtp_username and settings.smtp_password:
            server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(message)
