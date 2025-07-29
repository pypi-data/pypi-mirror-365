# our package imports.
# none

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIConnectionFoundEventArgs:
    """
    This class is used by the SIConnectionsParser class to inform interested parties 
    that a protocol connection string has been found.

    Threadsafety:
        This class is fully thread-safe.
    """
    def __init__(self, protocol:str, options:str) -> None:
        """
        Initializes a new instance of the class.

        Args:
          protocol (str):
            The protocol name which has been found.
          options (str):
            The options of the new protocol.

        """

        # initialize instance.
        self._fProtocol:str = protocol
        self._fOptions:str = options


    @property
    def Options(self) -> str:
        """
        This read-only property returns the key of the option which
        has just been found by a SIConnectionsParser object.
        """
        return self._fOptions


    @property
    def Protocol(self) -> str:
        """
        This read-only property returns the protocol which has just
        been found by a SIConnectionsParser object.
        """
        return self._fProtocol


    def __str__(self) -> str:
        """
        Returns a string representation of the object.
        
        Returns:
            A string in the form of "Protocol Name=NN, Options=OO".
        """
        return str.format("Protocol Name=\"{0}\", Options=\"{1}\"", self._fProtocol, self._fOptions)


@export
class SIConnectionFoundEventHandler:
    """
    This is the callback type for the SIConnectionsParser.Parse method.
    """

    def __init__(self, sender:object, e:SIConnectionFoundEventArgs) -> None:
        """
        Initializes a new instance of the class.

        Args:
            sender (object):
                The object which fired the event.
            e (ConnectionFoundEventArgs):
                Arguments that contain detailed information related to the event.
        """
