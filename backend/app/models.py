from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, func
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False, default='admin')
    password = Column(String(255), nullable=False, default='admin')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    projects = relationship("Project", back_populates="owner")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tasks = relationship("Task", back_populates="project")
    owner = relationship("User", back_populates="projects")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"))
    project = relationship("Project", back_populates="tasks")
    time_entries = relationship("TimeEntry", back_populates="task")
    owner = relationship("User")


class TimeEntry(Base):
    __tablename__ = "time_entries"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=False)
    task = relationship("Task", back_populates="time_entries")
