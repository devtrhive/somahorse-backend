from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Project, ProjectOutcome, AuditLog
from pydantic import BaseModel, condecimal, conint, confloat
from typing import Optional
from app.security.roles import requires_role

router = APIRouter(prefix="/v1", tags=["ProjectOutcome"])

class OutcomeCreate(BaseModel):
    forecast_accuracy_percentage: condecimal(ge=0, le=100, max_digits=5, decimal_places=2)
    client_satisfaction_rating: conint(ge=1, le=5)
    code_quality_score: conint(ge=1, le=5)
    delivery_speed_days: conint(ge=0)
    user_engagement_rate: Optional[confloat(ge=0, le=1)]
    retention_rate: Optional[confloat(ge=0, le=1)]

@router.post("/projects/{project_id}/outcomes", status_code=201)
def create_outcome(project_id: int, payload: OutcomeCreate, db: Session = Depends(get_db), user=Depends(requires_role("client"))):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check if outcome already exists — make outcomes immutable per spec
    existing = db.query(ProjectOutcome).filter(ProjectOutcome.project_id == project_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Outcome for project already recorded and is immutable")

    # create outcome
    outcome = ProjectOutcome(
        project_id=project_id,
        forecast_accuracy_percentage=payload.forecast_accuracy_percentage,
        client_satisfaction_rating=payload.client_satisfaction_rating,
        code_quality_score=payload.code_quality_score,
        delivery_speed_days=payload.delivery_speed_days,
        user_engagement_rate=payload.user_engagement_rate,
        retention_rate=payload.retention_rate,
        created_by=user.get("id")
    )
    db.add(outcome)
    db.commit()
    db.refresh(outcome)

    # audit
    audit = AuditLog(
        actor_user_id=user.get("id"),
        action_type="create_project_outcome",
        resource_type="project_outcomes",
        resource_id=outcome.id,
        details=payload.dict()
    )
    db.add(audit)
    db.commit()

    return {"id": outcome.id, "project_id": project_id}
