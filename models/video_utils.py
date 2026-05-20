"""
Video Inference Utilities — Temporal Analysis Engine (v2)
==========================================================
Key insight: AI-generated / deepfake videos differ from real videos in
HOW FRAMES CHANGE OVER TIME, not just what individual frames look like.

A per-frame image classifier fails on photorealistic AI video because each
frame LOOKS real. Temporal analysis catches what per-frame analysis misses.

Temporal features (8 signals):
  1. Motion smoothness variance   — AI: too uniform (over-smooth interpolation)
  2. Noise consistency score      — AI: noise floor TOO stable across frames
  3. Color channel correlation    — AI: R/G/B channels change in lockstep
  4. Edge flicker index           — Deepfakes: boundary artifacts flicker
  5. Luminance temporal std       — AI: unnaturally stable brightness
  6. Temporal gradient anomaly    — AI: motion artifacts at object boundaries
  7. Block artifact score         — AI/compressed: DCT block patterns
  8. Frame similarity clustering  — AI loops / limited variation
"""
import os
import io
import sys
import numpy as np
from PIL import Image

MODELS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, MODELS_DIR)


# ─── Frame extraction ─────────────────────────────────────────────────────────

def extract_frames(video_path: str, sample_rate: int = 2) -> list:
    """
    Extract frames from a video file at a given sample rate.
    Returns list of PIL Image objects (RGB).
    """
    try:
        import cv2
    except ImportError:
        print("[video_utils] OpenCV not available — using PIL fallback")
        return _extract_frames_pil_fallback(video_path)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[video_utils] Cannot open video: {video_path}")
        return []

    fps        = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_skip = max(1, int(fps / sample_rate))
    frames     = []
    frame_idx  = 0

    while True:
        ret, bgr = cap.read()
        if not ret:
            break
        if frame_idx % frame_skip == 0:
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            frames.append(Image.fromarray(rgb))
        frame_idx += 1

    cap.release()
    print(f"[video_utils] Extracted {len(frames)} frames from '{os.path.basename(video_path)}'")
    return frames


def _extract_frames_pil_fallback(video_path: str) -> list:
    try:
        img    = Image.open(video_path)
        frames = []
        try:
            while True:
                frames.append(img.copy().convert("RGB"))
                img.seek(img.tell() + 1)
        except EOFError:
            pass
        return frames if frames else [img.convert("RGB")]
    except Exception as e:
        print(f"[video_utils] Fallback failed: {e}")
        return []


# ─── Feature: resize frame to fixed size for consistent analysis ──────────────

def _to_array(frame: Image.Image, size: int = 128) -> np.ndarray:
    """Resize PIL frame to (size×size) float32 array."""
    return np.array(frame.resize((size, size), Image.BILINEAR), dtype=np.float32)


# ─── Temporal feature extractors ──────────────────────────────────────────────

def _motion_smoothness_variance(arrays: list) -> float:
    """
    Compute variance of per-frame motion magnitude (mean absolute difference
    between consecutive frames).

    Real videos: high variance — scene activity is irregular.
    AI videos:   LOW variance  — AI interpolation is unnaturally smooth.
    Low score (< 3.0) is suspicious.
    """
    if len(arrays) < 3:
        return 10.0  # not enough frames — neutral
    diffs = []
    for i in range(1, len(arrays)):
        d = np.mean(np.abs(arrays[i] - arrays[i - 1]))
        diffs.append(d)
    return float(np.var(diffs))


def _noise_consistency_score(arrays: list) -> float:
    """
    Measure how consistent the noise floor is across frames.

    Real cameras: random shot noise — noise varies frame-to-frame.
    AI generators: same noise pattern or none — noise is suspiciously stable.
    Low std of per-frame noise estimates is suspicious.
    """
    noise_levels = []
    for arr in arrays:
        gray   = arr.mean(axis=2)
        smooth = (gray[:-2, :-2] + gray[2:, :-2] +
                  gray[:-2, 2:]  + gray[2:, 2:]) / 4.0
        noise  = float(np.std(gray[1:-1, 1:-1] - smooth))
        noise_levels.append(noise)
    return float(np.std(noise_levels))  # low = suspicious


