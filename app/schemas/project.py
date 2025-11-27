from typing import Optional
from pydantic import BaseModel, ConfigDict

class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    technical_brief: Optional[str] = None
    expected_duration_days: Optional[int] = None
    time_to_match_days: Optional[int] = None
    days_of_trial_and_error: Optional[int] = None
    status: str = "draft"


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    technical_brief: Optional[str] = None
    expected_duration_days: Optional[int] = None
    time_to_match_days: Optional[int] = None
    days_of_trial_and_error: Optional[int] = None
    status: Optional[str] = None


class ProjectRead(ProjectBase):
    id: int

    model_config = ConfigDict(from_attributes=True)