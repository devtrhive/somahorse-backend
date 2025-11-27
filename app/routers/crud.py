from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/api",
    tags=["CRUD"],
)
from app.dependencies import require_admin, require_talent

@router.get("/admin/talents", dependencies=[Depends(require_admin)])
def admin_list_all_talents(db: Session = Depends(get_db)):
    return db.query(models.Talent).all()

# -----------------------------------------
# USERS
# -----------------------------------------
@router.post("/users", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=user.password,   # hash later in Step 3
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/users", response_model=list[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


# -----------------------------------------
# SKILLS
# -----------------------------------------
@router.post("/skills")
def create_skill(skill: schemas.SkillCreate, db: Session = Depends(get_db)):
    new_skill = models.Skill(name=skill.name)
    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)
    return new_skill


@router.get("/skills")
def get_skills(db: Session = Depends(get_db)):
    return db.query(models.Skill).all()


# -----------------------------------------
# TALENTS
# -----------------------------------------
@router.post("/talents", response_model=schemas.TalentResponse)
def create_talent(talent: schemas.TalentCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == talent.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_talent = models.Talent(
        user_id=talent.user_id,
        bio=talent.bio,
        experience_level=talent.experience_level
    )

    # Add skills
    skills = db.query(models.Skill).filter(models.Skill.id.in_(talent.skill_ids)).all()
    new_talent.skills = skills

    db.add(new_talent)
    db.commit()
    db.refresh(new_talent)
    return new_talent


@router.get("/talents")
def list_talents(db: Session = Depends(get_db)):
    return db.query(models.Talent).all()


# -----------------------------------------
# PROJECTS
# -----------------------------------------
@router.post("/projects", response_model=schemas.ProjectResponse)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    owner = db.query(models.User).filter(models.User.id == project.owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")

    new_project = models.Project(
        title=project.title,
        description=project.description,
        owner_id=project.owner_id
    )

    skills = db.query(models.Skill).filter(models.Skill.id.in_(project.skill_ids)).all()
    new_project.required_skills = skills

    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


@router.get("/projects")
def list_projects(db: Session = Depends(get_db)):
    return db.query(models.Project).all()


# -----------------------------------------
# PROJECT OUTCOMES
# -----------------------------------------
@router.post("/projects/{project_id}/outcome")
def create_outcome(project_id: int, outcome: schemas.ProjectOutcomeCreate, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    new_outcome = models.ProjectOutcome(
        project_id=project_id,
        is_completed=outcome.is_completed,
        score=outcome.score,
        feedback=outcome.feedback
    )

    db.add(new_outcome)
    db.commit()
    db.refresh(new_outcome)
    return new_outcome
from sqlalchemy.orm import Session
from . import models

def calculate_match_score(talent_skills, project_skills):
    if not talent_skills:
        return 0
    
    matches = set([s.name for s in talent_skills]).intersection(
        set([s.name for s in project_skills])
    )

    score = (len(matches) / len(project_skills)) * 100
    return round(score, 2)


def match_talents_to_project(db: Session, project_id: int):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    
    if not project:
        return None

    talents = db.query(models.Talent).all()
    results = []

    for t in talents:
        score = calculate_match_score(
            talent_skills=t.skills, 
            project_skills=project.required_skills
        )

        results.append({
            "talent_id": t.id,
            "talent_name": t.user.username,
            "skills": [s.name for s in t.skills],
            "match_score": score
        })

    results.sort(key=lambda x: x["match_score"], reverse=True)

    return results
