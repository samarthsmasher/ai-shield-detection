"""
Image Authenticity Classifier — Training Script (v2)
=====================================================
Trains a RandomForestClassifier on 3000 synthetic samples
(1500 real + 1500 fake) with 8 pure-numpy image features.

KEY FIX (v2): The previous version labeled pure random noise as REAL,
which caused the model to learn an inverted decision boundary.

REAL images (natural photos):
  - Complex, multi-region scenes with natural textures
  - Natural noise floor (camera sensor noise, ~8-15σ)
  - High colour diversity (thousands of unique colours)
  - Non-uniform, spatially-varying local statistics
  - JPEG compression-like artifacts with block edges

FAKE images (AI/GAN-generated):
  - Smooth, overly-clean interpolated regions
  - Periodic/symmetric patterns (checkerboard, radial gradient)
  - Very low noise floor or unnaturally uniform noise
  - Flat colour regions with minimal variance
  - Abnormally high colour uniformity / low entropy in patches
"""
import os, sys, io, joblib
import numpy as np
from PIL import Image
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score, StratifiedKFold

MODELS_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODELS_DIR, "image_auth_model.joblib")


# ── Feature extraction (identical to image_inference.py) ─────────────────────
def extract_features(img_arr: np.ndarray) -> list:
    """8 discriminative features from a 224×224 float32 RGB array."""
    arr  = img_arr.astype(np.float32)
    gray = arr.mean(axis=2)

    # 1. Laplacian variance — REAL images have rich texture edges
    lap_x   = gray[:, 2:] - 2*gray[:, 1:-1] + gray[:, :-2]
    lap_y   = gray[2:, :] - 2*gray[1:-1, :] + gray[:-2, :]
    lap_var = float(np.var(lap_x) + np.var(lap_y))

    # 2. Colour histogram entropy — REAL images have diverse histograms
    entropy = 0.0
    for ch in range(3):
        h, _ = np.histogram(arr[:, :, ch], bins=64, range=(0, 256))
        h     = h / (h.sum() + 1e-9)
        entropy -= float(np.sum(h * np.log(h + 1e-9)))
    entropy /= 3.0

    # 3. Mean gradient magnitude — REAL images have natural edges
    gx       = np.diff(gray, axis=1)
    gy       = np.diff(gray, axis=0)
    grad_mag = float(np.mean(np.abs(gx)) + np.mean(np.abs(gy)))

    # 4. Mean local patch std-dev (32×32 patches)
    local_stds     = [np.std(arr[i:i+32, j:j+32])
                      for i in range(0, 192, 32) for j in range(0, 192, 32)]
    mean_local_std = float(np.mean(local_stds))

    # 5. High-frequency energy — REAL images have fine detail
    small     = arr[::4, ::4, :]
    up        = np.repeat(np.repeat(small, 4, axis=0), 4, axis=1)[:224, :224]
    hf_energy = float(np.mean(np.abs(arr - up)))

    # 6. Minimum patch variance — FAKE images have zero-variance flat regions
    patch_vars    = [np.var(arr[i:i+16, j:j+16])
                     for i in range(0, 208, 16) for j in range(0, 208, 16)]
    min_patch_var = float(np.min(patch_vars))

    # 7. Colour diversity — REAL images have thousands of unique colours
    unique_px = len(np.unique(arr.reshape(-1, 3).astype(np.uint8), axis=0))
    color_div = min(unique_px / 5000.0, 1.0)

    # 8. Global noise estimate (camera noise floor)
    smooth    = (arr[:-2,:-2] + arr[2:,:-2] + arr[:-2,2:] + arr[2:,2:]) / 4.0
    noise_std = float(np.std(arr[1:-1, 1:-1] - smooth))

    return [lap_var, entropy, grad_mag, mean_local_std,
            hf_energy, min_patch_var, color_div, noise_std]


