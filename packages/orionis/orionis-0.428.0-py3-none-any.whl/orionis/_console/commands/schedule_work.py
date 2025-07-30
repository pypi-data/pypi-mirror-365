import importlib
from orionis._console.base.command import BaseCommand
from orionis._console.exceptions.cli_runtime_error import CLIOrionisRuntimeError
from orionis._contracts.console.task_manager import ITaskManager
from orionis._facades.commands.scheduler_facade import Schedule

class ScheduleWorkCommand(BaseCommand):
    """
    Command class to handle scheduled tasks within the Orionis application.

    This command initializes the scheduling system, registers the schedule,
    and starts the execution of scheduled tasks.
    """

    signature = "schedule:work"

    description = "Starts the scheduled tasks."

    def __init__(self, schedule : Schedule) -> None:
        """
        Initialize a new instance of the ScheduleWorkCommand class.

        Args:
            schedule (ScheduleService): The schedule instance to use for scheduling tasks.
        """
        self.schedule : Schedule = schedule

    def handle(self) -> None:
        """
        Execute the scheduled tasks.

        This method initializes a Schedule instance, creates a TaskManager (Kernel),
        registers the schedule, and starts the execution of scheduled tasks.

        Raises
        ------
        RuntimeError
            If an unexpected error occurs during execution, a RuntimeError is raised
            with the original exception message.
        """
        try:

            # Create an instance of the TaskManager to manage the scheduling.
            tasks_manager = importlib.import_module("app.console.tasks_manager")
            TaskManager = getattr(tasks_manager, "TaskManager")
            kernel: ITaskManager = TaskManager()
            kernel.schedule(self.schedule)

            # Start running the scheduled tasks using the schedule runner.
            self.schedule.start()

        except Exception as e:

            # Handle any unexpected error and display the error message
            raise CLIOrionisRuntimeError(f"An unexpected error occurred: {e}") from e