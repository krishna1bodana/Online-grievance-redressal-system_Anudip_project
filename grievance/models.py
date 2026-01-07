from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta

# =========================
# CATEGORY
# =========================
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


# =========================
# OFFICER
# =========================
class Officer(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='officer_profile'
    )

    categories = models.ManyToManyField(
        Category,
        related_name='officers',
        blank=True
    )

    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} ({self.department})"


# =========================
# GRIEVANCE
# =========================
class Grievance(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
    ]

    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='grievances'
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='grievances'
    )

    title = models.CharField(max_length=200)
    description = models.TextField()

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='Medium',
        db_index=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending',
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # SLA and Escalation
    due_date = models.DateTimeField(blank=True, null=True)
    escalation_level = models.IntegerField(default=0)  # Moved inside class
    last_escalated_at = models.DateTimeField(null=True, blank=True) # Moved inside class

    # Officer feedback
    officer_remark = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        # Set due date only on creation
        if not self.id and not self.due_date:
            self.due_date = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)

    # SLA HELPERS
    @property
    def sla_remaining(self):
        if not self.due_date:
            return None
        delta = self.due_date - timezone.now()
        return int(delta.total_seconds())

    @property
    def sla_status(self):
        if not self.due_date:
            return 'unknown'

        seconds = self.sla_remaining
        if seconds <= 0:
            return 'overdue'
        elif seconds <= 48 * 3600:
            return 'warning'
        return 'ok'

    @property
    def is_overdue(self):
        return (
            self.status != 'Resolved'
            and self.due_date
            and timezone.now() > self.due_date
        )

    def __str__(self):
        return f"{self.title} ({self.status})"


# =========================
# GRIEVANCE ASSIGNMENT
# =========================
class GrievanceAssignment(models.Model):
    grievance = models.ForeignKey(
        Grievance,
        on_delete=models.CASCADE,
        related_name='assignments'
    )

    officer = models.ForeignKey(
        Officer,
        on_delete=models.CASCADE,
        related_name='assigned_grievances'
    )

    assigned_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assigned_by_me'
    )

    assigned_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.grievance.title} → {self.officer.user.username}"


# =========================
# STATUS HISTORY
# =========================
class GrievanceStatusHistory(models.Model):
    grievance = models.ForeignKey(
        Grievance,
        on_delete=models.CASCADE,
        related_name='status_history'
    )

    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)

    changed_by = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name='status_changes'
    )

    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.grievance.title}: {self.old_status} → {self.new_status}"


# =========================
# ATTACHMENTS
# =========================
class Attachment(models.Model):
    grievance = models.ForeignKey(
        Grievance,
        on_delete=models.CASCADE,
        related_name='attachments'
    )

    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.grievance.title}"


# =========================
# FEEDBACK
# =========================
class Feedback(models.Model):
    grievance = models.OneToOneField(
        Grievance,
        on_delete=models.CASCADE,
        related_name='feedback'
    )

    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    comment = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.grievance.title}"


# =========================
# NOTIFICATIONS
# =========================
class Notification(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=200)
    message = models.TextField() # Changed to TextField for longer messages
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    grievance = models.ForeignKey(
        Grievance,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username} - {self.title}"