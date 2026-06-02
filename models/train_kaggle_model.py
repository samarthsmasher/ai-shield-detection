"""
Kaggle Dataset Training Script for Image Authenticity - Fast Version
===================================================================
Trains the RandomForest model on Kaggle real-vs-fake face dataset.
Uses parallel processing to speed up feature extraction.
"""
import os
import sys
import glob
import numpy as np
from PIL import Image
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report
from joblib import Parallel, delayed

MODELS_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.normpath(os.path.join(MODELS_DIR, "image_auth_model.joblib"))
DATASET_ROOT = os.path.normpath(os.path.join(MODELS_DIR, "..", "real-vs-fake"))

sys.path.insert(0, MODELS_DIR)
from image_inference import extract_features

TRAIN_REAL = os.path.join(DATASET_ROOT, "train", "real")
TRAIN_FAKE = os.path.join(DATASET_ROOT, "train", "fake")
VALID_REAL = os.path.join(DATASET_ROOT, "valid", "real")
VALID_FAKE = os.path.join(DATASET_ROOT, "valid", "fake")


def process_single_image(path, label):
    """Worker function to extract features from a single image."""
    try:
        img = Image.open(path).convert("RGB").resize((224, 224))
        feats = extract_features(np.array(img))
        return feats, label
    except Exception:
        return None


def load_dataset_parallel(real_dir, fake_dir, max_images_per_class=15000):
    """Loads and extracts features in parallel for both real and fake classes."""
    real_paths = glob.glob(os.path.join(real_dir, "*.jpg"))[:max_images_per_class]
    fake_paths = glob.glob(os.path.join(fake_dir, "*.jpg"))[:max_images_per_class]

    print(f"  Found {len(real_paths)} real and {len(fake_paths)} fake files to process.")

    tasks = []
    for p in real_paths:
        tasks.append((p, 0))  # 0 = Real
    for p in fake_paths:
        tasks.append((p, 1))  # 1 = Fake

    print(f"  Running feature extraction in parallel using all CPU cores...")
    results = Parallel(n_jobs=-1)(
        delayed(process_single_image)(p, lbl) for p, lbl in tasks
    )

    X, y = [], []
    for res in results:
        if res is not None:
            X.append(res[0])
            y.append(res[1])

    return np.array(X), np.array(y)


if __name__ == "__main__":
    print("=" * 60)
    print("  Kaggle Real-vs-Fake Model Training (Fast Parallel version)")
    print("=" * 60)

    # Verify dataset directories exist
    for d in [TRAIN_REAL, TRAIN_FAKE, VALID_REAL, VALID_FAKE]:
        if not os.path.exists(d):
            print(f"ERROR: Directory not found: {d}")
            sys.exit(1)

    # 1. Load training data
    print("\n[1/4] Loading training dataset (15000 per class)...")
    X_train, y_train = load_dataset_parallel(TRAIN_REAL, TRAIN_FAKE, max_images_per_class=15000)
    print(f"  Training set ready: {len(X_train)} samples.")

    # 2. Load validation data
    print("\n[2/4] Loading validation dataset (1000 per class)...")
    X_val, y_val = load_dataset_parallel(VALID_REAL, VALID_FAKE, max_images_per_class=1000)
    print(f"  Validation set ready: {len(X_val)} samples.")

    # 3. Train model
    print("\n[3/4] Training RandomForest classifier on training data...")
    clf = Pipeline([
        ("scaler", StandardScaler()),
        ("rf", RandomForestClassifier(
            n_estimators=300,
            max_depth=16,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )),
    ])
    clf.fit(X_train, y_train)
    print("  Training complete.")

    # 4. Evaluate
    print("\n[4/4] Evaluating on validation dataset...")
    y_pred = clf.predict(X_val)
    acc = accuracy_score(y_val, y_pred)
    print(f"  Validation Accuracy: {acc*100:.2f}%")
    print("\n  Classification Report:")
    print(classification_report(y_val, y_pred, target_names=["real", "fake"]))

    # Save trained model
    joblib.dump(clf, MODEL_PATH)
    print(f"\n  Model successfully saved to -> {MODEL_PATH}")
    print(f"  Model size: {os.path.getsize(MODEL_PATH) / 1024 / 1024:.2f} MB")
    print("\n[SUCCESS] Model perfectly trained and deployed!")
