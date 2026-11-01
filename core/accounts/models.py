from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """Custom manager required by old migrations — do not remove."""

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        if email:
            email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_approved', True)
        return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('student',  'Student'),
        ('educator', 'Educator'),
        ('parent',   'Parent'),
        ('admin',    'Admin'),
    ]

    objects = CustomUserManager()

    role               = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    date_of_birth      = models.DateField(null=True, blank=True)
    phone              = models.CharField(max_length=20, blank=True)
    institution        = models.CharField(max_length=200, blank=True)
    preferred_language = models.CharField(max_length=50, default='English')
    is_approved        = models.BooleanField(default=True)
    profile_pic        = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at         = models.DateTimeField(auto_now_add=True)

    def is_admin_user(self):
        return self.role == 'admin' or self.is_superuser

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = 'admin'
            self.is_approved = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"


class StudentProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='student_profile'
    )
    grade_level = models.CharField(max_length=50, blank=True)
    parent = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='children', limit_choices_to={'role': 'parent'}
    )
    educator = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='students', limit_choices_to={'role': 'educator'}
    )
    dyslexia_risk_score = models.FloatField(default=0.0)
    notes               = models.TextField(blank=True)

    def __str__(self):
        return f"Profile: {self.user.username}"


class ParentStudentRequest(models.Model):
    STATUS_CHOICES = [
        ('pending',  'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    parent  = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='parent_requests',
        limit_choices_to={'role': 'parent'}
    )
    student = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='student_requests',
        limit_choices_to={'role': 'student'}
    )
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reason      = models.TextField(blank=True)
    admin_note  = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reviewed_requests'
    )
    created_at  = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('parent', 'student')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.parent.username} -> {self.student.username} [{self.get_status_display()}]"