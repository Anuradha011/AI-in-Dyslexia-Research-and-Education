"""
Generates a synthetic dyslexia reading assessment dataset.
Run: python generate_dataset.py
"""
import pandas as pd
import numpy as np
import random

random.seed(42)
np.random.seed(42)
n = 3000

rows = []
for i in range(n):
    reading_speed_wpm = np.random.normal(100, 40)
    error_rate = np.random.beta(2, 5) * 100
    phonological_score = np.random.normal(65, 20)
    working_memory_score = np.random.normal(60, 18)
    comprehension_score = np.random.normal(65, 22)
    letter_reversal_count = random.randint(0, 12)
    word_omission_count = random.randint(0, 10)
    repetition_count = random.randint(0, 8)
    substitution_count = random.randint(0, 9)
    hesitation_count = random.randint(0, 15)
    age = random.randint(6, 18)
    gender = random.choice([0, 1])
    family_history = random.choice([0, 0, 0, 1])

    reading_speed_wpm = max(20, min(250, reading_speed_wpm))
    error_rate = max(0, min(100, error_rate))
    phonological_score = max(0, min(100, phonological_score))
    working_memory_score = max(0, min(100, working_memory_score))
    comprehension_score = max(0, min(100, comprehension_score))

    # Risk = weighted formula
    risk = (
        (100 - phonological_score) * 0.35 +
        error_rate * 0.25 +
        (100 - working_memory_score) * 0.2 +
        letter_reversal_count * 2.5 +
        (100 - comprehension_score) * 0.15 +
        family_history * 8
    )
    risk = max(0, min(100, risk))

    if risk > 65:
        label = 2  # high risk
    elif risk > 40:
        label = 1  # moderate
    else:
        label = 0  # low

    rows.append({
        'age': age, 'gender': gender,
        'reading_speed_wpm': round(reading_speed_wpm, 2),
        'error_rate': round(error_rate, 2),
        'phonological_score': round(phonological_score, 2),
        'working_memory_score': round(working_memory_score, 2),
        'comprehension_score': round(comprehension_score, 2),
        'letter_reversal_count': letter_reversal_count,
        'word_omission_count': word_omission_count,
        'repetition_count': repetition_count,
        'substitution_count': substitution_count,
        'hesitation_count': hesitation_count,
        'family_history': family_history,
        'risk_score': round(risk, 2),
        'label': label
    })

df = pd.DataFrame(rows)
df.to_csv('dyslexia_dataset.csv', index=False)
print(f"✅ Dataset generated: dyslexia_dataset.csv ({n} records)")
print(f"Label distribution:\n{df['label'].value_counts().rename({0:'Low Risk',1:'Moderate',2:'High Risk'})}")