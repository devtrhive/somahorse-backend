from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Project, Talent

router = APIRouter(prefix="/v1", tags=["Matching"])

def calculate_skill_match(talent_skills, project_skills):
    if not talent_skills:
        return 0.0
    matches = set(talent_skills).intersection(set(project_skills))
    if not project_skills:
        return 0.0
    return (len(matches) / len(project_skills)) * 100.0

@router.get("/match/{project_id}")
def match_talents(
    project_id: int,
    vetting_min: float = Query(0.0, ge=0.0, le=100.0),
    location: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_skills = [s.name for s in getattr(project, "required_skills", [])]  # adjust to real model
    talents_q = db.query(Talent)
    if location:
        talents_q = talents_q.filter(Talent.location == location)
    talents = talents_q.all()

    results = []
    for t in talents:
        talent_skills = [s.name for s in getattr(t, "skills", [])]
        skill_score = calculate_skill_match(talent_skills, project_skills)  # 0-100
        vetting_score = getattr(t, "vetting_overall_score", 0)  # make sure field exists on Talent
        # Combine scores: 70% skill match, 30% vetting (simple heuristic)
        combined = round((0.7 * skill_score) + (0.3 * vetting_score), 2)
        if vetting_score < vetting_min:
            continue
        results.append({
            "talent_id": t.id,
            "name": getattr(t, "full_name", None),
            "skills": talent_skills,
            "skill_score": round(skill_score,2),
            "vetting_score": vetting_score,
            "combined_score": combined,
            "location": getattr(t, "location", None)
        })

    results.sort(key=lambda x: x["combined_score"], reverse=True)
    return {"project_id": project_id, "matches": results[:limit]}
