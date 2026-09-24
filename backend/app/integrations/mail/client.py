"""Mail adapter — outbound only, used for vendor deviation notifications
(architecture doc Section 6.2) and M1 password-reset emails. Fire-and-forget
via FastAPI BackgroundTasks at the call site, not here."""

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


async def send_password_reset_email(to_address: str, reset_link: str) -> None:
    if not settings.smtp_host:
        # No SMTP configured yet (dev/local) — log instead of failing, same
        # as send_deviation_email above. This is how reset links show up
        # when testing locally without SMTP set up.
        print(f"[mail:mock] Password reset link for {to_address}: {reset_link}")
        return

    message = EmailMessage()
    message["Subject"] = "Reset your PPC CBE Tracking Application password"
    message["From"] = settings.smtp_username or "noreply@ppc-cbe.local"
    message["To"] = to_address
    message.set_content(
        "We received a request to reset your password.\n\n"
        f"Reset it here: {reset_link}\n\n"
        "This link expires in 60 minutes. If you didn't request this, you can ignore this email."
    )

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        if settings.smtp_username and settings.smtp_password:
            server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(message)
