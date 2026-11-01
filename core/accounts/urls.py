from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),

    # Role Dashboards
    path('educator/', views.educator_dashboard, name='educator_dashboard'),
    path('parent/', views.parent_dashboard, name='parent_dashboard'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),

    # Parent → Student Link (request-based, admin approval required)
    path('parent/request-link/', views.request_child_link, name='request_child_link'),
    path('parent/cancel-request/<int:pk>/', views.cancel_request, name='cancel_request'),


    # Student Detail (educators/admins)
    path('students/<int:pk>/', views.student_detail, name='student_detail'),

    # Admin User Management
    path('admin/users/', views.admin_user_list, name='user_list'),
    path('admin/users/<int:pk>/delete/', views.delete_user, name='delete_user'),
    path('admin/users/<int:pk>/role/', views.change_role, name='change_role'),
]