import asyncio
import random
from datetime import datetime, timedelta


# Task execution logic
async def execute_task(task_id: int, execution_time: datetime, recurrence_pattern: str):
    await asyncio.sleep(random.randint(1, 10))  # Simulate work
    print(f"Task {task_id} executed at {execution_time}")

    # Schedule next execution for recurring tasks
    if recurrence_pattern == "daily":
        next_execution_time = execution_time + timedelta(days=1)
    elif recurrence_pattern == "weekly":
        next_execution_time = execution_time + timedelta(weeks=1)
    else:
        next_execution_time = None

    # if next_execution_time:
    #     db_task = get_task(db, task_id)
    #     if db_task:
    #         db_task.execution_time = next_execution_time
    #         db.commit()
    #         asyncio.create_task(
    #             execute_task(task_id, next_execution_time, recurrence_pattern, db)
    #         )


# def calculate_next_execution_time(current_execution_time: datetime, recurrence: str):
#     if recurrence == RecurrencePattern.DAILY:
#         return current_execution_time + timedelta(days=1)
#     elif recurrence == RecurrencePattern.WEEKLY:
#         return current_execution_time + timedelta(weeks=1)
#     elif recurrence == RecurrencePattern.MONTHLY:
#         return current_execution_time + timedelta(days=30)  # Naive approach for monthly recurrence
