"""
Tasks 4.5 → 4.9 — Detection Router
Routes (all under /api/detect):
  POST /text   → spam text detection
  POST /image  → fake image detection
  POST /video  → deepfake video detection

Each endpoint:
  - Runs ML inference
  - Asynchronously writes a DetectionResult to MongoDB (Task 4.9)
  - Returns structured JSON response
"""
import os
import sys
import io
import time
import tempfile
import joblib
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Form, status
from bson import ObjectId

# ─── Path setup: add /models to sys.path so we can import ML modules ─────────
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR  = os.path.normpath(os.path.join(BACKEND_DIR, '..', '..', 'models'))
if MODELS_DIR not in sys.path:
    sys.path.insert(0, MODELS_DIR)

from image_inference import predict_image
from video_utils    import predict_video

from database       import db
from dependencies   import get_current_user
from models.result_model import DetectionResult, DetectionResponse

router = APIRouter(prefix="/api/detect", tags=["Detection"])

# ─── Lazy-load text model (loaded once per worker process) ────────────────────
_TEXT_MODEL     = None
_TEXT_MODEL_PATH = os.path.normpath(
    os.path.join(BACKEND_DIR, '..', '..', 'models', 'text_spam_model.joblib')
)

def _get_text_model():
    global _TEXT_MODEL
    if _TEXT_MODEL is None:
        if not os.path.exists(_TEXT_MODEL_PATH):
            # Model not found — train it now using the bundled dataset
            import subprocess
            train_script = os.path.normpath(
                os.path.join(BACKEND_DIR, '..', '..', 'models', 'train_text_model.py')
            )
            subprocess.run(
                [sys.executable, train_script],
                check=True,
                cwd=os.path.dirname(train_script),
            )
        _TEXT_MODEL = joblib.load(_TEXT_MODEL_PATH)
        print("[detect] Text spam model loaded")
    return _TEXT_MODEL


# ── Pre-warm text model at startup (avoids slow first request) ────────────────
try:
    _get_text_model()
except Exception as _e:
    print(f"[detect] WARNING: text model pre-warm failed: {_e}")


# ─── Helper: persist DetectionResult to MongoDB (Task 4.9) ───────────────────
async def _save_result(
    input_type: str,
    result: str,
    confidence: float,
    user_id: Optional[str],
) -> None:
    """Async write a DetectionResult document to the detection_results collection."""
    try:
        doc = {
            "user_id":    user_id,
            "input_type": input_type,
            "result":     result,
            "confidence": confidence,
            "timestamp":  datetime.now(timezone.utc),
        }
        await db["detection_results"].insert_one(doc)
    except Exception:
        pass  # Never let DB write failure break the detection response


# ─── Task 4.6 — POST /text ────────────────────────────────────────────────────
@router.post(
    "/text",
    response_model=DetectionResponse,
    summary="Detect spam in text",
)
async def detect_text(
    payload: dict,
    current_user: Optional[dict] = Depends(get_current_user),
):
    """
    Body: {"text": "your message here"}
    Returns: {"result": "spam"|"ham", "confidence": float, "input_type": "text"}
    """
    text = (payload.get("text") or "").strip()
    if not text:
        raise HTTPException(status_code=422, detail="'text' field is required and cannot be empty.")

    model  = _get_text_model()
    proba  = model.predict_proba([text])[0]   # [ham_prob, spam_prob]
    label  = "spam" if proba[1] >= 0.5 else "ham"
    conf   = float(max(proba))

    user_id = str(current_user["_id"]) if current_user else None
    await _save_result("text", label, conf, user_id)

    return DetectionResponse(result=label, confidence=round(conf, 4), input_type="text")


