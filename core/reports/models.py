from django.db import models
from accounts.models import CustomUser

class ProgressReport(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='progress_reports')
    generated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='generated_reports')
    title = models.CharField(max_length=200)
    summary = models.TextField()
    strengths = models.TextField(blank=True)
    areas_for_improvement = models.TextField(blank=True)
    overall_score = models.FloatField(default=0.0)
    risk_level = models.CharField(max_length=20, blank=True)
    ai_explanation = models.TextField(blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report: {self.student.username} - {self.title}"


class AuditLog(models.Model):
    ACTION_TYPES = [
        ('login', 'Login'),
        ('assessment', 'Assessment'),
        ('report_view', 'Report Viewed'),
        ('data_upload', 'Data Upload'),
        ('model_update', 'Model Updated'),
        ('settings_change', 'Settings Changed'),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=30, choices=ACTION_TYPES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action} at {self.timestamp}"