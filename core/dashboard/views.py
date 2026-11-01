from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from assessment.models import Assessment
from learning.models import LearningPlan, StudentProgress
from speech.models import SpeechSession
from reports.models import ProgressReport
from accounts.models import CustomUser

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    return render(request, 'dashboard/home.html')

@login_required
def dashboard(request):
    user = request.user
    # Redirect each role to their dedicated dashboard
    # Note: avoid treating a superuser student as admin – check the role explicitly
    if user.role == 'educator':
        return redirect('accounts:educator_dashboard')
    elif user.role == 'parent':
        return redirect('accounts:parent_dashboard')
    elif user.role == 'admin':
        # only users assigned the admin role should see the admin dashboard
        return redirect('accounts:admin_dashboard')

    # Student dashboard only
    from assessment.models import Assessment
    from learning.models import LearningPlan
    from speech.models import SpeechSession
    from reports.models import ProgressReport

    context = {
        'assessments': Assessment.objects.filter(student=user).order_by('-created_at')[:3],
        'plans': LearningPlan.objects.filter(student=user, is_active=True)[:3],
        'sessions': SpeechSession.objects.filter(student=user).order_by('-created_at')[:3],
        'assessment_count': Assessment.objects.filter(student=user).count(),
        'completed_count': Assessment.objects.filter(student=user, status='completed').count(),
        'latest_assessment': Assessment.objects.filter(student=user, status='completed').last(),
    }
    return render(request, 'dashboard/dashboard.html', context)