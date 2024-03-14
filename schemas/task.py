import datetime


class TaskBase:
    name: str
    execution_time: datetime.datetime
    recurrence_pattern: str | None
    task_definition: str

    def __init__(
        self,
        name: str,
        execution_time: datetime.datetime,
        recurrence_pattern: str | None,
        task_definition: str,
    ):
        self.name = name
        self.execution_time = execution_time
        self.recurrence_pattern = recurrence_pattern
        self.task_definition = task_definition


class TaskCreate(TaskBase):

    def __init__(
        self,
        name: str,
        execution_time: datetime.datetime,
        recurrence_pattern: str | None,
        task_definition: str,
    ):
        super().__init__(name, execution_time, recurrence_pattern, task_definition)


class TaskUpdate(TaskBase):

    def __init__(
        self,
        name: str,
        execution_time: datetime.datetime,
        recurrence_pattern: str | None,
        task_definition: str,
    ):
        super().__init__(name, execution_time, recurrence_pattern, task_definition)


class Task(TaskBase):
    id: int

    class Config:
        orm_mode = True

    def __init__(
        self,
        id: int,
        name: str,
        execution_time: datetime.datetime,
        recurrence_pattern: str | None,
        task_definition: str,
    ):
        super().__init__(name, execution_time, recurrence_pattern, task_definition)
        self.id = id
