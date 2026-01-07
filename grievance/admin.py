from django.contrib import admin
from .models import (
    Category,
    Officer,
    Grievance,
    GrievanceAssignment,
    GrievanceStatusHistory,
    Attachment,
    Feedback,
    Notification  # Added this
)

from .utils.assignment import reassign_grievances_from_officer

# =========================
# INLINES
# =========================
class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 1

class AssignmentInline(admin.TabularInline):
    model = GrievanceAssignment
    extra = 0
    readonly_fields = ('assigned_date',)

# =========================
# GRIEVANCE ADMIN
# =========================
@admin.register(Grievance)
class GrievanceAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'priority', 'status', 'created_at', 'is_overdue_flag')
    list_filter = ('status', 'priority', 'category', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('user', 'category')
    ordering = ('-created_at',)
    inlines = [AttachmentInline, AssignmentInline]

    def is_overdue_flag(self, obj):
        return obj.is_overdue
    is_overdue_flag.boolean = True
    is_overdue_flag.short_description = "Overdue?"

# =========================
# OFFICER ADMIN
# =========================
@admin.register(Officer)
class OfficerAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'designation', 'is_active')
    list_editable = ('is_active',) # Quickly toggle status
    list_filter = ('department', 'is_active')
    search_fields = ('user__username', 'department', 'designation')
    filter_horizontal = ('categories',)

    def save_model(self, request, obj, form, change):
        if change:
            previous = Officer.objects.filter(pk=obj.pk).first()
            if previous and previous.is_active and not obj.is_active:
                reassign_grievances_from_officer(obj)
        super().save_model(request, obj, form, change)

# =========================
# STATUS HISTORY & ASSIGNMENT
# =========================
@admin.register(GrievanceStatusHistory)
class GrievanceStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('grievance', 'old_status', 'new_status', 'changed_at', 'changed_by')
    list_filter = ('new_status', 'changed_at')
    readonly_fields = ('changed_at',)
    list_select_related = ('grievance', 'changed_by')

@admin.register(GrievanceAssignment)
class GrievanceAssignmentAdmin(admin.ModelAdmin):
    list_display = ('grievance', 'officer', 'assigned_by', 'assigned_date')
    list_filter = ('officer', 'assigned_date')
    list_select_related = ('grievance', 'officer', 'assigned_by')
    raw_id_fields = ('grievance',)

# =========================
# NOTIFICATION ADMIN
# =========================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')

# =========================
# OTHER MODELS
# =========================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('grievance', 'rating', 'submitted_at')
    list_select_related = ('grievance',)
    list_filter = ('rating',)

# Registering Attachment separately as well, though it's now an Inline too
@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('grievance', 'uploaded_at')
    list_select_related = ('grievance',)