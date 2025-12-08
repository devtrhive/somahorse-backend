from sqlalchemy import Column, Integer, String, DateTime, func, JSON
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    actor_user_id = Column(Integer, nullable=True)
    action_type = Column(String, nullable=False)
    resource_type = Column(String, nullable=True)
    resource_id = Column(Integer, nullable=True)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
