from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from . import models, schemas


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_projects_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    projects = (
        db.query(models.Project)
        .filter(models.Project.owner_id == owner_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Обновляем общее время проектов на основе задач
    for project in projects:
        total_time = 0
        for task in project.tasks:
            total_time += task.total_time or 0
            # Если таймер запущен, добавляем текущее время
            if task.is_timer_running and task.last_start_time:
                current_session_time = (
                    datetime.now() - task.last_start_time
                ).total_seconds()
                total_time += current_session_time

        project.total_time = total_time

    return projects


def create_project(db: Session, project: schemas.ProjectCreate, owner_id: int):
    db_project = models.Project(name=project.name, owner_id=owner_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def update_project(db: Session, project_id: int, project_update: schemas.ProjectUpdate):
    db_project = (
        db.query(models.Project).filter(models.Project.id == project_id).first()
    )
    if not db_project:
        return None

    update_data = project_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_project, field, value)

    db.commit()
    db.refresh(db_project)
    return db_project


def create_task(db: Session, task: schemas.TaskCreate, user_id: int):
    db_task = models.Task(
        title=task.title,
        project_id=task.project_id,
        owner_id=user_id,
        total_time=0.0,
        is_timer_running=False,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_tasks_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    tasks = (
        db.query(models.Task)
        .filter(models.Task.owner_id == owner_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Обновляем время для задач с запущенным таймером
    for task in tasks:
        if task.is_timer_running and task.last_start_time:
            current_session_time = (
                datetime.now() - task.last_start_time
            ).total_seconds()
            task.total_time = (task.total_time or 0) + current_session_time

    return tasks


def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        return None

    update_data = task_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_task, field, value)

    db.commit()
    db.refresh(db_task)
    return db_task


def start_timer(db: Session, task_id: int):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        return None

    # Обновляем общее время перед запуском
    if task.is_timer_running and task.last_start_time:
        current_session_time = (datetime.now() - task.last_start_time).total_seconds()
        task.total_time = (task.total_time or 0) + current_session_time

    task.is_timer_running = True
    task.last_start_time = datetime.now()
    db.commit()
    db.refresh(task)
    return task


def pause_timer(db: Session, task_id: int):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task or not task.is_timer_running:
        return None

    # Добавляем время текущей сессии к общему времени
    if task.last_start_time:
        current_session_time = (datetime.now() - task.last_start_time).total_seconds()
        task.total_time = (task.total_time or 0) + current_session_time

    task.is_timer_running = False
    task.last_start_time = None
    db.commit()
    db.refresh(task)
    return task


def delete_project(db: Session, project_id: int):
    db_project = (
        db.query(models.Project).filter(models.Project.id == project_id).first()
    )
    if db_project:
        # Удаляем связанные задачи
        db.query(models.Task).filter(models.Task.project_id == project_id).delete()
        db.delete(db_project)
        db.commit()
        return True
    return False


def delete_task(db: Session, task_id: int):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
        return True
    return False


def auto_pause_old_timers(db: Session, max_duration_hours: int = 24):
    """
    Автоматически останавливает таймеры, которые работают дольше указанного времени
    """
    cutoff_time = datetime.now() - timedelta(hours=max_duration_hours)

    old_tasks = (
        db.query(models.Task)
        .filter(
            models.Task.is_timer_running == True,
            models.Task.last_start_time < cutoff_time,
        )
        .all()
    )

    for task in old_tasks:
        if task.last_start_time:
            # Рассчитываем максимальное время (24 часа)
            max_duration = timedelta(hours=max_duration_hours)
            elapsed_time = datetime.now() - task.last_start_time

            if elapsed_time > max_duration:
                # Добавляем только максимальное разрешенное время
                task.total_time = (task.total_time or 0) + max_duration.total_seconds()
                task.is_timer_running = False
                task.last_start_time = None

    db.commit()
    return len(old_tasks)
