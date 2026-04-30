"""
Tasks 4.1, 4.2, 4.3 — Authentication Router
Routes:
  POST /api/auth/register  → hash password, insert User into MongoDB
  POST /api/auth/login     → verify password, return JWT access token
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from fastapi import APIRouter, HTTPException, status
from jose import jwt

from database import db
from models.user_model import UserCreate, UserResponse

# ─── Config ───────────────────────────────────────────────────────────────────
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

JWT_SECRET    = os.getenv("JWT_SECRET", "change_me_in_production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

# ─── Helpers ──────────────────────────────────────────────────────────────────
router = APIRouter(prefix="/api/auth", tags=["Auth"])


def _hash_password(plain: str) -> str:
    """Hash a password using bcrypt directly (avoids passlib/bcrypt 5.x bug)."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def _create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    payload = data.copy()
    expire  = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=JWT_EXPIRE_MINUTES))
    payload.update({"exp": expire})
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


# ─── Task 4.2 — POST /register ────────────────────────────────────────────────
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(user_in: UserCreate):
    """Accept username, email, password. Hash password and insert into MongoDB."""
    users_col = db["users"]

    # Check uniqueness
    if await users_col.find_one({"email": user_in.email}):
        raise HTTPException(status_code=400, detail="Email already registered.")
    if await users_col.find_one({"username": user_in.username}):
        raise HTTPException(status_code=400, detail="Username already taken.")

    doc = {
        "username":        user_in.username,
        "email":           user_in.email,
        "hashed_password": _hash_password(user_in.password),
        "created_at":      datetime.now(timezone.utc),
    }
    result = await users_col.insert_one(doc)

    return UserResponse(
        id         = str(result.inserted_id),
        username   = user_in.username,
        email      = user_in.email,
        created_at = doc["created_at"],
    )


# ─── Task 4.3 — POST /login ───────────────────────────────────────────────────
@router.post(
    "/login",
    summary="Login and receive a JWT access token",
)
async def login(credentials: dict):
    """
    Accepts JSON body: {"email": "...", "password": "..."}.
    Returns {"access_token": "...", "token_type": "bearer"}.
    """
    email    = credentials.get("email", "")
    password = credentials.get("password", "")

    users_col = db["users"]
    user_doc  = await users_col.find_one({"email": email})

    if not user_doc or not _verify_password(password, user_doc["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = _create_access_token(
        data={"sub": str(user_doc["_id"]), "username": user_doc["username"]}
    )
    return {"access_token": token, "token_type": "bearer"}
