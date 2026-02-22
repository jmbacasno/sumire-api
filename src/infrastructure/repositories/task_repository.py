from datetime import datetime
from typing import List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities import Task
from domain.utils import num_to_frequency, str_weekdays_to_set_weekdays, set_weekdays_to_str_weekdays
from infrastructure.persistence.models import TaskModel

class TaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, task: Task) -> Task:
        """Add a new task."""
        task_model = TaskModel.from_entity(task)

        self._session.add(task_model)

        await self._session.flush()

        await self._session.refresh(task_model)

        return task_model.to_entity()
    
    async def get_by_id(self, id: int) -> Task:
        """Get a task by id."""
        result = await self._session.execute(
            select(TaskModel).where(TaskModel.id == id)
        )
        
        task_model = result.scalars().one_or_none()

        if task_model is None:
            return None
        
        return task_model.to_entity()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks with pagination."""
        result = await self._session.execute(
            select(TaskModel).offset(skip).limit(limit)
        )

        task_models = result.scalars().all()

        return [model.to_entity() for model in task_models]
    
    async def update(self, task: Task) -> Task:
        """Update a task."""
        if task.id is None:
            raise ValueError("Cannot update task without id.")
        
        # Get existing task
        result = await self._session.execute(
            select(TaskModel).where(TaskModel.id == task.id)
        )
        task_model = result.scalars().one_or_none()

        if task_model is None:
            raise ValueError(f"Task with id {task.id} not found.")

        # Update fields from entity
        task_model.title = task.title
        task_model.note = task.note
        task_model.due_date = task.due_date
        task_model.is_completed = task.is_completed
        task_model.is_important = task.is_important

        if task.repeat:
            task_model.repeat_frequency = task.repeat.frequency.value
            task_model.repeat_interval = task.repeat.interval
            task_model.repeat_allowed_weekdays = set_weekdays_to_str_weekdays(task.repeat.allowed_weekdays)
        else:
            task_model.repeat_frequency = None
            task_model.repeat_interval = None
            task_model.repeat_allowed_weekdays = None

        # Manually update updated_at
        task_model.updated_at = datetime.now()

        await self._session.flush()
        await self._session.refresh(task_model)

        return task_model.to_entity()

    async def delete(self, id: int) -> bool:
        """Delete a task by id."""
        result = await self._session.execute(
            select(TaskModel).where(TaskModel.id == id)
        )

        task_model = result.scalars().one_or_none()

        if task_model is None:
            return False
        
        await self._session.delete(task_model)
        await self._session.flush()

        return True
    
    async def exists(self, id: int) -> bool:
        """Check if a task exists."""
        result = await self._session.execute(
            select(TaskModel).where(TaskModel.id == id)
        )

        return result.scalar_one_or_none() is not None