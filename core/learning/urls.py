from django.urls import path
from . import views
app_name = 'learning'
urlpatterns = [
    path('', views.learning_home, name='home'),
    path('plan/<int:pk>/', views.plan_detail, name='plan_detail'),
    path('plan/create/<int:student_id>/', views.create_plan, name='create_plan'),
    path('exercise/<int:pk>/', views.exercise_detail, name='exercise'),
    path('exercises/', views.exercise_list, name='exercises'),
    path('progress/', views.progress_view, name='progress'),
]