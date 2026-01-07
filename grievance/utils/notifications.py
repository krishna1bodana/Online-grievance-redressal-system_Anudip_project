import logging
from grievance.models import Notification

# Setup logging to track if notifications fail
logger = logging.getLogger(__name__)

def create_notification(user, title, message, grievance=None, **kwargs):
    """
    Central notification creator. 
    Handles logic for creating in-app notifications safely.
    """
    if user is None:
        logger.warning(f"Attempted to create notification '{title}' for a None user.")
        return None

    try:
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            grievance=grievance
        )
        return notification
    except Exception as e:
        logger.error(f"Failed to create notification for {user.username}: {e}")
        return None