from collections.abc import Callable
from typing import List, Tuple

from application.dtos.task_dto import CreateTaskDTO, UpdateTaskDTO, TaskDTO
from domain.entities import Task, Repeat
from domain.enums import RepeatFrequency
from domain.utils import num_to_frequency, str_weekdays_to_set_weekdays, set_weekdays_to_str_weekdays


class TaskService:
    def __init__(self, uow_factory) -> None:
        self._uow_factory = uow_factory
    
    async def create_task(self, create_task_dto: CreateTaskDTO) -> TaskDTO:
        """Create a new task."""
        async with self._uow_factory as uow:
            # Create domain entity
            repeat = Repeat.create_new(
                frequency=num_to_frequency(create_task_dto.repeat_frequency),
                interval=create_task_dto.repeat_interval,
                allowed_weekdays=str_weekdays_to_set_weekdays(create_task_dto.repeat_allowed_weekdays)
            )
            task = Task(
                title=create_task_dto.title,
                note=create_task_dto.note,
                due_date=create_task_dto.due_date,
                #is_completed=create_task_dto.is_completed,
                is_important=create_task_dto.is_important,
                repeat=repeat
            )

            # Persist via repository
            task = await uow.tasks.add(task)

            # Commit transaction
            await uow.commit()

            # Return TaskDTO
            return TaskDTO.from_entity(task)

    async def get_task_by_id(self, task_id: int) -> TaskDTO:
        """Get a task by id."""
        async with self._uow_factory as uow:
            task = await uow.tasks.get_by_id(task_id)
            
            if task is None:
                raise ValueError(f"Task with id {task_id} not found.")

            return TaskDTO.from_entity(task)
    
    async def get_all_tasks(self, skip: int = 0, limit: int = 100) -> List[TaskDTO]:
        """Get all tasks with pagination."""
        async with self._uow_factory as uow:
            tasks = await uow.tasks.get_all(skip=skip, limit=limit)
            return [TaskDTO.from_entity(task) for task in tasks]
    
    async def update_task(self, task_id: int, update_task_dto: UpdateTaskDTO) -> TaskDTO:
        """Update a task."""
        async with self._uow_factory as uow:
            # Get existing task
            task = await uow.tasks.get_by_id(task_id)
            
            if task is None:
                raise ValueError(f"Task with id {task_id} not found.")

            # Update validated fields by domain entity method
            if update_task_dto.title:
                task.change_title(update_task_dto.title)
            
            # Update non-validated fields directly
            task.note = update_task_dto.note
            task.is_important = update_task_dto.is_important

            # Due date and repeat
            repeat = Repeat.create_new(
                frequency=num_to_frequency(update_task_dto.repeat_frequency),
                interval=update_task_dto.repeat_interval,
                allowed_weekdays=str_weekdays_to_set_weekdays(update_task_dto.repeat_allowed_weekdays)
            )
            task.change_due_date_and_repeat(update_task_dto.due_date, repeat)

            # Persist via repository
            task = await uow.tasks.update(task)

            # Commit transaction
            await uow.commit()

            # Return TaskDTO
            return TaskDTO.from_entity(task)
    
    async def delete_task(self, task_id: int) -> None:
        """Delete a task by id."""
        async with self._uow_factory as uow:
            is_deleted = await uow.tasks.delete(task_id)
        
            if not is_deleted:
                raise ValueError(f"Task with id {task_id} not found.")

            await uow.commit()
    
    async def complete_task(self, task_id: int) -> Tuple[TaskDTO, TaskDTO | None]:
        """Complete a task by id."""
        async with self._uow_factory as uow:
            task = await uow.tasks.get_by_id(task_id)
            
            if task is None:
                raise ValueError(f"Task with id {task_id} not found.")

            if task.is_completed:
                raise ValueError(f"Task with id {task_id} is already completed.")
            
            # Create new repeat task if repeating
            generated_repeat_task = task.create_new_repeating_task()

            # Persist via repository
            new_repeat_task = await uow.tasks.add(generated_repeat_task) if generated_repeat_task else None

            # Update existing task
            task.is_completed = True
            task.repeat = None

            # Persist via repository
            task = await uow.tasks.update(task)

            # Commit transaction
            await uow.commit()

            """
            return (
                TaskDTO.from_entity(task),
                TaskDTO.from_entity(new_repeat_task) if new_repeat_task else None
            )
            """

            return task, new_repeat_task
                

    async def uncomplete_task(self, task_id: int) -> TaskDTO:
        """Uncomplete a task by id."""
        async with self._uow_factory as uow:
            task = await uow.tasks.get_by_id(task_id)
            
            if task is None:
                raise ValueError(f"Task with id {task_id} not found.")

            if not task.is_completed:
                raise ValueError(f"Task with id {task_id} is not completed.")
            
            task.is_completed = False

            # Persist via repository
            task = await uow.tasks.update(task)

            # Commit transaction
            await uow.commit()

            # Return TaskDTO
            return TaskDTO.from_entity(task)
