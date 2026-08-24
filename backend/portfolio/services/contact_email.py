import logging
from django.conf import settings
import resend

logger = logging.getLogger(__name__)


def send_contact_notification_email(contact_message) -> bool:
    api_key = getattr(settings, 'RESEND_API_KEY', '')
    if not api_key:
        logger.error(
            "RESEND_API_KEY is not configured; skipped sending notification email for message ID %s.",
            contact_message.id,
        )
        return False

    recipient = getattr(settings, 'CONTACT_NOTIFICATION_EMAIL', '')
    if not recipient:
        logger.error(
            "CONTACT_NOTIFICATION_EMAIL is not configured; skipped sending notification email for message ID %s.",
            contact_message.id,
        )
        return False

    resend.api_key = api_key

    from_email = "onboarding@resend.dev"

    subject_text = (
        f"Portfolio Contact: {contact_message.subject}"
        if contact_message.subject
        else "Portfolio Contact Message"
    )

    body = (
        f"New contact message received:\n\n"
        f"Sender Name: {contact_message.name}\n"
        f"Sender Email: {contact_message.email}\n"
        f"Subject: {contact_message.subject or 'N/A'}\n"
        f"Submitted At: {contact_message.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
        f"Message:\n{contact_message.message}\n"
    )

    params: resend.Emails.SendParams = {
        "from": from_email,
        "to": [recipient],
        "subject": subject_text,
        "text": body,
        "reply_to": contact_message.email,
    }

    try:
        resend.Emails.send(params)
        return True
    except Exception as e:
        logger.error(
            "Failed to send contact notification email for message ID %s: %s",
            contact_message.id,
            type(e).__name__,
        )
        return False
