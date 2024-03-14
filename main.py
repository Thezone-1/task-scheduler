from fastapi import FastAPI, HTTPException, APIRouter
from database import (
    engine,
    Base,
    find_task_by_id,
    delete_task_by_id,
    create_task,
    update_task,
    find_task_definition_by_id,
)
from response import TaskResponse
from request import TaskRequest
from models.task import TaskModel
from schemas.task import TaskCreate, Task, TaskUpdate
from utils.schedule_worker import get_scheduler, decide_next_move

app = FastAPI()
router_v1 = APIRouter(prefix="/api/v1")

Base.metadata.create_all(bind=engine)  # type: ignore


# Create
@router_v1.post("/task", response_model=int)
async def create_task_api(request: TaskRequest):
    task_to_be_created = TaskCreate(
        request.name,
        request.execution_time,
        request.recurrence_pattern,
        request.task_definition,
    )
    task_id = create_task(task_to_be_created)
    task = find_task_by_id(task_id)
    decide_next_move(task)
    return task_id


# Get all posts
# @app.get("/tasks/", response_model=List[Task])
# async def read_tasks(db: Session = Depends(get_db)):
#     return get_tasks(db)


# Get one post
@router_v1.get("/task/{task_id}", response_model=TaskResponse)
async def read_task(task_id: int):
    task = find_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task_response = TaskResponse(
        id=task.id,
        name=task.name,
        execution_time=task.execution_time,
        recurrence_pattern=task.recurrence_pattern,
    )
    return task_response


@router_v1.put("/tasks/{task_id}", response_model=int)
async def update_task_api(task_id: int, request: TaskRequest):

    task_to_be_updated = TaskUpdate(
        request.name,
        request.execution_time,
        request.recurrence_pattern,
        request.task_definition,
    )
    task = find_task_by_id(task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    updated_task = update_task(task_to_be_updated)

    decide_next_move(updated_task)

    return updated_task


@router_v1.delete("/task/{task_id}")
async def delete_task_api(task_id: int):
    return delete_task_by_id(task_id)


app.include_router(router_v1)
sw = get_scheduler()
sw.start()
