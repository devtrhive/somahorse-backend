from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.security.firebase import verify_firebase_token
from app.models.user import User
from app.schemas.user import UserRead
from app.security.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=UserRead)
def login(id_token: str, db: Session = Depends(get_db)):
    user_info = verify_firebase_token(id_token)

    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid Firebase token")

    email = user_info["email"]
    uid = user_info["uid"]

    user = db.query(User).filter(User.email == email).first()

    # Auto-create user on login (like most platforms)
    if not user:
        user = User(email=email, firebase_uid=uid, is_admin=False)
        db.add(user)
        db.commit()
        db.refresh(user)

    return user


@router.get("/me", response_model=UserRead)
def get_profile(current_user=Depends(get_current_user)):
    return current_user
