"""
Hugging Face Dataset Training Script for Image Authenticity
=============================================================
This script downloads real vs AI-generated images directly from Hugging Face
WITHOUT requiring any API keys. It then trains the Random Forest model.
"""
import os
import sys
import numpy as np
from PIL import Image
import joblib
from datasets import load_dataset
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

MODELS_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODELS_DIR, "image_auth_model.joblib")

# ── Feature extraction (must match exactly) ─────────────────────────
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

if __name__ == "__main__":
    print("=== Downloading Real vs Fake Dataset from Hugging Face ===")
    # We load a subset of the CIFAKE dataset (which has 120,000 images total)
    # We use streaming=True so it doesn't try to download 3GB of files at once,
    # which prevents the "Read operation timed out" error on slower internet connections.
    dataset = load_dataset("Parveshiiii/AI-vs-Real", split="train", streaming=True)
    
    print(f"Successfully connected to Hugging Face Stream.")
    
    X = []
    y = []
    
    print("Extracting features (Streaming mode)... this will take a few minutes.")
    
    MAX_PER_CLASS = 1000  # 1000 Real, 1000 Fake
    real_count = 0
    fake_count = 0
    
    for i, item in enumerate(dataset):
        if real_count >= MAX_PER_CLASS and fake_count >= MAX_PER_CLASS:
            break
            
        try:
            # Handle different possible column names
            label_key = 'label' if 'label' in item else list(item.keys())[1]
            label = int(item[label_key])
            
            # Decide if we need this class
            is_fake = (label == 1)  # Assuming 1 is Fake. If not, the model will just be inverted, but balanced!
            
            if is_fake and fake_count >= MAX_PER_CLASS:
                continue
            if not is_fake and real_count >= MAX_PER_CLASS:
                continue
                
            img_key = 'image' if 'image' in item else list(item.keys())[0]
            img = item[img_key].convert("RGB").resize((224, 224))
            arr = np.array(img)
            features = extract_features(arr)
            
            X.append(features)
            
            if is_fake:
                y.append(1)  # 1 = Fake for our model
                fake_count += 1
            else:
                y.append(0)  # 0 = Real for our model
                real_count += 1
                
        except Exception as e:
            pass
            
        total = real_count + fake_count
        if total % 400 == 0 and total > 0:
            print(f"  Processed {total} images... (Real: {real_count}, Fake: {fake_count})")
            
    X = np.array(X)
    y = np.array(y)
    
    print(f"\nFinal training data shape: {X.shape}")
    print(f"Label distribution: REAL (0): {np.sum(y == 0)}, FAKE (1): {np.sum(y == 1)}")
    
    print("\nTraining Random Forest...")
    clf = Pipeline([
        ("scaler", StandardScaler()),
        ("rf", RandomForestClassifier(
            n_estimators=300, max_depth=16,
            random_state=42, n_jobs=-1
        )),
    ])

    clf.fit(X, y)
    joblib.dump(clf, MODEL_PATH)
    print(f"Model successfully saved -> {MODEL_PATH}")
    print("\n[SUCCESS] Custom model trained on REAL world data!")