# ── FAKE sample generators (AI / GAN-like patterns) ──────────────────────────
def make_fake_sample(rng) -> np.ndarray:
    """
    Simulate AI-generated image characteristics:
    - Overly smooth / interpolated pixels
    - Periodic/symmetric patterns
    - Flat solid regions
    - Near-zero noise floor
    - Low colour diversity within patches
    """
    arr = np.zeros((224, 224, 3), dtype=np.float32)
    t   = rng.integers(0, 9)

    if t == 0:
        # Solid colour block (minimum variance, classic AI failure mode)
        arr[:] = rng.integers(30, 230, (1, 1, 3)).astype(np.float32)
        # Add imperceptibly tiny noise (AI smoothing)
        arr += rng.normal(0, 0.5, arr.shape)

    elif t == 1:
        # Pure horizontal / vertical linear gradient
        g = np.linspace(20, 235, 224, dtype=np.float32)
        for ch in range(3):
            if rng.random() > 0.5:
                arr[:, :, ch] = g[np.newaxis, :]
            else:
                arr[:, :, ch] = g[:, np.newaxis]
        arr += rng.normal(0, 1.0, arr.shape)

    elif t == 2:
        # Checkerboard / grid pattern (GAN frequency artifacts)
        tile = int(rng.integers(4, 24))
        c1   = rng.integers(10, 120, 3).astype(np.float32)
        c2   = rng.integers(130, 245, 3).astype(np.float32)
        for r in range(224):
            for c in range(224):
                arr[r, c] = c1 if (r//tile + c//tile) % 2 == 0 else c2
        arr += rng.normal(0, 1.5, arr.shape)

    elif t == 3:
        # Radial gradient (GAN radial bias)
        cx, cy = 112, 112
        yy, xx = np.mgrid[:224, :224]
        dist   = np.sqrt((xx-cx)**2 + (yy-cy)**2)
        val    = np.clip(dist / (dist.max() + 1e-9) * 255, 0, 255)
        arr[:,:,0] = val
        arr[:,:,1] = 255 - val
        arr[:,:,2] = val * 0.5
        arr += rng.normal(0, 1.0, arr.shape)

    elif t == 4:
        # GAN over-smoothed interpolation (bilinear resize artifact)
        small = rng.integers(0, 256, (14, 14, 3)).astype(np.float32)
        # Upsample — creates that blurry, overly-smooth AI look
        for r in range(224):
            for c in range(224):
                arr[r, c] = small[r * 14 // 224, c * 14 // 224]
        arr += rng.normal(0, 2.0, arr.shape)

    elif t == 5:
        # Very uniform smooth noise (GAN output without diversity)
        base  = rng.integers(80, 180, (1, 1, 3)).astype(np.float32)
        noise = rng.normal(0, 3, (224, 224, 3)).astype(np.float32)
        arr   = np.clip(base + noise, 0, 255)

    elif t == 6:
        # Sine wave pattern (deep learning frequency artifacts)
        x   = np.linspace(0, 6*np.pi, 224, dtype=np.float32)
        y   = np.linspace(0, 6*np.pi, 224, dtype=np.float32)
        XX, YY = np.meshgrid(x, y)
        pat = (np.sin(XX) * np.sin(YY) * 0.5 + 0.5) * 220
        arr[:,:,0] = pat
        arr[:,:,1] = pat * 0.8
        arr[:,:,2] = 220 - pat * 0.6
        arr += rng.normal(0, 1.5, arr.shape)

    elif t == 7:
        # Flat regions with single sharp edge (segmentation artifact)
        split = rng.integers(60, 164)
        c1    = rng.integers(30, 130, 3).astype(np.float32)
        c2    = rng.integers(130, 230, 3).astype(np.float32)
        arr[:split, :]  = c1
        arr[split:, :]  = c2
        arr += rng.normal(0, 1.0, arr.shape)

    else:
        # Colour-quantised (very few unique colours, like a posterised image)
        levels = rng.integers(4, 12)
        raw    = rng.integers(0, 256, (224, 224, 3)).astype(np.float32)
        raw    = np.floor(raw / (256 / levels)) * (256 / levels)
        arr    = raw + rng.normal(0, 1.0, raw.shape)

    return np.clip(arr, 0, 255)


# ── REAL sample generators (natural photographs) ──────────────────────────────
def make_real_sample(rng) -> np.ndarray:
    """
    Simulate natural photograph characteristics:
    - Complex multi-region scenes
    - Natural camera noise (σ ≈ 8-20)
    - High colour diversity
    - Varied local statistics (edges, flat sky, textured ground)
    - JPEG-like local block variations
    """
    arr = np.zeros((224, 224, 3), dtype=np.float32)
    t   = rng.integers(0, 8)

    if t == 0:
        # Landscape: sky + ground with natural grain
        sky_col    = rng.integers(100, 200, 3).astype(np.float32)
        ground_col = rng.integers(30, 130, 3).astype(np.float32)
        split      = rng.integers(80, 150)
        arr[:split]  = sky_col    + rng.normal(0, rng.uniform(10, 20), (split, 224, 3))
        arr[split:]  = ground_col + rng.normal(0, rng.uniform(12, 22), (224-split, 224, 3))
        # Add local texture variation
        arr += rng.normal(0, rng.uniform(5, 12), arr.shape)

    elif t == 1:
        # Portrait: background + face region with skin texture
        bg_col = rng.integers(20, 100, 3).astype(np.float32)
        arr[:] = bg_col + rng.normal(0, rng.uniform(8, 18), arr.shape)
        # Face oval
        cx, cy = rng.integers(80, 144), rng.integers(70, 130)
        rx, ry = rng.integers(45, 75), rng.integers(55, 85)
        yy, xx = np.ogrid[:224, :224]
        mask   = ((xx-cx)/rx)**2 + ((yy-cy)/ry)**2 <= 1.0
        skin   = np.array([rng.integers(140,210), rng.integers(100,160), rng.integers(70,130)], np.float32)
        arr[mask] = skin + rng.normal(0, rng.uniform(10, 18), (mask.sum(), 3))
        arr = np.clip(arr, 0, 255)
        # Hair region
        hair_mask = ((xx-cx)**2 + ((yy-cy-ry//2))**2 <= (rx*1.1)**2) & (yy < cy - ry//3)
        hair_col  = rng.integers(10, 80, 3).astype(np.float32)
        arr[hair_mask] = hair_col + rng.normal(0, rng.uniform(5, 12), (hair_mask.sum(), 3))

    elif t == 2:
        # Natural texture: wood / fabric / stone
        x   = np.linspace(0, rng.uniform(4, 14)*np.pi, 224, dtype=np.float32)
        y   = np.linspace(0, rng.uniform(4, 14)*np.pi, 224, dtype=np.float32)
        XX, YY = np.meshgrid(x, y)
        phase  = rng.uniform(0, 2*np.pi)
        pat    = np.sin(XX + phase) * np.cos(YY) * 0.4 + 0.6
        base   = rng.integers(60, 180, 3).astype(np.float32)
        for ch in range(3):
            arr[:,:,ch] = base[ch] * pat + rng.normal(0, rng.uniform(12, 22), (224, 224))
        # Random sub-texture overlays
        n_patches = rng.integers(3, 8)
        for _ in range(n_patches):
            r1, c1 = rng.integers(0, 180), rng.integers(0, 180)
            r2, c2 = r1+rng.integers(20, 44), c1+rng.integers(20, 44)
            arr[r1:r2, c1:c2] += rng.normal(0, rng.uniform(8, 20), arr[r1:r2, c1:c2].shape)

    elif t == 3:
        # Urban scene: building with windows (geometric but with noise)
        bg   = rng.integers(80, 180, 3).astype(np.float32)
        arr[:] = bg + rng.normal(0, rng.uniform(8, 15), arr.shape)
        # Window grid
        win_h, win_w = rng.integers(12, 28), rng.integers(12, 28)
        pad_h, pad_w = rng.integers(4, 10), rng.integers(4, 10)
        win_col = rng.integers(180, 255, 3).astype(np.float32)
        for r in range(pad_h, 224-win_h, win_h+pad_h):
            for c in range(pad_w, 224-win_w, win_w+pad_w):
                arr[r:r+win_h, c:c+win_w] = win_col + rng.normal(0, rng.uniform(6, 14), (win_h, win_w, 3))

    elif t == 4:
        # Forest / foliage: complex multi-colour texture
        base_green = np.array([rng.integers(20,80), rng.integers(80,160), rng.integers(10,60)], np.float32)
        arr[:] = base_green + rng.normal(0, rng.uniform(15, 30), arr.shape)
        # Leaf blobs
        for _ in range(rng.integers(20, 50)):
            cx, cy = rng.integers(10, 214), rng.integers(10, 214)
            r_blob = rng.integers(5, 20)
            yy, xx = np.ogrid[:224, :224]
            mask   = (xx-cx)**2 + (yy-cy)**2 <= r_blob**2
            col    = rng.integers(10, 140, 3).astype(np.float32) + np.array([0, 60, 0])
            arr[mask] = np.clip(col + rng.normal(0, rng.uniform(8, 18), (mask.sum(), 3)), 0, 255)

    elif t == 5:
        # Indoor scene: multiple surfaces
        n_regions = rng.integers(3, 7)
        cuts      = sorted(rng.integers(30, 194, n_regions-1).tolist())
        cuts      = [0] + cuts + [224]
        for i in range(len(cuts)-1):
            col = rng.integers(30, 220, 3).astype(np.float32)
            arr[cuts[i]:cuts[i+1]] = col + rng.normal(0, rng.uniform(8, 20), (cuts[i+1]-cuts[i], 224, 3))
        # Add overall lighting gradient
        light = np.linspace(0.85, 1.15, 224, dtype=np.float32)
        arr  *= light[:, np.newaxis, np.newaxis]

    elif t == 6:
        # Close-up texture (macro shot): high detail, lots of edges
        freq  = rng.uniform(6, 18)
        phase = rng.uniform(0, 2*np.pi, 3)
        x     = np.linspace(0, freq*np.pi, 224, dtype=np.float32)
        y     = np.linspace(0, freq*np.pi, 224, dtype=np.float32)
        XX, YY = np.meshgrid(x, y)
        for ch in range(3):
            wave  = np.sin(XX + phase[ch]) * 0.3 + np.cos(YY * 0.7 + phase[ch]) * 0.3
            base  = rng.integers(40, 200)
            arr[:,:,ch] = np.clip(base + wave*70 + rng.normal(0, rng.uniform(10, 22), (224, 224)), 0, 255)

    else:
        # Document / text scan (white/grey background with dark marks)
        bg_val = rng.integers(210, 255)
        arr[:] = bg_val + rng.normal(0, rng.uniform(5, 12), arr.shape)
        # Random text-like strokes
        n_lines = rng.integers(8, 25)
        for _ in range(n_lines):
            r_pos = rng.integers(5, 218)
            width = rng.integers(1, 4)
            ink   = rng.integers(0, 80, 3).astype(np.float32)
            c_start, c_end = rng.integers(10, 100), rng.integers(120, 214)
            arr[r_pos:r_pos+width, c_start:c_end] = ink + rng.normal(0, 5, (width, c_end-c_start, 3))

    return np.clip(arr, 0, 255)


# ── Generate dataset ──────────────────────────────────────────────────────────
def generate_dataset(n_per_class: int = 1500, seed: int = 42):
    rng = np.random.default_rng(seed)
    X, y = [], []

    print(f"Generating {n_per_class} FAKE samples...")
    for i in range(n_per_class):
        arr = make_fake_sample(rng)
        X.append(extract_features(arr))
        y.append(1)   # 1 = fake
        if (i+1) % 300 == 0:
            print(f"  {i+1}/{n_per_class}")

    print(f"Generating {n_per_class} REAL samples...")
    for i in range(n_per_class):
        arr = make_real_sample(rng)
        X.append(extract_features(arr))
        y.append(0)   # 0 = real
        if (i+1) % 300 == 0:
            print(f"  {i+1}/{n_per_class}")

    return np.array(X), np.array(y)


# ── Train & save ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 56)
    print("  Image Authenticity Classifier — Training (v2)")
    print("=" * 56)

    X, y = generate_dataset(n_per_class=1500)

    clf = Pipeline([
        ("scaler", StandardScaler()),
        ("rf", RandomForestClassifier(
            n_estimators=300,
            max_depth=14,
            min_samples_leaf=3,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )),
    ])

    print("\nRunning 5-fold cross-validation...")
    cv    = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(clf, X, y, cv=cv, scoring="accuracy")
    print(f"  Cross-val accuracy: {scores.mean()*100:.1f}% ± {scores.std()*100:.1f}%")
    per_fold = "  |  ".join(f"{s*100:.1f}%" for s in scores)
    print(f"  Per fold          : {per_fold}")

    print("\nFitting final model on all data...")
    clf.fit(X, y)
    joblib.dump(clf, MODEL_PATH)
    print(f"  Model saved -> {MODEL_PATH}")

    # Quick sanity check
    print("\nSanity check on held-out synthetic samples:")
    rng = np.random.default_rng(999)
    checks = [
        ("Solid red block     (→ FAKE)", make_fake_sample.__wrapped__ if hasattr(make_fake_sample, '__wrapped__') else None, 1),
    ]
    # Override with direct arrays
    sanity = [
        ("Solid red           (FAKE)", np.full((224,224,3), [200,50,50],  dtype=np.float32), 1),
        ("Linear gradient     (FAKE)", np.tile(np.linspace(0,255,224,dtype=np.float32)[None,:,None],(224,1,3)), 1),
        ("Smooth GAN noise    (FAKE)", np.clip(np.full((224,224,3),128,dtype=np.float32)+rng.normal(0,2,(224,224,3)),0,255), 1),
        ("Sky+ground scene    (REAL)", None, 0),
        ("Portrait sim        (REAL)", None, 0),
        ("Textured fabric     (REAL)", None, 0),
    ]
    # Build real examples manually
    rng2 = np.random.default_rng(1234)
    sky = np.zeros((224,224,3),np.float32); sky[:100]=np.array([140,180,230],np.float32)+rng2.normal(0,14,(100,224,3)); sky[100:]=np.array([50,100,40],np.float32)+rng2.normal(0,16,(124,224,3))
    sanity[3] = ("Sky+ground scene    (REAL)", np.clip(sky,0,255), 0)
    skin_arr  = np.clip(np.array([170,130,100],np.float32)+rng2.normal(0,16,(224,224,3)), 0, 255)
    sanity[4] = ("Portrait sim        (REAL)", skin_arr, 0)
    x  = np.linspace(0, 10*np.pi, 224, dtype=np.float32)
    XX, YY = np.meshgrid(x, x)
    fab = np.zeros((224,224,3),np.float32)
    for ch,b in enumerate([80,50,30]):
        fab[:,:,ch] = np.clip(b + (np.sin(XX)+np.cos(YY))*25 + rng2.normal(0,14,(224,224)), 0, 255)
    sanity[5] = ("Textured fabric     (REAL)", fab, 0)

    all_correct = True
    for name, arr, true_label in sanity:
        feat  = extract_features(arr)
        proba = clf.predict_proba([feat])[0]   # [p_real, p_fake]
        pred  = int(np.argmax(proba))
        tag   = "FAKE" if pred == 1 else "REAL"
        ok    = "✅" if pred == true_label else "❌"
        if pred != true_label:
            all_correct = False
        print(f"  {ok}  [{tag}]  {name}  p_fake={proba[1]*100:.1f}%")

    print()
    if all_correct:
        print("  ✅ All sanity checks passed!")
    else:
        print("  ⚠️  Some sanity checks failed — review training data diversity.")
    print("=" * 56)
    print("[DONE] Image model v2 training complete!")
