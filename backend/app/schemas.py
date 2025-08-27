from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Float

class ProjectBase(BaseModel):
    name: str

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    created_at: datetime
    total_time: Optional[Float] = 0.0

    model_config = ConfigDict(from_attributes=True)

class TaskBase(BaseModel):
    title: str
    project_id: int

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    created_at: datetime
    total_time: Optional[Float] = 0.0
    is_timer_running: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)

class TimeEntryBase(BaseModel):
    id: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_active: Optional[bool]

    model_config = ConfigDict(from_attributes=True)