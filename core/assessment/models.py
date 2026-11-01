from django.db import models
from accounts.models import CustomUser

class Assessment(models.Model):
    RISK_LEVELS = [('low','Low Risk'),('moderate','Moderate Risk'),('high','High Risk')]
    STATUS_CHOICES = [('pending','Pending'),('in_progress','In Progress'),('completed','Completed')]

    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assessments')
    title = models.CharField(max_length=200, default='Reading Assessment')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS, blank=True)
    risk_score = models.FloatField(default=0.0)
    reading_speed_wpm = models.FloatField(null=True, blank=True)
    error_rate = models.FloatField(null=True, blank=True)
    comprehension_score = models.FloatField(null=True, blank=True)
    phonological_score = models.FloatField(null=True, blank=True)
    working_memory_score = models.FloatField(null=True, blank=True)
    ai_analysis = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.username} - {self.title} ({self.status})"


class AssessmentQuestion(models.Model):
    QUESTION_TYPES = [
        ('reading', 'Reading Task'),
        ('phonics', 'Phonics Task'),
        ('memory', 'Working Memory'),
        ('comprehension', 'Comprehension'),
        ('spelling', 'Spelling'),
    ]
    question_text = models.TextField()
    question_type = models.CharField(max_length=30, choices=QUESTION_TYPES)
    correct_answer = models.TextField()
    difficulty = models.IntegerField(default=1)
    audio_file = models.FileField(upload_to='assessment_audio/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.question_type}] {self.question_text[:60]}"


class AssessmentResponse(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(AssessmentQuestion, on_delete=models.CASCADE)
    student_answer = models.TextField()
    is_correct = models.BooleanField(default=False)
    time_taken_seconds = models.FloatField(default=0)
    error_type = models.CharField(max_length=100, blank=True)
    responded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response to Q{self.question.id}"