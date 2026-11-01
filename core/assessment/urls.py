from django.urls import path
from . import views
app_name = 'assessment'
urlpatterns = [
    path('', views.assessment_list, name='list'),
    path('start/', views.start_assessment, name='start'),
    path('<int:pk>/', views.assessment_detail, name='detail'),
    path('<int:pk>/take/', views.take_assessment, name='take'),
    path('<int:pk>/results/', views.assessment_results, name='results'),
    path('admin/questions/', views.question_list, name='questions'),
    path('admin/questions/add/', views.add_question, name='add_question'),
]