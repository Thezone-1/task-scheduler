from pydantic import BaseModel, Field
import datetime


class TaskRequest(BaseModel):
    name: str = Field(..., title="Task Name", min_length=1, max_length=100)
    execution_time: datetime.datetime
    recurrence_pattern: str | None = None
    task_definition: str
