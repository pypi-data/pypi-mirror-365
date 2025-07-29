# external package imports.
# none

# our package imports.
# none

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIInvalidConnectionsException(Exception):
    """
    Used to report errors concerning the connections string in the
    SmartInspect class.
    
    An invalid syntax, unknown protocols or inexistent options in the
    SmartInspect.Connections property value will result in
    an SIInvalidConnectionsException exception.
    
    Threadsafety:
        This class is not guaranteed to be thread-safe.
    """
    def __init__(self, message, *args, **kwargs) -> None:
        """
        Initializes a new instance of the class.

        Args:
            message (Any):
                The exception message.
        """

        # initialize base class.
        super().__init__(message, *args, **kwargs)
