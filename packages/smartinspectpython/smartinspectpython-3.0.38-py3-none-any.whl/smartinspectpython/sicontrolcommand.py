from copy import copy
from io import BytesIO

# our package imports.
from .sicontrolcommandtype import SIControlCommandType
from .silevel import SILevel
from .sipacket import SIPacket
from .sipackettype import SIPacketType

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIControlCommand(SIPacket):
    """
    Represents the Control Command packet type which is used for
    administrative tasks like resetting or clearing the Console.

    A Control Command can be used for several administrative Console
    tasks. Among other things, this packet type allows you to SISession.ClearAll.

    Threadsafety:
        This class is not guaranteed to be thread-safe. However, instances
        of this class will normally only be used in the context of a single thread.
    """

    HEADER_SIZE:int = 8

    def __init__(self, controlCommandType:SIControlCommandType) -> None:
        """ 
        Initializes a new ControlCommand instance with a custom control command type.

        Args:
            controlCommandType (SIControlCommandType):
                The type of the new Control Command describes the way the
                Console interprets this packet. Please see the SIControlCommandType
                enum for more information.
        """

        # initialize the base class.
        super().__init__()

        self._fData:BytesIO = BytesIO()
        self._fControlCommandType:SIControlCommandType = controlCommandType
        self.Level = SILevel.Control


    @property
    def ControlCommandType(self) -> SIControlCommandType:
        """ 
        Gets the ControlCommandType property value.

        The type of the Control Command describes the way the Console
        interprets this packet. Please see the SIControlCommandType enum
        for more information.
        """
        return self._fControlCommandType
    
    @ControlCommandType.setter
    def ControlCommandType(self, value:SIControlCommandType) -> None:
        """ 
        Sets the ControlCommandType property value.
        """ 
        if value != None:
            self._fControlCommandType = value


    @property
    def Data(self) -> BytesIO:
        """
        Gets the Data property value.

        This property contains an optional data stream of the Control Command.
        This property can be null if this Control Command does not
        contain additional data.

        <b>Important:</b> Treat this stream as read-only. This means,
        modifying this stream in any way is not supported. Additionally,
        only pass streams which support seeking. Streams which do not
        support seeking cannot be used by this class.
        """
        return self._fData

    @Data.setter
    def Data(self, value:BytesIO) -> None:
        """ 
        Sets the Data property value.
        """
        if value:
            self._fData = copy(value)
        else:
            self._fData.truncate(0)


    @property
    def DataLength(self) -> int:
        """
        Returns the number of bytes used in the Data property.
        Note that this is the actual # of bytes used, and not the # of bytes allocated!
        """
        if (self._fData != None):
            return self._fData.getbuffer().nbytes
        return 0


    @property
    def HasData(self) -> bool:
        """
        Returns true if this packet contains optional data; otherwise, false.
        """
        if (self._fData != None) & (self._fData.getbuffer().nbytes > 0):
            return True
        return False


    @property
    def PacketType(self) -> SIPacketType:
        """ 
        Overridden.  Returns SIPacketType.ControlCommand
        """
        return SIPacketType.ControlCommand


    @property
    def Size(self) -> int:
        """
        Overridden.  Returns the total occupied memory size of this Control Command packet.

        The total occupied memory size of this Control Command is
        the size of memory occupied the optional Data stream and any
        internal data structures of this Control Command.
        """
        result = (self.HEADER_SIZE)

        if self.HasData:
            result += self._fData.getbuffer().nbytes
        return result
