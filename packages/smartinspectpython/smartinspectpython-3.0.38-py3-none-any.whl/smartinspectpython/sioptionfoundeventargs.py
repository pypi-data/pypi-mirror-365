# our package imports.
# none

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIOptionFoundEventArgs:
    """
    This class is used by the SIOptionsParser class to inform interested parties 
    that a protocol option has been found.

    Threadsafety:
        This class is fully thread-safe.
    """
    def __init__(self, protocol:str, key:str, value:str) -> None:
        """
        Initializes a new instance of the class.

        Args:
          protocol (str):
            The protocol name of the new option.
          key (str):
            The key of the new option.
          value (str):
            The value of the new option.
        """

        # initialize instance.
        self._fProtocol:str = protocol
        self._fKey:str = key
        self._fValue:str = value


    @property
    def Protocol(self) -> str:
        """
        This read-only property returns the protocol name of the option
        which has just been found by a SIOptionsParser object.
        """
        return self._fProtocol


    @property
    def Key(self) -> str:
        """
        This read-only property returns the key of the option which
        has just been found by a SIOptionsParser object.
        """
        return self._fKey


    @property
    def Value(self) -> str:
        """
        This read-only property returns the value of the option which
        has just been found by a SIOptionsParser object.
        """
        return self._fValue


    def __str__(self) -> str:
        """
        Returns a string representation of the object.
        
        Returns:
            A string in the form of "Protocol Name=NN, Key=KK, Value=VV".
        """
        return str.format("Protocol Name=\"{0}\", Key=\"{1}\", Value=\"{2}\"", self._fProtocol, self._fKey, self._fValue)


@export
class SIOptionFoundEventHandler:
    """
    This is the callback type for the SIOptionsParser.Parse method.
    """

    def __init__(self, sender:object, e:SIOptionFoundEventArgs) -> None:
        """
        Initializes a new instance of the class.

        Args:
            sender (object):
                The object which fired the event.
            e (SIOptionFoundEventArgs):
                Arguments that contain detailed information related to the event.
        """
