"""
Tasks 3.9 & 3.10 — Video Inference Utilities
- extract_frames(video_path, sample_rate=1)  → list of PIL Images (1 per second)
- predict_video(video_path)                  → mean confidence score dict

Task 3.11 — Tested locally with a synthetic video-like image sequence.
"""
import os
import io
import sys
import tempfile
import numpy as np
from PIL import Image

# Add models directory to path so we can import image_inference
MODELS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, MODELS_DIR)

from image_inference import predict_image


def extract_frames(video_path: str, sample_rate: int = 1) -> list:
    """
    Extract frames from a video file at a given sample rate.

    Args:
        video_path  : Absolute path to the video file.
        sample_rate : Number of frames to extract per second (default: 1).

    Returns:
        List of PIL Image objects (RGB). Returns [] if video cannot be opened.
    """
    try:
        import cv2
    except ImportError:
        print("[video_utils] OpenCV not available — using PIL fallback for test")
        return _extract_frames_pil_fallback(video_path)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[video_utils] Cannot open video: {video_path}")
        return []

    fps         = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_skip  = max(1, int(fps / sample_rate))  # take 1 frame every N frames
    frames      = []
    frame_idx   = 0

    while True:
        ret, bgr = cap.read()
        if not ret:
            break
        if frame_idx % frame_skip == 0:
            # Convert BGR → RGB → PIL
            rgb  = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            img  = Image.fromarray(rgb)
            frames.append(img)
        frame_idx += 1

    cap.release()
    print(f"[video_utils] Extracted {len(frames)} frames from '{os.path.basename(video_path)}'")
    return frames


def _extract_frames_pil_fallback(video_path: str) -> list:
    """
    Fallback when OpenCV is unavailable.
    Tries to open the file as an animated GIF / APNG sequence.
    Otherwise returns a single frame (first image).
    """
    try:
        img = Image.open(video_path)
        frames = []
        try:
            while True:
                frames.append(img.copy().convert("RGB"))
                img.seek(img.tell() + 1)
        except EOFError:
            pass
        print(f"[video_utils] Fallback: extracted {len(frames)} frames via PIL")
        return frames if frames else [img.convert("RGB")]
    except Exception as e:
        print(f"[video_utils] Fallback failed: {e}")
        return []


def predict_video(video_path: str, sample_rate: int = 1) -> dict:
    """
    Predict whether a video is real or deepfake / AI-generated.

    Runs `predict_image()` on each extracted frame and aggregates:
    - Mean confidence score
    - Majority vote result

    Args:
        video_path  : Path to the video file (MP4, AVI, MOV, etc.)
        sample_rate : Frames to analyse per second (default: 1).

    Returns:
        {
            "result":      "real" | "fake",
            "confidence":  float (0.0–1.0),
            "frames_analysed": int,
            "label":       str
        }
    """
    frames = extract_frames(video_path, sample_rate=sample_rate)

    if not frames:
        return {
            "result":           "unknown",
            "confidence":       0.0,
            "frames_analysed":  0,
            "label":            "Could not process video",
        }

    confidences  = []
    fake_votes   = 0

    for frame in frames:
        buf = io.BytesIO()
        frame.save(buf, format="JPEG", quality=85)
        img_bytes = buf.getvalue()

        frame_result = predict_image(img_bytes)
        confidences.append(frame_result["confidence"])
        if frame_result["result"] == "fake":
            fake_votes += 1

    mean_conf = float(np.mean(confidences))
    fake_ratio = fake_votes / len(frames)

    # Majority vote: if >50% of frames flagged as fake → fake video
    if fake_ratio > 0.5:
        result     = "fake"
        confidence = round(mean_conf, 4)
    else:
        result     = "real"
        confidence = round(mean_conf, 4)

    return {
        "result":           result,
        "confidence":       confidence,
        "frames_analysed":  len(frames),
        "label":            "Authentic video" if result == "real" else "Possible deepfake / synthetic video",
    }


# ─── Task 3.11 — Local test ───────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Task 3.11 — Testing predict_video() with synthetic frames ===\n")

    # Create a synthetic multi-frame animated GIF as a stand-in for a video
    print("Creating synthetic animated GIF (simulating short video)...")
    tmp_path = os.path.join(tempfile.gettempdir(), "test_video.gif")

    rng    = np.random.default_rng(0)
    pil_frames = []
    for i in range(5):   # 5 synthetic frames
        arr = (rng.random((120, 160, 3)) * 255).astype(np.uint8)
        arr[:, :, 0] = np.clip(arr[:, :, 0] + i * 40, 0, 255)
        pil_frames.append(Image.fromarray(arr, 'RGB'))

    pil_frames[0].save(
        tmp_path, format="GIF",
        save_all=True, append_images=pil_frames[1:],
        duration=1000, loop=0
    )
    print(f"Synthetic video saved to: {tmp_path}")

    result = predict_video(tmp_path, sample_rate=1)
    print(f"\nResult          : {result['result']}")
    print(f"Confidence      : {result['confidence']}")
    print(f"Frames analysed : {result['frames_analysed']}")
    print(f"Label           : {result['label']}")

    assert isinstance(result['confidence'], float), "confidence must be float"
    assert 0.0 <= result['confidence'] <= 1.0,      "confidence must be in [0,1]"
    assert result['result'] in ('real', 'fake', 'unknown'), "invalid result"
    assert result['frames_analysed'] > 0,            "must analyse at least 1 frame"
    print("\n[PASS] predict_video() returns valid output!")

    # Clean up
    os.remove(tmp_path)
