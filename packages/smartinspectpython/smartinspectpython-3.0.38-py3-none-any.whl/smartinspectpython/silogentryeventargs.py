# our package imports.
from .silogentry import SILogEntry

# our package constants.
from .siconst import (
    UNKNOWN_VALUE
)

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SILogEntryEventArgs:
    """
    This class is used by the SmartInspect.LogEntry event.
    
    It has only one public class member named LogEntry. This member
    is a property, which just returns the sent packet.

    Threadsafety:
        This class is fully thread-safe.
    """

    def __init__(self, logEntry:SILogEntry) -> None:
        """
        Initializes a new instance of the class.

        Args:
            logEntry (SILogEntry):
                The Log Entry packet which caused the event.
        """

        # initialize instance.
        self._fLogEntry:SILogEntry = logEntry


    @property
    def LogEntry(self) -> SILogEntry:
        """
        Returns the LogEntry packet, which has just been sent.
        """
        return self._fLogEntry


    def __str__(self) -> str:
        """
        Returns a string representation of the object.
        
        Returns:
            A string in the form of "SILogEntryEventArgs: Type=X, Level=X, Title=\"X\".
        """
        argsType:str = UNKNOWN_VALUE
        title:str = UNKNOWN_VALUE
        level:str = UNKNOWN_VALUE

        if (self._fLogEntry != None):
            argsType = self._fLogEntry.LogEntryType.name
            title = self._fLogEntry.Title
            level = self._fLogEntry.Level.name

        return str.format("SILogEntryEventArgs: Type={0}, Level={1}, Title=\"{2}\"", argsType, level, title)


@export
class SILogEntryEventHandler:
    """
    This is the event handler type for the SmartInspect.LogEntryEvent event.
    """

    def __init__(self, sender:object, e:SILogEntryEventArgs) -> None:
        """
        Initializes a new instance of the class.

        Args:
            sender (object):
                The object which fired the event.
            e (LogEntryEventArgs):
                Arguments that contain detailed information related to the event.
        """
