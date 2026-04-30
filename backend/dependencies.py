"""
Task 4.4 — FastAPI dependency: get_current_user
Decodes the JWT Bearer token from the Authorization header
and returns the user document from MongoDB.

Uses auto_error=False so detection endpoints work both
with and without authentication (anonymous requests allowed).
"""
import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from bson import ObjectId

from database import db

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

JWT_SECRET    = os.getenv("JWT_SECRET", "change_me_in_production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# auto_error=False → returns None credentials instead of HTTP 401
# when the Authorization header is absent
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Optional[dict]:
    """
    Optional JWT dependency. Returns:
    - The full user document if a valid Bearer token is provided.
    - None if no Authorization header is present (anonymous).
    - Raises HTTP 401 if a token IS provided but is invalid or expired.
    """
    if credentials is None:
        return None   # anonymous request — detection still works

    token = credentials.credentials
    creds_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise creds_error
    except JWTError:
        raise creds_error

    user_doc = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user_doc:
        raise creds_error

    return user_doc
