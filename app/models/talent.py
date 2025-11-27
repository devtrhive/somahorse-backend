from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base
from sqlalchemy import ARRAY, Text

class Talent(Base):
    __tablename__ = "talent"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    skills = Column(ARRAY(Text), nullable=False, default=list)
    experience_years = Column(Integer, nullable=False, default=0)
    profile_completed = Column(Boolean, nullable=False, default=False)