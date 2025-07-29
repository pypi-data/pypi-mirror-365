# external package imports.
# none

# our package imports.
from .siwatch import SIWatch

# our package constants.
from .siconst import (
    UNKNOWN_VALUE
)

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIWatchEventArgs:
    """
    This class is used by the SmartInspect.WatchEvent event.

    Threadsafety:
        This class is fully thread-safe.
    """

    def __init__(self, watch:SIWatch) -> None:
        """
        Initializes a new instance of the class.

        Args:
            watch (SIWatch):
                The Watch item that was processed.
        """

        # initialize instance.
        self._fWatch:SIWatch = watch


    @property
    def Watch(self) -> SIWatch:
        """
        Returns the Watch item that was processed.
        """
        return self._fWatch


    def __str__(self) -> str:
        """
        Returns a string representation of the object.
        
        Returns:
            A string in the form of "SIWatchEventArgs: Type=X, Level=X, Name=\"X\", Value=\"X\""
        """
        argsType:str = UNKNOWN_VALUE
        name:str = UNKNOWN_VALUE
        level:str = UNKNOWN_VALUE
        value:str = UNKNOWN_VALUE

        if (self._fWatch != None):
            argsType = self._fWatch.WatchType.name
            level = self._fWatch.Level.name
            name = self._fWatch.Name
            value = self._fWatch.Value

        return str.format("SIWatchEventArgs: Type={0}, Level={1}, Name=\"{2}\", Value=\"{3}\"", argsType, level, name, value)


@export
class SIWatchEventHandler:
    """
    This is the event handler type for the SmartInspect.WatchEvent event.
    """

    def __init__(self, sender:object, e:SIWatchEventArgs) -> None:

        """
        Initializes a new instance of the class.

        Args:
            sender (object):
                The object which fired the event.
            e (SIWatchEventArgs):
                Arguments that contain detailed information related to the event.
        """
        pass
