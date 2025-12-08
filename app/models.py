from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database import Base

# Many-to-many: talent <-> skills
talent_skill_table = Table(
    "talent_skills",
    Base.metadata,
    Column("talent_id", Integer, ForeignKey("talents.id")),
    Column("skill_id", Integer, ForeignKey("skills.id")),
)

# Many-to-many: project <-> required_skills
project_skill_table = Table(
    "project_required_skills",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id")),
    Column("skill_id", Integer, ForeignKey("skills.id")),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(Text)
    role = Column(String(50), default="talent")  # admin, talent, project_owner

    talent_profile = relationship("Talent", back_populates="user", uselist=False)
    projects = relationship("Project", back_populates="owner")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)

    talents = relationship("Talent", secondary=talent_skill_table, back_populates="skills")
    projects = relationship("Project", secondary=project_skill_table, back_populates="required_skills")


class Talent(Base):
    __tablename__ = "talents"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    bio = Column(Text)
    experience_level = Column(String(50))

    user = relationship("User", back_populates="talent_profile")
    skills = relationship("Skill", secondary=talent_skill_table, back_populates="talents")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="projects")
    required_skills = relationship("Skill", secondary=project_skill_table, back_populates="projects")
    outcome = relationship("ProjectOutcome", back_populates="project", uselist=False)


class ProjectOutcome(Base):
    __tablename__ = "project_outcomes"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    forecast_accuracy_percentage = Column(Float, nullable=False)
    client_satisfaction_rating = Column(Integer, nullable=False)
    code_quality_score = Column(Integer, nullable=False)
    delivery_speed_days = Column(Integer, nullable=False)

    project = relationship("Project", back_populates="outcomes")


class Stable(Base):
    __tablename__ = "stables"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    trainers = relationship("Trainer", back_populates="stable")


class Trainer(Base):
    __tablename__ = "trainers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    specialty = Column(String(255), nullable=True)

    stable_id = Column(Integer, ForeignKey("stables.id"), nullable=True)

    stable = relationship("Stable", back_populates="trainers")
