"""
Tasks 3.6 & 3.7 — Image Inference Module (ML-based)

Uses a RandomForestClassifier trained on 1200 synthetic samples
(600 real + 600 fake) with 8 pure-numpy image features.

Features:
  1. Laplacian variance  — real images have natural texture/noise
  2. Colour entropy      — real images have diverse colour histograms
  3. Gradient magnitude  — real images have natural edges
  4. Local std-dev       — real images have varied local patches
  5. High-freq energy    — real images have fine detail lost by subsampling
  6. Min patch variance  — fakes have zero-variance flat regions
  7. Colour diversity    — real images have thousands of unique colours
  8. Noise std           — real images have camera noise floor

The model runs with zero GPU / torch dependency and fits within Render's
512 MB free-tier RAM. Training script: models/train_image_model.py
"""
import os
import io
import sys
import subprocess
import numpy as np
from PIL import Image

MODELS_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH  = os.path.join(MODELS_DIR, "image_auth_model.joblib")

# Module-level cache
_CLF        = None
_INITIALIZED = False


# ─── Feature extraction (must match train_image_model.py exactly) ─────────────

def extract_features(arr: np.ndarray) -> list:
    """8 discriminative features from a 224×224 float32 RGB array."""
    arr = arr.astype(np.float32)
    gray = arr.mean(axis=2)

    # 1. Laplacian variance
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

    # 4. Mean local patch std-dev
    local_stds = [np.std(arr[i:i+32, j:j+32])
                  for i in range(0, 192, 32) for j in range(0, 192, 32)]
    mean_local_std = float(np.mean(local_stds))

    # 5. High-frequency energy
    small = arr[::4, ::4, :]
    up    = np.repeat(np.repeat(small, 4, axis=0), 4, axis=1)[:224, :224]
    hf_energy = float(np.mean(np.abs(arr - up)))

    # 6. Minimum patch variance
    patch_vars = [np.var(arr[i:i+16, j:j+16])
                  for i in range(0, 208, 16) for j in range(0, 208, 16)]
    min_patch_var = float(np.min(patch_vars))

    # 7. Colour diversity
    unique_px = len(np.unique(arr.reshape(-1, 3).astype(np.uint8), axis=0))
    color_div = min(unique_px / 5000.0, 1.0)

    # 8. Global noise std
    smooth    = (arr[:-2, :-2] + arr[2:, :-2] + arr[:-2, 2:] + arr[2:, 2:]) / 4.0
    noise_std = float(np.std(arr[1:-1, 1:-1] - smooth))

    return [lap_var, entropy, grad_mag, mean_local_std,
            hf_energy, min_patch_var, color_div, noise_std]


# ─── Model loader ─────────────────────────────────────────────────────────────

def _initialize():
    global _CLF, _INITIALIZED
    if _INITIALIZED:
        return
    import joblib

    if not os.path.exists(MODEL_PATH):
        print("[image_inference] Model not found — training now…")
        train_script = os.path.join(MODELS_DIR, "train_image_model.py")
        subprocess.run(
            [sys.executable, train_script],
            check=True,
            cwd=MODELS_DIR,
        )

    _CLF = joblib.load(MODEL_PATH)
    print("[image_inference] RandomForest image model loaded")
    _INITIALIZED = True


# ─── Public API ───────────────────────────────────────────────────────────────

def predict_image(image_bytes: bytes) -> dict:
    """
    Predict whether an image is real or AI-generated / fake.

    Returns:
        {
            "result":     "real" | "fake",
            "confidence": float  (0.0-1.0),
            "label":      str
        }
    """
    _initialize()

    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    arr = np.array(img.resize((224, 224)), dtype=np.float32)

    features = extract_features(arr)
    X        = np.array([features])

    pred      = int(_CLF.predict(X)[0])           # 0=real, 1=fake
    proba     = _CLF.predict_proba(X)[0]          # [p_real, p_fake]
    confidence = float(proba[pred])

    # Scale to [0.52, 0.97] for display
    confidence = round(0.52 + confidence * 0.45, 4)
    confidence = min(max(confidence, 0.52), 0.97)

    result = "fake" if pred == 1 else "real"

    return {
        "result":     result,
        "confidence": confidence,
        "label":      "Authentic photo" if result == "real"
                      else "Possibly AI-generated / synthetic",
    }


# ─── Local test ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    _initialize()

    rng = np.random.default_rng(99)
    tests = [
        ("Solid red (FAKE)",    np.full((224,224,3), [200,50,50],  dtype=np.float32)),
        ("Pure gradient (FAKE)",np.tile(np.linspace(0,255,224,dtype=np.float32)[None,:,None], (224,1,3))),
        ("Natural noise (REAL)",rng.integers(0,256,(224,224,3)).astype(np.float32)),
        ("Portrait sim (REAL)", None),
    ]

    skin = rng.integers(140,200,(224,224,3)).astype(np.float32)
    skin += rng.normal(0,18,skin.shape)
    tests[3] = ("Portrait sim (REAL)", np.clip(skin,0,255))

    print("=" * 50)
    for name, arr in tests:
        buf = io.BytesIO()
        Image.fromarray(arr.astype(np.uint8)).save(buf, "JPEG")
        r   = predict_image(buf.getvalue())
        tag = "REAL" if r["result"] == "real" else "FAKE"
        print(f"  [{tag}]  {name:<28} {r['confidence']*100:.1f}%")
    print("=" * 50)
