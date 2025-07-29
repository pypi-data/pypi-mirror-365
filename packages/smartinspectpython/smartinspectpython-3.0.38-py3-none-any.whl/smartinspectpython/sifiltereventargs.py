# our package imports.
from .sipacket import SIPacket

# our package constants.
from .siconst import (
    UNKNOWN_VALUE
)

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIFilterEventArgs:
    """
    This class is used by the SmartInspect.Filter event.

    Threadsafety:
        This class is fully thread-safe.
    """
    def __init__(self, packet:SIPacket) -> None:
        """
        Initializes a new instance of the class.

        Args:
            packet (SIPacket):
                The packet which caused the event.
        """

        # initialize instance.
        self._fCancel:bool = False
        self._fPacket:SIPacket = packet


    @property
    def Packet(self) -> SIPacket:
        """
        This read-only property returns the packet, which caused
        the event.
        """
        return self._fPacket


    @property
    def Cancel(self) -> bool:
        """ 
        Gets the Cancel property value.

        This property can be used to cancel the processing of certain
        packets during the SmartInspect.Filter event.
        """
        return self._fCancel
    

    @Cancel.setter
    def Cancel(self, value:bool) -> None:
        """ 
        Sets the Cancel property value.
        """
        if value != None:
            self._fCancel = value


    def __str__(self) -> str:
        """
        Returns a string representation of the object.
        
        Returns:
            A string in the form of "SIFilterEventArgs: PacketType=X, Size=N".
        """
        argsType:str = UNKNOWN_VALUE
        size:int = 0

        if (self._fPacket != None):
            argsType = self._fPacket.PacketType.name
            size = self._fPacket.Size

        return str.format("SIFilterEventArgs: PacketType={0}, Size={1}", argsType, size)


@export
class SIFilterEventHandler:
    """
    This is the event handler type for the SmartInspect.Filter event.
    """

    def __init__(self, sender:object, e:SIFilterEventArgs) -> None:
        """
        Initializes a new instance of the class.

        Args:
            sender (object):
                The object which fired the event.
            e (SIFilterEventArgs):
                Arguments that contain detailed information related to the event,
                and canceling of its processing.
        """
