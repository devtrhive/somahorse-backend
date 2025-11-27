from typing import List, Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class TalentBase(BaseModel):
    full_name: str
    email: EmailStr
    skills: List[str]
    experience_years: int = 0
    profile_completed: bool = False


class TalentCreate(TalentBase):
    pass


class TalentUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    profile_completed: Optional[bool] = None


class TalentRead(TalentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
