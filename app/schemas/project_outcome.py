from typing import Optional
from pydantic import BaseModel, ConfigDict

class ProjectOutcomeBase(BaseModel):
    delivery_speed_days: Optional[int] = None
    fraud_risk_score: Optional[int] = None
    client_feedback_score: Optional[int] = None


class ProjectOutcomeCreate(ProjectOutcomeBase):
    pass


class ProjectOutcomeUpdate(BaseModel):
    delivery_speed_days: Optional[int] = None
    fraud_risk_score: Optional[int] = None
    client_feedback_score: Optional[int] = None


class ProjectOutcomeRead(ProjectOutcomeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)