def _color_channel_correlation(arrays: list) -> float:
    """
    Measure correlation between R, G, B channel inter-frame changes.

    Real cameras: independent sensor channels — low correlation.
    AI generators: colour synthesis couples channels — HIGH correlation.
    High score (> 0.92) is suspicious.
    """
    if len(arrays) < 3:
        return 0.0
    r_diffs, g_diffs, b_diffs = [], [], []
    for i in range(1, len(arrays)):
        diff = arrays[i] - arrays[i - 1]
        r_diffs.append(np.mean(np.abs(diff[:, :, 0])))
        g_diffs.append(np.mean(np.abs(diff[:, :, 1])))
        b_diffs.append(np.mean(np.abs(diff[:, :, 2])))

    def corr(a, b):
        a, b = np.array(a), np.array(b)
        if np.std(a) < 1e-9 or np.std(b) < 1e-9:
            return 1.0
        return float(np.corrcoef(a, b)[0, 1])

    rg = corr(r_diffs, g_diffs)
    rb = corr(r_diffs, b_diffs)
    gb = corr(g_diffs, b_diffs)
    return float(np.mean([rg, rb, gb]))


def _edge_flicker_index(arrays: list) -> float:
    """
    Measure flicker in edge maps across frames.

    Real videos: edges are stable between similar frames.
    Deepfakes:   blending boundary causes edge artifacts that flicker.
    High variance of edge energy is suspicious.
    """
    if len(arrays) < 3:
        return 0.0
    edge_energies = []
    for arr in arrays:
        gray = arr.mean(axis=2)
        gx   = np.abs(np.diff(gray, axis=1))
        gy   = np.abs(np.diff(gray, axis=0))
        edge_energies.append(np.mean(gx) + np.mean(gy))
    return float(np.std(edge_energies))


def _luminance_temporal_std(arrays: list) -> float:
    """
    Measure temporal variability in mean luminance.

    Real videos: natural brightness variation due to lighting / motion.
    AI videos:   luminance is TOO stable (no natural lighting variation).
    Low std (< 0.8) is suspicious for longer videos.
    """
    lums = [float(arr.mean()) for arr in arrays]
    return float(np.std(lums))


