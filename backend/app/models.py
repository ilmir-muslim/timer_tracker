from sqlalchemy import Integer, String, DateTime, ForeignKey, Boolean, Float, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    projects: Mapped[list["Project"]] = relationship("Project", back_populates="owner")
    daily_sessions: Mapped[list["DailyWorkSession"]] = relationship(
        "DailyWorkSession", back_populates="user", cascade="all, delete-orphan"
    )


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )

    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="project")
    owner: Mapped["User"] = relationship("User", back_populates="projects")


class TaskComment(Base):
    __tablename__ = "task_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id"))
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    task: Mapped["Task"] = relationship("Task", back_populates="comments")


class SubTaskComment(Base):
    __tablename__ = "sub_task_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sub_task_id: Mapped[int] = mapped_column(Integer, ForeignKey("sub_tasks.id"))
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    sub_task: Mapped["SubTask"] = relationship("SubTask", back_populates="comments")


class SubTask(Base):
    __tablename__ = "sub_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id"))
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    completed_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    task: Mapped["Task"] = relationship("Task", back_populates="sub_tasks")
    comments: Mapped[list["SubTaskComment"]] = relationship(
        "SubTaskComment", back_populates="sub_task", cascade="all, delete-orphan"
    )


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=True
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    priority: Mapped[int] = mapped_column(
        Integer, default=1
    )  # 1 - низкий, 2 - средний, 3 - высокий
    due_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)

    total_time: Mapped[float] = mapped_column(Float, default=0.0)
    is_timer_running: Mapped[bool] = mapped_column(Boolean, default=False)
    last_start_time: Mapped[DateTime] = mapped_column(DateTime, nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="tasks")
    owner: Mapped["User"] = relationship("User")

    comments: Mapped[list["TaskComment"]] = relationship(
        "TaskComment", back_populates="task", cascade="all, delete-orphan"
    )
    sub_tasks: Mapped[list["SubTask"]] = relationship(
        "SubTask", back_populates="task", cascade="all, delete-orphan"
    )


class DailyWorkSession(Base):
    __tablename__ = "daily_work_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    date: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False
    )  # дата дня (без времени)
    total_time: Mapped[float] = mapped_column(Float, default=0.0)  # секунд
    is_timer_running: Mapped[bool] = mapped_column(Boolean, default=False)
    last_start_time: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=True, onupdate=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="daily_sessions")
