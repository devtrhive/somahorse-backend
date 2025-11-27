from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.security.firebase import verify_firebase_token

oauth2_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
):
    """
    Extract user info from Firebase token.
    """
    token = credentials.credentials
    decoded = verify_firebase_token(token)
    return decoded


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
):
    """
    Restrict endpoint access to ADMIN users only.
    """
    token = credentials.credentials
    decoded = verify_firebase_token(token)

    # Firebase custom claims must include: { role: "admin" }
    role = decoded.get("role")

    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access only",
        )

    return decoded
