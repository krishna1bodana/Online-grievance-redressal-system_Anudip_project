from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from grievance.models import Grievance, Notification


LEVEL_1_HOURS = 0        # immediately after due_date
LEVEL_2_HOURS = 48       # 48 hours after due_date


def escalate_overdue_grievances():
    """
    Escalate overdue grievances with level-based emails & notifications.
    Runs safely multiple times without spamming.
    """

    now = timezone.now()
    escalated = []

    overdue_grievances = Grievance.objects.filter(
        status__in=['Pending', 'In Progress'],
        due_date__lt=now
    )

    for grievance in overdue_grievances:
        hours_overdue = (now - grievance.due_date).total_seconds() / 3600

        # -------------------------
        # LEVEL 1 ESCALATION
        # -------------------------
        if grievance.escalation_level < 1 and hours_overdue >= LEVEL_1_HOURS:
            _send_admin_escalation(
                grievance,
                level=1,
                subject="🚨 Grievance Overdue (Level 1)"
            )

            grievance.escalation_level = 1
            grievance.last_escalated_at = now
            grievance.save(update_fields=['escalation_level', 'last_escalated_at'])
            escalated.append(grievance)

        # -------------------------
        # LEVEL 2 ESCALATION
        # -------------------------
        elif grievance.escalation_level < 2 and hours_overdue >= LEVEL_2_HOURS:
            _send_admin_escalation(
                grievance,
                level=2,
                subject="🔥 CRITICAL: Grievance Escalation (Level 2)"
            )

            grievance.escalation_level = 2
            grievance.last_escalated_at = now
            grievance.save(update_fields=['escalation_level', 'last_escalated_at'])
            escalated.append(grievance)

    return escalated


def _send_admin_escalation(grievance, level, subject):
    """
    Internal helper: email + notification to admin
    """

    message = (
        f"Grievance Escalation Level {level}\n\n"
        f"Title: {grievance.title}\n"
        f"User: {grievance.user.username}\n"
        f"Category: {grievance.category}\n"
        f"Status: {grievance.status}\n"
        f"Due Date: {grievance.due_date}\n\n"
        f"Please take immediate action."
    )

    # 📧 Email admin
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.ADMIN_EMAIL],
        fail_silently=True,
    )

    # 🔔 In-app admin notification
    Notification.objects.create(
        user=settings.ADMIN_USER,
        title=f"Escalation Level {level}",
        message=f"Grievance '{grievance.title}' has crossed SLA.",
        grievance=grievance
    )
