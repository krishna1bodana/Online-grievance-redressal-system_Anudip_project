from .models import Notification


def notification_context(request):
    """
    Makes notifications available globally in templates.
    """

    if not request.user.is_authenticated:
        return {
            'notifications': [],
            'unread_notifications_count': 0
        }

    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]

    unread_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    return {
        'notifications': notifications,
        'unread_notifications_count': unread_count
    }
from .models import Notification

def notifications_context(request):
    if request.user.is_authenticated:
        return {
            'unread_notifications_count': Notification.objects.filter(
                user=request.user,
                is_read=False
            ).count()
        }
    return {
        'unread_notifications_count': 0
    }
from .models import Notification