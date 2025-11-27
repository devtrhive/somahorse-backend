from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.security.admin_utils import get_current_admin
from app.models.user import User
from app.models.talent import Talent
from app.models.project import Project

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats")
def get_stats(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    return {
        "users": db.query(User).count(),
        "talents": db.query(Talent).count(),
        "projects": db.query(Project).count(),
    }


@router.post("/promote/{user_id}")
def promote_admin(
    user_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    user = db.query(User).get(user_id)
    if not user:
        return {"error": "User not found"}

    user.is_admin = True
    db.commit()
    return {"status": "success", "message": "User promoted"}
