from fastapi import Depends, HTTPException, status
from app.auth.firebase import verify_firebase_token


async def get_current_user(token: str = Depends(verify_firebase_token)):
    """
    Extract user information returned by Firebase token verification.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials."
        )
    return token  # contains { uid, email, role }
