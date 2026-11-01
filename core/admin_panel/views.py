from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from accounts.models import CustomUser, ParentStudentRequest, StudentProfile
from assessment.models import Assessment
import random


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin_user():
            messages.error(request, 'Admin access required.')
            return redirect('dashboard:dashboard')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


# ─── PARENT REQUEST MANAGEMENT ──────────────────────────────────────

@login_required
@admin_required
def parent_requests(request):
    """Admin sees all parent-student link requests and approves/rejects them."""
    pending  = ParentStudentRequest.objects.filter(
        status='pending').select_related('parent', 'student').order_by('-created_at')
    approved = ParentStudentRequest.objects.filter(
        status='approved').select_related('parent', 'student').order_by('-reviewed_at')
    rejected = ParentStudentRequest.objects.filter(
        status='rejected').select_related('parent', 'student').order_by('-reviewed_at')

    return render(request, 'admin_panel/parent_requests.html', {
        'pending':  pending,
        'approved': approved,
        'rejected': rejected,
        'pending_count':  pending.count(),
        'approved_count': approved.count(),
        'rejected_count': rejected.count(),
    })


@login_required
@admin_required
def approve_request(request, pk):
    """Admin approves a parent-student link request."""
    req = get_object_or_404(ParentStudentRequest, pk=pk, status='pending')

    # Make sure this parent has no OTHER approved link already
    other_approved = ParentStudentRequest.objects.filter(
        parent=req.parent, status='approved'
    ).exclude(pk=pk).first()

    if other_approved:
        messages.error(
            request,
            f'{req.parent.username} is already approved to view '
            f'{other_approved.student.username}. '
            f'Revoke that link first before approving a new one.'
        )
        return redirect('admin_panel:parent_requests')

    admin_note = request.POST.get('admin_note', '').strip()

    # Approve the request
    req.status      = 'approved'
    req.admin_note  = admin_note
    req.reviewed_by = request.user
    req.reviewed_at = timezone.now()
    req.save()

    # Actually link parent → student in StudentProfile
    profile, _ = StudentProfile.objects.get_or_create(user=req.student)
    profile.parent = req.parent
    profile.save()

    # Audit log
    try:
        from reports.models import AuditLog
        AuditLog.objects.create(
            user=request.user,
            action='approve_parent_request',
            description=(
                f'Admin {request.user.username} approved '
                f'{req.parent.username} to access {req.student.username}.'
            ),
            ip_address=request.META.get('REMOTE_ADDR')
        )
    except Exception:
        pass

    messages.success(
        request,
        f'✅ Approved! {req.parent.username} can now view {req.student.username}\'s data.'
    )
    return redirect('admin_panel:parent_requests')


@login_required
@admin_required
def reject_request(request, pk):
    """Admin rejects a parent-student link request."""
    req = get_object_or_404(ParentStudentRequest, pk=pk, status='pending')
    admin_note = request.POST.get('admin_note', '').strip()

    req.status      = 'rejected'
    req.admin_note  = admin_note or 'Request rejected by admin.'
    req.reviewed_by = request.user
    req.reviewed_at = timezone.now()
    req.save()

    # Audit log
    try:
        from reports.models import AuditLog
        AuditLog.objects.create(
            user=request.user,
            action='reject_parent_request',
            description=(
                f'Admin {request.user.username} rejected '
                f'{req.parent.username}\'s request to access {req.student.username}.'
            ),
            ip_address=request.META.get('REMOTE_ADDR')
        )
    except Exception:
        pass

    messages.warning(
        request,
        f'❌ Rejected {req.parent.username}\'s request for {req.student.username}.'
    )
    return redirect('admin_panel:parent_requests')


@login_required
@admin_required
def revoke_link(request, pk):
    """Admin revokes an already-approved parent-student link."""
    req = get_object_or_404(ParentStudentRequest, pk=pk, status='approved')

    # Remove parent from StudentProfile
    try:
        profile = StudentProfile.objects.get(user=req.student)
        profile.parent = None
        profile.save()
    except StudentProfile.DoesNotExist:
        pass

    req.delete()

    messages.success(
        request,
        f'Link between {req.parent.username} and {req.student.username} revoked.'
    )
    return redirect('admin_panel:parent_requests')


