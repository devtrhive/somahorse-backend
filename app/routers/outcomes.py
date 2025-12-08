from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Project, ProjectOutcome

router = APIRouter(prefix="/api/projects", tags=["Project Outcomes"])

@router.post("/{project_id}/outcomes")
def submit_outcomes(
    project_id: int,
    payload: dict,
    db: Session = Depends(get_db)
):

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Validation
    if not (0 <= payload["forecast_accuracy_percentage"] <= 100):
        raise HTTPException(400, "forecast_accuracy_percentage must be 0–100")

    if not (1 <= payload["client_satisfaction_rating"] <= 5):
        raise HTTPException(400, "client_satisfaction_rating must be 1–5")

    if not (1 <= payload["code_quality_score"] <= 5):
        raise HTTPException(400, "code_quality_score must be 1–5")

    if payload["delivery_speed_days"] < 0:
        raise HTTPException(400, "delivery_speed_days must be >= 0")

    outcome = ProjectOutcome(
        project_id=project_id,
        **payload
    )
    db.add(outcome)
    db.commit()
    db.refresh(outcome)

    return {"status": "success", "outcome_id": outcome.id}
