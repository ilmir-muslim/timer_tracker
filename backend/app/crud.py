from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from . import models, schemas


# ------------------------------------------------------------
# User
# ------------------------------------------------------------
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ------------------------------------------------------------
# Projects
# ------------------------------------------------------------
def get_projects_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    projects = (
        db.query(models.Project)
        .filter(models.Project.owner_id == owner_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    for project in projects:
        total_time = 0
        for task in project.tasks:
            total_time += task.total_time or 0
            if task.is_timer_running and task.last_start_time:
                current_session_time = (
                    datetime.now() - task.last_start_time
                ).total_seconds()
                total_time += current_session_time
        project.total_time = total_time
        project.earned_amount = total_time * project.hourly_rate / 3600
    return projects


def create_project(db: Session, project: schemas.ProjectCreate, owner_id: int):
    user = db.query(models.User).filter(models.User.id == owner_id).first()
    hourly_rate = project.hourly_rate
    if hourly_rate is None:
        hourly_rate = user.default_hourly_rate if user else 0.0
    if hourly_rate is None:
        hourly_rate = 0.0
    db_project = models.Project(
        name=project.name, owner_id=owner_id, hourly_rate=hourly_rate
    )
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


def delete_project(db: Session, project_id: int):
    db_project = (
        db.query(models.Project).filter(models.Project.id == project_id).first()
    )
    if db_project:
        db.query(models.Task).filter(models.Task.project_id == project_id).delete()
        db.delete(db_project)
        db.commit()
        return True
    return False


# ------------------------------------------------------------
# Tasks
# ------------------------------------------------------------
def create_task(db: Session, task: schemas.TaskCreate, user_id: int):
    db_task = models.Task(
        title=task.title,
        project_id=task.project_id,
        owner_id=user_id,
        total_time=0.0,
        is_timer_running=False,
        priority=task.priority or 1,
        due_date=task.due_date,
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
    if update_data.get("is_completed") and not db_task.is_completed:
        update_data["completed_at"] = datetime.now()
    elif not update_data.get("is_completed") and db_task.is_completed:
        update_data["completed_at"] = None
    for field, value in update_data.items():
        setattr(db_task, field, value)
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
        return True
    return False


# ------------------------------------------------------------
# Timer (Tasks)
# ------------------------------------------------------------
def start_timer(db: Session, task_id: int):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        return None
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
    if task.last_start_time:
        current_session_time = (datetime.now() - task.last_start_time).total_seconds()
        task.total_time = (task.total_time or 0) + current_session_time
    task.is_timer_running = False
    task.last_start_time = None
    db.commit()
    db.refresh(task)
    return task


def auto_pause_old_timers(db: Session, max_duration_hours: int = 1):
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
            max_duration = timedelta(hours=max_duration_hours)
            elapsed_time = datetime.now() - task.last_start_time
            if elapsed_time > max_duration:
                task.total_time = (task.total_time or 0) + max_duration.total_seconds()
                task.is_timer_running = False
                task.last_start_time = None
    db.commit()
    return len(old_tasks)


# ------------------------------------------------------------
# Task Comments
# ------------------------------------------------------------
def create_task_comment(db: Session, comment: schemas.TaskCommentCreate, task_id: int):
    db_comment = models.TaskComment(content=comment.content, task_id=task_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_task_comments(db: Session, task_id: int):
    return (
        db.query(models.TaskComment).filter(models.TaskComment.task_id == task_id).all()
    )


def delete_task_comment(db: Session, comment_id: int):
    db_comment = (
        db.query(models.TaskComment).filter(models.TaskComment.id == comment_id).first()
    )
    if db_comment:
        db.delete(db_comment)
        db.commit()
        return True
    return False


# ------------------------------------------------------------
# SubTasks
# ------------------------------------------------------------
def create_sub_task(db: Session, sub_task: schemas.SubTaskCreate, task_id: int):
    db_sub_task = models.SubTask(title=sub_task.title, task_id=task_id)
    db.add(db_sub_task)
    db.commit()
    db.refresh(db_sub_task)
    return db_sub_task


def get_sub_tasks(db: Session, task_id: int):
    sub_tasks = db.query(models.SubTask).filter(models.SubTask.task_id == task_id).all()
    for sub in sub_tasks:
        sub.comments = get_sub_task_comments(db, sub.id)
    return sub_tasks


def update_sub_task(
    db: Session, sub_task_id: int, sub_task_update: schemas.SubTaskUpdate
):
    db_sub_task = (
        db.query(models.SubTask).filter(models.SubTask.id == sub_task_id).first()
    )
    if not db_sub_task:
        return None
    update_data = sub_task_update.dict(exclude_unset=True)
    if update_data.get("is_completed") and not db_sub_task.is_completed:
        update_data["completed_at"] = datetime.now()
    elif not update_data.get("is_completed") and db_sub_task.is_completed:
        update_data["completed_at"] = None
    for field, value in update_data.items():
        setattr(db_sub_task, field, value)
    db.commit()
    db.refresh(db_sub_task)
    return db_sub_task


def delete_sub_task(db: Session, sub_task_id: int):
    db_sub_task = (
        db.query(models.SubTask).filter(models.SubTask.id == sub_task_id).first()
    )
    if db_sub_task:
        db.delete(db_sub_task)
        db.commit()
        return True
    return False


# ------------------------------------------------------------
# SubTask Comments
# ------------------------------------------------------------
def create_sub_task_comment(
    db: Session, comment: schemas.SubTaskCommentCreate, sub_task_id: int
):
    db_comment = models.SubTaskComment(content=comment.content, sub_task_id=sub_task_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_sub_task_comments(db: Session, sub_task_id: int):
    return (
        db.query(models.SubTaskComment)
        .filter(models.SubTaskComment.sub_task_id == sub_task_id)
        .all()
    )


def delete_sub_task_comment(db: Session, comment_id: int):
    db_comment = (
        db.query(models.SubTaskComment)
        .filter(models.SubTaskComment.id == comment_id)
        .first()
    )
    if db_comment:
        db.delete(db_comment)
        db.commit()
        return True
    return False


# ------------------------------------------------------------
# Daily Work Sessions
# ------------------------------------------------------------
def get_or_create_daily_session(db: Session, user_id: int, for_date: datetime = None):
    """Получить или создать сессию для указанной даты."""
    if for_date is None:
        for_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        for_date = for_date.replace(hour=0, minute=0, second=0, microsecond=0)

    session = (
        db.query(models.DailyWorkSession)
        .filter(
            models.DailyWorkSession.user_id == user_id,
            models.DailyWorkSession.date == for_date,
        )
        .first()
    )

    if not session:
        session = models.DailyWorkSession(
            user_id=user_id,
            date=for_date,
            total_time=0.0,
            is_timer_running=False,
            last_start_time=None,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    return session


def start_daily_timer(db: Session, user_id: int):
    """Запустить ежедневный таймер, если ещё не запущен."""
    session = get_or_create_daily_session(db, user_id)
    if not session.is_timer_running:
        # Если таймер не запущен, но есть last_start_time (остаток от предыдущего дня?) – обнулим
        session.last_start_time = datetime.now()
        session.is_timer_running = True
        db.commit()
        db.refresh(session)
    return session


def pause_daily_timer(db: Session, user_id: int):
    """Остановить ежедневный таймер, добавив время текущей сессии."""
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    session = (
        db.query(models.DailyWorkSession)
        .filter(
            models.DailyWorkSession.user_id == user_id,
            models.DailyWorkSession.date == today_start,
        )
        .first()
    )

    if session and session.is_timer_running and session.last_start_time:
        elapsed = (datetime.now() - session.last_start_time).total_seconds()
        session.total_time += elapsed
        session.is_timer_running = False
        session.last_start_time = None
        db.commit()
        db.refresh(session)
    return session


def get_daily_stats(db: Session, user_id: int, days: int = 30):
    """Получить статистику за последние N дней."""
    end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=days - 1)

    sessions = (
        db.query(models.DailyWorkSession)
        .filter(
            models.DailyWorkSession.user_id == user_id,
            models.DailyWorkSession.date >= start_date,
        )
        .order_by(models.DailyWorkSession.date)
        .all()
    )

    # Преобразуем в список словарей для удобства
    stats = []
    for sess in sessions:
        total = sess.total_time
        if sess.is_timer_running and sess.last_start_time:
            total += (datetime.now() - sess.last_start_time).total_seconds()
        stats.append({"date": sess.date.strftime("%Y-%m-%d"), "total_seconds": total})

    # Заполним отсутствующие дни нулями
    existing_dates = {s["date"] for s in stats}
    result = []
    for i in range(days):
        day = (start_date + timedelta(days=i)).date()
        day_str = day.strftime("%Y-%m-%d")
        if day_str in existing_dates:
            result.append(next(s for s in stats if s["date"] == day_str))
        else:
            result.append({"date": day_str, "total_seconds": 0.0})
    return result


def get_today_daily_session(db: Session, user_id: int):
    """Получить сегодняшнюю сессию из БД (без учёта текущего времени)."""
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    session = (
        db.query(models.DailyWorkSession)
        .filter(
            models.DailyWorkSession.user_id == user_id,
            models.DailyWorkSession.date == today_start,
        )
        .first()
    )
    return session


def check_any_task_running(db: Session, user_id: int) -> bool:
    """Проверяет, есть ли у пользователя хотя бы одна запущенная задача."""
    return (
        db.query(models.Task)
        .filter(models.Task.owner_id == user_id, models.Task.is_timer_running == True)
        .first()
        is not None
    )


# ------------------------------------------------------------
# Earnings
# ------------------------------------------------------------
def get_user_earnings_summary(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None

    projects = db.query(models.Project).filter(models.Project.owner_id == user_id).all()
    total_earned = 0.0
    for project in projects:
        total_time = 0
        for task in project.tasks:
            total_time += task.total_time or 0
            if task.is_timer_running and task.last_start_time:
                total_time += (datetime.now() - task.last_start_time).total_seconds()
        # Используем ставку проекта, если она > 0, иначе ставку пользователя
        rate = project.hourly_rate if project.hourly_rate > 0 else user.default_hourly_rate
        total_earned += total_time * rate / 3600

    now = datetime.now()
    months_since = (now.year - user.created_at.year) * 12 + (
        now.month - user.created_at.month
    )
    if months_since < 1:
        months_since = 1

    average_monthly = total_earned / months_since

    return {
        "total_earned": total_earned,
        "months_since_registration": months_since,
        "average_monthly": average_monthly,
    }
