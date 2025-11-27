from pydantic import BaseModel
from typing import List

class LoginSchema(BaseModel):
    email: str
    password: str

# -------------------
# USER SCHEMAS
# -------------------
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "talent"


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str

    class Config:
        orm_mode = True


# -------------------
# SKILL SCHEMAS
# -------------------
class SkillCreate(BaseModel):
    name: str


# -------------------
# TALENT SCHEMAS
# -------------------
class TalentCreate(BaseModel):
    user_id: int
    bio: str
    experience_level: str
    skill_ids: List[int]


class TalentResponse(BaseModel):
    id: int
    user_id: int
    bio: str
    experience_level: str
    skill_ids: List[int] = []

    class Config:
        orm_mode = True


# -------------------
# PROJECT SCHEMAS
# -------------------
class ProjectCreate(BaseModel):
    owner_id: int
    title: str
    description: str
    skill_ids: List[int]


class ProjectResponse(BaseModel):
    id: int
    title: str
    description: str
    owner_id: int

    class Config:
        orm_mode = True


# -------------------
# OUTCOME SCHEMA
# -------------------
class ProjectOutcomeCreate(BaseModel):
    is_completed: bool
    score: int
    feedback: str
