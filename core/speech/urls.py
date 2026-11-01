from django.urls import path
from . import views

app_name = 'speech'

urlpatterns = [
    path('', views.speech_home, name='home'),
    path('session/', views.speech_session, name='session'),
    path('analyze/', views.analyze_speech, name='analyze'),
    path('tts/', views.tts_view, name='tts'),
    path('sessions/', views.sessions_list, name='sessions'),
    path('sessions/<int:pk>/', views.session_detail, name='session_detail'),
]