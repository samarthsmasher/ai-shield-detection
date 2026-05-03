"""
Kaggle Dataset Training Script for Image Authenticity
=====================================================
Trains the RandomForest model on 50k real + 50k fake faces from Kaggle.

Dataset path: C:\\2ST Sem Study Material & Assignment\\ASEP 2\\chat gpt\\real-vs-fake
Structure:
  real-vs-fake/
    train/real/   ← 51,081 images
    train/fake/   ← 50,960 images
    valid/real/
    valid/fake/

HOW TO RUN:
  python models/train_kaggle_model.py

This will take 30-90 minutes to extract features from ~100k images.
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

MODELS_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH   = os.path.join(MODELS_DIR, "image_auth_model.joblib")

# ── Dataset root (the extracted Kaggle folder) ────────────────────────────────
DATASET_ROOT = os.path.normpath(
    os.path.join(MODELS_DIR, "..", "real-vs-fake")
)

TRAIN_REAL = os.path.join(DATASET_ROOT, "train", "real")
TRAIN_FAKE = os.path.join(DATASET_ROOT, "train", "fake")
VALID_REAL = os.path.join(DATASET_ROOT, "valid", "real")
VALID_FAKE = os.path.join(DATASET_ROOT, "valid", "fake")

# ── Feature extraction (must EXACTLY match image_inference.py) ────────────────
def extract_features(img_arr: np.ndarray) -> list:
    arr  = img_arr.astype(np.float32)
    gray = arr.mean(axis=2)

    lap_x   = gray[:, 2:] - 2*gray[:, 1:-1] + gray[:, :-2]
    lap_y   = gray[2:, :] - 2*gray[1:-1, :] + gray[:-2, :]
    lap_var = float(np.var(lap_x) + np.var(lap_y))

    entropy = 0.0
    for ch in range(3):
        h, _ = np.histogram(arr[:, :, ch], bins=64, range=(0, 256))
        h     = h / (h.sum() + 1e-9)
        entropy -= float(np.sum(h * np.log(h + 1e-9)))
    entropy /= 3.0

    gx       = np.diff(gray, axis=1)
    gy       = np.diff(gray, axis=0)
    grad_mag = float(np.mean(np.abs(gx)) + np.mean(np.abs(gy)))

    local_stds     = [np.std(arr[i:i+32, j:j+32])
                      for i in range(0, 192, 32) for j in range(0, 192, 32)]
    mean_local_std = float(np.mean(local_stds))

    small     = arr[::4, ::4, :]
    up        = np.repeat(np.repeat(small, 4, axis=0), 4, axis=1)[:224, :224]
    hf_energy = float(np.mean(np.abs(arr - up)))

    patch_vars    = [np.var(arr[i:i+16, j:j+16])
                     for i in range(0, 208, 16) for j in range(0, 208, 16)]
    min_patch_var = float(np.min(patch_vars))

    unique_px = len(np.unique(arr.reshape(-1, 3).astype(np.uint8), axis=0))
    color_div = min(unique_px / 5000.0, 1.0)

    smooth    = (arr[:-2,:-2] + arr[2:,:-2] + arr[:-2,2:] + arr[2:,2:]) / 4.0
    noise_std = float(np.std(arr[1:-1, 1:-1] - smooth))

    return [lap_var, entropy, grad_mag, mean_local_std,
            hf_energy, min_patch_var, color_div, noise_std]


# ── Load images from a directory ─────────────────────────────────────────────
def load_images(directory: str, label: int, max_images: int = 50000) -> tuple:
    X, y = [], []
    paths = glob.glob(os.path.join(directory, "*.jpg"))[:max_images]
    paths += glob.glob(os.path.join(directory, "*.jpeg"))[:max(0, max_images - len(paths))]
    paths += glob.glob(os.path.join(directory, "*.png"))[:max(0, max_images - len(paths))]
    paths = paths[:max_images]

    tag = "REAL" if label == 0 else "FAKE"
    print(f"  Processing {len(paths)} {tag} images from {os.path.basename(directory)}/...")

    for idx, path in enumerate(paths):
        try:
            img = Image.open(path).convert("RGB").resize((224, 224))
            X.append(extract_features(np.array(img)))
            y.append(label)
        except Exception:
            pass
        if (idx + 1) % 5000 == 0:
            print(f"    {idx+1}/{len(paths)} done...")

    return X, y


# ── Main training ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  Kaggle Real-vs-Fake Training (50k + 50k)")
    print("=" * 60)

    # Verify dataset exists
    for d in [TRAIN_REAL, TRAIN_FAKE, VALID_REAL, VALID_FAKE]:
        if not os.path.exists(d):
            print(f"ERROR: Directory not found: {d}")
            sys.exit(1)

    # ── Load training data ────────────────────────────────────────────────────
    print("\n[1/4] Loading training data...")
    X_train, y_train = [], []

    rx, ry = load_images(TRAIN_REAL, label=0, max_images=50000)
    X_train.extend(rx); y_train.extend(ry)

    fx, fy = load_images(TRAIN_FAKE, label=1, max_images=50000)
    X_train.extend(fx); y_train.extend(fy)

    X_train = np.array(X_train)
    y_train = np.array(y_train)
    print(f"  Training set: {len(X_train)} samples ({y_train.sum()} fake, {(y_train==0).sum()} real)")

    # ── Load validation data ──────────────────────────────────────────────────
    print("\n[2/4] Loading validation data...")
    X_val, y_val = [], []

    rx, ry = load_images(VALID_REAL, label=0, max_images=10000)
    X_val.extend(rx); y_val.extend(ry)

    fx, fy = load_images(VALID_FAKE, label=1, max_images=10000)
    X_val.extend(fx); y_val.extend(fy)

    X_val = np.array(X_val)
    y_val = np.array(y_val)
    print(f"  Validation set: {len(X_val)} samples")

    # ── Train model ───────────────────────────────────────────────────────────
    print("\n[3/4] Training RandomForest on Kaggle data...")
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
    print("  Training complete!")

    # ── Evaluate on validation set ────────────────────────────────────────────
    print("\n[4/4] Evaluating on validation set...")
    y_pred = clf.predict(X_val)
    acc    = accuracy_score(y_val, y_pred)
    print(f"  Validation accuracy: {acc*100:.2f}%")
    print("\n  Classification report:")
    print(classification_report(y_val, y_pred, target_names=["real", "fake"]))

    # ── Save model ────────────────────────────────────────────────────────────
    joblib.dump(clf, MODEL_PATH)
    print(f"\n  Model saved -> {MODEL_PATH}")
    print(f"  Model size  : {os.path.getsize(MODEL_PATH) / 1024 / 1024:.1f} MB")
    print("\n[SUCCESS] Kaggle model trained and saved!")

import os
import sys
import glob
import numpy as np
from PIL import Image
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score

# Ensure Kaggle API is available
try:
    import kaggle
except OSError:
    print("WARNING: Kaggle API credentials not found. Please place kaggle.json in your .kaggle folder.")
    sys.exit(1)

MODELS_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODELS_DIR, "image_auth_model.joblib")
DATA_DIR   = os.path.join(MODELS_DIR, "kaggle_data")

# ── Feature extraction (matches your inference script) ─────────────────────
def extract_features(img_arr: np.ndarray) -> list:
    arr = img_arr.astype(np.float32)
    gray = arr.mean(axis=2)

    lap_x = gray[:, 2:] - 2*gray[:, 1:-1] + gray[:, :-2]
    lap_y = gray[2:, :] - 2*gray[1:-1, :] + gray[:-2, :]
    lap_var = float(np.var(lap_x) + np.var(lap_y))

    entropy = 0.0
    for ch in range(3):
        h, _ = np.histogram(arr[:, :, ch], bins=64, range=(0, 256))
        h = h / (h.sum() + 1e-9)
        entropy -= float(np.sum(h * np.log(h + 1e-9)))
    entropy /= 3.0

    gx = np.diff(gray, axis=1)
    gy = np.diff(gray, axis=0)
    grad_mag = float(np.mean(np.abs(gx)) + np.mean(np.abs(gy)))

    local_stds = [np.std(arr[i:i+32, j:j+32])
                  for i in range(0, 192, 32) for j in range(0, 192, 32)]
    mean_local_std = float(np.mean(local_stds))

    small = arr[::4, ::4, :]
    up    = np.repeat(np.repeat(small, 4, axis=0), 4, axis=1)[:224, :224]
    hf_energy = float(np.mean(np.abs(arr - up)))

    patch_vars = [np.var(arr[i:i+16, j:j+16])
                  for i in range(0, 208, 16) for j in range(0, 208, 16)]
    min_patch_var = float(np.min(patch_vars))

    unique_px = len(np.unique(arr.reshape(-1, 3).astype(np.uint8), axis=0))
    color_div = min(unique_px / 5000.0, 1.0)

    smooth = (arr[:-2, :-2] + arr[2:, :-2] + arr[:-2, 2:] + arr[2:, 2:]) / 4.0
    noise_std = float(np.std(arr[1:-1, 1:-1] - smooth))

    return [lap_var, entropy, grad_mag, mean_local_std,
            hf_energy, min_patch_var, color_div, noise_std]

# ── Download Dataset ──────────────────────────────────────────────────────────
def download_dataset():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # Dataset contains ~140k real and fake faces
    dataset_name = "xhlulu/140k-real-and-fake-faces"
    
    print(f"Downloading {dataset_name} from Kaggle (This will take a while)...")
    kaggle.api.dataset_download_cli(dataset_name, path=DATA_DIR, unzip=True)
    print("Download and extraction complete.")

# ── Process Images ────────────────────────────────────────────────────────────
def load_and_extract_features(max_images=100000): # Process up to 100k to save time
    X, y = [], []
    
    # Paths (adjust based on extracted folder structure)
    real_dir = os.path.join(DATA_DIR, "real_vs_fake", "real-vs-fake", "train", "real")
    fake_dir = os.path.join(DATA_DIR, "real_vs_fake", "real-vs-fake", "train", "fake")
    
    if not os.path.exists(real_dir) or not os.path.exists(fake_dir):
        print("Error: Could not find extracted image directories.")
        return [], []
        
    real_images = glob.glob(os.path.join(real_dir, "*.jpg"))[:max_images//2]
    fake_images = glob.glob(os.path.join(fake_dir, "*.jpg"))[:max_images//2]
    
    print(f"Extracting features from {len(real_images)} REAL images...")
    for idx, path in enumerate(real_images):
        try:
            img = Image.open(path).convert("RGB").resize((224, 224))
            X.append(extract_features(np.array(img)))
            y.append(0) # 0 = real
        except Exception:
            pass
        if (idx+1) % 1000 == 0: print(f"  Processed {idx+1} real images...")

    print(f"Extracting features from {len(fake_images)} FAKE images...")
    for idx, path in enumerate(fake_images):
        try:
            img = Image.open(path).convert("RGB").resize((224, 224))
            X.append(extract_features(np.array(img)))
            y.append(1) # 1 = fake
        except Exception:
            pass
        if (idx+1) % 1000 == 0: print(f"  Processed {idx+1} fake images...")

    return np.array(X), np.array(y)

# ── Train & Save ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    download_dataset()
    X, y = load_and_extract_features(max_images=100000) # Load 1 Lakh images (50k real, 50k fake)
    
    if len(X) == 0:
        print("No data extracted. Exiting.")
        sys.exit(1)
        
    print("\nTraining Random Forest on Kaggle Data...")
    clf = Pipeline([
        ("scaler", StandardScaler()),
        ("rf", RandomForestClassifier(
            n_estimators=200, max_depth=15, # Deeper tree for larger dataset
            random_state=42, n_jobs=-1
        )),
    ])

    clf.fit(X, y)
    joblib.dump(clf, MODEL_PATH)
    print(f"Model saved to -> {MODEL_PATH}")
    print("\n[SUCCESS] Image model trained on Kaggle dataset successfully!")
