from django.contrib import admin
from .models import ProgressReport, AuditLog
admin.site.register(ProgressReport)
admin.site.register(AuditLog)