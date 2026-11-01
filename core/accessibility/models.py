from django.db import models
from accounts.models import CustomUser

class UserPreferences(models.Model):
    FONT_SIZE_CHOICES = [('small','Small'),('medium','Medium'),('large','Large'),('xlarge','Extra Large')]
    FONT_FAMILY_CHOICES = [
        ('dyslexie', 'Dyslexie Font'),
        ('opendyslexic', 'OpenDyslexic'),
        ('arial', 'Arial'),
        ('verdana', 'Verdana'),
        ('times', 'Times New Roman'),
    ]
    THEME_CHOICES = [('light','Light'),('dark','Dark'),('high_contrast','High Contrast'),('cream','Cream/Sepia')]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='preferences')
    font_size = models.CharField(max_length=20, choices=FONT_SIZE_CHOICES, default='medium')
    font_family = models.CharField(max_length=30, choices=FONT_FAMILY_CHOICES, default='arial')
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='light')
    preferred_language = models.CharField(max_length=50, default='English')
    text_spacing = models.BooleanField(default=False)
    reading_ruler = models.BooleanField(default=False)
    tts_enabled = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Prefs: {self.user.username}"