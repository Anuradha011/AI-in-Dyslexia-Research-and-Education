from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import LearningPlan, LearningModule, Exercise, StudentProgress
from accounts.models import CustomUser

@login_required
def learning_home(request):
    if request.user.role == 'student':
        plans = LearningPlan.objects.filter(student=request.user, is_active=True)
    elif request.user.role in ['educator', 'admin']:
        plans = LearningPlan.objects.all().order_by('-created_at')
    else:
        plans = LearningPlan.objects.filter(student__student_profile__parent=request.user)
    return render(request, 'learning/home.html', {'plans': plans})

@login_required
def plan_detail(request, pk):
    plan = get_object_or_404(LearningPlan, pk=pk)
    modules = plan.modules.all()
    return render(request, 'learning/plan_detail.html', {'plan': plan, 'modules': modules})

@login_required
def create_plan(request, student_id):
    if not (request.user.is_admin_user() or request.user.role == 'educator'):
        return redirect('learning:home')
    student = get_object_or_404(CustomUser, pk=student_id)
    if request.method == 'POST':
        title = request.POST.get('title', 'Personalized Learning Plan')
        description = request.POST.get('description', '')
        plan = LearningPlan.objects.create(
            student=student, title=title, description=description,
            created_by=request.user
        )
        # Auto-generate modules based on student's risk score
        modules_data = [
            ('Phonics Foundation', 'phonics', 'beginner', 'Practice letter-sound relationships. Focus on consonants and vowels.'),
            ('Word Recognition', 'reading', 'beginner', 'Practice recognizing common sight words quickly.'),
            ('Spelling Patterns', 'spelling', 'intermediate', 'Learn common spelling rules and patterns.'),
            ('Reading Comprehension', 'comprehension', 'intermediate', 'Read short passages and answer questions.'),
            ('Working Memory Games', 'memory', 'beginner', 'Sequence and memory exercises to improve retention.'),
        ]
        for i, (title_m, mtype, diff, content) in enumerate(modules_data, 1):
            LearningModule.objects.create(
                plan=plan, title=title_m, module_type=mtype,
                difficulty=diff, content=content, order=i
            )
        messages.success(request, f'Learning plan created for {student.username}.')
        return redirect('learning:plan_detail', pk=plan.pk)
    return render(request, 'learning/create_plan.html', {'student': student})

@login_required
def exercise_list(request):
    exercises = Exercise.objects.filter(is_active=True).order_by('difficulty')
    return render(request, 'learning/exercises.html', {'exercises': exercises})

@login_required
def exercise_detail(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk)
    result = None
    if request.method == 'POST':
        answer = request.POST.get('answer', '').strip().lower()
        correct = exercise.answer.strip().lower()
        result = 'correct' if answer == correct else 'incorrect'
    return render(request, 'learning/exercise.html', {'exercise': exercise, 'result': result})

@login_required
def progress_view(request):
    if request.user.role == 'student':
        progress = StudentProgress.objects.filter(student=request.user).order_by('-recorded_at')
    else:
        progress = StudentProgress.objects.all().order_by('-recorded_at')
    return render(request, 'learning/progress.html', {'progress': progress})