"""
CVBoost AI — Contact Form API
POST /contact — validates, stores, optionally sends email
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.limits import limiter, CONTACT_LIMIT
from app.core.logging import get_logger
from app.core.security import check_honeypot, sanitize_text
from app.models.database import get_db
from app.models.db import ContactMessageRecord
from app.schemas.cv import ContactMessage

router = APIRouter(prefix="/contact", tags=["contact"])
logger = get_logger(__name__)


@router.post("/", summary="Submit contact form message")
@limiter.limit(CONTACT_LIMIT)
async def submit_contact(
    request: Request,
    body: ContactMessage,
    db: AsyncSession = Depends(get_db),
) -> dict:
    # Spam protection
    check_honeypot(body.honeypot)

    # Sanitize inputs
    name = sanitize_text(body.name)
    message = sanitize_text(body.message)
    ip = request.client.host if request.client else ""

    # Persist
    record = ContactMessageRecord(
        name=name,
        email=str(body.email),
        message=message,
        ip_address=ip,
    )
    db.add(record)
    await db.flush()

    # Try to send email (non-blocking, failures don't affect response)
    try:
        await _send_contact_email(name, str(body.email), message)
        record.emailed = True
    except Exception as exc:
        logger.warning("contact_email_failed", error=str(exc))

    logger.info("contact_message_received", message_id=record.id, ip=ip)
    return {"message": "Thank you! Your message has been received."}


async def _send_contact_email(name: str, email: str, message: str) -> None:
    from app.core.config import get_settings
    settings = get_settings()
    if not settings.smtp_user or not settings.smtp_pass:
        return

    import aiosmtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    msg = MIMEMultipart()
    msg["From"] = settings.smtp_from
    msg["To"] = settings.contact_recipient
    msg["Subject"] = f"CVBoost AI Contact: {name}"
    body_text = f"From: {name} <{email}>\n\n{message}"
    msg.attach(MIMEText(body_text, "plain"))

    await aiosmtplib.send(
        msg,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_user,
        password=settings.smtp_pass,
        start_tls=True,
        timeout=10,
    )
