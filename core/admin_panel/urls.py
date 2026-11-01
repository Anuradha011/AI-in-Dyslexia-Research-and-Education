from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # ── Parent Request Management (NEW) ──────────────────────────────
    path('parent-requests/',                views.parent_requests,   name='parent_requests'),
    path('parent-requests/<int:pk>/approve/', views.approve_request, name='approve_request'),
    path('parent-requests/<int:pk>/reject/',  views.reject_request,  name='reject_request'),
    path('parent-requests/<int:pk>/revoke/',  views.revoke_link,     name='revoke_link'),

    # ── AI Model Management ──────────────────────────────────────────
    path('models/',                    views.model_management, name='model_management'),
    path('models/upload/',             views.upload_model,     name='upload_model'),
    path('models/<int:pk>/activate/',  views.activate_model,   name='activate_model'),
    path('models/<int:pk>/delete/',    views.delete_model,     name='delete_model'),
    path('models/performance/',        views.model_performance,name='model_performance'),

    # ── Risk Scoring Config ──────────────────────────────────────────
    path('risk-config/', views.risk_config, name='risk_config'),

    # ── Content Management ───────────────────────────────────────────
    path('content/',                views.content_management, name='content_management'),
    path('content/add/',            views.add_exercise,       name='add_exercise'),
    path('content/<int:pk>/edit/',  views.edit_exercise,      name='edit_exercise'),
    path('content/<int:pk>/delete/',views.delete_exercise,    name='delete_exercise'),

    # ── NLP Config ───────────────────────────────────────────────────
    path('nlp/', views.nlp_config, name='nlp_config'),

    # ── Compliance ───────────────────────────────────────────────────
    path('compliance/',                views.compliance,   name='compliance'),
    path('compliance/add/',            views.add_policy,   name='add_policy'),
    path('compliance/<int:pk>/edit/',  views.edit_policy,  name='edit_policy'),

    # ── Bias Monitoring ──────────────────────────────────────────────
    path('bias/',           views.bias_monitoring,      name='bias_monitoring'),
    path('bias/generate/',  views.generate_bias_report, name='generate_bias_report'),

    # ── Language Management ──────────────────────────────────────────
    path('languages/', views.language_management, name='language_management'),

    # ── XAI ──────────────────────────────────────────────────────────
    path('xai/<int:assessment_id>/', views.xai_report, name='xai_report'),
]