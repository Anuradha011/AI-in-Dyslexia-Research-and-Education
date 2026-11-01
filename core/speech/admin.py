from django.contrib import admin
from .models import SpeechSession, TTSRequest
admin.site.register(SpeechSession)
admin.site.register(TTSRequest)