from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserPreferences

@login_required
def accessibility_settings(request):
    prefs, _ = UserPreferences.objects.get_or_create(user=request.user)
    return render(request, 'accessibility/settings.html', {'prefs': prefs})

@login_required
def save_preferences(request):
    if request.method == 'POST':
        prefs, _ = UserPreferences.objects.get_or_create(user=request.user)
        prefs.font_size = request.POST.get('font_size', 'medium')
        prefs.font_family = request.POST.get('font_family', 'arial')
        prefs.theme = request.POST.get('theme', 'light')
        prefs.preferred_language = request.POST.get('preferred_language', 'English')
        prefs.text_spacing = request.POST.get('text_spacing') == 'on'
        prefs.reading_ruler = request.POST.get('reading_ruler') == 'on'
        prefs.tts_enabled = request.POST.get('tts_enabled') == 'on'
        prefs.save()
        messages.success(request, 'Accessibility preferences saved!')
    return redirect('accessibility:settings')