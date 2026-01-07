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

# Internal Imports
from .models import (
    Grievance,
    GrievanceAssignment,
    GrievanceStatusHistory,
    Officer,
    Notification,
    Feedback,
    Attachment
)
from .forms import (
    GrievanceForm,
    FeedbackForm,
    AttachmentForm,
    CustomSignupForm
)

# Utility Imports
from .utils.duplicate_detector import find_duplicate_grievance
from .utils.scraper import analyze_grievance_text, fetch_related_news
from .utils.escalation import escalate_overdue_grievances

# ==================================================
# HOME & AUTH
# ==================================================
def home(request):
    return render(request, 'grievance/home.html')

def signup(request):
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.email:
                send_mail(
                    subject='Welcome to the Grievance Portal',
                    message=f"Hello {user.username},\n\nThank you for signing up. You can now track grievances easily.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            login(request, user)
            return redirect('grievance:post_login_redirect')
    else:
        form = CustomSignupForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def post_login_redirect(request):
    if hasattr(request.user, 'officer_profile'):
        return redirect('grievance:officer_dashboard')
    return redirect('grievance:home')

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

# ==================================================
# GRIEVANCE MANAGEMENT
# ==================================================
@login_required
def submit_grievance(request):
    duplicate_warning = request.session.pop('duplicate_warning', None)
    
    if request.method == 'POST':
        form = GrievanceForm(request.POST)
        if form.is_valid():
            grievance = form.save(commit=False)
            grievance.user = request.user

            # AI Analysis & Duplicate Check
            try:
                grievance.priority = analyze_grievance_text(grievance.description)
            except:
                grievance.priority = 'Medium'
            
            if grievance.category:
                duplicate = find_duplicate_grievance(grievance.description, grievance.category)
                if duplicate:
                    request.session['duplicate_warning'] = {'title': duplicate.title, 'id': duplicate.id}

            grievance.save()

            # Auto Assignment Logic
            MAX_GRIEVANCES = 10
            assigned_officer = None
            if grievance.category:
                officers = Officer.objects.filter(categories=grievance.category, is_active=True)
                for officer in officers:
                    active_count = GrievanceAssignment.objects.filter(
                        officer=officer, 
                        grievance__status__in=['Pending', 'In Progress']
                    ).count()
                    if active_count < MAX_GRIEVANCES:
                        assigned_officer = officer
                        break

            if assigned_officer:
                GrievanceAssignment.objects.create(grievance=grievance, officer=assigned_officer)
                Notification.objects.create(
                    user=assigned_officer.user,
                    title="New Grievance Assigned",
                    message=f"New grievance assigned: {grievance.title}",
                    grievance=grievance
                )

            return redirect('grievance:grievance_detail', grievance_id=grievance.id)
    else:
        form = GrievanceForm()

    return render(request, 'grievance/submit_grievance.html', {
        'form': form, 
        'duplicate_warning': duplicate_warning
    })

@login_required
def my_grievances(request):
    grievances = Grievance.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'grievance/my_grievances.html', {'grievances': grievances})

@login_required
def grievance_detail(request, grievance_id):
    query_params = {'id': grievance_id} if request.user.is_staff else {'id': grievance_id, 'user': request.user}
    grievance = get_object_or_404(Grievance, **query_params)
    
    history = grievance.status_history.all().order_by('-changed_at')
    news = fetch_related_news(grievance.category.name) if grievance.category else []

    return render(request, 'grievance/grievance_detail.html', {
        'grievance': grievance,
        'history': history,
        'news_articles': news
    })

