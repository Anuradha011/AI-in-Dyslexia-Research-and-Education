from django.db import models
from accounts.models import CustomUser

class NeuroimagingUpload(models.Model):
    SCAN_TYPES = [('fmri','fMRI'),('eeg','EEG'),('mri','Structural MRI'),('other','Other')]
    STATUS_CHOICES = [('uploaded','Uploaded'),('processing','Processing'),('analyzed','Analyzed'),('failed','Failed')]

    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='neuro_uploads')
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='neuro_scans',
                                 limit_choices_to={'role': 'student'})
    scan_type = models.CharField(max_length=20, choices=SCAN_TYPES)
    file = models.FileField(upload_to='neuroimaging/')
    file_name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.scan_type.upper()} for {self.patient.username}"


class NeuroimagingReport(models.Model):
    scan = models.OneToOneField(NeuroimagingUpload, on_delete=models.CASCADE, related_name='report')
    neural_patterns_detected = models.TextField(blank=True)
    dyslexia_indicators = models.TextField(blank=True)
    confidence_score = models.FloatField(default=0.0)
    simplified_interpretation = models.TextField(blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for scan {self.scan.id}"