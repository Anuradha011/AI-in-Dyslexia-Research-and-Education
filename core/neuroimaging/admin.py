from django.contrib import admin
from .models import NeuroimagingUpload, NeuroimagingReport
admin.site.register(NeuroimagingUpload)
admin.site.register(NeuroimagingReport)