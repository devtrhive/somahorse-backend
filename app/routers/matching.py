from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Project, Talent
from app.schemas.talent import TalentResponse

router = APIRouter(
    prefix="/api",
    tags=["Matching"]
)

def calculate_match(talent_skills, project_skills):
    if not talent_skills:
        return 0

    matches = set(talent_skills).intersection(set(project_skills))
    if len(project_skills) == 0:
        return 0

    return round((len(matches) / len(project_skills)) * 100, 2)


@router.get("/match/{project_id}")
def match_talents(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    required = [s.name for s in project.required_skills]
    talents = db.query(Talent).all()

    results = []

    for talent in talents:
        skills = [s.name for s in talent.skills]
        score = calculate_match(skills, required)

        results.append({
            "talent_id": talent.id,
            "name": talent.user.username,
            "skills": skills,
            "match_score": score
        })

    results.sort(key=lambda x: x["match_score"], reverse=True)
    return {"project_id": project_id, "matches": results}
