from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import SpeechSession, TTSRequest
from accounts.models import CustomUser
import difflib
import re


def calculate_speech_scores(transcribed_text, passage_text, duration_seconds, word_count):
    """
    Core scoring engine — compares spoken text to original passage
    and returns detailed scores.
    """
    scores = {}

    # Clean texts
    spoken = transcribed_text.lower().strip()
    original = passage_text.lower().strip()

    spoken_words = re.findall(r'\b\w+\b', spoken)
    original_words = re.findall(r'\b\w+\b', original)

    if not spoken_words or not original_words:
        return {
            'fluency_score': 0,
            'pronunciation_score': 0,
            'grammar_score': 0,
            'accuracy_score': 0,
            'reading_speed_wpm': 0,
            'words_correct': 0,
            'words_total': len(original_words),
            'words_missed': original_words,
            'words_extra': spoken_words,
            'similarity_ratio': 0,
            'error_count': len(original_words),
            'feedback': ['No speech detected. Please try again.'],
            'strengths': [],
            'improvements': ['Speak clearly and close to the microphone.'],
        }

    # ── 1. ACCURACY SCORE ──────────────────────────────────────────────
    matcher = difflib.SequenceMatcher(None, original_words, spoken_words)
    similarity_ratio = matcher.ratio()
    accuracy_score = round(similarity_ratio * 100, 1)

    # Count correct words
    correct_words = 0
    matched_blocks = matcher.get_matching_blocks()
    for block in matched_blocks:
        correct_words += block.size

    words_correct = correct_words
    words_total = len(original_words)

    # Find missed words
    words_missed = []
    words_extra = []
    opcodes = matcher.get_opcodes()
    for tag, i1, i2, j1, j2 in opcodes:
        if tag == 'delete':
            words_missed.extend(original_words[i1:i2])
        elif tag == 'insert':
            words_extra.extend(spoken_words[j1:j2])
        elif tag == 'replace':
            words_missed.extend(original_words[i1:i2])

    error_count = len(words_missed) + len(words_extra)

    # ── 2. READING SPEED (WPM) ─────────────────────────────────────────
    if duration_seconds and duration_seconds > 0:
        wpm = round((len(spoken_words) / duration_seconds) * 60, 1)
    else:
        wpm = 0

    # Ideal reading speed: 90–150 wpm for children, 150–200 for adults
    if 90 <= wpm <= 200:
        speed_score = 100
    elif 70 <= wpm < 90 or 200 < wpm <= 250:
        speed_score = 80
    elif 50 <= wpm < 70 or 250 < wpm <= 300:
        speed_score = 60
    elif wpm > 0:
        speed_score = 40
    else:
        speed_score = 0

    # ── 3. FLUENCY SCORE ───────────────────────────────────────────────
    # Based on accuracy + speed together
    fluency_score = round((accuracy_score * 0.6) + (speed_score * 0.4), 1)

    # ── 4. PRONUNCIATION SCORE ─────────────────────────────────────────
    # Based on word-level accuracy (close matches get partial credit)
    pronunciation_points = 0
    for orig_word in original_words:
        best_match = max(
            (difflib.SequenceMatcher(None, orig_word, sp_word).ratio()
             for sp_word in spoken_words),
            default=0
        )
        pronunciation_points += best_match

    pronunciation_score = round(
        (pronunciation_points / max(len(original_words), 1)) * 100, 1
    )

    # ── 5. GRAMMAR / STRUCTURE SCORE ───────────────────────────────────
    # Check sentence completeness and word order
    orig_sentences = re.split(r'[.!?]+', original)
    spoken_sentences = re.split(r'[.!?]+', spoken)

    sentence_scores = []
    for orig_s in orig_sentences:
        orig_s = orig_s.strip()
        if not orig_s:
            continue
        best = max(
            (difflib.SequenceMatcher(None, orig_s, sp_s.strip()).ratio()
             for sp_s in spoken_sentences if sp_s.strip()),
            default=0
        )
        sentence_scores.append(best)

    grammar_score = round(
        (sum(sentence_scores) / max(len(sentence_scores), 1)) * 100, 1
    )

    # ── 6. BUILD FEEDBACK ──────────────────────────────────────────────
    feedback = []
    strengths = []
    improvements = []

    # Overall performance
    if accuracy_score >= 90:
        strengths.append('Excellent accuracy — you read most words correctly!')
    elif accuracy_score >= 75:
        strengths.append('Good accuracy overall.')
    elif accuracy_score >= 60:
        improvements.append('Focus on reading each word carefully.')
    else:
        improvements.append('Practice reading the passage slowly before recording.')

    # Speed feedback
    if wpm >= 90 and wpm <= 200:
        strengths.append(f'Good reading speed at {wpm} words per minute.')
    elif wpm < 60 and wpm > 0:
        improvements.append(f'Reading speed is {wpm} wpm — try to read more smoothly.')
    elif wpm > 250:
        improvements.append(f'Reading too fast at {wpm} wpm — slow down for clarity.')

    # Pronunciation feedback
    if pronunciation_score >= 85:
        strengths.append('Clear pronunciation throughout.')
    elif pronunciation_score >= 70:
        feedback.append('Some words could be pronounced more clearly.')
    else:
        improvements.append('Focus on pronouncing each syllable distinctly.')

    # Missed words feedback
    if words_missed:
        top_missed = words_missed[:5]
        improvements.append(f'Words to practice: {", ".join(top_missed)}')

    # Grammar feedback
    if grammar_score >= 85:
        strengths.append('Good sentence structure and flow.')
    elif grammar_score < 60:
        improvements.append('Try to maintain the sentence structure of the passage.')

    return {
        'fluency_score': min(fluency_score, 100),
        'pronunciation_score': min(pronunciation_score, 100),
        'grammar_score': min(grammar_score, 100),
        'accuracy_score': min(accuracy_score, 100),
        'reading_speed_wpm': wpm,
        'words_correct': words_correct,
        'words_total': words_total,
        'words_missed': words_missed[:10],  # top 10
        'words_extra': words_extra[:5],
        'similarity_ratio': round(similarity_ratio * 100, 1),
        'error_count': error_count,
        'feedback': feedback,
        'strengths': strengths,
        'improvements': improvements,
    }


