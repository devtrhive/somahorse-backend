from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Talent, Project, ProjectOutcome, User
from app.schemas.talent import TalentCreate, TalentUpdate, TalentResponse
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.schemas.project_outcome import ProjectOutcomeCreate, ProjectOutcomeUpdate
from app.auth.dependencies import get_current_user
from app.routes.matching import calculate_match
from typing import List

router = APIRouter(prefix="/admin", tags=["Admin"])


# ------------------------------
# ADMIN AUTH CHECK
# ------------------------------
def verify_admin(user: User):
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")


# ------------------------------
# TALENT MANAGEMENT
# ------------------------------
@router.get("/talents", response_model=List[TalentResponse])
def list_talents(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    verify_admin(user)
    return db.query(Talent).all()


@router.post("/talents", response_model=TalentResponse)
def create_talent(
    payload: TalentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    verify_admin(user)

    talent = Talent(**payload.dict())
    db.add(talent)
    db.commit()
    db.refresh(talent)
    return talent


@router.patch("/talents/{talent_id}", response_model=TalentResponse)
def update_talent(
    talent_id: int,
    payload: TalentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    verify_admin(user)

    talent = db.query(Talent).filter(Talent.id == talent_id).first()
    if not talent:
        raise HTTPException(status_code=404, detail="Talent not found")

    for key, value in payload.dict(exclude_unset=True).items():
        setattr(talent, key, value)

    db.commit()
    db.refresh(talent)
    return talent


@router.delete("/talents/{talent_id}")
def delete_talent(
    talent_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    verify_admin(user)

    talent = db.query(Talent).filter(Talent.id == talent_id).first()
    if not talent:
        raise HTTPException(status_code=404, detail="Talent not found")

    db.delete(talent)
    db.commit()
    return {"message": "Talent deleted successfully"}


# ------------------------------
# PROJECT MANAGEMENT
# ------------------------------
@router.get("/projects", response_model=List[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    verify_admin(user)
    return db.query(Project).all()


@router.post("/projects", response_model=ProjectResponse)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    verify_admin(user)

    project = Project(**payload.dict())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.patch("/projects/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    verify_admin(user)

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    for key, value in payload.dict(exclude_unset=True).items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)
    return project


@router.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    verify_admin(user)

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}


# ------------------------------
# OUTCOME MANAGEMENT
# ------------------------------
@router.get("/outcomes")
def list_outcomes(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    verify_admin(user)
    return db.query(ProjectOutcome).all()


# ------------------------------
# ADMIN: VIEW MATCHES FOR ANY PROJECT
# ------------------------------
@router.get("/match/{project_id}")
def admin_match_view(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    verify_admin(user)

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    required_skills = [s.name for s in project.required_skills]
    talents = db.query(Talent).all()

    matches = []

    for t in talents:
        skills = [s.name for s in t.skills]
        score = calculate_match(skills, required_skills, t.experience_years or 0)

        matches.append({
            "talent_id": t.id,
            "name": t.user.username if t.user else None,
            "match_score": score,
            "skills": skills,
            "experience_years": t.experience_years
        })

    matches.sort(key=lambda x: x["match_score"], reverse=True)
    return {"project_id": project_id, "matches": matches}


# ------------------------------
# ADMIN FORCE MATCH TALENT -> PROJECT
# ------------------------------
@router.post("/match/{project_id}/assign/{talent_id}")
def admin_force_assign(
    project_id: int,
    talent_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    verify_admin(user)

    project = db.query(Project).filter(Project.id == project_id).first()
    talent = db.query(Talent).filter(Talent.id == talent_id).first()

    if not project or not talent:
        raise HTTPException(status_code=404, detail="Project or Talent not found")

    project.assigned_talent_id = talent.id
    db.commit()

    return {"message": f"Talent {talent.id} assigned to project {project.id}"}