# ==================================================
# OFFICER ACTIONS
# ==================================================
@staff_member_required
def officer_dashboard(request):
    escalate_overdue_grievances()
    
    grievances = Grievance.objects.filter(assignments__officer__user=request.user).distinct()
    
    total = grievances.count()
    resolved = grievances.filter(status='Resolved').count()
    pending = grievances.filter(status='Pending').count()
    in_progress = grievances.filter(status='In Progress').count()
    overdue = grievances.filter(status__in=['Pending', 'In Progress'], due_date__lt=timezone.now()).count()
    
    avg_resolution = grievances.filter(status='Resolved').annotate(
        duration=ExpressionWrapper(F('updated_at') - F('created_at'), output_field=DurationField())
    ).aggregate(avg=Avg('duration'))['avg']

    return render(request, 'officer/dashboard.html', {
        'grievances': grievances,
        'total_assigned': total,
        'resolved_count': resolved,
        'pending_count': pending,
        'in_progress_count': in_progress,
        'overdue_count': overdue,
        'avg_resolution': avg_resolution,
        'resolution_rate': round((resolved / total) * 100, 2) if total else 0
    })

@staff_member_required
def officer_update_status(request, grievance_id):
    assignment = get_object_or_404(GrievanceAssignment, grievance_id=grievance_id, officer__user=request.user)
    grievance = assignment.grievance

    if request.method == 'POST':
        new_status = request.POST.get('status')
        new_priority = request.POST.get('priority')
        remark = request.POST.get('remark')

        if new_status and new_status != grievance.status:
            GrievanceStatusHistory.objects.create(
                grievance=grievance, old_status=grievance.status, 
                new_status=new_status, changed_by=request.user
            )
            grievance.status = new_status
            
            Notification.objects.create(
                user=grievance.user, title="Status Updated",
                message=f"Grievance '{grievance.title}' is now {new_status}.",
                grievance=grievance
            )

        if new_priority: grievance.priority = new_priority
        if remark: grievance.officer_remark = remark
        
        grievance.save()
        return redirect('grievance:officer_dashboard')

    return render(request, 'officer/update_status.html', {
        'grievance': grievance,
        'status_choices': Grievance.STATUS_CHOICES,
        'priority_choices': Grievance.PRIORITY_CHOICES
    })

# ==================================================
# FEEDBACK & ATTACHMENTS
# ==================================================
@login_required
def submit_feedback(request, grievance_id):
    grievance = get_object_or_404(Grievance, id=grievance_id, user=request.user)
    if grievance.status != 'Resolved' or hasattr(grievance, 'feedback'):
        return redirect('grievance:grievance_detail', grievance_id=grievance.id)

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.grievance = grievance
            feedback.save()
            return redirect('grievance:grievance_detail', grievance_id=grievance.id)
    return render(request, 'grievance/submit_feedback.html', {'form': FeedbackForm(), 'grievance': grievance})

@login_required
def upload_attachment(request, grievance_id):
    grievance = get_object_or_404(Grievance, id=grievance_id, user=request.user)
    if request.method == 'POST':
        form = AttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.grievance = grievance
            attachment.save()
            return redirect('grievance:grievance_detail', grievance_id=grievance.id)
    return render(request, 'grievance/upload_attachment.html', {'form': AttachmentForm(), 'grievance': grievance})

# ==================================================
# NOTIFICATIONS & API
# ==================================================
@login_required
def notification_list(request):
    notifications = request.user.notifications.all().order_by('-created_at')
    return render(request, 'grievance/notifications.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save(update_fields=['is_read'])
    unread_count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'success': True, 'unread_count': unread_count})

@login_required
def grievance_status_api(request, grievance_id):
    try:
        query_params = {'id': grievance_id} if request.user.is_staff else {'id': grievance_id, 'user': request.user}
        grievance = Grievance.objects.get(**query_params)
        history = grievance.status_history.all().values('old_status', 'new_status', 'changed_at')
        return JsonResponse({'status': grievance.status, 'history': list(history)})
    except Grievance.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

def public_dashboard(request):
    """
    Public transparency dashboard (anonymous, read-only).
    Optimized to prevent template errors.
    """
    now = timezone.now()
    
    # Global Stats
    total = Grievance.objects.count()
    resolved = Grievance.objects.filter(status='Resolved').count()
    pending = total - resolved
    
    # Querying overdue status directly from the database
    overdue = Grievance.objects.filter(
        status__in=['Pending', 'In Progress'],
        due_date__lt=now
    ).count()

    resolution_rate = round((resolved / total) * 100, 2) if total else 0

    # Category-wise stats: Using explicit aliases to match template variables
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
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

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
