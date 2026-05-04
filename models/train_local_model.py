"""
Local Dataset Training Script for Image Authenticity
=============================================================
This script trains the Random Forest model using a dataset you downloaded manually.
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

MODELS_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODELS_DIR, "image_auth_model.joblib")

# ── Feature extraction ─────────────────────────
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

def train_on_local_data(real_folder_path, fake_folder_path, max_images_per_class=5000):
    print(f"Loading REAL images from: {real_folder_path}")
    print(f"Loading FAKE images from: {fake_folder_path}")
    
    real_images = glob.glob(os.path.join(real_folder_path, "*.[jp][pn]*")) # matches .jpg, .png, .jpeg
    fake_images = glob.glob(os.path.join(fake_folder_path, "*.[jp][pn]*"))
    
    if len(real_images) == 0 or len(fake_images) == 0:
        print("\nERROR: Could not find images in the specified folders!")
        print("Please make sure the folder paths are correct and contain image files.")
        return
        
    print(f"Found {len(real_images)} real images and {len(fake_images)} fake images.")
    
    real_images = real_images[:max_images_per_class]
    fake_images = fake_images[:max_images_per_class]
    
    X = []
    y = []
    
    print(f"\nExtracting features from {len(real_images)} REAL images...")
    for i, img_path in enumerate(real_images):
        try:
            img = Image.open(img_path).convert("RGB").resize((224, 224))
            arr = np.array(img)
            X.append(extract_features(arr))
            y.append(0)  # 0 = Real
        except Exception:
            pass
        if (i+1) % 500 == 0:
            print(f"  Processed {i+1} REAL images...")

    print(f"\nExtracting features from {len(fake_images)} FAKE images...")
    for i, img_path in enumerate(fake_images):
        try:
            img = Image.open(img_path).convert("RGB").resize((224, 224))
            arr = np.array(img)
            X.append(extract_features(arr))
            y.append(1)  # 1 = Fake
        except Exception:
            pass
        if (i+1) % 500 == 0:
            print(f"  Processed {i+1} FAKE images...")

    X = np.array(X)
    y = np.array(y)
    
    print(f"\nFinal training data shape: {X.shape}")
    
    print("Training Random Forest...")
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
    print("\n[SUCCESS] Model perfectly trained on your local Kaggle dataset!")

if __name__ == "__main__":
    # USER MUST PASTE THEIR FOLDER PATHS HERE BEFORE RUNNING:
    REAL_IMAGES_FOLDER = r"C:\PATH\TO\YOUR\EXTRACTED\REAL\IMAGES"
    FAKE_IMAGES_FOLDER = r"C:\PATH\TO\YOUR\EXTRACTED\FAKE\IMAGES"
    
    train_on_local_data(REAL_IMAGES_FOLDER, FAKE_IMAGES_FOLDER, max_images_per_class=5000)
