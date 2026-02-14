from domain.entities import Task
from datetime import datetime

from domain.enums import RepeatType

if __name__ == "__main__":
    # Initialize task
    my_task = Task(title="Finish Anki decks")
    # Set due date
    my_task.set_due_date(datetime.now())
    # Set repeat
    my_task.set_repeat(RepeatType.WEEKDAYS)
    # Print task
    print(my_task)