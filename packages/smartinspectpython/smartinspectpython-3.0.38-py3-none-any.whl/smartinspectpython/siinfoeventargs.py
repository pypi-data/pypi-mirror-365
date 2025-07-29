# our package constants.
from .siconst import (
    UNKNOWN_VALUE
)

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIInfoEventArgs:
    """
    Arguments passed to the SmartInspect.InfoEvent event.

    It has only one public class property named Message.

    Threadsafety:
        This class is fully thread-safe.
    """

    def __init__(self, message:str) -> None:
        """
        Initializes a new instance of the class.

        Args:
            message (str):
                Informational message to convey.
        """

        # initialize instance.
        self._fMessage:Exception = message


    @property
    def Message(self) -> str:
        """
        Informational message to convey.
        """
        return self._fMessage


    def __str__(self) -> str:
        """
        Returns a string representation of the object.
        
        Returns:
            A string in the form of "SIInfoEventArgs: Message".
        """
        msg:str = UNKNOWN_VALUE

        if (self._fMessage != None):
            msg = self._fMessage

        return "SIInfoEventArgs: {0}".format(msg)


@export
class SIInfoEventHandler:
    """
    Event handler type for the SmartInspect.InfoEvent event.
    """

    def __init__(self, sender:object, e:SIInfoEventArgs) -> None:
        """
        Initializes a new instance of the class.

        Args:
            sender (object):
                The object which fired the event.
            e (SIInfoEventArgs):
                Arguments that contain detailed information related to the event.
        """
        pass
