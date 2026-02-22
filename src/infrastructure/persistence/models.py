from datetime import datetime

from sqlalchemy import String, Text, Integer, Boolean, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column

from domain.entities import Task, Repeat, Step
from domain.utils import num_to_frequency, str_weekdays_to_set_weekdays, set_weekdays_to_str_weekdays
from infrastructure.persistence.database import Base

class StepModel(Base):
    __tablename__ = "steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False)

    title: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(default=datetime.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now(), onupdate=datetime.now(), nullable=False)

    def to_entity(self) -> Step:
        return Step(
            title=self.title,

            id=self.id,
            task_id=self.task_id,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    @staticmethod
    def from_entity(step: Step) -> StepModel:
        return StepModel(
            id=step.id,
            task_id=step.task_id,

            title=step.title,

            created_at=step.created_at,
            updated_at=step.updated_at
        )

"""
class RepeatModel(Base):
    __tablename__ = "repeats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False)

    frequency: Mapped[int] = mapped_column(nullable=False)
    interval: Mapped[int] = mapped_column(nullable=False)
    allowed_weekdays: Mapped[str] = mapped_column(String(7), nullable=True)

    created_at: Mapped[datetime] = mapped_column(default=datetime.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now(), onupdate=datetime.now(), nullable=False)

    def to_entity(self) -> Repeat:
        frequency = RepeatFrequency(self.frequency)
        allowed_weekdays = {int(day) for day in self.allowed_weekdays} if self.allowed_weekdays else None

        return Repeat(
            frequency=frequency,
            interval=self.interval,
            allowed_weekdays=allowed_weekdays,

            id=self.id,
            task_id=self.task_id,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    @staticmethod
    def from_entity(repeat: Repeat) -> RepeatModel:
        frequency = repeat.frequency.value
        allowed_weekdays = "".join(map(str, repeat.allowed_weekdays)) if repeat.allowed_weekdays else None

        return RepeatModel(
            id=repeat.id,
            task_id=repeat.task_id,

            frequency=frequency,
            interval=repeat.interval,
            allowed_weekdays=allowed_weekdays,

            created_at=repeat.created_at,
            updated_at=repeat.updated_at
        )
"""

class TaskModel(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    title: Mapped[str] = mapped_column(Text, nullable=False)
    note: Mapped[str] = mapped_column(Text, nullable=True)
    due_date: Mapped[datetime] = mapped_column(nullable=True)
    is_completed: Mapped[bool] = mapped_column(nullable=False, server_default=text("0"))
    is_important: Mapped[bool] = mapped_column(nullable=False, server_default=text("0"))

    repeat_frequency: Mapped[int] = mapped_column(nullable=True)
    repeat_interval: Mapped[int] = mapped_column(nullable=True)
    repeat_allowed_weekdays: Mapped[str] = mapped_column(String(7), nullable=True)

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now())

    def to_entity(self) -> Task:
        repeat = Repeat.create_new(
            frequency=num_to_frequency(self.repeat_frequency),
            interval=self.repeat_interval,
            allowed_weekdays=str_weekdays_to_set_weekdays(self.repeat_allowed_weekdays)
        )
        return Task(
            title=self.title,
            note=self.note,
            due_date=self.due_date,
            is_completed=self.is_completed,
            is_important=self.is_important,

            repeat=repeat,

            id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    @staticmethod
    def from_entity(task: Task) -> TaskModel:
        if task.repeat:
            frequency = task.repeat.frequency.value
            interval = task.repeat.interval
            allowed_weekdays = set_weekdays_to_str_weekdays(task.repeat.allowed_weekdays)
        else:
            frequency = None
            interval = None
            allowed_weekdays = None

        return TaskModel(
            id=task.id,

            title=task.title,
            note=task.note,
            due_date=task.due_date,
            is_completed=task.is_completed,
            is_important=task.is_important,

            repeat_frequency=frequency,
            repeat_interval=interval,
            repeat_allowed_weekdays=allowed_weekdays,

            created_at=task.created_at,
            updated_at=task.updated_at
        )
