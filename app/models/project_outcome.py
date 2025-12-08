from sqlalchemy import Column, Integer, ForeignKey, Numeric, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.sql import func
from sqlalchemy import DateTime, JSON

class ProjectOutcome(Base):
    __tablename__ = "project_outcomes"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)

    # Week 4 required metrics
    forecast_accuracy_percentage = Column(Numeric(5,2), nullable=False)   # 0.00 - 100.00
    client_satisfaction_rating = Column(Integer, nullable=False)           # 1-5
    code_quality_score = Column(Integer, nullable=False)                  # 1-5
    delivery_speed_days = Column(Integer, nullable=False)                 # >= 0

    # optional/derived fields
    user_engagement_rate = Column(Numeric(6,4), nullable=True)            # 0.0000 - 1.0000
    retention_rate = Column(Numeric(6,4), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(Integer, nullable=True)  # user id who submitted (for audit)

    # Relationship back to Project
    project = relationship("Project", back_populates="outcome", uselist=False)

    __table_args__ = (
        CheckConstraint('forecast_accuracy_percentage >= 0 AND forecast_accuracy_percentage <= 100', name='chk_forecast_accuracy'),
        CheckConstraint('client_satisfaction_rating >= 1 AND client_satisfaction_rating <= 5', name='chk_client_satisfaction'),
        CheckConstraint('code_quality_score >= 1 AND code_quality_score <= 5', name='chk_code_quality'),
        CheckConstraint('delivery_speed_days >= 0', name='chk_delivery_speed'),
        CheckConstraint('user_engagement_rate >= 0 AND user_engagement_rate <= 1', name='chk_user_engagement'),
        CheckConstraint('retention_rate >= 0 AND retention_rate <= 1', name='chk_retention_rate'),
    )
