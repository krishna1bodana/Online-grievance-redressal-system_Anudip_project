from django.contrib import admin
from .models import (
    Category,
    Officer,
    Grievance,
    GrievanceAssignment,
    GrievanceStatusHistory,
    Attachment,
    Feedback
)

from .utils.assignment import reassign_grievances_from_officer


# =========================
# GRIEVANCE ADMIN
# =========================
@admin.register(Grievance)
class GrievanceAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'priority', 'status', 'created_at')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('user', 'category')
    ordering = ('-created_at',)


# =========================
# STATUS HISTORY ADMIN
# =========================
@admin.register(GrievanceStatusHistory)
class GrievanceStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('grievance', 'old_status', 'new_status', 'changed_at')
    list_filter = ('new_status',)
    readonly_fields = ('changed_at',)
    list_select_related = ('grievance',)


# =========================
# ASSIGNMENT ADMIN
# =========================
@admin.register(GrievanceAssignment)
class GrievanceAssignmentAdmin(admin.ModelAdmin):
    list_display = ('grievance', 'officer', 'assigned_by', 'assigned_date')
    list_filter = ('officer',)
    list_select_related = ('grievance', 'officer')
    raw_id_fields = ('grievance',)


# =========================
# CATEGORY ADMIN
# =========================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# =========================
# OFFICER ADMIN
# =========================
@admin.register(Officer)
class OfficerAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'designation', 'is_active')
    list_filter = ('department', 'is_active')
    search_fields = ('user__username', 'department', 'designation')
    filter_horizontal = ('categories',)

    def save_model(self, request, obj, form, change):
        """
        Automatically reassign grievances if officer becomes inactive.
        """
        if change:
            previous = Officer.objects.filter(pk=obj.pk).first()
            if previous and previous.is_active and not obj.is_active:
                reassign_grievances_from_officer(obj)

        super().save_model(request, obj, form, change)


# =========================
# ATTACHMENT ADMIN
# =========================
@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('grievance', 'uploaded_at')
    list_select_related = ('grievance',)


# =========================
# FEEDBACK ADMIN
# =========================
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('grievance', 'rating', 'submitted_at')
    list_select_related = ('grievance',)
    list_filter = ('rating',)
# =========================