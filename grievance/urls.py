from django.urls import path
from . import views

# IMPORTANT: namespace for safety
app_name = 'grievance'

urlpatterns = [
    # =========================
    # PUBLIC / USER
    # =========================
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('post-login/', views.post_login_redirect, name='post_login_redirect'),
    path('submit/', views.submit_grievance, name='submit_grievance'),
    path('my-grievances/', views.my_grievances, name='my_grievances'),
    path('grievance/<int:grievance_id>/', views.grievance_detail, name='grievance_detail'),
    path('feedback/<int:grievance_id>/', views.submit_feedback, name='submit_feedback'),
    path('attachment/<int:grievance_id>/', views.upload_attachment, name='upload_attachment'),
    path('complete-profile/', views.complete_profile, name='complete_profile'),

    # =========================
    # API
    # =========================
    path('api/grievance-status/<int:grievance_id>/', views.grievance_status_api, name='grievance_status_api'),

    # =========================
    # OFFICER
    # =========================
    path('officer/dashboard/', views.officer_dashboard, name='officer_dashboard'),
    path('officer/update-status/<int:grievance_id>/', views.officer_update_status, name='officer_update_status'),

    # =========================
    # NOTIFICATIONS
    # =========================
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),

    # =========================
    # ANALYTICS / VISIBILITY
    # =========================
    path('public-dashboard/', views.public_dashboard, name='public_dashboard'),
]