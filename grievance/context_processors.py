from .models import Notification

def notification_context(request):
    """
    Injects notifications into the context of all templates.
    Usage: {{ unread_notifications_count }} and {% for n in notifications %}
    """
    # Check if user is logged in
    if not request.user.is_authenticated:
        return {
            'notifications': [],
            'unread_notifications_count': 0
        }

    # Get the latest 5 notifications for the dropdown
    notifications = Notification.objects.filter(
        user=request.user
    ).select_related('grievance').order_by('-created_at')[:5]

    # Get the unread count for the badge icon
    unread_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    return {
        'notifications': notifications,
        'unread_notifications_count': unread_count
    }