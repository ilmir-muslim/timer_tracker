from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


class ProjectBase(BaseModel):
    name: str


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None


class Project(ProjectBase):
    id: int
    created_at: datetime
    total_time: Optional[float] = 0.0

    model_config = ConfigDict(from_attributes=True)


class TaskBase(BaseModel):
    title: str
    project_id: Optional[int] = None


class TaskCreate(TaskBase):
    priority: Optional[int] = 1
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    total_time: Optional[float] = None
    project_id: Optional[int] = None
    is_completed: Optional[bool] = None
    priority: Optional[int] = None
    due_date: Optional[datetime] = None
    created_at: Optional[datetime] = None


class SubTaskBase(BaseModel):
    title: str


class SubTaskCreate(SubTaskBase):
    pass


class SubTaskUpdate(BaseModel):
    title: Optional[str] = None
    is_completed: Optional[bool] = None


class SubTaskCommentBase(BaseModel):
    content: str


class SubTaskCommentCreate(SubTaskCommentBase):
    pass


class SubTaskComment(SubTaskCommentBase):
    id: int
    sub_task_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubTask(SubTaskBase):
    id: int
    task_id: int
    is_completed: bool
    created_at: datetime
    completed_at: Optional[datetime] = None
    comments: List["SubTaskComment"] = []

    model_config = ConfigDict(from_attributes=True)


class TaskCommentBase(BaseModel):
    content: str


class TaskCommentCreate(TaskCommentBase):
    pass


class TaskComment(TaskCommentBase):
    id: int
    task_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Task(TaskBase):
    id: int
    created_at: datetime
    total_time: Optional[float] = 0.0
    is_timer_running: Optional[bool] = False
    is_completed: Optional[bool] = False
    completed_at: Optional[datetime] = None
    priority: Optional[int] = 1
    due_date: Optional[datetime] = None
    comments: List["TaskComment"] = []
    sub_tasks: List["SubTask"] = []

    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    username: str
    password: str
