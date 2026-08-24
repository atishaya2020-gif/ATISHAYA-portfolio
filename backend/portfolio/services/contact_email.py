import logging
from django.conf import settings
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)


def send_contact_notification_email(contact_message) -> bool:
    recipient = getattr(settings, 'CONTACT_NOTIFICATION_EMAIL', '') or getattr(
        settings, 'DEFAULT_FROM_EMAIL', ''
    ) or 'webmaster@localhost'

    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', '') or 'webmaster@localhost'

    subject_text = f"Portfolio Contact: {contact_message.subject}" if contact_message.subject else "Portfolio Contact Message"

    body = (
        f"New contact message received:\n\n"
        f"Sender Name: {contact_message.name}\n"
        f"Sender Email: {contact_message.email}\n"
        f"Subject: {contact_message.subject or 'N/A'}\n"
        f"Submitted At: {contact_message.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
        f"Message:\n{contact_message.message}\n"
    )

    email = EmailMessage(
        subject=subject_text,
        body=body,
        from_email=from_email,
        to=[recipient],
        reply_to=[contact_message.email],
    )

    try:
        email.send(fail_silently=False)
        return True
    except Exception as e:
        logger.error(
            "Failed to send contact notification email for message ID %s: %s",
            contact_message.id,
            type(e).__name__,
        )
        return False