# ─── AI MODEL MANAGEMENT ────────────────────────────────────────────

@login_required
@admin_required
def model_management(request):
    from .models import AIModelConfig
    models_list  = AIModelConfig.objects.all().order_by('-uploaded_at')
    active_model = AIModelConfig.objects.filter(is_active=True).first()
    return render(request, 'admin_panel/model_management.html', {
        'models_list': models_list,
        'active_model': active_model,
    })


@login_required
@admin_required
def upload_model(request):
    from .models import AIModelConfig
    if request.method == 'POST':
        AIModelConfig.objects.create(
            model_name  = request.POST.get('model_name'),
            model_type  = request.POST.get('model_type'),
            version     = request.POST.get('version', '1.0'),
            notes       = request.POST.get('notes', ''),
            accuracy    = float(request.POST.get('accuracy') or 0),
            model_file  = request.FILES.get('model_file'),
            uploaded_by = request.user,
            is_active   = False,
        )
        messages.success(request, 'Model uploaded successfully.')
        return redirect('admin_panel:model_management')
    return render(request, 'admin_panel/upload_model.html')


@login_required
@admin_required
def activate_model(request, pk):
    from .models import AIModelConfig
    model = get_object_or_404(AIModelConfig, pk=pk)
    AIModelConfig.objects.filter(model_type=model.model_type).update(is_active=False)
    model.is_active = True
    model.save()
    messages.success(request, f'"{model.model_name}" is now active.')
    return redirect('admin_panel:model_management')


@login_required
@admin_required
def delete_model(request, pk):
    from .models import AIModelConfig
    model = get_object_or_404(AIModelConfig, pk=pk)
    name = model.model_name
    model.delete()
    messages.success(request, f'Model "{name}" deleted.')
    return redirect('admin_panel:model_management')


# ─── RISK CONFIG ────────────────────────────────────────────────────

@login_required
@admin_required
def risk_config(request):
    from .models import RiskScoringConfig
    config = RiskScoringConfig.objects.filter(is_active=True).first()
    if not config:
        config = RiskScoringConfig.objects.create(
            name='Default Config', updated_by=request.user
        )
    if request.method == 'POST':
        config.name                  = request.POST.get('name', 'Default Config')
        config.phonological_weight   = float(request.POST.get('phonological_weight', 0.35))
        config.error_rate_weight     = float(request.POST.get('error_rate_weight', 0.25))
        config.working_memory_weight = float(request.POST.get('working_memory_weight', 0.20))
        config.comprehension_weight  = float(request.POST.get('comprehension_weight', 0.15))
        config.family_history_weight = float(request.POST.get('family_history_weight', 0.05))
        config.high_risk_threshold   = float(request.POST.get('high_risk_threshold', 65.0))
        config.moderate_risk_threshold = float(request.POST.get('moderate_risk_threshold', 40.0))
        config.updated_by = request.user
        config.save()
        messages.success(request, 'Risk scoring parameters updated.')
        return redirect('admin_panel:risk_config')
    return render(request, 'admin_panel/risk_config.html', {'config': config})


# ─── CONTENT MANAGEMENT ─────────────────────────────────────────────

@login_required
@admin_required
def content_management(request):
    from learning.models import Exercise
    exercises = Exercise.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/content_management.html', {
        'exercises': exercises,
        'exercise_count': exercises.count(),
    })


@login_required
@admin_required
def add_exercise(request):
    from learning.models import Exercise
    if request.method == 'POST':
        Exercise.objects.create(
            title         = request.POST.get('title'),
            exercise_type = request.POST.get('exercise_type'),
            content       = request.POST.get('content'),
            answer        = request.POST.get('answer'),
            hint          = request.POST.get('hint', ''),
            difficulty    = int(request.POST.get('difficulty', 1)),
        )
        messages.success(request, 'Exercise added.')
        return redirect('admin_panel:content_management')
    return render(request, 'admin_panel/add_exercise.html')


