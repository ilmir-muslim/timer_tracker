from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from jose import JWTError, jwt
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from app.auth import verify_password
from . import crud, models, schemas
from .database import SessionLocal, engine

# Создаём таблицы
models.Base.metadata.create_all(bind=engine)

SECRET_KEY = "simple-secret-key-for-development-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60  # 24 часа

scheduler = None


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(schemas.oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user


def auto_pause_old_timers():
    with SessionLocal() as db:
        try:
            paused_count = crud.auto_pause_old_timers(db)
            if paused_count > 0:
                print(f"Автоматически остановлено {paused_count} старых таймеров")
        except Exception as e:
            print(f"Ошибка при автоматической остановке таймеров: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Запуск приложения...")
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.interval import IntervalTrigger

    global scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        auto_pause_old_timers,
        trigger=IntervalTrigger(minutes=30),
        id="auto_pause_timers",
        replace_existing=True,
    )
    scheduler.start()
    print("Планировщик запущен")
    yield
    print("Остановка приложения...")
    if scheduler and scheduler.running:
        scheduler.shutdown()
        print("Планировщик остановлен")


app = FastAPI(
    title="Task Tracker API",
    root_path="/api",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------
# Auth
# ------------------------------------------------------------
@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)


@app.post("/login")
def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=login_data.username)
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# ------------------------------------------------------------
# Users
# ------------------------------------------------------------
@app.get("/users/me", response_model=schemas.User)
def read_current_user(current_user: models.User = Depends(get_current_user)):
    return current_user


