from django.db.models import Count, Q
from grievance.models import GrievanceAssignment, Officer, Notification

MAX_GRIEVANCES = 10
ACTIVE_STATUSES = ['Pending', 'In Progress']

def reassign_grievances_from_officer(inactive_officer):
    """
    Reassign all active grievances from an inactive officer
    to another eligible active officer in the same category.
    """

    # 1. Fetch all assignments that need moving
    assignments = GrievanceAssignment.objects.filter(
        officer=inactive_officer,
        grievance__status__in=ACTIVE_STATUSES
    ).select_related('grievance', 'grievance__category')

    for assignment in assignments:
        grievance = assignment.grievance

        if not grievance.category:
            continue

        # 2. Optimized search for a new officer
        # We find officers in the same category, who are active, 
        # and annotate them with their current workload count.
        new_officer = Officer.objects.filter(
            categories=grievance.category,
            is_active=True
        ).exclude(
            id=inactive_officer.id
        ).annotate(
            current_workload=Count(
                'assigned_grievances', 
                filter=Q(assigned_grievances__grievance__status__in=ACTIVE_STATUSES)
            )
        ).filter(
            current_workload__lt=MAX_GRIEVANCES
        ).order_by('current_workload').first() # Get the person with the least work

        if new_officer:
            old_officer_name = inactive_officer.user.username
            assignment.officer = new_officer
            assignment.assigned_by = None  # System reassigned
            assignment.save()

            # 3. 🔔 Notify the NEW Officer
            Notification.objects.create(
                user=new_officer.user,
                title="Grievance Reassigned to You",
                message=f"Grievance '{grievance.title}' has been moved to you from {old_officer_name}.",
                grievance=grievance
            )

            # 4. 🔔 Notify the User (Transparency)
            Notification.objects.create(
                user=grievance.user,
                title="Officer Updated",
                message=f"Your grievance '{grievance.title}' has been reassigned to a new officer for faster processing.",
                grievance=grievance
            )