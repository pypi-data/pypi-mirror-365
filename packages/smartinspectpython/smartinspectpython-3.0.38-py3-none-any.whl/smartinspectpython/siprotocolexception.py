# external package imports.
# none

# our package imports.
from .smartinspectexception import SmartInspectException

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIProtocolException(SmartInspectException):
    """
    Used to report any errors concerning the protocol classes.
    """

    def __init__(self, message:str, protocol:str, options:str, *args, **kwargs) -> None:
        """
        Initializes a new instance of the class.

        Args:
            message (str):
                The exception message.
            protocol (str):
                The protocol name value.
            options (str):
                The protocol options string.
        """

        # initialize base class.
        super().__init__(message, *args, **kwargs)

        # initialize instance.
        self._fProtocolName:str = protocol
        self._fProtocolOptions:str = options


    @property
    def ProtocolName(self) -> str:
        """ 
        Gets the ProtocolName property value.
        """
        return self._fProtocolName
    

    @property
    def ProtocolOptions(self) -> str:
        """ 
        Gets the ProtocolOptions property value.
        """
        return self._fProtocolOptions
