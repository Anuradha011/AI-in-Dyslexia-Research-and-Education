from django.contrib import admin
from .models import Assessment, AssessmentQuestion, AssessmentResponse
admin.site.register(Assessment)
admin.site.register(AssessmentQuestion)
admin.site.register(AssessmentResponse)