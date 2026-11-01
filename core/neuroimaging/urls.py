from django.urls import path
from . import views
app_name = 'neuroimaging'
urlpatterns = [
    path('', views.upload_list, name='list'),
    path('upload/', views.upload_scan, name='upload'),
    path('<int:pk>/', views.scan_detail, name='detail'),
    path('<int:pk>/analyze/', views.analyze_scan, name='analyze'),
]