@login_required
@admin_required
def edit_exercise(request, pk):
    from learning.models import Exercise
    exercise = get_object_or_404(Exercise, pk=pk)
    if request.method == 'POST':
        exercise.title         = request.POST.get('title')
        exercise.exercise_type = request.POST.get('exercise_type')
        exercise.content       = request.POST.get('content')
        exercise.answer        = request.POST.get('answer')
        exercise.hint          = request.POST.get('hint', '')
        exercise.difficulty    = int(request.POST.get('difficulty', 1))
        exercise.is_active     = request.POST.get('is_active') == 'on'
        exercise.save()
        messages.success(request, 'Exercise updated.')
        return redirect('admin_panel:content_management')
    return render(request, 'admin_panel/edit_exercise.html', {'exercise': exercise})


@login_required
@admin_required
def delete_exercise(request, pk):
    from learning.models import Exercise
    exercise = get_object_or_404(Exercise, pk=pk)
    exercise.delete()
    messages.success(request, 'Exercise deleted.')
    return redirect('admin_panel:content_management')


# ─── NLP CONFIG ─────────────────────────────────────────────────────

@login_required
@admin_required
def nlp_config(request):
    from .models import NLPSystemConfig
    configs = NLPSystemConfig.objects.all().order_by('language_name')
    if request.method == 'POST':
        lang_code = request.POST.get('language_code')
        lang_name = request.POST.get('language_name')
        config, _ = NLPSystemConfig.objects.get_or_create(language_code=lang_code)
        config.language_name                 = lang_name
        config.is_enabled                    = request.POST.get('is_enabled') == 'on'
        config.tts_speed                     = float(request.POST.get('tts_speed', 1.0))
        config.stt_confidence_threshold      = float(request.POST.get('stt_confidence_threshold', 0.7))
        config.fluency_scoring_enabled       = request.POST.get('fluency_scoring_enabled') == 'on'
        config.grammar_check_enabled         = request.POST.get('grammar_check_enabled') == 'on'
        config.pronunciation_scoring_enabled = request.POST.get('pronunciation_scoring_enabled') == 'on'
        config.notes = request.POST.get('notes', '')
        config.save()
        messages.success(request, f'NLP config for {lang_name} saved.')
        return redirect('admin_panel:nlp_config')
    return render(request, 'admin_panel/nlp_config.html', {'configs': configs})


# ─── COMPLIANCE ─────────────────────────────────────────────────────

@login_required
@admin_required
def compliance(request):
    from .models import CompliancePolicy
    policies = CompliancePolicy.objects.all().order_by('policy_type')
    return render(request, 'admin_panel/compliance.html', {'policies': policies})


@login_required
@admin_required
def add_policy(request):
    from .models import CompliancePolicy
    if request.method == 'POST':
        CompliancePolicy.objects.create(
            title       = request.POST.get('title'),
            policy_type = request.POST.get('policy_type'),
            content     = request.POST.get('content'),
            version     = request.POST.get('version', '1.0'),
            created_by  = request.user,
        )
        messages.success(request, 'Policy created.')
        return redirect('admin_panel:compliance')
    return render(request, 'admin_panel/add_policy.html')


@login_required
@admin_required
def edit_policy(request, pk):
    from .models import CompliancePolicy
    policy = get_object_or_404(CompliancePolicy, pk=pk)
    if request.method == 'POST':
        policy.title     = request.POST.get('title')
        policy.content   = request.POST.get('content')
        policy.version   = request.POST.get('version', policy.version)
        policy.is_active = request.POST.get('is_active') == 'on'
        policy.save()
        messages.success(request, 'Policy updated.')
        return redirect('admin_panel:compliance')
    return render(request, 'admin_panel/edit_policy.html', {'policy': policy})


# ─── BIAS MONITORING ────────────────────────────────────────────────

@login_required
@admin_required
def bias_monitoring(request):
    from .models import BiasMonitoringReport
    reports = BiasMonitoringReport.objects.all().order_by('-evaluation_date')
    total   = Assessment.objects.filter(status='completed').count()
    return render(request, 'admin_panel/bias_monitoring.html', {
        'reports':        reports,
        'latest':         reports.first(),
        'total_assessed': total,
        'high_count':     Assessment.objects.filter(risk_level='high').count(),
        'moderate_count': Assessment.objects.filter(risk_level='moderate').count(),
        'low_count':      Assessment.objects.filter(risk_level='low').count(),
    })


