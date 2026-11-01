from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import CustomUser, StudentProfile, ParentStudentRequest
from .forms import RegisterForm


# ─── AUTH ────────────────────────────────────────────────────────────

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            StudentProfile.objects.get_or_create(user=user)
            messages.success(request, 'Account created! Please log in.')
            return redirect('accounts:login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
            return render(request, 'accounts/login.html')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            try:
                from reports.models import AuditLog
                AuditLog.objects.create(
                    user=user, action='login',
                    description=f'{user.username} logged in.',
                    ip_address=request.META.get('REMOTE_ADDR')
                )
            except Exception:
                pass
            return redirect('dashboard:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')


# ─── EDUCATOR ────────────────────────────────────────────────────────

@login_required
def educator_dashboard(request):
    if request.user.role != 'educator' and not request.user.is_admin_user():
        return redirect('dashboard:dashboard')
    from assessment.models import Assessment
    from learning.models import LearningPlan
    students = CustomUser.objects.filter(role='student').order_by('username')
    return render(request, 'accounts/educator_dashboard.html', {
        'students': students,
        'recent_assessments': Assessment.objects.all().order_by('-created_at')[:10],
        'high_risk': Assessment.objects.filter(
            risk_level='high').select_related('student')[:5],
        'student_count': students.count(),
        'plan_count': LearningPlan.objects.count(),
    })


# ─── PARENT ──────────────────────────────────────────────────────────

@login_required
def parent_dashboard(request):
    if request.user.role != 'parent' and not request.user.is_admin_user():
        return redirect('dashboard:dashboard')

    from reports.models import ProgressReport
    from learning.models import LearningPlan
    from assessment.models import Assessment

    # Get approved link only
    approved_request = ParentStudentRequest.objects.filter(
        parent=request.user, status='approved'
    ).first()

    # Get pending request
    pending_request = ParentStudentRequest.objects.filter(
        parent=request.user, status='pending'
    ).first()

    # Get rejected request
    rejected_request = ParentStudentRequest.objects.filter(
        parent=request.user, status='rejected'
    ).first()

    child_data = None
    if approved_request:
        child = approved_request.student
        child_data = {
            'child': child,
            'latest_assessment': Assessment.objects.filter(
                student=child, status='completed'
            ).order_by('-created_at').first(),
            'plans': LearningPlan.objects.filter(
                student=child, is_active=True
            ),
            'reports': ProgressReport.objects.filter(
                student=child
            ).order_by('-generated_at')[:3],
            'assessment_count': Assessment.objects.filter(student=child).count(),
        }

    return render(request, 'accounts/parent_dashboard.html', {
        'child_data': child_data,
        'approved_request': approved_request,
        'pending_request': pending_request,
        'rejected_request': rejected_request,
    })


@login_required
def request_child_link(request):
    """Parent submits a request to be linked to a student — needs admin approval."""
    if request.user.role != 'parent':
        messages.error(request, 'Only parents can request child links.')
        return redirect('dashboard:dashboard')

    # Check if parent already has an approved link
    existing_approved = ParentStudentRequest.objects.filter(
        parent=request.user, status='approved'
    ).first()
    if existing_approved:
        messages.warning(
            request,
            f'You are already linked to {existing_approved.student.username}. '
            f'Each parent can only be linked to one student.'
        )
        return redirect('accounts:parent_dashboard')

    # Check if parent already has a pending request
    existing_pending = ParentStudentRequest.objects.filter(
        parent=request.user, status='pending'
    ).first()
    if existing_pending:
        messages.info(
            request,
            f'You already have a pending request for {existing_pending.student.username}. '
            f'Please wait for admin approval.'
        )
        return redirect('accounts:parent_dashboard')

    students = CustomUser.objects.filter(role='student').order_by('username')

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        reason = request.POST.get('reason', '').strip()

        if not student_id:
            messages.error(request, 'Please select a student.')
            return render(request, 'accounts/request_child_link.html',
                          {'students': students})

        student = get_object_or_404(CustomUser, pk=student_id, role='student')

        # Check if this student is already linked to another parent
        already_linked = StudentProfile.objects.filter(
            user=student
        ).exclude(parent=None).first()
        if already_linked and already_linked.parent != request.user:
            messages.error(
                request,
                f'Student {student.username} is already linked to another parent.'
            )
            return render(request, 'accounts/request_child_link.html',
                          {'students': students})

        # Check for duplicate request
        existing = ParentStudentRequest.objects.filter(
            parent=request.user, student=student
        ).first()
        if existing:
            if existing.status == 'rejected':
                # Allow re-request after rejection
                existing.status = 'pending'
                existing.reason = reason
                existing.admin_note = ''
                existing.reviewed_by = None
                existing.reviewed_at = None
                existing.save()
                messages.success(
                    request,
                    'Re-request submitted. Please wait for admin approval.'
                )
            else:
                messages.info(
                    request,
                    f'Request for {student.username} already exists.'
                )
            return redirect('accounts:parent_dashboard')

        # Create new request
        ParentStudentRequest.objects.create(
            parent=request.user,
            student=student,
            reason=reason,
            status='pending',
        )

        messages.success(
            request,
            f'Request to link with {student.username} submitted successfully! '
            f'Please wait for admin approval. You will be notified once approved.'
        )
        return redirect('accounts:parent_dashboard')

    return render(request, 'accounts/request_child_link.html',
                  {'students': students})


@login_required
def cancel_request(request, pk):
    """Parent cancels their own pending request."""
    if request.user.role != 'parent':
        return redirect('dashboard:dashboard')
    req = get_object_or_404(
        ParentStudentRequest, pk=pk, parent=request.user, status='pending'
    )
    req.delete()
    messages.success(request, 'Request cancelled.')
    return redirect('accounts:parent_dashboard')


# ─── ADMIN ───────────────────────────────────────────────────────────

@login_required
def parent_request_list(request):
    """Redirect to the dedicated admin_panel page."""
    if not request.user.is_admin_user():
        return redirect('dashboard:dashboard')
    return redirect('admin_panel:parent_requests')


# the review_parent_request view is no longer used; admin_panel handles approval/rejection


@login_required
def admin_dashboard(request):
    if not request.user.is_admin_user():
        return redirect('dashboard:dashboard')
    from assessment.models import Assessment
    from learning.models import LearningPlan
    from reports.models import AuditLog
    from speech.models import SpeechSession

    pending_count = ParentStudentRequest.objects.filter(status='pending').count()

    return render(request, 'accounts/admin_dashboard.html', {
        'total_users': CustomUser.objects.count(),
        'student_count': CustomUser.objects.filter(role='student').count(),
        'educator_count': CustomUser.objects.filter(role='educator').count(),
        'parent_count': CustomUser.objects.filter(role='parent').count(),
        'total_assessments': Assessment.objects.count(),
        'high_risk_count': Assessment.objects.filter(risk_level='high').count(),
        'moderate_risk_count': Assessment.objects.filter(risk_level='moderate').count(),
        'low_risk_count': Assessment.objects.filter(risk_level='low').count(),
        'total_plans': LearningPlan.objects.count(),
        'total_sessions': SpeechSession.objects.count(),
        'recent_users': CustomUser.objects.order_by('-created_at')[:8],
        'recent_audits': AuditLog.objects.order_by('-timestamp')[:6],
        'high_risk_students': Assessment.objects.filter(
            risk_level='high', status='completed'
        ).select_related('student').order_by('-created_at')[:5],
        'pending_requests_count': pending_count,
    })


@login_required
def student_detail(request, pk):
    if request.user.role not in ['educator', 'admin'] \
            and not request.user.is_admin_user():
        return redirect('dashboard:dashboard')
    student = get_object_or_404(CustomUser, pk=pk, role='student')
    from assessment.models import Assessment
    from learning.models import LearningPlan, StudentProgress
    from reports.models import ProgressReport
    from speech.models import SpeechSession
    assessments = Assessment.objects.filter(student=student).order_by('-created_at')
    return render(request, 'accounts/student_detail.html', {
        'student': student,
        'assessments': assessments,
        'plans': LearningPlan.objects.filter(student=student),
        'progress': StudentProgress.objects.filter(
            student=student).order_by('-recorded_at')[:10],
        'reports': ProgressReport.objects.filter(student=student),
        'sessions': SpeechSession.objects.filter(
            student=student).order_by('-created_at')[:5],
        'latest_assessment': assessments.filter(status='completed').first(),
    })


@login_required
def admin_user_list(request):
    if not request.user.is_admin_user():
        return redirect('dashboard:dashboard')
    users = CustomUser.objects.all().order_by('-created_at')
    return render(request, 'accounts/user_list.html', {'users': users})


@login_required
def delete_user(request, pk):
    if not request.user.is_admin_user():
        return redirect('dashboard:dashboard')
    user = get_object_or_404(CustomUser, pk=pk)
    if user == request.user:
        messages.error(request, 'You cannot delete yourself.')
        return redirect('accounts:user_list')
    user.delete()
    messages.success(request, 'User deleted.')
    return redirect('accounts:user_list')


@login_required
def change_role(request, pk):
    if not request.user.is_admin_user():
        return redirect('dashboard:dashboard')
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in ['student', 'educator', 'parent', 'admin']:
            user.role = new_role
            user.save()
            messages.success(request, f'Role updated to {new_role}.')
    return redirect('accounts:user_list')