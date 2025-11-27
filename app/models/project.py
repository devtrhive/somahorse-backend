from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    technical_brief = Column(String(2000), nullable=True)

    expected_duration_days = Column(Integer, nullable=True)
    time_to_match_days = Column(Integer, nullable=True)

    status = Column(String(50), nullable=False, default="pending")

    # Relationship → one project has ONE outcome
    outcome = relationship("ProjectOutcome", back_populates="project", uselist=False)
