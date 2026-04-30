"""
Tasks 3.2 → 3.5  — Text Spam Detection Model
- Load spam.csv, clean text, train/test split 80/20
- TF-IDF + MultinomialNB pipeline
- Evaluate (accuracy, precision, recall)
- Save as /models/text_spam_model.joblib
"""
import os
import re
import string
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, classification_report

# ─── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_PATH  = os.path.join(BASE_DIR, '..', 'models', 'data', 'spam.csv')
MODEL_PATH = os.path.join(BASE_DIR, '..', 'models', 'text_spam_model.joblib')

# ─── Task 3.2: Load & clean ───────────────────────────────────────────────────
print("[3.2] Loading and cleaning dataset...")
df = pd.read_csv(DATA_PATH, encoding='latin-1', usecols=[0, 1], names=['label', 'text'], header=0)
df = df.dropna(subset=['label', 'text'])
df = df[df['label'].isin(['ham', 'spam'])].reset_index(drop=True)

def clean_text(text: str) -> str:
    """Lowercase, remove punctuation, strip extra spaces."""
    text = text.lower()
    text = re.sub(f"[{re.escape(string.punctuation)}]", " ", text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

df['clean_text'] = df['text'].apply(clean_text)
df['label_int']  = df['label'].map({'ham': 0, 'spam': 1})

print(f"    Total samples : {len(df)}")
print(f"    Spam samples  : {df['label_int'].sum()}")
print(f"    Ham samples   : {(df['label_int'] == 0).sum()}")

X_train, X_test, y_train, y_test = train_test_split(
    df['clean_text'], df['label_int'],
    test_size=0.20, random_state=42, stratify=df['label_int']
)
print(f"    Train / Test  : {len(X_train)} / {len(X_test)}")

# ─── Task 3.3: Build TF-IDF + MultinomialNB pipeline ─────────────────────────
print("\n[3.3] Building TF-IDF + MultinomialNB pipeline...")
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(
        max_features=10_000,
        ngram_range=(1, 2),      # unigrams + bigrams
        sublinear_tf=True,
        min_df=2,
    )),
    ('clf', MultinomialNB(alpha=0.1)),
])

# ─── Task 3.4: Train & evaluate ───────────────────────────────────────────────
print("[3.4] Training pipeline...")
pipeline.fit(X_train, y_train)

y_pred = pipeline.predict(X_test)
accuracy  = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall    = recall_score(y_test, y_pred)

print(f"\n    Accuracy  : {accuracy:.4f}  ({accuracy*100:.2f}%)")
print(f"    Precision : {precision:.4f}")
print(f"    Recall    : {recall:.4f}")
print("\n    Full Classification Report:")
print(classification_report(y_test, y_pred, target_names=['ham', 'spam']))

# ─── Task 3.5: Export model ───────────────────────────────────────────────────
print("[3.5] Saving pipeline to disk...")
joblib.dump(pipeline, MODEL_PATH)
size = os.path.getsize(MODEL_PATH)
print(f"    Saved: {MODEL_PATH}  ({size:,} bytes)")
print("\n[DONE] Text spam model ready!")
