from django.contrib import admin
from .models import LearningPlan, LearningModule, Exercise, StudentProgress
admin.site.register(LearningPlan)
admin.site.register(LearningModule)
admin.site.register(Exercise)
admin.site.register(StudentProgress)