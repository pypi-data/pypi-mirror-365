# our package imports.
from .sicontrolcommand import SIControlCommand

# our package constants.
from .siconst import (
    UNKNOWN_VALUE
)

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIControlCommandEventArgs:
    """
    This class is used by the SmartInspect.ControlCommandEvent event.

    Threadsafety:
        This class is fully thread-safe.
    """
    def __init__(self, controlCommand:SIControlCommand) -> None:
        """
        Initializes a new instance of the class.

        Args:
            controlCommand (SIControlCommand):
                The Control Command packet which caused the event.
        """

        # initialize instance.
        self._fControlCommand:SIControlCommand = controlCommand


    @property
    def ControlCommand(self) -> SIControlCommand:
        """
        Returns the ControlCommand item that was processed.
        """
        return self._fControlCommand


    def __str__(self) -> str:
        """
        Returns a string representation of the object.
        
        Returns:
            A string in the form of "SIControlCommandEventArgs: Type=X, Level=X".
        """
        argsType:str = UNKNOWN_VALUE
        level:str = UNKNOWN_VALUE

        if (self._fControlCommand != None):
            argsType = self._fControlCommand.ControlCommandType.name
            level = self._fControlCommand.Level.name

        return str.format("SIControlCommandEventArgs: Type={0}, Level={1}", argsType, level)


@export
class SIControlCommandEventHandler:
    """
    This is the event handler type for the SmartInspect.ControlCommandEvent event.
    """

    def __init__(self, sender:object, e:SIControlCommandEventArgs) -> None:
        """
        Initializes a new instance of the class.

        Args:
            sender (object):
                The object which fired the event.
            e (SIControlCommandEventArgs):
                Arguments that contain detailed information related to the event.
        """
