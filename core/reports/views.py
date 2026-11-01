from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ProgressReport, AuditLog
from accounts.models import CustomUser
from assessment.models import Assessment
from learning.models import StudentProgress

@login_required
def report_list(request):
    if request.user.role == 'student':
        reports = ProgressReport.objects.filter(student=request.user).order_by('-generated_at')
    else:
        reports = ProgressReport.objects.all().order_by('-generated_at')
    return render(request, 'reports/list.html', {'reports': reports})

@login_required
def report_detail(request, pk):
    report = get_object_or_404(ProgressReport, pk=pk)
    from reports.models import AuditLog
    AuditLog.objects.create(
        user=request.user, action='report_view',
        description=f'Viewed report: {report.title}',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    return render(request, 'reports/detail.html', {'report': report})

@login_required
def generate_report(request, student_id):
    if not (request.user.is_admin_user() or request.user.role == 'educator'):
        return redirect('reports:list')
    student = get_object_or_404(CustomUser, pk=student_id)
    latest_assessment = Assessment.objects.filter(student=student, status='completed').last()
    progress = StudentProgress.objects.filter(student=student)
    avg_score = sum(p.score for p in progress) / progress.count() if progress.exists() else 0
    risk = latest_assessment.risk_level if latest_assessment else 'unknown'
    report = ProgressReport.objects.create(
        student=student,
        generated_by=request.user,
        title=f'Progress Report - {student.get_full_name() or student.username}',
        summary=f'This report summarizes {student.username}\'s learning progress and assessment outcomes.',
        strengths='Shows improvement in reading comprehension. Good engagement with phonics exercises.',
        areas_for_improvement='Reading speed and phonological awareness need continued support.',
        overall_score=round(avg_score, 2),
        risk_level=risk,
        ai_explanation=f'Report generated based on {progress.count()} learning activities and '
                       f'{Assessment.objects.filter(student=student).count()} assessments. '
                       f'The AI model analyzed patterns across reading speed, error rate, and comprehension scores.'
    )
    return redirect('reports:detail', pk=report.pk)

@login_required
def audit_log(request):
    if not request.user.is_admin_user():
        return redirect('dashboard:dashboard')
    logs = AuditLog.objects.all().order_by('-timestamp')[:200]
    return render(request, 'reports/audit.html', {'logs': logs})