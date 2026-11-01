"""
Train a Random Forest dyslexia risk classifier.
Run: python train_model.py
Upload the saved .joblib file in the admin section.
"""
import pandas as pd, numpy as np, joblib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

print("Loading dataset...")
df = pd.read_csv('dyslexia_dataset.csv')

features = ['age','gender','reading_speed_wpm','error_rate','phonological_score',
            'working_memory_score','comprehension_score','letter_reversal_count',
            'word_omission_count','repetition_count','substitution_count',
            'hesitation_count','family_history']

X = df[features]
y = df['label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
print(f"Train: {len(X_train)} | Test: {len(X_test)}")

# Random Forest
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('clf', RandomForestClassifier(n_estimators=150, max_depth=12, random_state=42, n_jobs=-1))
])

print("Training model...")
pipeline.fit(X_train, y_train)

y_pred = pipeline.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"\n✅ Accuracy: {acc*100:.2f}%")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['Low Risk','Moderate Risk','High Risk']))

cv_scores = cross_val_score(pipeline, X, y, cv=5)
print(f"Cross-validation: {cv_scores.mean()*100:.2f}% ± {cv_scores.std()*100:.2f}%")

joblib.dump(pipeline, 'dyslexia_rf_model.joblib')
joblib.dump(features, 'model_features.joblib')
print("\n✅ Model saved as: dyslexia_rf_model.joblib")
print("Feature list saved as: model_features.joblib")