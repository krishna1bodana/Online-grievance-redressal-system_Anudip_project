from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count, Avg, Q, F, ExpressionWrapper, DurationField
from django.utils import timezone
from datetime import timedelta
from .utils.duplicate_detector import find_duplicate_grievance

from .models import (
    Grievance,
    GrievanceAssignment,
    GrievanceStatusHistory,
    Officer,
    Notification
)

from .forms import (
    GrievanceForm,
    FeedbackForm,
    AttachmentForm,
    CustomSignupForm,
    CustomSignupForm
)

from .utils.scraper import analyze_grievance_text, fetch_related_news
from .utils.escalation import escalate_overdue_grievances


# ==================================================
# HOME
# ==================================================
def home(request):
    return render(request, 'grievance/home.html')


# ==================================================
# SIGNUP
# ==================================================
def signup(request):
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save()

            
            # OPTIONAL: Welcome email (safe)
            if user.email:
                send_mail(
                    subject='Welcome to the Grievance Portal',
                    message=(
                        f"Hello {user.username},\n\n"
                        "Thank you for signing up at our Grievance Management Portal. "
                        "You can now submit and track your grievances easily.\n\n"
                        "Best regards,\nGrievance Team"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            login(request, user)
            return redirect('grievance:post_login_redirect')
    else:
        form = CustomSignupForm()

    return render(request, 'registration/signup.html', {'form': form})


# ==================================================
# POST LOGIN REDIRECT
# ==================================================
@login_required
def post_login_redirect(request):
    if hasattr(request.user, 'officer_profile'):
        return redirect('grievance:officer_dashboard')
    return redirect('grievance:home')


# ==================================================
# SUBMIT GRIEVANCE
# ==================================================
@login_required
def submit_grievance(request):
    duplicate_warning = request.session.pop('duplicate_warning', None)
    if request.method == 'POST':
        form = GrievanceForm(request.POST)
        if form.is_valid():
            grievance = form.save(commit=False)
            grievance.user = request.user

            try:
                grievance.priority = analyze_grievance_text(grievance.description)
            except Exception:
                grievance.priority = 'Medium'
            duplicate = None
            if grievance.category:
                duplicate = find_duplicate_grievance(
                    grievance.description,
                    grievance.category
                )

            if duplicate:
                request.session['duplicate_warning'] = {
                    'title': duplicate.title,
                    'id': duplicate.id
                }

            grievance.save()

            # 🔔 Notify user (submission)
            Notification.objects.create(
                user=request.user,
                title="Grievance Submitted",
                message=f"Your grievance '{grievance.title}' has been submitted successfully.",
                grievance=grievance
            )

            # ---------- AUTO ASSIGNMENT ----------
            MAX_GRIEVANCES = 10
            assigned_officer = None

            if grievance.category:
                officers = Officer.objects.filter(
                    categories=grievance.category,
                    is_active=True
                )

                for officer in officers:
                    active_count = GrievanceAssignment.objects.filter(
                        officer=officer,
                        grievance__status__in=['Pending', 'In Progress']
                    ).count()

                    if active_count < MAX_GRIEVANCES:
                        assigned_officer = officer
                        break

            if assigned_officer:
                GrievanceAssignment.objects.create(
                    grievance=grievance,
                    officer=assigned_officer,
                    assigned_by=None
                )

                # 🔔 Notify officer
                Notification.objects.create(
                    user=assigned_officer.user,
                    title="New Grievance Assigned",
                    message=f"You have been assigned a new grievance: '{grievance.title}'.",
                    grievance=grievance
                )

            return redirect(
                'grievance:grievance_detail',
                grievance_id=grievance.id
            )

    else:
        form = GrievanceForm()

    return render(request, 'grievance/submit_grievance.html', {'form': form})


# ==================================================
# MY GRIEVANCES
# ==================================================
@login_required
def my_grievances(request):
    grievances = Grievance.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'grievance/my_grievances.html',
        {'grievances': grievances}
    )


# ==================================================
# GRIEVANCE DETAIL
# ==================================================
@login_required
def grievance_detail(request, grievance_id):
    if request.user.is_staff:
        grievance = get_object_or_404(Grievance, id=grievance_id)
    else:
        grievance = get_object_or_404(
            Grievance,
            id=grievance_id,
            user=request.user
        )

    history = GrievanceStatusHistory.objects.filter(
        grievance=grievance
    ).order_by('-changed_at')

    news_articles = []
    if grievance.category:
        news_articles = fetch_related_news(grievance.category.name)

    return render(request, 'grievance/grievance_detail.html', {
        'grievance': grievance,
        'history': history,
        'news_articles': news_articles
    })


# ==================================================
# FEEDBACK
# ==================================================
@login_required
def submit_feedback(request, grievance_id):
    grievance = get_object_or_404(
        Grievance,
        id=grievance_id,
        user=request.user
    )

    if grievance.status != 'Resolved' or hasattr(grievance, 'feedback'):
        return redirect(
            'grievance:grievance_detail',
            grievance_id=grievance.id
        )

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.grievance = grievance
            feedback.save()

            return redirect(
                'grievance:grievance_detail',
                grievance_id=grievance.id
            )
    else:
        form = FeedbackForm()

    return render(
        request,
        'grievance/submit_feedback.html',
        {'form': form, 'grievance': grievance}
    )


# ==================================================
# ATTACHMENT
# ==================================================
@login_required
def upload_attachment(request, grievance_id):
    grievance = get_object_or_404(
        Grievance,
        id=grievance_id,
        user=request.user
    )

    if request.method == 'POST':
        form = AttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.grievance = grievance
            attachment.save()

            return redirect(
                'grievance:grievance_detail',
                grievance_id=grievance.id
            )
    else:
        form = AttachmentForm()

    return render(
        request,
        'grievance/upload_attachment.html',
        {'form': form, 'grievance': grievance}
    )


# ==================================================
# AJAX STATUS API
# ==================================================
@login_required
def grievance_status_api(request, grievance_id):
    try:
        grievance = (
            Grievance.objects.get(id=grievance_id)
            if request.user.is_staff
            else Grievance.objects.get(id=grievance_id, user=request.user)
        )

        history = GrievanceStatusHistory.objects.filter(
            grievance=grievance
        ).values('old_status', 'new_status', 'changed_at')

        return JsonResponse({
            'status': grievance.status,
            'history': list(history)
        })

    except Grievance.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)


