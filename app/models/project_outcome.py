from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class ProjectOutcome(Base):
    __tablename__ = "project_outcomes"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)

    delivery_speed_days = Column(Integer, nullable=True)
    fraud_risk_score = Column(Integer, nullable=True)
    client_feedback_score = Column(Integer, nullable=True)

    # Relationship back to Project
    project = relationship("Project", back_populates="outcome")
