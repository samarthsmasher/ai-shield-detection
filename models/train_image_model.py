"""
Image Authenticity Classifier — Training Script
Trains a RandomForestClassifier on synthetic real vs fake image samples.
Features are pure-numpy (no scipy/torch), so it runs on Render free tier.
"""
import os, sys, io, joblib
import numpy as np
from PIL import Image
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score

MODELS_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODELS_DIR, "image_auth_model.joblib")

# ── Feature extraction (same function used in inference) ─────────────────────
def extract_features(img_arr: np.ndarray) -> list:
    """8 discriminative features from a 224×224 float32 RGB array."""
    arr = img_arr.astype(np.float32)
    gray = arr.mean(axis=2)

    # 1. Laplacian variance — real images have texture/noise; fakes are smooth
    lap_x = gray[:, 2:] - 2*gray[:, 1:-1] + gray[:, :-2]
    lap_y = gray[2:, :] - 2*gray[1:-1, :] + gray[:-2, :]
    lap_var = float(np.var(lap_x) + np.var(lap_y))

    # 2. Colour histogram entropy
    entropy = 0.0
    for ch in range(3):
        h, _ = np.histogram(arr[:, :, ch], bins=64, range=(0, 256))
        h = h / (h.sum() + 1e-9)
        entropy -= float(np.sum(h * np.log(h + 1e-9)))
    entropy /= 3.0

    # 3. Mean gradient magnitude
    gx = np.diff(gray, axis=1)
    gy = np.diff(gray, axis=0)
    grad_mag = float(np.mean(np.abs(gx)) + np.mean(np.abs(gy)))

    # 4. Mean local patch std-dev (32×32 patches)
    local_stds = [np.std(arr[i:i+32, j:j+32])
                  for i in range(0, 192, 32) for j in range(0, 192, 32)]
    mean_local_std = float(np.mean(local_stds))

    # 5. High-frequency energy (original vs 4× subsampled-then-upsampled)
    small = arr[::4, ::4, :]
    up    = np.repeat(np.repeat(small, 4, axis=0), 4, axis=1)[:224, :224]
    hf_energy = float(np.mean(np.abs(arr - up)))

    # 6. Minimum patch variance (flat regions → near zero for fakes)
    patch_vars = [np.var(arr[i:i+16, j:j+16])
                  for i in range(0, 208, 16) for j in range(0, 208, 16)]
    min_patch_var = float(np.min(patch_vars))

    # 7. Colour diversity (unique colours / 5000 cap)
    unique_px = len(np.unique(arr.reshape(-1, 3).astype(np.uint8), axis=0))
    color_div = min(unique_px / 5000.0, 1.0)

    # 8. Global noise estimate (std of difference between image and smoothed)
    smooth = (arr[:-2, :-2] + arr[2:, :-2] + arr[:-2, 2:] + arr[2:, 2:]) / 4.0
    noise_std = float(np.std(arr[1:-1, 1:-1] - smooth))

    return [lap_var, entropy, grad_mag, mean_local_std,
            hf_energy, min_patch_var, color_div, noise_std]

