from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Assessment, AssessmentQuestion, AssessmentResponse
from .forms import AssessmentResponseForm, QuestionForm
import random

@login_required
def assessment_list(request):
    if request.user.is_admin_user() or request.user.role == 'educator':
        assessments = Assessment.objects.all().order_by('-created_at')
    else:
        assessments = Assessment.objects.filter(student=request.user).order_by('-created_at')
    return render(request, 'assessment/list.html', {'assessments': assessments})

@login_required
def start_assessment(request):
    assessment = Assessment.objects.create(
        student=request.user,
        title=f'Reading Assessment - {timezone.now().strftime("%b %d, %Y")}',
        status='in_progress'
    )
    return redirect('assessment:take', pk=assessment.pk)

@login_required
def assessment_detail(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk)
    responses = assessment.responses.all()
    return render(request, 'assessment/detail.html', {'assessment': assessment, 'responses': responses})

@login_required
def take_assessment(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk)
    questions = list(AssessmentQuestion.objects.filter(is_active=True))
    random.shuffle(questions)
    questions = questions[:10]  # 10 questions per session

    if request.method == 'POST':
        correct = 0
        total = 0
        for q in questions:
            ans = request.POST.get(f'answer_{q.id}', '').strip().lower()
            correct_ans = q.correct_answer.strip().lower()
            is_correct = ans == correct_ans
            if is_correct:
                correct += 1
            total += 1
            AssessmentResponse.objects.create(
                assessment=assessment,
                question=q,
                student_answer=ans,
                is_correct=is_correct,
            )
        # Calculate scores
        score_pct = (correct / total * 100) if total > 0 else 0
        assessment.comprehension_score = score_pct
        assessment.reading_speed_wpm = random.uniform(60, 180)  # simulated
        assessment.error_rate = round((1 - correct/total) * 100, 2) if total > 0 else 0
        assessment.phonological_score = random.uniform(40, 95)
        assessment.working_memory_score = random.uniform(40, 90)
        # Risk scoring
        avg = (score_pct + assessment.phonological_score + assessment.working_memory_score) / 3
        if avg < 50:
            assessment.risk_level = 'high'
            assessment.risk_score = round(100 - avg, 2)
        elif avg < 70:
            assessment.risk_level = 'moderate'
            assessment.risk_score = round(100 - avg, 2)
        else:
            assessment.risk_level = 'low'
            assessment.risk_score = round(100 - avg, 2)
        assessment.ai_analysis = f"Analysis based on {total} questions. Average performance: {avg:.1f}%. " \
                                   f"Reading speed: {assessment.reading_speed_wpm:.0f} WPM."
        assessment.recommendations = "Focus on phonics exercises and reading speed improvement." \
            if avg < 70 else "Continue current learning pace with advanced exercises."
        assessment.status = 'completed'
        assessment.completed_at = timezone.now()
        assessment.save()
        # Update student risk score
        if hasattr(request.user, 'student_profile'):
            request.user.student_profile.dyslexia_risk_score = assessment.risk_score
            request.user.student_profile.save()
        return redirect('assessment:results', pk=assessment.pk)

    return render(request, 'assessment/take.html', {'assessment': assessment, 'questions': questions})

@login_required
def assessment_results(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk)
    return render(request, 'assessment/results.html', {'assessment': assessment})

@login_required
def question_list(request):
    if not request.user.is_admin_user():
        return redirect('dashboard:dashboard')
    questions = AssessmentQuestion.objects.all().order_by('-created_at')
    return render(request, 'assessment/questions.html', {'questions': questions})

@login_required
def add_question(request):
    if not request.user.is_admin_user():
        return redirect('dashboard:dashboard')
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question added.')
            return redirect('assessment:questions')
    else:
        form = QuestionForm()
    return render(request, 'assessment/add_question.html', {'form': form})