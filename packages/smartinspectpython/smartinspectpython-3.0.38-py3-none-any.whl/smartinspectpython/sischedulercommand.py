# external package imports.
# none

# our package imports.
from .sischeduleraction import SISchedulerAction

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SISchedulerCommand():
    """
    Represents a scheduler command as used by the SIScheduler class
    and the asynchronous protocol mode.

    This class is used by the SIScheduler class to enqueue protocol
    operations for later execution when operating in asynchronous
    mode. For detailed information about the asynchronous protocol 
    mode, please refer to SIProtocol.IsValidOption.

    Threadsafety:
        This class is not guaranteed to be thread-safe.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """

        # initialize instance.
        self._fAction:SISchedulerAction = SISchedulerAction.Connect
        self._fState:object = None


    @property
    def Action(self) -> SISchedulerAction:
        """
        Gets the Action property value.

        Represents the scheduler action to execute. Please refer
        to the documentation of the SISchedulerAction enum for more
        information about possible values.
        """
        return self._fAction
    
    @Action.setter
    def Action(self, value:SISchedulerAction):
        """
        Sets the Action property value.
        """
        if (value != None):
            self._fAction = value


    @property
    def Size(self) -> int:
        """
        Gets the Size property value.

        Calculates and returns the total memory size occupied by
        this scheduler command.

        This read-only property returns the total occupied memory
        size of this scheduler command. This functionality is used by
        the SIProtocol.IsValidOption to track the total size of scheduler commands.
        """
        if (self._fAction != SISchedulerAction.WritePacket):
            return 0

        if (self._fState != None):
            return self._fState.Size
        
        return 0


    @property
    def State(self) -> object:
        """
        Gets the State property value.

        Represents the optional scheduler command state object which
        provides additional information about the scheduler command.
        This property can be null.
        """
        return self._fState
    
    @State.setter
    def State(self, value:object):
        """
        Sets the State property value.
        """
        self._fState = value
