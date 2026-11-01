from django.db import models
from accounts.models import CustomUser


class AIModelConfig(models.Model):
    """Admin can configure AI model parameters"""
    MODEL_TYPES = [
        ('risk_classifier', 'Dyslexia Risk Classifier'),
        ('phonological', 'Phonological Analyzer'),
        ('reading_speed', 'Reading Speed Model'),
        ('nlp_grammar', 'NLP Grammar Checker'),
    ]
    model_name = models.CharField(max_length=200)
    model_type = models.CharField(max_length=30, choices=MODEL_TYPES)
    model_file = models.FileField(upload_to='ai_models/', blank=True, null=True)
    version = models.CharField(max_length=20, default='1.0')
    is_active = models.BooleanField(default=False)
    accuracy = models.FloatField(default=0.0)
    precision = models.FloatField(default=0.0)
    recall = models.FloatField(default=0.0)
    f1_score = models.FloatField(default=0.0)
    parameters = models.JSONField(default=dict, blank=True)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.model_name} v{self.version} ({'Active' if self.is_active else 'Inactive'})"


class RiskScoringConfig(models.Model):
    """Admin configures the weights used in risk calculation"""
    name = models.CharField(max_length=100, default='Default Config')
    is_active = models.BooleanField(default=True)
    phonological_weight = models.FloatField(default=0.35)
    error_rate_weight = models.FloatField(default=0.25)
    working_memory_weight = models.FloatField(default=0.20)
    comprehension_weight = models.FloatField(default=0.15)
    family_history_weight = models.FloatField(default=0.05)
    high_risk_threshold = models.FloatField(default=65.0)
    moderate_risk_threshold = models.FloatField(default=40.0)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Risk Config: {self.name} ({'Active' if self.is_active else 'Inactive'})"


class NLPSystemConfig(models.Model):
    """Admin configures NLP/speech settings"""
    LANGUAGE_CHOICES = [
        ('en', 'English'), ('es', 'Spanish'), ('fr', 'French'),
        ('hi', 'Hindi'), ('ar', 'Arabic'), ('de', 'German'),
    ]
    language_code = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='en')
    language_name = models.CharField(max_length=50)
    is_enabled = models.BooleanField(default=True)
    tts_speed = models.FloatField(default=1.0)
    stt_confidence_threshold = models.FloatField(default=0.7)
    fluency_scoring_enabled = models.BooleanField(default=True)
    grammar_check_enabled = models.BooleanField(default=True)
    pronunciation_scoring_enabled = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"NLP Config: {self.language_name}"


class CompliancePolicy(models.Model):
    """Data privacy and compliance policies"""
    POLICY_TYPES = [
        ('privacy', 'Privacy Policy'),
        ('data_retention', 'Data Retention Policy'),
        ('consent', 'User Consent Policy'),
        ('bias', 'AI Bias Policy'),
        ('accessibility', 'Accessibility Policy'),
    ]
    title = models.CharField(max_length=200)
    policy_type = models.CharField(max_length=30, choices=POLICY_TYPES)
    content = models.TextField()
    version = models.CharField(max_length=20, default='1.0')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} v{self.version}"


class BiasMonitoringReport(models.Model):
    """AI fairness and bias monitoring"""
    report_title = models.CharField(max_length=200)
    evaluation_date = models.DateField(auto_now_add=True)
    total_assessments_reviewed = models.IntegerField(default=0)
    gender_bias_score = models.FloatField(default=0.0)
    age_bias_score = models.FloatField(default=0.0)
    language_bias_score = models.FloatField(default=0.0)
    overall_fairness_score = models.FloatField(default=0.0)
    findings = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    generated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Bias Report: {self.report_title}"


class SupportedLanguage(models.Model):
    """Languages supported on the platform"""
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    native_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    content_available = models.BooleanField(default=False)
    tts_available = models.BooleanField(default=False)
    stt_available = models.BooleanField(default=False)
    added_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"