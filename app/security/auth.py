# app/security/auth.py

from fastapi import Depends, Header, HTTPException, status
from app.security.firebase import verify_firebase_token


async def get_current_user(authorization: str = Header(None)):
    """
    Extracts and verifies Firebase Bearer token.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")

    token = authorization.split(" ")[1]

    user = verify_firebase_token(token)

    return user
