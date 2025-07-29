# external package imports.
# none

# our package imports.
# none

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIProtocolCommand:
    """
    Represents a custom protocol action command as used by the
    SIProtocol.Dispatch method.

    This class is used by custom protocol actions. For detailed 
    information about custom protocol actions, please refer to
    the SIProtocol.Dispatch and SmartInspect.Dispatch methods.

    Threadsafety:
        The public members of this class are thread-safe.
    """

    def __init__(self, action:int, state:object) -> None:
        """
        Initializes a new instance of the class.

        Args:
            action (int):
                The custom protocol action to execute.
            state (object):
                Optional object which provides additional information about
                the custom protocol action.
        """
        # initialize instance.
        self._fAction:int = action
        self._fState:object = state


    @property
    def Action(self) -> int:
        """
        Gets the Action property value.

        Returns the custom protocol action to execute. The value
        of this property is protocol specific.
        """
        return self._fAction
    

    @property
    def State(self) -> object:
        """
        Gets the State property value.

        Returns the optional protocol command object which provides
        additional information about the custom protocol action.
        This property can be null.
        """
        return self._fState
