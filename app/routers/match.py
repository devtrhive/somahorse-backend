from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.talent import Talent
from app.models.project import Project
from app.security.admin_utils import get_current_admin

router = APIRouter(prefix="/match", tags=["Matching"])


def compute_match_score(talent, project):
    score = 0
    for skill in project.skills.split(","):
        if skill.strip().lower() in talent.skills.lower():
            score += 1
    return score


@router.get("/{project_id}")
def match_talents(
    project_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    project = db.query(Project).get(project_id)
    if not project:
        return {"error": "Project not found"}

    talents = db.query(Talent).all()

    results = []
    for talent in talents:
        score = compute_match_score(talent, project)
        results.append({"talent": talent, "score": score})

    results.sort(key=lambda x: x["score"], reverse=True)

    return results
