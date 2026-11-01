from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=False)
    role = forms.ChoiceField(choices=[
        ('student', 'Student'),
        ('educator', 'Educator'),
        ('parent', 'Parent'),
    ])
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    institution = forms.CharField(max_length=200, required=False)

    class Meta:
        model = CustomUser
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'role', 'date_of_birth', 'institution',
            'password1', 'password2'
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.role = self.cleaned_data['role']
        user.institution = self.cleaned_data.get('institution', '')
        user.date_of_birth = self.cleaned_data.get('date_of_birth')
        user.is_approved = True  # auto approve on registration
        if commit:
            user.save()
        return user