# ==================================================
# OFFICER DASHBOARD
# ==================================================
@staff_member_required
def officer_dashboard(request):
    # 🔥 Auto escalation check
    escalate_overdue_grievances()

    # Assignments for this officer
    assignments = GrievanceAssignment.objects.filter(
        officer__user=request.user
    ).select_related('grievance')

    # All grievances assigned to this officer
    grievances = Grievance.objects.filter(
        assignments__officer__user=request.user
    ).distinct()

    # =========================
    # ANALYTICS CALCULATIONS
    # =========================
    total_assigned = grievances.count()

    resolved_count = grievances.filter(status='Resolved').count()
    pending_count = grievances.filter(status='Pending').count()
    in_progress_count = grievances.filter(status='In Progress').count()
    overdue_count = grievances.filter(
        status__in=['Pending', 'In Progress'],
        due_date__lt=timezone.now()
    ).count()
    # Average resolution time (resolved only)
    avg_resolution = grievances.filter(
        status='Resolved'
    ).annotate(
        resolution_time=ExpressionWrapper(
            F('updated_at') - F('created_at'),
            output_field=DurationField()
        )
    ).aggregate(avg=Avg('resolution_time'))['avg']

    # Resolution rate %
    resolution_rate = (
        round((resolved_count / total_assigned) * 100, 2)
        if total_assigned else 0
    )

    return render(
        request,
        'officer/dashboard.html',
        {
            'assignments': assignments,

            # KPIs
            'total_assigned': total_assigned,
            'resolved_count': resolved_count,
            'pending_count': pending_count,
            'in_progress_count': in_progress_count,
            'overdue_count': overdue_count,
            'avg_resolution': avg_resolution,
            'resolution_rate': resolution_rate,
        }
    )


