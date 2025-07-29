# external package imports.
# none

# our package imports.
from .siprocessflow import SIProcessFlow

# our package constants.
from .siconst import (
    UNKNOWN_VALUE
)

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIProcessFlowEventArgs:
    """
    This class is used by the SmartInspect.ProcessFlow event.

    It has only one public class member named ProcessFlow. This
    member is a property, which just returns the sent packet.

    Threadsafety:
        This class is fully thread-safe.
    """

    def __init__(self, processFlow:SIProcessFlow) -> None:
        """
        Initializes a new instance of the class.

        Args:
            processFlow (SIProcessFlow):
                The Process Flow packet which caused the event.
        """

        # initialize instance.
        self._fProcessFlow:SIProcessFlow = processFlow


    @property
    def ProcessFlow(self) -> SIProcessFlow:
        """
        Returns the ProcessFlow packet, which has just been sent.
        """
        return self._fWatch


    def __str__(self) -> str:
        """
        Returns a string representation of the object.
        
        Returns:
            A string in the form of "SIProcessFlowEventArgs: Type=X, Level=X, Title=\"X\"
        """
        argsType:str = UNKNOWN_VALUE
        title:str = UNKNOWN_VALUE
        level:str = UNKNOWN_VALUE

        if (self._fProcessFlow != None):
            argsType = self._fProcessFlow.ProcessFlowType.name
            title = self._fProcessFlow.Title
            level = self._fProcessFlow.Level.name

        return str.format("SIProcessFlowEventArgs: Type={0}, Level={1}, Title=\"{2}\"", argsType, level, title)


@export
class SIProcessFlowEventHandler:
    """
    This is the event handler type for the SmartInspect.ProcessFlowEvent event.
    """

    def __init__(self, sender:object, e:SIProcessFlowEventArgs) -> None:
        """
        Initializes a new instance of the class.

        Args:
            sender (object):
                The object which fired the event.
            e (SIProcessFlowEventArgs):
                Arguments that contain detailed information related to the event.
        """
