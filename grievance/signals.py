from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Grievance, GrievanceStatusHistory

@receiver(pre_save, sender=Grievance)
def log_status_change(sender, instance, **kwargs):
    # If this is a new object, there is no "previous" status
    if not instance.pk:
        return

    try:
        previous = Grievance.objects.get(pk=instance.pk)
        if previous.status != instance.status:
            GrievanceStatusHistory.objects.create(
                grievance=instance,
                old_status=previous.status,
                new_status=instance.status,
                changed_by=None # Note: Request user isn't directly available in signals
            )
    except Grievance.DoesNotExist:
        pass