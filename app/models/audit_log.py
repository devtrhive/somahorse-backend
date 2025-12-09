from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, nullable=False)
    entity = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=False)
    performed_by = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
