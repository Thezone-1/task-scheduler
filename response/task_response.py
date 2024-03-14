from pydantic import BaseModel
import datetime


class TaskResponse(BaseModel):
    id: int
    name: str
    execution_time: datetime.datetime
    recurrence_pattern: str | None
