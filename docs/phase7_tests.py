"""
Phase 7 — End-to-End Test Suite
Tasks 7.1, 7.2, 7.3, 7.5, 7.6
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import os
import time
import json
import asyncio
import urllib.request
import numpy as np
from PIL import Image

BASE_URL  = "http://127.0.0.1:8000"
DOTENV    = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend', '.env')
SEP       = "-" * 60


# ─── Helpers ──────────────────────────────────────────────────────────────────

def http_post_json(endpoint: str, payload: dict, token: str | None = None) -> tuple[dict, float]:
    url  = f"{BASE_URL}{endpoint}"
    data = json.dumps(payload).encode()
    req  = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    t0   = time.perf_counter()
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read())
    elapsed = time.perf_counter() - t0
    return body, elapsed


def http_post_multipart(endpoint: str, field: str, filename: str, file_bytes: bytes,
                        content_type: str, token: str | None = None) -> tuple[dict, float]:
    """Minimal multipart/form-data POST without requests library."""
    boundary = "----FormBoundary7MA4YWxkTrZu0gW"
    body_parts = [
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{field}"; filename="{filename}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n".encode(),
        file_bytes,
        f"\r\n--{boundary}--\r\n".encode(),
    ]
    body = b"".join(p if isinstance(p, bytes) else p.encode() for p in body_parts)

    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read())
    elapsed = time.perf_counter() - t0
    return result, elapsed


def make_test_image(width=128, height=128) -> bytes:
    """Create a synthetic JPEG image."""
    rng = np.random.default_rng(42)
    arr = (rng.random((height, width, 3)) * 255).astype(np.uint8)
    arr[:, :, 0] = np.linspace(0, 255, width).astype(np.uint8)
    img = Image.fromarray(arr, "RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def make_test_video_gif(frames=5) -> bytes:
    """Create a small animated GIF (video proxy)."""
    rng = np.random.default_rng(7)
    pil_frames = []
    for i in range(frames):
        arr = (rng.random((64, 64, 3)) * 255).astype(np.uint8)
        arr[:, :, 2] = np.clip(arr[:, :, 2] + i * 40, 0, 255)
        pil_frames.append(Image.fromarray(arr, "RGB"))
    buf = io.BytesIO()
    pil_frames[0].save(buf, format="GIF", save_all=True,
                       append_images=pil_frames[1:], duration=500, loop=0)
    return buf.getvalue()


# ─── Run tests ────────────────────────────────────────────────────────────────
def run():
    results = {}
    PASS = "PASS ✅"
    FAIL = "FAIL ❌"

    print("=" * 60)
    print("  PHASE 7 — END-TO-END TEST SUITE")
    print("=" * 60)

    # ── Login to get JWT ──────────────────────────────────────────────────────
    print("\n[AUTH] Logging in as test user…")
    try:
        token_res, _ = http_post_json("/api/auth/login", {
            "email": "phase4test@example.com",
            "password": "Phase4@Test"
        })
        token = token_res["access_token"]
        print(f"  JWT obtained: {token[:40]}…")
    except Exception as e:
        print(f"  Could not login: {e}")
        print("  Continuing with anonymous requests…")
        token = None

    # ══════════════════════════════════════════════════════════════════════════
    # Task 7.1 — Text Detection  (target < 1.0 s)
    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + SEP)
    print("[7.1] TEXT DETECTION — target: < 1.0 second")

    spam_text = "URGENT! Claim your FREE $1,000 Amazon gift card NOW! Limited time offer. Click bit.ly/claimfree"
    ham_text  = "Hey, just checking if you received my last email about the project deadline."

    for label, text, expected in [("SPAM", spam_text, "spam"), ("HAM", ham_text, "ham")]:
        try:
            res, elapsed = http_post_json("/api/detect/text", {"text": text}, token)
            ok       = res["result"] == expected and elapsed < 1.0
            status   = PASS if ok else FAIL
            print(f"  [{label}] result={res['result']}  conf={res['confidence']:.4f}  time={elapsed*1000:.0f}ms  → {status}")
            results[f"text_{label.lower()}"] = {"ok": ok, "elapsed": elapsed, "result": res}
        except Exception as e:
            print(f"  [{label}] ERROR: {e}")
            results[f"text_{label.lower()}"] = {"ok": False, "error": str(e)}

    # ══════════════════════════════════════════════════════════════════════════
    # Task 7.2 — Image Detection  (target < 3.0 s)
    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + SEP)
    print("[7.2] IMAGE DETECTION — target: < 3.0 seconds")

    img_bytes = make_test_image(224, 224)
    print(f"  Test image: 224×224 JPEG ({len(img_bytes):,} bytes)")

    try:
        res, elapsed = http_post_multipart(
            "/api/detect/image", "file", "test_image.jpg",
            img_bytes, "image/jpeg", token
        )
        ok     = elapsed < 3.0 and res["result"] in ("real", "fake")
        status = PASS if ok else FAIL
        print(f"  result={res['result']}  conf={res['confidence']:.4f}  time={elapsed*1000:.0f}ms  → {status}")
        results["image"] = {"ok": ok, "elapsed": elapsed, "result": res}
    except Exception as e:
        print(f"  ERROR: {e}")
        results["image"] = {"ok": False, "error": str(e)}

    # ══════════════════════════════════════════════════════════════════════════
    # Task 7.3 — Video Detection  (target < 10.0 s)
    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + SEP)
    print("[7.3] VIDEO DETECTION — target: < 10.0 seconds")

    gif_bytes = make_test_video_gif(frames=5)
    print(f"  Test video: 5-frame GIF ({len(gif_bytes):,} bytes)")

    try:
        res, elapsed = http_post_multipart(
            "/api/detect/video", "file", "test_video.gif",
            gif_bytes, "image/gif", token
        )
        ok     = elapsed < 10.0 and res["result"] in ("real", "fake", "unknown")
        status = PASS if ok else FAIL
        print(f"  result={res['result']}  conf={res['confidence']:.4f}  frames={res.get('frames_analysed', '?')}  time={elapsed*1000:.0f}ms  → {status}")
        if elapsed >= 10.0:
            print("  ⚠️  Exceeded 10s — Task 7.4 will increase sample_rate")
        results["video"] = {"ok": ok, "elapsed": elapsed, "result": res}
    except Exception as e:
        print(f"  ERROR: {e}")
        results["video"] = {"ok": False, "error": str(e)}

    # ══════════════════════════════════════════════════════════════════════════
    # Task 7.5 — Verify MongoDB results have correct user_id
    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + SEP)
    print("[7.5] MONGODB user_id VALIDATION")

    from dotenv import load_dotenv
    load_dotenv(DOTENV)

    async def check_mongo():
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
        db = client["ai_detection_db"]

        total   = await db["detection_results"].count_documents({})
        with_id = await db["detection_results"].count_documents({"user_id": {"$ne": None}})
        anon    = total - with_id

        logs    = await db["system_logs"].count_documents({})
        users   = await db["users"].count_documents({})

        # Get latest 3 results
        cursor = db["detection_results"].find().sort("timestamp", -1).limit(3)
        recent = await cursor.to_list(length=3)

        return {
            "total_results":   total,
            "with_user_id":    with_id,
            "anonymous":       anon,
            "total_logs":      logs,
            "users":           users,
            "recent":          recent,
        }

    try:
        mongo_data = asyncio.run(check_mongo())
        print(f"  Users                : {mongo_data['users']}")
        print(f"  Detection results    : {mongo_data['total_results']}")
        print(f"    ↳ With user_id     : {mongo_data['with_user_id']}")
        print(f"    ↳ Anonymous        : {mongo_data['anonymous']}")
        print(f"  System logs          : {mongo_data['total_logs']}")
        print(f"\n  Latest 3 results:")
        for r in mongo_data["recent"]:
            uid = r.get("user_id", "None")[:12] + "…" if r.get("user_id") else "anonymous"
            print(f"    {r['input_type']:6s}  {r['result']:6s}  conf={r['confidence']:.3f}  user={uid}")
        ok = mongo_data["with_user_id"] > 0
        print(f"\n  user_id properly saved: {PASS if ok else FAIL}")
        results["mongo"] = {"ok": ok, **mongo_data}
    except Exception as e:
        print(f"  ERROR: {e}")
        results["mongo"] = {"ok": False, "error": str(e)}

    # ══════════════════════════════════════════════════════════════════════════
    # Summary
    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("  PHASE 7 TEST SUMMARY")
    print("=" * 60)
    all_pass = all(v.get("ok", False) for v in results.values())
    for key, val in results.items():
        icon = "✅" if val.get("ok") else "❌"
        t    = f"  {val['elapsed']*1000:.0f}ms" if "elapsed" in val else ""
        print(f"  {icon}  {key:<25}{t}")
    print()
    print(f"  Overall: {'ALL TESTS PASSED ✅' if all_pass else 'SOME TESTS FAILED ❌'}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    run()
