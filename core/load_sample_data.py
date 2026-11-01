"""
Seeds the database with sample questions, exercises, and users.
Run: python load_sample_data.py
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from assessment.models import AssessmentQuestion
from learning.models import Exercise

questions = [
    ('Read this word aloud: "was"', 'reading', 'was', 1),
    ('What sound does the letter "ph" make?', 'phonics', 'f', 2),
    ('Spell the word: "because"', 'spelling', 'because', 2),
    ('Read: "The big dog ran fast." What did the dog do?', 'comprehension', 'ran fast', 2),
    ('Remember these letters in order: B, M, T, R', 'memory', 'b m t r', 3),
    ('What rhymes with "cat"?', 'phonics', 'bat', 1),
    ('Spell: "friend"', 'spelling', 'friend', 3),
    ('Read: "She was happy." Who was happy?', 'comprehension', 'she', 1),
    ('What sound does "ch" make in "chair"?', 'phonics', 'ch', 2),
    ('Spell: "enough"', 'spelling', 'enough', 4),
    ('Read: "The sun sets in the west." Where does the sun set?', 'comprehension', 'west', 2),
    ('Remember: 3, 7, 1, 9, 5 — what was the 3rd number?', 'memory', '1', 3),
    ('What sound does "tion" make in "nation"?', 'phonics', 'shun', 3),
    ('Spell: "necessary"', 'spelling', 'necessary', 5),
    ('Read: "Tom and Sara went to school." Name one person.', 'comprehension', 'tom', 1),
]

for qtext, qtype, answer, diff in questions:
    AssessmentQuestion.objects.get_or_create(
        question_text=qtext,
        defaults={'question_type': qtype, 'correct_answer': answer, 'difficulty': diff}
    )
print(f"✅ {len(questions)} assessment questions loaded")

exercises = [
    ('Vowel Sounds Practice', 'phonics', 'Say the vowel sound for each letter: A, E, I, O, U', 'a e i o u', 'Short vowels: a=apple, e=egg, i=insect, o=octopus, u=umbrella', 1),
    ('Sight Word Reading', 'reading', 'Read these sight words: the, was, said, have, they', 'the was said have they', 'These are common words that do not follow regular phonics rules.', 1),
    ('Rhyming Words', 'spelling', 'What word rhymes with "light" and means the opposite of wrong?', 'right', 'Think of words that end in "-ight"', 2),
    ('Sentence Comprehension', 'fill_blank', 'The cat sat on the ___. (mat/hat/bat)', 'mat', 'The most common nursery rhyme answer', 1),
    ('Word Matching', 'matching', 'Match the word to its meaning: "happy" means...', 'glad', 'Think of synonyms!', 2),
    ('Blending Sounds', 'phonics', 'Blend these sounds together: /b/ /oa/ /t/', 'boat', 'Put the sounds together quickly', 2),
    ('Reading Fluency', 'reading', 'Read aloud: "The quick brown fox jumps over the lazy dog."', 'the quick brown fox jumps over the lazy dog', 'Try to read smoothly without stopping', 3),
    ('Spelling Challenge', 'spelling', 'Spell the word that means a large body of salt water', 'ocean', 'O-C-E-A-N', 3),
]

for title, etype, content, answer, hint, diff in exercises:
    Exercise.objects.get_or_create(
        title=title,
        defaults={'exercise_type': etype, 'content': content, 'answer': answer, 'hint': hint, 'difficulty': diff}
    )
print(f"✅ {len(exercises)} exercises loaded")
print("\n🎉 Sample data loaded successfully!")