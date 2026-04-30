import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from database import ping_db, db
from routers import auth, detect


# ─── Lifespan: startup ping ───────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup tasks before accepting requests."""
    await ping_db()
    yield


# ─── App factory ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="Multi-Modal AI Content & Spam Detection System",
    description=(
        "API for detecting spam text, fake images, and deepfake videos "
        "using Machine Learning."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ─── Task 4.11 — CORS middleware ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",                          # local dev
        "https://ai-shield-detection.vercel.app",        # Vercel production
        "https://ai-shield-detection-samarthsmasher.vercel.app",  # Vercel preview
        "https://*.vercel.app",                          # all Vercel previews
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Task 4.10 — Request logging middleware ───────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    After every HTTP response, asynchronously write a SystemLog document
    to MongoDB with endpoint, method, status_code, and processing_time_ms.
    """
    start  = time.perf_counter()
    response: JSONResponse = await call_next(request)
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

    try:
        log_doc = {
            "endpoint":           request.url.path,
            "method":             request.method,
            "status_code":        response.status_code,
            "processing_time_ms": elapsed_ms,
            "timestamp":          datetime.now(timezone.utc),
        }
        await db["system_logs"].insert_one(log_doc)
    except Exception:
        pass  # Never let logging failures break the response

    return response


# ─── Tasks 4.1 & 4.5 — Register routers ──────────────────────────────────────
app.include_router(auth.router)
app.include_router(detect.router)


# ─── Health check ─────────────────────────────────────────────────────────────
@app.get("/api/health", tags=["Health"])
async def health_check():
    """Simple health-check endpoint to confirm the server is running."""
    return {"status": "ok", "message": "AI Detection API is live."}
