from django.urls import path
from . import views
app_name = 'reports'
urlpatterns = [
    path('', views.report_list, name='list'),
    path('<int:pk>/', views.report_detail, name='detail'),
    path('generate/<int:student_id>/', views.generate_report, name='generate'),
    path('audit/', views.audit_log, name='audit'),
]