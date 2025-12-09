import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Depends, Request

from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User



# Load Firebase service account JSON
cred = credentials.Certificate("firebase-service-account.json")

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)


def verify_token(request: Request):
    """Extract and verify Firebase token from Authorization header."""
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = auth_header.split(" ")[1]

    try:
        decoded = auth.verify_id_token(token)
        return decoded

    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


def verify_firebase_token(token: str):
    """Compatibility wrapper for old imports."""
    try:
        decoded = auth.verify_id_token(token)
        return decoded
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


def get_current_user(request: Request, db: Session = Depends(get_db)):
    """Get the authenticated Firebase user + DB user with role."""
    decoded = verify_token(request)

    email = decoded.get("email")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=403, detail="User not found or unauthorized")

    return user