@app.patch("/users/me/rate")
def update_default_rate(
    rate_data: schemas.UpdateRateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    current_user.default_hourly_rate = rate_data.default_hourly_rate
    db.commit()
    return {
        "message": "Rate updated",
        "default_hourly_rate": current_user.default_hourly_rate,
    }


# ------------------------------------------------------------
# Projects
# ------------------------------------------------------------
@app.post("/projects/", response_model=schemas.Project)
def create_project(
    project: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.create_project(db=db, project=project, owner_id=current_user.id)


@app.get("/projects/", response_model=List[schemas.Project])
def read_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.get_projects_by_owner(
        db=db, owner_id=current_user.id, skip=skip, limit=limit
    )


@app.put("/projects/{project_id}", response_model=schemas.Project)
def update_project(
    project_id: int,
    project_update: schemas.ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    updated_project = crud.update_project(
        db=db, project_id=project_id, project_update=project_update
    )
    if not updated_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated_project


@app.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    success = crud.delete_project(db, project_id=project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted"}


# ------------------------------------------------------------
# Tasks
# ------------------------------------------------------------
@app.post("/tasks/", response_model=schemas.Task)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if task.project_id is not None:
        project = (
            db.query(models.Project)
            .filter(models.Project.id == task.project_id)
            .first()
        )
        if not project or project.owner_id != current_user.id:
            raise HTTPException(status_code=404, detail="Project not found")
    return crud.create_task(db=db, task=task, user_id=current_user.id)


@app.get("/tasks/", response_model=List[schemas.Task])
def read_tasks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.get_tasks_by_owner(
        db=db, owner_id=current_user.id, skip=skip, limit=limit
    )


@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    if task_update.project_id and task_update.project_id != task.project_id:
        new_project = (
            db.query(models.Project)
            .filter(models.Project.id == task_update.project_id)
            .first()
        )
        if not new_project or new_project.owner_id != current_user.id:
            raise HTTPException(status_code=404, detail="Project not found")
    updated_task = crud.update_task(db=db, task_id=task_id, task_update=task_update)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task


@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    success = crud.delete_task(db, task_id=task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}


@app.get("/tasks-with-details/", response_model=List[schemas.Task])
def read_tasks_with_details(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    tasks = crud.get_tasks_by_owner(
        db=db, owner_id=current_user.id, skip=skip, limit=limit
    )
    for task in tasks:
        task.comments = crud.get_task_comments(db=db, task_id=task.id)
        task.sub_tasks = crud.get_sub_tasks(db=db, task_id=task.id)
    return tasks


# ------------------------------------------------------------
# Timer (Task-specific)
# ------------------------------------------------------------
@app.post("/timer/start/{task_id}")
def start_timer(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    crud.start_timer(db=db, task_id=task_id)
    crud.start_daily_timer(db, current_user.id)
    daily_session = crud.get_today_daily_session(db, current_user.id)
    if daily_session:
        if daily_session.is_timer_running and daily_session.last_start_time:
            elapsed = (datetime.now() - daily_session.last_start_time).total_seconds()
            daily_session.total_time += elapsed
    return {
        "message": "Timer started",
        "task_id": task_id,
        "daily_session": daily_session,
    }


@app.post("/timer/pause/{task_id}")
def pause_timer(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    crud.pause_timer(db=db, task_id=task_id)

    # Проверяем, остались ли ещё запущенные задачи
    any_running = crud.check_any_task_running(db, current_user.id)
    if not any_running:
        crud.pause_daily_timer(db, current_user.id)

    daily_session = crud.get_today_daily_session(db, current_user.id)
    if (
        daily_session
        and daily_session.is_timer_running
        and daily_session.last_start_time
    ):
        elapsed = (datetime.now() - daily_session.last_start_time).total_seconds()
        daily_session.total_time += elapsed

    return {
        "message": "Timer paused",
        "task_id": task_id,
        "daily_session": daily_session,
    }


@app.post("/timer/stop-all")
def stop_all_timers(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    active_tasks = (
        db.query(models.Task)
        .filter(
            models.Task.owner_id == current_user.id,
            models.Task.is_timer_running == True,
        )
        .all()
    )
    stopped_count = 0
    for task in active_tasks:
        if crud.pause_timer(db=db, task_id=task.id):
            stopped_count += 1

    # Останавливаем daily таймер
    crud.pause_daily_timer(db, current_user.id)

    return {"message": f"Остановлено {stopped_count} таймеров"}


# ------------------------------------------------------------
# Task Comments
# ------------------------------------------------------------
@app.post("/tasks/{task_id}/comments", response_model=schemas.TaskComment)
def create_task_comment(
    task_id: int,
    comment: schemas.TaskCommentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.create_task_comment(db=db, comment=comment, task_id=task_id)


@app.get("/tasks/{task_id}/comments", response_model=List[schemas.TaskComment])
def get_task_comments(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.get_task_comments(db=db, task_id=task_id)


@app.delete("/comments/{comment_id}")
def delete_task_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    comment = (
        db.query(models.TaskComment).filter(models.TaskComment.id == comment_id).first()
    )
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    task = db.query(models.Task).filter(models.Task.id == comment.task_id).first()
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    success = crud.delete_task_comment(db, comment_id=comment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"message": "Comment deleted"}


# ------------------------------------------------------------
# SubTasks
# ------------------------------------------------------------
@app.post("/tasks/{task_id}/subtasks", response_model=schemas.SubTask)
def create_sub_task(
    task_id: int,
    sub_task: schemas.SubTaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.create_sub_task(db=db, sub_task=sub_task, task_id=task_id)


@app.get("/tasks/{task_id}/subtasks", response_model=List[schemas.SubTask])
def get_sub_tasks(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.get_sub_tasks(db=db, task_id=task_id)


@app.put("/subtasks/{sub_task_id}", response_model=schemas.SubTask)
def update_sub_task(
    sub_task_id: int,
    sub_task_update: schemas.SubTaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    sub_task = db.query(models.SubTask).filter(models.SubTask.id == sub_task_id).first()
    if not sub_task:
        raise HTTPException(status_code=404, detail="Sub task not found")
    task = db.query(models.Task).filter(models.Task.id == sub_task.task_id).first()
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    updated_sub_task = crud.update_sub_task(
        db=db, sub_task_id=sub_task_id, sub_task_update=sub_task_update
    )
    if not updated_sub_task:
        raise HTTPException(status_code=404, detail="Sub task not found")
    return updated_sub_task


@app.delete("/subtasks/{sub_task_id}")
def delete_sub_task(
    sub_task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    sub_task = db.query(models.SubTask).filter(models.SubTask.id == sub_task_id).first()
    if not sub_task:
        raise HTTPException(status_code=404, detail="Sub task not found")
    task = db.query(models.Task).filter(models.Task.id == sub_task.task_id).first()
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    success = crud.delete_sub_task(db, sub_task_id=sub_task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sub task not found")
    return {"message": "Sub task deleted"}


# ------------------------------------------------------------
# SubTask Comments
# ------------------------------------------------------------
@app.post("/subtasks/{sub_task_id}/comments", response_model=schemas.SubTaskComment)
def create_sub_task_comment(
    sub_task_id: int,
    comment: schemas.SubTaskCommentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    sub_task = db.query(models.SubTask).filter(models.SubTask.id == sub_task_id).first()
    if not sub_task:
        raise HTTPException(status_code=404, detail="Sub task not found")
    task = db.query(models.Task).filter(models.Task.id == sub_task.task_id).first()
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.create_sub_task_comment(db=db, comment=comment, sub_task_id=sub_task_id)


@app.get(
    "/subtasks/{sub_task_id}/comments", response_model=List[schemas.SubTaskComment]
)
def get_sub_task_comments(
    sub_task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    sub_task = db.query(models.SubTask).filter(models.SubTask.id == sub_task_id).first()
    if not sub_task:
        raise HTTPException(status_code=404, detail="Sub task not found")
    task = db.query(models.Task).filter(models.Task.id == sub_task.task_id).first()
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.get_sub_task_comments(db=db, sub_task_id=sub_task_id)


@app.delete("/subtask-comments/{comment_id}")
def delete_sub_task_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    comment = (
        db.query(models.SubTaskComment)
        .filter(models.SubTaskComment.id == comment_id)
        .first()
    )
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    sub_task = (
        db.query(models.SubTask)
        .filter(models.SubTask.id == comment.sub_task_id)
        .first()
    )
    if not sub_task:
        raise HTTPException(status_code=404, detail="Sub task not found")
    task = db.query(models.Task).filter(models.Task.id == sub_task.task_id).first()
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    success = crud.delete_sub_task_comment(db, comment_id=comment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"message": "Comment deleted"}


# ------------------------------------------------------------
# Daily Work Session (новые эндпоинты)
# ------------------------------------------------------------
@app.get("/daily/current", response_model=Optional[schemas.DailyWorkSession])
def get_current_daily_session(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Получить сегодняшнюю сессию (с текущим временем, если таймер запущен)."""
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    session = (
        db.query(models.DailyWorkSession)
        .filter(
            models.DailyWorkSession.user_id == current_user.id,
            models.DailyWorkSession.date == today_start,
        )
        .first()
    )
    if session and session.is_timer_running and session.last_start_time:
        # Для ответа добавим текущее время к total_time
        elapsed = (datetime.now() - session.last_start_time).total_seconds()
        # Создадим копию, чтобы не менять объект БД
        session_copy = schemas.DailyWorkSession.model_validate(session)
        session_copy.total_time = session.total_time + elapsed
        return session_copy
    return session


@app.get("/daily/stats", response_model=schemas.DailyStatsResponse)
def get_daily_stats(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Получить статистику за последние N дней, сегодняшний день и т.д."""
    stats = crud.get_daily_stats(db, current_user.id, days)
    # Отфильтруем только нужные периоды
    today_str = datetime.now().strftime("%Y-%m-%d")
    week_start = datetime.now() - timedelta(days=7)
    week_items = [s for s in stats if s["date"] >= week_start.strftime("%Y-%m-%d")]

    # Выделим сегодня
    today_item = next(
        (s for s in stats if s["date"] == today_str),
        {"date": today_str, "total_seconds": 0.0},
    )

    return schemas.DailyStatsResponse(
        today=today_item, week=week_items, month=stats[-30:]  # последние 30 дней
    )


# ------------------------------------------------------------
# Earnings
# ------------------------------------------------------------
@app.get("/earnings/summary", response_model=schemas.EarningsSummaryResponse)
def get_earnings_summary(
    db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    summary = crud.get_user_earnings_summary(db, current_user.id)
    if not summary:
        raise HTTPException(status_code=404, detail="User not found")
    return summary


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
