# our package constants.
from .siconst import (
    UNKNOWN_VALUE
)

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIErrorEventArgs:
    """
    Arguments passed to the SmartInspect.ErrorEvent event.

    It has only one public class member named Exception. This member
    is a property, which just returns the occurred exception.

    Threadsafety:
        This class is fully thread-safe.
    """

    def __init__(self, e:Exception) -> None:
        """
        Initializes a new instance of the class.

        Args:
            e (Exception):
                Exception that caused the event.
        """

        # initialize instance.
        self._fException:Exception = e


    @property
    def Exception(self) -> Exception:
        """
        Exception that caused the event.
        """
        return self._fException


    def __str__(self) -> str:
        """
        Returns a string representation of the object.
        
        Returns:
            A string in the form of "SIErrorEventArgs: Exception Message".
        """
        exMsg:str = UNKNOWN_VALUE

        if (self._fException != None):
            exMsg = str(self._fException)

        return "SIErrorEventArgs: {0}".format(exMsg)


@export
class SIErrorEventHandler:
    """
    Event handler type for the SmartInspect.ErrorEvent event.
    """

    def __init__(self, sender:object, e:SIErrorEventArgs) -> None:
        """
        Initializes a new instance of the class.

        Args:
            sender (object):
                The object which fired the event.
            e (SIErrorEventArgs):
                Arguments that contain detailed information related to the event.
        """
        pass
