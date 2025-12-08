from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Text
from app.database import Base
import enum

class AvailabilityStatus(str, enum.Enum):
    available = "available"
    busy = "busy"
    on_project = "on_project"

class Talent(Base):
    __tablename__ = "talent"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)

    skills = Column(ARRAY(Text), nullable=False, default=list)
    experience_years = Column(Integer, nullable=False, default=0)
    profile_completed = Column(Boolean, nullable=False, default=False)

    availability_status = Column(
        Enum(AvailabilityStatus, name="availability_enum"),
        nullable=False,
        default=AvailabilityStatus.available
    )
