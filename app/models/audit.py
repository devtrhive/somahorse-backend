from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    actor_email = Column(String)
    action = Column(String)
    timestamp = Column(DateTime, server_default=func.now())
