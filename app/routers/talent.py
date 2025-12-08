# app/routers/talent.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.talent import Talent
from app.schemas.talent import TalentCreate, TalentRead, TalentUpdate

# Auth helpers (admin_utils exposes get_current_user and get_current_admin)
from app.security.admin_utils import get_current_user, get_current_admin

router = APIRouter(prefix="/talent", tags=["Talent"])


# --- CREATE TALENT (authenticated user or admin) ---
@router.post("/", response_model=TalentRead, status_code=status.HTTP_201_CREATED)
def create_talent(
    payload: TalentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Create a talent profile. Allowed for authenticated users (role 'user') and admin.
    The function checks email uniqueness and uses the payload to create the record.
    """
    # Basic role check: allow users and admins to create
    role = current_user.get("role")
    if role not in ("user", "admin"):
        raise HTTPException(status_code=403, detail="Only authenticated users may create talent profiles")

    # prevent duplicates
    existing = db.query(Talent).filter(Talent.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Optionally: ensure the creator's email matches the talent email (recommended)
    # if current_user.get("email") != payload.email and role != "admin":
    #     raise HTTPException(status_code=403, detail="You can only create a talent profile for your own account")

    talent = Talent(**payload.model_dump())
    # if you have firebase uid / want to store it:
    # talent.firebase_uid = current_user.get("uid")
    db.add(talent)
    db.commit()
    db.refresh(talent)
    return talent


# --- LIST ALL TALENT (admin only) ---
@router.get("/", response_model=List[TalentRead])
def list_talent(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    return db.query(Talent).all()


# --- GET TALENT (public read) ---
@router.get("/{talent_id}", response_model=TalentRead)
def get_talent(talent_id: int, db: Session = Depends(get_db)):
    """
    Public endpoint to view talent profiles (per spec, these are public).
    If you want them restricted, swap to Depends(get_current_user) and adjust.
    """
    talent = db.get(Talent, talent_id)
    if not talent:
        raise HTTPException(status_code=404, detail="Talent not found")
    return talent


# --- UPDATE: owner (talent) OR admin ---
@router.patch("/{talent_id}", response_model=TalentRead)
def update_talent(
    talent_id: int,
    payload: TalentUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    talent = db.get(Talent, talent_id)
    if not talent:
        raise HTTPException(status_code=404, detail="Talent not found")

    role = current_user.get("role")
    user_email = current_user.get("email")
    user_uid = current_user.get("uid")

    # Owner check: prefer firebase_uid if you store it; otherwise match by email
    is_owner = False
    if hasattr(talent, "firebase_uid") and talent.firebase_uid:
        is_owner = talent.firebase_uid == user_uid
    else:
        is_owner = talent.email == user_email

    # Allow owner OR admin
    if not (is_owner or role == "admin"):
        raise HTTPException(status_code=403, detail="Not authorized to update this talent")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(talent, field, value)

    db.commit()
    db.refresh(talent)
    return talent


# --- DELETE: owner (self) OR admin ---
@router.delete("/{talent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_talent(
    talent_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    talent = db.get(Talent, talent_id)
    if not talent:
        raise HTTPException(status_code=404, detail="Talent not found")

    role = current_user.get("role")
    user_email = current_user.get("email")
    user_uid = current_user.get("uid")

    # Owner check
    is_owner = False
    if hasattr(talent, "firebase_uid") and talent.firebase_uid:
        is_owner = talent.firebase_uid == user_uid
    else:
        is_owner = talent.email == user_email

    if not (is_owner or role == "admin"):
        raise HTTPException(status_code=403, detail="Not authorized to delete this talent")

    db.delete(talent)
    db.commit()
    return None
@router.get("/talents")
def list_talents(
    location: str = None,
    min_vetting_score: float = 0.0,
    db: Session = Depends(get_db)
):
    q = db.query(Talent)

    if location:
        q = q.filter(Talent.location.ilike(location))

    q = q.filter(Talent.vetting_overall_score >= min_vetting_score)

    return q.all()