# ── Synthetic training data generator ────────────────────────────────────────
def make_fake_sample(rng):
    arr = np.zeros((224, 224, 3), dtype=np.float32)
    t = rng.integers(0, 6)
    if t == 0:   # solid colour
        arr[:] = rng.integers(0, 256, (1, 1, 3))
    elif t == 1: # linear gradient
        g = np.linspace(0, 255, 224, dtype=np.float32)
        arr[:, :, rng.integers(0,3)] = g[np.newaxis, :]
        arr[:, :, rng.integers(0,3)] = g[:, np.newaxis]
    elif t == 2: # checkerboard
        tile = rng.integers(8, 40)
        for r in range(224):
            for c in range(224):
                arr[r, c] = 255 if (r//tile + c//tile) % 2 == 0 else 0
    elif t == 3: # radial gradient
        cx, cy = 112, 112
        yy, xx = np.mgrid[:224, :224]
        dist = np.sqrt((xx-cx)**2 + (yy-cy)**2)
        val  = np.clip(dist / dist.max() * 255, 0, 255)
        arr[:,:,0] = val; arr[:,:,1] = 255-val; arr[:,:,2] = val*0.5
    elif t == 4: # simple shapes only
        arr[:] = rng.integers(200, 256, (1,1,3))
        cv2_x, cv2_y = rng.integers(30,180), rng.integers(30,180)
        r = rng.integers(20, 70)
        yy, xx = np.ogrid[:224, :224]
        mask = (xx - cv2_x)**2 + (yy - cv2_y)**2 <= r**2
        arr[mask] = rng.integers(0, 80, (1,3))
    else:        # tiny uniform noise (AI-like too-smooth)
        base = rng.integers(50, 200, (1, 1, 3)).astype(np.float32)
        noise = rng.normal(0, 2, (224, 224, 3)).astype(np.float32)
        arr = np.clip(base + noise, 0, 255)
    return arr

def make_real_sample(rng):
    arr = np.zeros((224, 224, 3), dtype=np.float32)
    t = rng.integers(0, 5)
    if t == 0:   # natural random noise (camera simulation)
        base = rng.integers(0, 256, (224, 224, 3)).astype(np.float32)
        for i in range(224):
            base[i, :, 0] = np.clip(base[i, :, 0] + i * 0.5, 0, 255)
        noise = rng.normal(0, 12, (224, 224, 3)).astype(np.float32)
        arr = np.clip(base + noise, 0, 255)
    elif t == 1: # sky + ground with natural grain
        sky   = rng.integers(100, 220, (112, 224, 3)).astype(np.float32)
        ground= rng.integers(20,  120, (112, 224, 3)).astype(np.float32)
        sky   += rng.normal(0, 15, sky.shape)
        ground+= rng.normal(0, 18, ground.shape)
        arr[:112] = sky; arr[112:] = ground
        arr = np.clip(arr, 0, 255)
    elif t == 2: # textured noise (fabric/wood simulation)
        x = np.linspace(0, 8*np.pi, 224)
        y = np.linspace(0, 8*np.pi, 224)
        XX, YY = np.meshgrid(x, y)
        pattern = (np.sin(XX) * np.cos(YY) * 0.5 + 0.5) * 200
        arr[:,:,0] = pattern + rng.normal(0,20,(224,224))
        arr[:,:,1] = (255-pattern) + rng.normal(0,20,(224,224))
        arr[:,:,2] = pattern*0.6 + rng.normal(0,20,(224,224))
        arr = np.clip(arr, 0, 255)
    elif t == 3: # portrait simulation (skin tones + background)
        arr[:] = rng.integers(50, 150, (1,1,3))
        arr[:] += rng.normal(0, 20, arr.shape)
        cx, cy, r = 112, 100, 60
        yy, xx = np.ogrid[:224, :224]
        mask = (xx-cx)**2 + (yy-cy)**2 <= r**2
        skin = np.array([rng.integers(140,200), rng.integers(100,160), rng.integers(80,140)], dtype=np.float32)
        arr[mask] = skin + rng.normal(0, 15, (mask.sum(), 3))
        arr = np.clip(arr, 0, 255)
    else:        # high-frequency noise image (resembles WhatsApp compressed)
        arr = rng.integers(0, 256, (224, 224, 3)).astype(np.float32)
        arr += rng.normal(0, 25, arr.shape)
        arr = np.clip(arr, 0, 255)
    return arr

# ── Generate dataset ──────────────────────────────────────────────────────────
def generate_dataset(n_per_class=600, seed=0):
    rng = np.random.default_rng(seed)
    X, y = [], []
    print(f"Generating {n_per_class} FAKE samples...")
    for i in range(n_per_class):
        arr = make_fake_sample(rng)
        X.append(extract_features(arr))
        y.append(1)   # 1 = fake
        if (i+1) % 100 == 0: print(f"  {i+1}/{n_per_class}")
    print(f"Generating {n_per_class} REAL samples...")
    for i in range(n_per_class):
        arr = make_real_sample(rng)
        X.append(extract_features(arr))
        y.append(0)   # 0 = real
        if (i+1) % 100 == 0: print(f"  {i+1}/{n_per_class}")
    return np.array(X), np.array(y)

# ── Train & save ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Training Image Authenticity Classifier ===\n")
    X, y = generate_dataset(n_per_class=600)

    clf = Pipeline([
        ("scaler", StandardScaler()),
        ("rf", RandomForestClassifier(
            n_estimators=200, max_depth=12,
            random_state=42, n_jobs=-1
        )),
    ])

    scores = cross_val_score(clf, X, y, cv=5, scoring="accuracy")
    print(f"\nCross-val accuracy: {scores.mean()*100:.1f}% ± {scores.std()*100:.1f}%")

    clf.fit(X, y)
    joblib.dump(clf, MODEL_PATH)
    print(f"Model saved → {MODEL_PATH}")
    print("\n[DONE] Image model trained successfully!")