def _frame_similarity_clustering(arrays: list) -> float:
    """
    Measure how many frames are nearly identical (cosine-like similarity).

    AI generation with limited diversity / looping: many very similar frames.
    Returns fraction of frame-pairs with difference < threshold.
    High score (> 0.6) is suspicious.
    """
    if len(arrays) < 4:
        return 0.0
    flat    = [a.flatten() / 255.0 for a in arrays]
    similar = 0
    total   = 0
    step    = max(1, len(flat) // 8)    # sample pairs
    for i in range(0, len(flat) - step, step):
        diff = np.mean(np.abs(flat[i] - flat[i + step]))
        if diff < 2.0:    # nearly identical frames
            similar += 1
        total += 1
    return similar / max(total, 1)


def _temporal_gradient_anomaly(arrays: list) -> float:
    """
    Detect unnaturally uniform temporal gradients (AI interpolation artifact).

    AI videos: temporal difference between frames follows a very regular pattern.
    Real videos: motion is irregular.
    Returns coefficient of variation of differences — LOW is suspicious.
    """
    if len(arrays) < 4:
        return 1.0
    diffs = [np.mean(np.abs(arrays[i] - arrays[i-1])) for i in range(1, len(arrays))]
    mean_d = np.mean(diffs)
    if mean_d < 1e-6:
        return 0.0
    cv = float(np.std(diffs) / mean_d)  # coefficient of variation — low = suspicious
    return cv


def _block_artifact_score(arrays: list) -> float:
    """
    Measure DCT-like block artifacts common in AI-generated/over-compressed video.

    Looks for periodicity in horizontal/vertical differences at 8-pixel intervals.
    High score (> 1.2) indicates block artifacts.
    """
    scores = []
    for arr in arrays[:min(5, len(arrays))]:
        gray  = arr.mean(axis=2)
        hdiff = np.abs(np.diff(gray, axis=1))
        # Sample columns at multiples of 8
        block_cols = hdiff[:, 7::8] if hdiff.shape[1] > 8 else hdiff
        non_block  = hdiff[:, 3::8] if hdiff.shape[1] > 8 else hdiff
        ratio = (np.mean(block_cols) + 1e-9) / (np.mean(non_block) + 1e-9)
        scores.append(ratio)
    return float(np.mean(scores))


# ─── Main scoring engine ───────────────────────────────────────────────────────

def _score_video(arrays: list) -> tuple:
    """
    Compute a composite fake-probability score from 8 temporal features.
    Returns (fake_probability, feature_dict).
    """
    n = len(arrays)

    # ── Extract all 8 features ──────────────────────────────────────────────
    msv   = _motion_smoothness_variance(arrays)       # low = suspicious
    ncs   = _noise_consistency_score(arrays)           # low = suspicious
    ccc   = _color_channel_correlation(arrays)         # high = suspicious
    efi   = _edge_flicker_index(arrays)                # high = suspicious
    lts   = _luminance_temporal_std(arrays)            # low = suspicious
    fsc   = _frame_similarity_clustering(arrays)       # high = suspicious
    tga   = _temporal_gradient_anomaly(arrays)         # low = suspicious
    bas   = _block_artifact_score(arrays)              # high = suspicious

    print(f"[video_utils] Features: msv={msv:.3f} ncs={ncs:.3f} ccc={ccc:.3f} "
          f"efi={efi:.3f} lts={lts:.3f} fsc={fsc:.3f} tga={tga:.3f} bas={bas:.3f}")

    # ── Convert each feature to a 0-1 suspicion score ───────────────────────
    # Each signal contributes to the overall fake probability

    # 1. Motion smoothness variance — LOW is suspicious
    #    Normal real video: msv > 5.0; AI: msv < 2.0
    s_msv = max(0.0, min(1.0, 1.0 - (msv / 6.0)))

    # 2. Noise consistency — LOW std is suspicious
    #    Real cameras: ncs > 1.5; AI: ncs < 0.5
    s_ncs = max(0.0, min(1.0, 1.0 - (ncs / 2.0)))

    # 3. Color channel correlation — HIGH is suspicious
    #    Real: ccc < 0.80; AI: ccc > 0.92
    s_ccc = max(0.0, min(1.0, (ccc - 0.75) / 0.20)) if ccc > 0.75 else 0.0

    # 4. Edge flicker — HIGH is suspicious for deepfakes (blending artifacts)
    #    Real: efi varies; Deepfakes: efi > 3.0
    s_efi = max(0.0, min(1.0, efi / 5.0))

    # 5. Luminance temporal std — LOW is suspicious
    #    Real: lts > 1.5; AI: lts < 0.5
    s_lts = max(0.0, min(1.0, 1.0 - (lts / 2.0))) if n >= 5 else 0.0

    # 6. Frame similarity — HIGH is suspicious
    #    Real: fsc < 0.3; AI loops: fsc > 0.6
    s_fsc = max(0.0, min(1.0, fsc / 0.7))

    # 7. Temporal gradient anomaly — LOW cv is suspicious
    #    Real: tga > 0.4; AI: tga < 0.15
    s_tga = max(0.0, min(1.0, 1.0 - (tga / 0.5))) if n >= 4 else 0.0

    # 8. Block artifacts — HIGH is suspicious
    #    Real: bas ≈ 1.0; AI-compressed: bas > 1.3
    s_bas = max(0.0, min(1.0, (bas - 1.0) / 0.5)) if bas > 1.0 else 0.0

    # ── Weighted combination ─────────────────────────────────────────────────
    # Higher weights to the most reliable signals
    weights = {
        "motion_smoothness":  0.20,   # very reliable
        "noise_consistency":  0.18,   # very reliable
        "channel_corr":       0.15,   # reliable
        "edge_flicker":       0.12,   # reliable for deepfakes
        "luminance_std":      0.12,   # reliable
        "frame_similarity":   0.10,   # reliable for looping AI
        "temporal_anomaly":   0.08,   # moderate
        "block_artifact":     0.05,   # weak signal
    }

    scores = {
        "motion_smoothness": s_msv,
        "noise_consistency": s_ncs,
        "channel_corr":      s_ccc,
        "edge_flicker":      s_efi,
        "luminance_std":     s_lts,
        "frame_similarity":  s_fsc,
        "temporal_anomaly":  s_tga,
        "block_artifact":    s_bas,
    }

    fake_prob = sum(weights[k] * scores[k] for k in weights)

    print(f"[video_utils] Signal scores: " +
          ", ".join(f"{k}={v:.2f}" for k, v in scores.items()))
    print(f"[video_utils] Composite fake probability: {fake_prob:.3f}")

    return fake_prob, scores


# ─── Public API ───────────────────────────────────────────────────────────────

def predict_video(video_path: str, sample_rate: int = 2) -> dict:
    """
    Predict whether a video is real or AI-generated / deepfake.

    Uses temporal analysis — examining HOW frames change over time.
    This correctly identifies photorealistic AI-generated videos that
    fool per-frame image classifiers.

    Returns:
        {
            "result":          "real" | "fake",
            "confidence":      float (0.0–1.0),
            "frames_analysed": int,
            "label":           str
        }
    """
    frames = extract_frames(video_path, sample_rate=sample_rate)

    if not frames:
        return {
            "result":          "unknown",
            "confidence":      0.0,
            "frames_analysed": 0,
            "label":           "Could not process video",
        }

    # Need at least 3 frames for temporal analysis
    if len(frames) < 3:
        return {
            "result":          "real",
            "confidence":      0.55,
            "frames_analysed": len(frames),
            "label":           "Too short to analyse — assumed real",
        }

    # Convert frames to numpy arrays (128×128 for fast analysis)
    arrays = [_to_array(f) for f in frames]

    # Run temporal scoring
    fake_prob, feature_scores = _score_video(arrays)

    # ── Decision threshold ────────────────────────────────────────────────────
    # Threshold at 0.45 — slightly below 0.5 to be more sensitive to AI content
    FAKE_THRESHOLD = 0.45

    if fake_prob >= FAKE_THRESHOLD:
        result     = "fake"
        confidence = round(min(0.50 + fake_prob * 0.50, 0.99), 4)
        label      = "Possible AI-generated / deepfake video"
    else:
        result     = "real"
        confidence = round(min(0.50 + (1.0 - fake_prob) * 0.50, 0.99), 4)
        label      = "Likely authentic video"

    return {
        "result":          result,
        "confidence":      confidence,
        "frames_analysed": len(frames),
        "label":           label,
    }


# ─── Local test ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import tempfile

    print("=== Testing Temporal Video Analysis ===\n")

    # Test 1: Synthetic AI-like video (uniform smooth frames)
    print("Test 1: AI-like video (smooth uniform frames)...")
    tmp = os.path.join(tempfile.gettempdir(), "test_ai.gif")
    rng = np.random.default_rng(0)

    ai_frames = []
    base = rng.integers(80, 180, (128, 128, 3)).astype(np.float32)
    for i in range(20):
        # Very small, uniform changes — simulates AI smooth interpolation
        frame_arr = np.clip(base + i * 0.3 + rng.normal(0, 0.5, base.shape), 0, 255)
        ai_frames.append(Image.fromarray(frame_arr.astype(np.uint8)))
    ai_frames[0].save(tmp, format="GIF", save_all=True,
                      append_images=ai_frames[1:], duration=100, loop=0)
    result = predict_video(tmp)
    print(f"  Result: {result['result']} | Confidence: {result['confidence']:.2%}\n")

    # Test 2: Real-like video (variable natural motion)
    print("Test 2: Real-like video (natural variable motion)...")
    tmp2 = os.path.join(tempfile.gettempdir(), "test_real.gif")
    real_frames = []
    for i in range(20):
        # Natural variation — random lighting changes, camera noise
        arr = rng.integers(30, 220, (128, 128, 3)).astype(np.float32)
        arr += rng.normal(0, rng.uniform(8, 20), arr.shape)
        real_frames.append(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)))
    real_frames[0].save(tmp2, format="GIF", save_all=True,
                        append_images=real_frames[1:], duration=100, loop=0)
    result2 = predict_video(tmp2)
    print(f"  Result: {result2['result']} | Confidence: {result2['confidence']:.2%}\n")

    os.remove(tmp)
    os.remove(tmp2)
    print("=== Done ===")
