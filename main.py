from fastapi import FastAPI, HTTPException, APIRouter
from database import (
    engine,
    Base,
    find_task_by_id,
    delete_task_by_id,
    create_task,
    update_task,
)

from fastapi.staticfiles import StaticFiles
from response import TaskResponse
from request import TaskRequest
from schemas.task import TaskCreate, TaskUpdate
from utils.schedule_worker import get_scheduler, decide_next_move
import uvicorn

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

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
    if task_id != -1:
        task = find_task_by_id(task_id)
        decide_next_move(task)
    else:
        print("could not create task")
    return task_id


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


@router_v1.put("/task/{task_id}", response_model=int)
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


if __name__ == "__main__":
    sw = get_scheduler()
    sw.start()
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
