from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session

from app.auth import decode_access_token
from app.database import get_db
from app import models


def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = authorization.split(" ")[1]  # "Bearer <token>"
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(models.User).filter(models.User.id == payload["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


def require_admin(user=Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    return user


def require_talent(user=Depends(get_current_user)):
    if user.role != "talent":
        raise HTTPException(status_code=403, detail="Talent only")
    return user
