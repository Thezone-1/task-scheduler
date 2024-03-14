from . import SessionLocal
from functools import lru_cache
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from sqlalchemy.engine.row import Row
from models.task import TaskModel
from schemas.task import TaskCreate, Task, TaskUpdate
from datetime import datetime


@lru_cache
def get_db() -> Session:
    db: Session = SessionLocal()
    return db


def find_all_tasks() -> list[Task]:
    """
    This is get tasks function.
    """
    db = get_db()
    task_models = db.query(TaskModel).all()
    tasks = [
        Task(
            task_model.id,
            task_model.name,
            task_model.execution_time,
            task_model.recurrence_pattern,
            task_model.task_definition,
        )
        for task_model in task_models
    ]
    return tasks


def find_task_by_id(task_id: int) -> Task:
    db = get_db()
    task_query = db.query(TaskModel)
    task_model: TaskModel | None = task_query.filter(TaskModel.id == task_id).first()  # type: ignore
    if task_model is None:
        raise Exception("task with given id not found")
    task = Task(
        task_model.id,
        task_model.name,
        task_model.execution_time,
        task_model.recurrence_pattern,
        task_model.task_definition,
    )
    return task


def find_task_definition_by_id(tid: int):
    db = get_db()
    row: Row = db.query(TaskModel.task_definition).where(TaskModel.id == tid).first()

    if row is None:
        raise Exception("task id does not exist")

    return row["task_definition"]


def find_next_scheduled_task():
    db = get_db()

    row = db.execute(
        "SELECT * FROM tasks HAVING execution_time IN (SELECT MIN(execution_time) FROM tasks WHERE execution_time > now())"
    ).first()

    next_task = Task(
        id=row["id"],
        name=row["name"],
        execution_time=row["execution_time"],
        recurrence_pattern=row["recurrence_pattern"],
        task_definition=row["task_definition"],
    )
    return next_task


def create_task(task: TaskCreate):
    db = get_db()

    task_model = TaskModel()
    task_model.name = task.name
    task_model.execution_time = task.execution_time
    task_model.recurrence_pattern = task.recurrence_pattern
    task_model.task_definition = task.task_definition

    db.add(task_model)
    db.commit()
    return task_model.id


def update_task(task: TaskUpdate):
    db = get_db()

    task_model = TaskModel()
    task_model.name = task.name
    task_model.execution_time = task.execution_time

    db._update_impl(task_model)
    db.commit()

    return task_model.id


def delete_task_by_id(task_id: int):
    db = get_db()
    task = db.execute(select(TaskModel).where(TaskModel.id == task_id))
    if task:
        db.delete(task)
        db.commit()
        return {"message": "Task deleted successfully"}
    else:
        raise Exception("Task not found!!")
