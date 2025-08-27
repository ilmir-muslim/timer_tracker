from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from . import crud, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title='Task Tracker API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/projects/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    return crud.create_project(db=db, project=project)

@app.get("/projects/", response_model=List[schemas.Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_projects(db=db, skip=skip, limit=limit)

@app.post("/tasks/", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db=db, task=task)

@app.get("/tasks/", response_model=List[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_tasks(db=db, skip=skip, limit=limit)

# Timer endpoints
@app.post('/timer/start/{task_id}')
def start_timer(task_id: int, db: Session = Depends(get_db)):
    time_entry = crud.start_timer(db=db, task_id=task_id)
    return {'message': 'Timer started', 'time_entry': time_entry.id}


@app.post("/timer/pause/{time_entry_id}")
def pause_timer(time_entry_id: int, db: Session = Depends(get_db)):
    time_entry = crud.pause_timer(db=db, time_entry_id=time_entry_id)
    if time_entry:
        return {"message": "Timer paused"}
    else:
        raise HTTPException(
            status_code=404, detail="Time entry not found or already paused"
        )


@app.post("/timer/stop/{time_entry_id}")
def stop_timer(time_entry_id: int, db: Session = Depends(get_db)):
    time_entry = crud.stop_timer(db=db, time_entry_id=time_entry_id)
    if time_entry:
        return {"message": "Timer stopped"}
    else:
        raise HTTPException(
            status_code=404, detail="Time entry not found or already stopped"
        )


@app.get("/time_entries/", response_model=List[schemas.TimeEntry])
def read_time_entries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    time_entries = crud.get_time_entries(db, skip=skip, limit=limit)
    return time_entries


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
