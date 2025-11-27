# app/routers/project.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate

from app.security.admin_utils import get_current_user, get_current_admin

router = APIRouter(prefix="/project", tags=["Project"])


# --- CREATE PROJECT (user or admin) ---
@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Allow authenticated 'user' creators, or admin to create projects.
    If you want to attach ownership, add a field like owner_email or owner_uid to Project model.
    """
    role = current_user.get("role")
    if role not in ("user", "admin", "client"):
        raise HTTPException(status_code=403, detail="Only clients/users or admins may create projects")

    # Create project record
    project = Project(**payload.model_dump())
    # recommend storing ownership:
    # project.owner_email = current_user.get("email")
    # project.owner_uid = current_user.get("uid")
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


# --- LIST PROJECTS (public read) ---
@router.get("/", response_model=List[ProjectRead])
def list_projects(db: Session = Depends(get_db)):
    """
    Public listing of projects. If you want only authenticated listing, add Depends(get_current_user).
    """
    return db.query(Project).all()


# --- GET PROJECT (public read) ---
@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# --- UPDATE PROJECT (owner OR admin) ---
@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    role = current_user.get("role")
    user_email = current_user.get("email")
    user_uid = current_user.get("uid")

    # Ownership check: if your Project has owner_email or owner_uid fields use them
    is_owner = False
    if hasattr(project, "owner_uid") and project.owner_uid:
        is_owner = project.owner_uid == user_uid
    elif hasattr(project, "owner_email") and project.owner_email:
        is_owner = project.owner_email == user_email
    else:
        # If ownership fields are not present, default to admin-only updates
        if role != "admin":
            raise HTTPException(status_code=403, detail="Only project owner or admin can update this project")

    if not (is_owner or role == "admin"):
        raise HTTPException(status_code=403, detail="Only project owner or admin can update this project")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project


# --- DELETE PROJECT (owner OR admin) ---
@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    role = current_user.get("role")
    user_email = current_user.get("email")
    user_uid = current_user.get("uid")

    is_owner = False
    if hasattr(project, "owner_uid") and project.owner_uid:
        is_owner = project.owner_uid == user_uid
    elif hasattr(project, "owner_email") and project.owner_email:
        is_owner = project.owner_email == user_email
    else:
        if role != "admin":
            raise HTTPException(status_code=403, detail="Only project owner or admin can delete this project")

    if not (is_owner or role == "admin"):
        raise HTTPException(status_code=403, detail="Only project owner or admin can delete this project")

    db.delete(project)
    db.commit()
    return None
