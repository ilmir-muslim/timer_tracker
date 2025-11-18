from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Boolean,
    func,
    Float,
    Text,
)
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(
        String(50), unique=True, index=True, nullable=False, default="admin"
    )
    password = Column(String(255), nullable=False, default="admin")
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


class TaskComment(Base):
    __tablename__ = "task_comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Используем строку для отложенной оценки
    task = relationship("Task", back_populates="comments")


class SubTaskComment(Base):
    __tablename__ = "sub_task_comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    sub_task_id = Column(Integer, ForeignKey("sub_tasks.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Используем строку для отложенной оценки
    sub_task = relationship("SubTask", back_populates="comments")


class SubTask(Base):
    __tablename__ = "sub_tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Используем строку для отложенной оценки
    task = relationship("Task", back_populates="sub_tasks")
    comments = relationship("SubTaskComment", back_populates="sub_task", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Новые поля для трекера задач
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    priority = Column(Integer, default=1)  # 1-низкий, 2-средний, 3-высокий
    due_date = Column(DateTime(timezone=True), nullable=True)

    # Поля для трекера времени
    total_time = Column(Float, default=0.0)
    is_timer_running = Column(Boolean, default=False)
    last_start_time = Column(DateTime, nullable=True)

    project = relationship("Project", back_populates="tasks")
    owner = relationship("User")

    # Используем строки для отложенной оценки
    comments = relationship(
        "TaskComment", back_populates="task", cascade="all, delete-orphan"
    )
    sub_tasks = relationship(
        "SubTask", back_populates="task", cascade="all, delete-orphan"
    )