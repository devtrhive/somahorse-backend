# app/routers/project_outcome.py
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.project_outcome import ProjectOutcome
from app.models.project import Project
from app.schemas.project_outcome import (
    ProjectOutcomeCreate,
    ProjectOutcomeRead,
    ProjectOutcomeUpdate,
)

from app.security.admin_utils import get_current_user, get_current_admin

router = APIRouter(prefix="/project-outcome", tags=["Project Outcome"])


# --- CREATE OUTCOME (talent assigned to project OR admin) ---
@router.post("/", response_model=ProjectOutcomeRead, status_code=status.HTTP_201_CREATED)
def create_outcome(
    payload: ProjectOutcomeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    project = db.get(Project, payload.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    role = current_user.get("role")
    user_email = current_user.get("email")
    user_uid = current_user.get("uid")

    # Talent allowed only if assigned to project
    is_assigned = False
    # recommended fields: assigned_talent_uids (list of UIDs) or assigned_talent_ids/emails
    if hasattr(project, "assigned_talent_uids") and project.assigned_talent_uids:
        is_assigned = user_uid in (project.assigned_talent_uids or [])
    elif hasattr(project, "assigned_talent_ids") and project.assigned_talent_ids:
        # if you store numeric DB ids, ensure you compare appropriately
        is_assigned = str(current_user.get("uid")) in [str(x) for x in (project.assigned_talent_ids or [])]
    elif hasattr(project, "assigned_talent_emails") and project.assigned_talent_emails:
        is_assigned = user_email in (project.assigned_talent_emails or [])

    if role == "talent" and not is_assigned and role != "admin":
        raise HTTPException(status_code=403, detail="You are not assigned to this project")

    # create outcome
    outcome = ProjectOutcome(**payload.model_dump())
    db.add(outcome)
    db.commit()
    db.refresh(outcome)
    return outcome


# --- GET OUTCOME (project owner, assigned talent, or admin) ---
@router.get("/{project_id}", response_model=ProjectOutcomeRead)
def get_outcome(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    outcome = db.query(ProjectOutcome).filter(ProjectOutcome.project_id == project_id).first()
    if not outcome:
        raise HTTPException(status_code=404, detail="Outcome not found")

    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    role = current_user.get("role")
    user_email = current_user.get("email")
    user_uid = current_user.get("uid")

    # Check permissions: admin always allowed
    if role == "admin":
        return outcome

    # Project owner check
    is_owner = False
    if hasattr(project, "owner_uid") and project.owner_uid:
        is_owner = project.owner_uid == user_uid
    elif hasattr(project, "owner_email") and project.owner_email:
        is_owner = project.owner_email == user_email

    # Assigned talent check
    is_assigned = False
    if hasattr(project, "assigned_talent_uids") and project.assigned_talent_uids:
        is_assigned = user_uid in (project.assigned_talent_uids or [])
    elif hasattr(project, "assigned_talent_ids") and project.assigned_talent_ids:
        is_assigned = str(user_uid) in [str(x) for x in (project.assigned_talent_ids or [])]
    elif hasattr(project, "assigned_talent_emails") and project.assigned_talent_emails:
        is_assigned = user_email in (project.assigned_talent_emails or [])

    if not (is_owner or is_assigned):
        raise HTTPException(status_code=403, detail="Not authorized to view this outcome")

    return outcome


# --- UPDATE OUTCOME (outcome owner (talent) OR admin) ---
@router.patch("/{outcome_id}", response_model=ProjectOutcomeRead)
def update_outcome(
    outcome_id: int,
    payload: ProjectOutcomeUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    outcome = db.get(ProjectOutcome, outcome_id)
    if not outcome:
        raise HTTPException(status_code=404, detail="Outcome not found")

    project = db.get(Project, outcome.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    role = current_user.get("role")
    user_email = current_user.get("email")
    user_uid = current_user.get("uid")

    # owner of outcome: prefer a stored outcome.submitter_uid or match by email
    is_outcome_owner = False
    if hasattr(outcome, "submitter_uid") and outcome.submitter_uid:
        is_outcome_owner = outcome.submitter_uid == user_uid
    elif hasattr(outcome, "submitter_email") and outcome.submitter_email:
        is_outcome_owner = outcome.submitter_email == user_email
    else:
        # fallback: if not stored, require admin to update
        if role != "admin":
            raise HTTPException(status_code=403, detail="Only outcome owner or admin can update this outcome")

    if not (is_outcome_owner or role == "admin"):
        raise HTTPException(status_code=403, detail="Only outcome owner or admin can update this outcome")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(outcome, field, value)

    db.commit()
    db.refresh(outcome)
    return outcome


# --- DELETE OUTCOME (outcome owner OR admin) ---
@router.delete("/{outcome_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_outcome(
    outcome_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    outcome = db.get(ProjectOutcome, outcome_id)
    if not outcome:
        raise HTTPException(status_code=404, detail="Outcome not found")

    role = current_user.get("role")
    user_email = current_user.get("email")
    user_uid = current_user.get("uid")

    is_outcome_owner = False
    if hasattr(outcome, "submitter_uid") and outcome.submitter_uid:
        is_outcome_owner = outcome.submitter_uid == user_uid
    elif hasattr(outcome, "submitter_email") and outcome.submitter_email:
        is_outcome_owner = outcome.submitter_email == user_email
    else:
        if role != "admin":
            raise HTTPException(status_code=403, detail="Only outcome owner or admin can delete this outcome")

    if not (is_outcome_owner or role == "admin"):
        raise HTTPException(status_code=403, detail="Only outcome owner or admin can delete this outcome")

    db.delete(outcome)
    db.commit()
    return None