# ─── Task 4.7 — POST /image ───────────────────────────────────────────────────
@router.post(
    "/image",
    response_model=DetectionResponse,
    summary="Detect if an image is real or AI-generated / fake",
)
async def detect_image(
    file: UploadFile = File(...),
    current_user: Optional[dict] = Depends(get_current_user),
):
    """
    Accepts an image file (JPEG, PNG, WebP, etc.).
    Returns: {"result": "real"|"fake", "confidence": float, "input_type": "image"}
    """
    allowed = {"image/jpeg", "image/png", "image/webp", "image/gif", "image/bmp"}
    if file.content_type and file.content_type not in allowed:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{file.content_type}'. Use JPEG, PNG, or WebP."
        )

    img_bytes = await file.read()
    if len(img_bytes) > 20 * 1024 * 1024:  # 20 MB cap
        raise HTTPException(status_code=413, detail="Image exceeds 20 MB limit.")

    prediction = predict_image(img_bytes)
    result     = prediction["result"]
    confidence = prediction["confidence"]

    user_id = str(current_user["_id"]) if current_user else None
    await _save_result("image", result, confidence, user_id)

    return DetectionResponse(result=result, confidence=confidence, input_type="image")


# ─── Task 4.8 — POST /video ───────────────────────────────────────────────────
@router.post(
    "/video",
    response_model=DetectionResponse,
    summary="Detect if a video is real or a deepfake",
)
async def detect_video(
    file: UploadFile = File(...),
    current_user: Optional[dict] = Depends(get_current_user),
):
    """
    Accepts a video file (MP4, AVI, MOV, WebM, GIF).
    Saves temporarily, runs frame-by-frame inference, deletes temp file.
    Returns: {"result": "real"|"fake", "confidence": float, "input_type": "video"}
    """
    allowed_ext = {".mp4", ".avi", ".mov", ".webm", ".mkv", ".gif"}
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext and ext not in allowed_ext:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported video format '{ext}'. Use MP4, AVI, MOV, WebM, or GIF."
        )

    video_bytes = await file.read()
    if len(video_bytes) > 200 * 1024 * 1024:  # 200 MB cap
        raise HTTPException(status_code=413, detail="Video exceeds 200 MB limit.")

    # Save to a named temp file so OpenCV can open it
    suffix  = ext if ext else ".mp4"
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=suffix)
    try:
        os.write(tmp_fd, video_bytes)
        os.close(tmp_fd)

        prediction = predict_video(tmp_path, sample_rate=2)
        result     = prediction["result"]
        confidence = prediction["confidence"]
    finally:
        # Task 4.8: always delete the temp file
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    user_id = str(current_user["_id"]) if current_user else None
    await _save_result("video", result, confidence, user_id)

    return DetectionResponse(
        result          = result,
        confidence      = confidence,
        input_type      = "video",
        frames_analysed = prediction.get("frames_analysed"),
    )


# ─── GET /history — Detection History Dashboard ──────────────────────────────
@router.get(
    "/history",
    summary="Get recent detection results for the history dashboard",
)
async def get_history(
    limit: int = 50,
    input_type: Optional[str] = None,   # filter by "text"|"image"|"video"
):
    """
    Returns the last `limit` detection results (newest first) plus aggregate stats.
    Optionally filter by input_type.
    """
    query: dict = {}
    if input_type and input_type in ("text", "image", "video"):
        query["input_type"] = input_type

    cursor = db["detection_results"].find(query).sort("timestamp", -1).limit(limit)
    docs   = await cursor.to_list(length=limit)

    # Serialise ObjectId → string
    items = []
    for doc in docs:
        items.append({
            "id":         str(doc.get("_id", "")),
            "input_type": doc.get("input_type", ""),
            "result":     doc.get("result", ""),
            "confidence": round(float(doc.get("confidence", 0)), 4),
            "timestamp":  doc.get("timestamp").isoformat() if doc.get("timestamp") else "",
            "user_id":    doc.get("user_id"),
        })

    # Aggregate stats (all time, ignoring current filter)
    total       = await db["detection_results"].count_documents({})
    spam_count  = await db["detection_results"].count_documents({"result": "spam"})
    fake_count  = await db["detection_results"].count_documents({"result": "fake"})
    real_count  = await db["detection_results"].count_documents({"result": "real"})
    ham_count   = await db["detection_results"].count_documents({"result": "ham"})
    text_count  = await db["detection_results"].count_documents({"input_type": "text"})
    image_count = await db["detection_results"].count_documents({"input_type": "image"})
    video_count = await db["detection_results"].count_documents({"input_type": "video"})

    return {
        "items": items,
        "stats": {
            "total":     total,
            "by_type":   {"text": text_count, "image": image_count, "video": video_count},
            "by_result": {"spam": spam_count, "fake": fake_count, "real": real_count, "ham": ham_count},
        },
    }