@login_required
def speech_home(request):
    sessions = SpeechSession.objects.filter(
        student=request.user
    ).order_by('-created_at')[:5]
    return render(request, 'speech/home.html', {'sessions': sessions})


@login_required
def speech_session(request):
    """Start a new speech session"""
    passages = [
        "The quick brown fox jumps over the lazy dog. Reading is an important skill that helps us learn and grow every day. Practice makes perfect when we work hard and stay focused on our goals.",
        "Once upon a time, a young girl named Lily loved to read books. She visited the library every week and discovered new worlds through stories. Books helped her understand people and places she had never seen.",
        "The sun rises in the east and sets in the west. Every morning brings a new chance to learn something wonderful. Science helps us understand why the sky is blue and how birds can fly.",
        "Learning to spell can be challenging but rewarding. Break words into smaller parts called syllables. Practice each syllable slowly and then combine them together to say the whole word clearly.",
        "Phonics is the method of learning to read by connecting letters to sounds. The letter A makes different sounds in different words. Understanding phonics helps us decode new words we have never seen before.",
    ]
    import random
    passage = random.choice(passages)

    # Create a new session
    session = SpeechSession.objects.create(
        student=request.user,
        session_type='reading',
        passage_text=passage,
        status='in_progress',
    )
    return render(request, 'speech/session.html', {'session': session})


@login_required
def analyze_speech(request):
    """Process submitted speech transcript and generate report"""
    if request.method != 'POST':
        return redirect('speech:home')

    transcribed_text = request.POST.get('transcribed_text', '').strip()
    passage_text = request.POST.get('passage_text', '').strip()
    duration_seconds = int(request.POST.get('duration_seconds', 0))
    word_count = int(request.POST.get('word_count', 0))
    session_id = request.POST.get('session_id')

    if not transcribed_text:
        messages.error(request, 'No speech was detected. Please try recording again.')
        return redirect('speech:session')

    if not passage_text:
        passage_text = transcribed_text  # fallback

    # Calculate all scores
    scores = calculate_speech_scores(
        transcribed_text, passage_text, duration_seconds, word_count
    )

    # Save/update session
    if session_id:
        try:
            session = SpeechSession.objects.get(pk=session_id, student=request.user)
        except SpeechSession.DoesNotExist:
            session = SpeechSession(student=request.user)
    else:
        session = SpeechSession(student=request.user)

    session.transcribed_text = transcribed_text
    session.passage_text = passage_text
    session.duration_seconds = duration_seconds
    session.word_count = word_count
    session.fluency_score = scores['fluency_score']
    session.pronunciation_score = scores['pronunciation_score']
    session.grammar_score = scores['grammar_score']
    session.accuracy_score = scores['accuracy_score']
    session.reading_speed_wpm = scores['reading_speed_wpm']
    session.words_correct = scores['words_correct']
    session.words_total = scores['words_total']
    session.status = 'completed'
    session.completed_at = timezone.now()
    session.save()

    # Log to audit
    try:
        from reports.models import AuditLog
        AuditLog.objects.create(
            user=request.user,
            action='speech_session',
            description=f'{request.user.username} completed speech session. '
                        f'Fluency: {scores["fluency_score"]}%, '
                        f'Accuracy: {scores["accuracy_score"]}%',
            ip_address=request.META.get('REMOTE_ADDR')
        )
    except Exception:
        pass

    return render(request, 'speech/report.html', {
        'session': session,
        'scores': scores,
        'transcribed_text': transcribed_text,
        'passage_text': passage_text,
    })


@login_required
def tts_view(request):
    """Text to speech page"""
    audio_url = None
    text_input = ''
    if request.method == 'POST':
        text_input = request.POST.get('text', '').strip()
        if text_input:
            try:
                from gtts import gTTS
                import os
                import uuid
                filename = f'tts_{uuid.uuid4().hex[:8]}.mp3'
                filepath = f'media/tts_audio/{filename}'
                os.makedirs('media/tts_audio', exist_ok=True)
                tts = gTTS(text=text_input, lang='en', slow=False)
                tts.save(filepath)
                audio_url = f'/media/tts_audio/{filename}'
                TTSRequest.objects.create(
                    user=request.user,
                    text=text_input,
                    audio_file=f'tts_audio/{filename}'
                )
            except Exception as e:
                messages.error(request, f'TTS error: {str(e)}')
    return render(request, 'speech/tts.html', {
        'audio_url': audio_url,
        'text_input': text_input
    })


@login_required
def sessions_list(request):
    sessions = SpeechSession.objects.filter(
        student=request.user
    ).order_by('-created_at')
    return render(request, 'speech/sessions.html', {'sessions': sessions})


@login_required
def session_detail(request, pk):
    session = get_object_or_404(SpeechSession, pk=pk, student=request.user)
    return render(request, 'speech/session_detail.html', {'session': session})