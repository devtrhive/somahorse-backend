from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.notification import Notification
from app.security.auth import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/")
def list_notifications(user=Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Notification).filter(Notification.user_id == user.id).all()


@router.post("/")
def send_notification(message: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    notif = Notification(user_id=user.id, message=message)
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif
