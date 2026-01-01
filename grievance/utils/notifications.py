from grievance.models import Notification

def create_notification(user, title, message, grievance=None):
    """
    Central notification creator.
    Keeps logic clean and reusable.
    """
    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        grievance=grievance
    )
