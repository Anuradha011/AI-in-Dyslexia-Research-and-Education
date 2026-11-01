from django.db import models
from accounts.models import CustomUser


class SpeechSession(models.Model):
    SESSION_TYPES = [
        ('reading', 'Reading Practice'),
        ('pronunciation', 'Pronunciation'),
        ('fluency', 'Fluency Training'),
        ('free', 'Free Speech'),
    ]
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    student = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='speech_sessions'
    )
    session_type = models.CharField(
        max_length=20, choices=SESSION_TYPES, default='reading'
    )
    passage_text = models.TextField(blank=True)
    transcribed_text = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='in_progress'
    )

    # Scores
    fluency_score = models.FloatField(default=0.0)
    pronunciation_score = models.FloatField(default=0.0)
    grammar_score = models.FloatField(default=0.0)
    accuracy_score = models.FloatField(default=0.0)
    reading_speed_wpm = models.FloatField(default=0.0)

    # Stats
    duration_seconds = models.IntegerField(default=0)
    word_count = models.IntegerField(default=0)
    words_correct = models.IntegerField(default=0)
    words_total = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def overall_score(self):
        scores = [
            self.fluency_score,
            self.pronunciation_score,
            self.grammar_score,
            self.accuracy_score,
        ]
        valid = [s for s in scores if s > 0]
        return round(sum(valid) / len(valid), 1) if valid else 0.0

    def get_grade(self):
        score = self.overall_score()
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'

    def __str__(self):
        return f"{self.student.username} - {self.get_session_type_display()} ({self.created_at.date()})"


class TTSRequest(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField()
    audio_file = models.FileField(upload_to='tts_audio/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"TTS: {self.user.username} - {self.created_at.date()}"