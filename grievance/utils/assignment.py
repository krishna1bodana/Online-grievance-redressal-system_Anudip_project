from grievance.models import GrievanceAssignment, Officer

MAX_GRIEVANCES = 10
ACTIVE_STATUSES = ['Pending', 'In Progress']


def reassign_grievances_from_officer(inactive_officer):
    """
    Reassign all active grievances from an inactive officer
    to another eligible active officer in the same category.

    If no suitable officer is found, the grievance remains unassigned.
    """

    assignments = GrievanceAssignment.objects.filter(
        officer=inactive_officer,
        grievance__status__in=ACTIVE_STATUSES
    )

    for assignment in assignments:
        grievance = assignment.grievance

        # Safety check: grievance must have a category
        if not grievance.category:
            continue

        officers = Officer.objects.filter(
            categories=grievance.category,
            is_active=True
        ).exclude(id=inactive_officer.id)

        new_officer = None

        for officer in officers:
            active_count = GrievanceAssignment.objects.filter(
                officer=officer,
                grievance__status__in=ACTIVE_STATUSES
            ).count()

            if active_count < MAX_GRIEVANCES:
                new_officer = officer
                break

        if new_officer:
            assignment.officer = new_officer
            assignment.assigned_by = None  # system reassigned
            assignment.save()
        