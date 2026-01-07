from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from grievance.models import Grievance, Notification

LEVEL_1_HOURS = 0         # Immediately after due_date
LEVEL_2_HOURS = 48        # 48 hours after due_date

def escalate_overdue_grievances():
    """
    Escalate overdue grievances with level-based emails & notifications.
    """
    now = timezone.now()
    escalated = []

    # select_related avoids the "N+1" query problem when accessing user/category names
    overdue_grievances = Grievance.objects.filter(
        status__in=['Pending', 'In Progress'],
        due_date__lt=now
    ).select_related('user', 'category')

    # Get a list of actual Admin User objects to send notifications to
    admin_users = User.objects.filter(is_superuser=True)

    for grievance in overdue_grievances:
        hours_overdue = (now - grievance.due_date).total_seconds() / 3600

        # LEVEL 1 ESCALATION
        if grievance.escalation_level < 1 and hours_overdue >= LEVEL_1_HOURS:
            _handle_escalation(grievance, level=1, subject="🚨 Grievance Overdue (Level 1)", admin_users=admin_users)
            grievance.escalation_level = 1
            grievance.last_escalated_at = now
            grievance.save(update_fields=['escalation_level', 'last_escalated_at'])
            escalated.append(grievance)

        # LEVEL 2 ESCALATION
        elif grievance.escalation_level < 2 and hours_overdue >= LEVEL_2_HOURS:
            _handle_escalation(grievance, level=2, subject="🔥 CRITICAL: Grievance Escalation (Level 2)", admin_users=admin_users)
            grievance.escalation_level = 2
            grievance.last_escalated_at = now
            grievance.save(update_fields=['escalation_level', 'last_escalated_at'])
            escalated.append(grievance)

    return escalated


def _handle_escalation(grievance, level, subject, admin_users):
    """
    Helper to notify all superusers via email and in-app notifications.
    """
    message = (
        f"Grievance Escalation Level {level}\n\n"
        f"Title: {grievance.title}\n"
        f"User: {grievance.user.username}\n"
        f"Category: {grievance.category.name if grievance.category else 'N/A'}\n"
        f"Due Date: {grievance.due_date}\n\n"
        f"Please take immediate action."
    )

    # 1. 📧 Email Admins
    # We pull emails from all superusers or a designated setting
    recipient_list = [u.email for u in admin_users if u.email]
    if hasattr(settings, 'ADMIN_EMAIL'):
        recipient_list.append(settings.ADMIN_EMAIL)

    if recipient_list:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=list(set(recipient_list)), # Ensure unique emails
            fail_silently=True,
        )

    # 2. 🔔 In-app notification for every admin
    for admin in admin_users:
        Notification.objects.create(
            user=admin,
            title=f"Escalation Level {level}",
            message=f"Grievance '{grievance.title}' is overdue and needs attention.",
            grievance=grievance
        )