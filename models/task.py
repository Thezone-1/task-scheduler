from sqlalchemy import Column, Integer, String, DateTime, Boolean
from database.database_config import Base


class TaskModel(Base):

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50))
    execution_time = Column(DateTime)
    recurrence_pattern = Column(String, nullable=True, name="recurrence_pattern")
    task_definition = Column(String, nullable=True, name="task_definition")
    valid = Column(Boolean, nullable=False, name="valid", default=True)
    # recurring_Interval = Column(Integer)
    # creationTime = Column(TIMESTAMP, default=True)
    # updated_time = Column(TIMESTAMP, default=True)
