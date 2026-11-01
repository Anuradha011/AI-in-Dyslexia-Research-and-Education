from django.db import models
from accounts.models import CustomUser

class LearningPlan(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='learning_plans')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_plans')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.username} - {self.title}"


class LearningModule(models.Model):
    MODULE_TYPES = [
        ('phonics', 'Phonics Training'),
        ('reading', 'Reading Exercise'),
        ('comprehension', 'Comprehension'),
        ('spelling', 'Spelling Practice'),
        ('memory', 'Memory Training'),
        ('writing', 'Writing Support'),
    ]
    DIFFICULTY_LEVELS = [('beginner','Beginner'),('intermediate','Intermediate'),('advanced','Advanced')]

    plan = models.ForeignKey(LearningPlan, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    module_type = models.CharField(max_length=30, choices=MODULE_TYPES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, default='beginner')
    content = models.TextField()
    instructions = models.TextField(blank=True)
    order = models.IntegerField(default=1)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.module_type}: {self.title}"


class Exercise(models.Model):
    EXERCISE_TYPES = [
        ('phonics', 'Phonics'),
        ('reading', 'Reading'),
        ('spelling', 'Spelling'),
        ('matching', 'Word Matching'),
        ('fill_blank', 'Fill in the Blank'),
    ]
    title = models.CharField(max_length=200)
    exercise_type = models.CharField(max_length=30, choices=EXERCISE_TYPES)
    content = models.TextField()
    answer = models.TextField()
    hint = models.TextField(blank=True)
    difficulty = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.exercise_type}] {self.title}"


class StudentProgress(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='progress_records')
    module = models.ForeignKey(LearningModule, on_delete=models.CASCADE)
    score = models.FloatField()
    time_spent_minutes = models.FloatField(default=0)
    attempts = models.IntegerField(default=1)
    completed = models.BooleanField(default=False)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.module.title}: {self.score}%"