# ==================================================
# OFFICER UPDATE STATUS
# ==================================================
@staff_member_required
def officer_update_status(request, grievance_id):
    assignment = get_object_or_404(
        GrievanceAssignment,
        grievance_id=grievance_id,
        officer__user=request.user
    )

    grievance = assignment.grievance

    if request.method == 'POST':
        new_status = request.POST.get('status')
        new_priority = request.POST.get('priority')
        remark = request.POST.get('remark')

        if new_status and new_status != grievance.status:
            old_status = grievance.status

            GrievanceStatusHistory.objects.create(
                grievance=grievance,
                old_status=old_status,
                new_status=new_status,
                changed_by=request.user
            )

            grievance.status = new_status

            # 🔔 Notify user
            Notification.objects.create(
                user=grievance.user,
                title="Grievance Status Updated",
                message=f"Status of '{grievance.title}' changed to {new_status}.",
                grievance=grievance
            )

            # 📧 EMAIL ON RESOLUTION
            if new_status == 'Resolved' and grievance.user.email:
                send_mail(
                    subject='Your grievance has been resolved',
                    message=(
                        f"Hello {grievance.user.username},\n\n"
                        f"Your grievance '{grievance.title}' has been resolved.\n\n"
                        f"Officer remarks:\n{remark or 'No remarks provided.'}"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[grievance.user.email],
                    fail_silently=True,
                )

        if new_priority:
            grievance.priority = new_priority

        if remark:
            grievance.officer_remark = remark

        grievance.save()

        return redirect('grievance:officer_dashboard')

    return render(request, 'officer/update_status.html', {
        'grievance': grievance,
        'status_choices': Grievance.STATUS_CHOICES,
        'priority_choices': Grievance.PRIORITY_CHOICES
    })


# ==================================================
# NOTIFICATIONS
# ==================================================
@login_required
def notification_list(request):
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'grievance/notifications.html',
        {'notifications': notifications}
    )


@login_required
def mark_notification_read(request, notification_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    notification = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user
    )

    notification.is_read = True
    notification.save(update_fields=['is_read'])

    unread_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    return JsonResponse({
        'success': True,
        'unread_count': unread_count
    })
    return f"Notification for {self.user.username} - {self.title}"

def public_dashboard(request):
    """
    Public transparency dashboard (anonymous, read-only)
    """

    total = Grievance.objects.count()
    resolved = Grievance.objects.filter(status='Resolved').count()
    pending = total - resolved
    overdue = Grievance.objects.filter(is_overdue=True).count()

    resolution_rate = round((resolved / total) * 100, 2) if total else 0

    # Category-wise stats
    category_stats = (
        Grievance.objects
        .values('category__name')
        .annotate(
            total=Count('id'),
            resolved=Count('id', filter=Q(status='Resolved'))
        )
        .order_by('-total')
    )

    # Monthly stats
    now = timezone.now()
    month_start = now.replace(day=1)

    monthly_filed = Grievance.objects.filter(
        created_at__gte=month_start
    ).count()

    monthly_resolved = Grievance.objects.filter(
        status='Resolved',
        updated_at__gte=month_start
    ).count()

    return render(request, 'grievance/public_dashboard.html', {
        'total': total,
        'resolved': resolved,
        'pending': pending,
        'overdue': overdue,
        'resolution_rate': resolution_rate,
        'category_stats': category_stats,
        'monthly_filed': monthly_filed,
        'monthly_resolved': monthly_resolved,
    })
@login_required
def complete_profile(request):
    if request.user.email:
        return redirect('grievance:home')

    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            request.user.email = email
            request.user.save(update_fields=['email'])
            return redirect('grievance:home')

    return render(request, 'registration/complete_profile.html')
    