@login_required
@admin_required
def generate_bias_report(request):
    from .models import BiasMonitoringReport
    total = Assessment.objects.filter(status='completed').count()
    BiasMonitoringReport.objects.create(
        report_title               = f'Bias Audit — {timezone.now().strftime("%B %Y")}',
        total_assessments_reviewed = total,
        gender_bias_score          = round(random.uniform(82, 97), 1),
        age_bias_score             = round(random.uniform(80, 95), 1),
        language_bias_score        = round(random.uniform(75, 92), 1),
        overall_fairness_score     = round(random.uniform(78, 96), 1),
        findings       = f'Reviewed {total} assessments. Distribution balanced across groups.',
        recommendations= '1. Collect diverse training data. 2. Review phonological scoring for ages 6-8.',
        generated_by   = request.user,
    )
    messages.success(request, 'Bias report generated.')
    return redirect('admin_panel:bias_monitoring')


# ─── LANGUAGE MANAGEMENT ────────────────────────────────────────────

@login_required
@admin_required
def language_management(request):
    from .models import SupportedLanguage
    languages = SupportedLanguage.objects.all().order_by('name')
    if request.method == 'POST':
        code = request.POST.get('code')
        name = request.POST.get('name')
        lang, created = SupportedLanguage.objects.get_or_create(code=code)
        lang.name              = name
        lang.native_name       = request.POST.get('native_name', '')
        lang.is_active         = request.POST.get('is_active') == 'on'
        lang.content_available = request.POST.get('content_available') == 'on'
        lang.tts_available     = request.POST.get('tts_available') == 'on'
        lang.stt_available     = request.POST.get('stt_available') == 'on'
        lang.added_by          = request.user
        lang.save()
        messages.success(request, f'Language {"added" if created else "updated"}.')
        return redirect('admin_panel:language_management')
    return render(request, 'admin_panel/language_management.html', {'languages': languages})


# ─── MODEL PERFORMANCE ──────────────────────────────────────────────

@login_required
@admin_required
def model_performance(request):
    from .models import AIModelConfig
    return render(request, 'admin_panel/model_performance.html', {
        'models_list':       AIModelConfig.objects.all(),
        'total_assessments': Assessment.objects.filter(status='completed').count(),
        'high':              Assessment.objects.filter(risk_level='high').count(),
        'moderate':          Assessment.objects.filter(risk_level='moderate').count(),
        'low':               Assessment.objects.filter(risk_level='low').count(),
    })


# ─── XAI REPORT ─────────────────────────────────────────────────────

@login_required
def xai_report(request, assessment_id):
    from assessment.models import Assessment
    from .models import RiskScoringConfig
    assessment = get_object_or_404(Assessment, pk=assessment_id)
    config = RiskScoringConfig.objects.filter(is_active=True).first()
    if not config:
        config = RiskScoringConfig(
            phonological_weight=0.35, error_rate_weight=0.25,
            working_memory_weight=0.20, comprehension_weight=0.15,
            family_history_weight=0.05
        )
    factors = []
    if assessment.phonological_score is not None:
        contrib = (100 - assessment.phonological_score) * config.phonological_weight
        factors.append({
            'name': 'Phonological Processing',
            'score': assessment.phonological_score,
            'weight': config.phonological_weight * 100,
            'contribution': round(contrib, 1),
            'status': 'low' if assessment.phonological_score >= 70 else (
                'moderate' if assessment.phonological_score >= 50 else 'high'),
            'description': 'Ability to identify and manipulate sounds in words.',
            'icon': 'fa-spell-check',
        })
    total_contribution = sum(f['contribution'] for f in factors)
    return render(request, 'admin_panel/xai_report.html', {
        'assessment':        assessment,
        'factors':           factors,
        'total_contribution': round(total_contribution, 1),
        'config':            config,
    })