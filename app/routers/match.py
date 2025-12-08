from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Project, Talent

router = APIRouter(prefix="/match", tags=["Matching"])

@router.get("/{project_id}")
def match_talent(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    required = set(project.required_skills or [])

    talents = db.query(Talent).filter(Talent.profile_completed == True).all()

    results = []
    for t in talents:
        skill_overlap = len(required.intersection(set(t.skills)))
        total = len(required) if len(required) > 0 else 1
        score = skill_overlap / total

        results.append({
            "talent_id": t.id,
            "full_name": t.full_name,
            "email": t.email,
            "skills": t.skills,
            "score": round(score, 2)
        })

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return {"project_id": project_id, "matches": results}
