from datetime import datetime

from sqlalchemy import String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column

from domain.entities import Task
from infrastructure.persistence.database import Base

class TaskModel(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    note: Mapped[str] = mapped_column(Text, nullable=True)
    due_date: Mapped[datetime] = mapped_column(nullable=True)
    is_completed: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_important: Mapped[bool] = mapped_column(nullable=False, default=False)
    repeat_frequency: Mapped[int] = mapped_column(nullable=True)
    repeat_interval: Mapped[int] = mapped_column(nullable=True)
    repeat_weekdays: Mapped[str] = mapped_column(String(7), nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now())

    def to_entity(self) -> Task:
        return Task(
            description=self.description,
            note=self.note,
            due_date=self.due_date,
            is_completed=self.is_completed,
            is_important=self.is_important,
            repeat_frequency=self.repeat_frequency,
            repeat_interval=self.repeat_interval,
            repeat_weekdays=self.repeat_weekdays,
            id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    @staticmethod
    def from_entity(task: Task) -> TaskModel:
        return TaskModel(
            id=task.id,
            description=task.description,
            note=task.note,
            due_date=task.repeat_manager.due_date,
            is_completed=task.is_completed,
            is_important=task.is_important,
            repeat_frequency=task.repeat_manager.repeat.frequency,
            repeat_interval=task.repeat_manager.repeat.interval,
            repeat_weekdays=task.repeat_manager.repeat.weekdays_str,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
