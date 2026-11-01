from django import forms
from .models import AssessmentQuestion, AssessmentResponse

class AssessmentResponseForm(forms.ModelForm):
    class Meta:
        model = AssessmentResponse
        fields = ['student_answer']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = AssessmentQuestion
        fields = ['question_text', 'question_type', 'correct_answer', 'difficulty']
        widgets = {
            'question_text': forms.Textarea(attrs={'rows': 3}),
            'correct_answer': forms.Textarea(attrs={'rows': 2}),
        }