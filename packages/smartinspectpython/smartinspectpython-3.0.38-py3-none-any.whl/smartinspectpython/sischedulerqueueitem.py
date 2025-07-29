# external package imports.
# none

# our package imports.
from .sischedulercommand import SISchedulerCommand

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SISchedulerQueueItem:
    """
    SchedulerQueue item class.
    """
    
    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        self.Command:SISchedulerCommand = None
        """
        Scheduler command stored by this queue item.
        """
        self.Next:SISchedulerQueueItem = None
        """
        The next scheduler queue item in the queue.
        """
        self.Previous:SISchedulerQueueItem = None
        """
        The previous scheduler queue item in the queue.
        """
