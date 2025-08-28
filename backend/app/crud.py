from sqlalchemy.orm import Session
from datetime import datetime
from . import models, schemas


def get_projects(db: Session, skip: int = 0, limit: int = 100):
    projects = db.query(models.Project).offset(skip).limit(limit).all()

    for project in projects:
        total_seconds = 0
        for task in project.tasks:
            for time_entry in task.time_entries:
                if time_entry.end_time and time_entry.start_time:
                    total_seconds += (
                        time_entry.end_time - time_entry.start_time
                    ).total_seconds()
                elif time_entry.start_time and time_entry.is_active:
                    total_seconds += (
                        datetime.now() - time_entry.start_time
                    ).total_seconds()

        project.total_time = total_seconds

    return projects


def create_project(db: Session, project: schemas.ProjectCreate):
    db_project = models.Project(name=project.name)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def create_task(db: Session, task: schemas.TaskCreate):
    db_task = models.Task(title=task.title, project_id=task.project_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    tasks = db.query(models.Task).offset(skip).limit(limit).all()

    for task in tasks:
        total_seconds = 0
        is_time_running = False

        for time_entry in task.time_entries:
            if time_entry.end_time and time_entry.start_time:
                total_seconds += (
                    time_entry.end_time - time_entry.start_time
                ).total_seconds()
            elif time_entry.start_time and time_entry.is_active:
                is_time_running = True
                total_seconds += (
                    datetime.now() - time_entry.start_time
                ).total_seconds()

        task.total_time = total_seconds
        task.is_timer_running = is_time_running

    return tasks


def start_timer(db: Session, task_id: int):
    running_timers = (
        db.query(models.TimeEntry)
        .filter(models.TimeEntry.task_id == task_id, models.TimeEntry.is_active == True)
        .all()
    )

    for timer in running_timers:
        timer.is_active = False
        timer.end_time = datetime.now()

    db_time_entry = models.TimeEntry(
        task_id=task_id, start_time=datetime.now(), is_active=True
    )
    db.add(db_time_entry)
    db.commit()
    db.refresh(db_time_entry)
    return db_time_entry


def pause_timer(db: Session, task_id: int):
    # Find active timer for this task
    db_time_entry = (
        db.query(models.TimeEntry)
        .filter(models.TimeEntry.task_id == task_id, models.TimeEntry.is_active == True)
        .first()
    )

    if db_time_entry:
        db_time_entry.is_active = False
        db_time_entry.end_time = datetime.now()
        db.commit()
        db.refresh(db_time_entry)
        return db_time_entry
    return None


def get_time_entries(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.TimeEntry).offset(skip).limit(limit).all()
