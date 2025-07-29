# external package imports.
from io import BytesIO

# our package imports.
from .sibinaryformatter import SIBinaryFormatter
from .siformatter import SIFormatter
from .sipacket import SIPacket
from .sipackettype import SIPacketType
from .sipatternparser import SIPatternParser

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SITextFormatter(SIFormatter):
    """
    Responsible for creating a text representation of a packet and
    writing it to a stream.

    This class creates a text representation of a packet and writes
    it to a stream. The representation can be influenced with the
    Pattern property. The Compile method preprocesses a packet and
    computes the required size of the packet. The Write method writes
    the preprocessed packet to the supplied stream.

    Threadsafety:
        This class is not guaranteed to be thread-safe.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """

        # initialize instance.
        self._fLine = []
        self._fParser:SIPatternParser = SIPatternParser()


    @property
    def Indent(self) -> bool:
        """ 
        Gets the Indent property value.

        Indicates if this formatter should automatically intend log
        packets like in the Views of the SmartInspect Console.

        Log Entry packets of type EnterMethod increase the indentation
        and packets of type LeaveMethod decrease it.
        """
        return self._fParser.Indent
    
    @Indent.setter
    def Indent(self, value:bool) -> None:
        """ 
        Sets the Indent property value.
        """
        if value != None:
            self._fParser.Indent = value


    @property
    def Pattern(self) -> str:
        """
        Gets the Pattern property value.

        Represents the pattern used to create a text representation
        of a packet.

        For detailed information of how a pattern string can look like,
        please have a look at the documentation of the SIPatternParser
        class, especially the SIPatternParser.Pattern property.
        """
        return self._fParser.Pattern

    @Pattern.setter
    def Pattern(self, value:str) -> None:
        """
        Sets the Pattern property value.
        """
        self._fParser.Pattern = value


    def Compile(self, packet:SIPacket) -> int:
        """
        Overridden. Preprocesses (or compiles) a packet and returns the
        required size for the compiled result.

        Args:
            packet (SIPacket):
                The packet to compile.

        Returns:
            The size for the compiled result.

        This method creates a text representation of the supplied
        packet and computes the required size. The resulting
        representation can be influenced with the Pattern property.
        To write a compiled packet, call the Write method. Please
        note that this method only supports Log Entry objects and
        ignores any other packet. This means, for packets other
        than Log Entry, this method always returns 0.
        """
        if (packet.PacketType == SIPacketType.LogEntry):
        
            line:str = self._fParser.Expand(packet) + "\r\n"
            self._fLine = SIBinaryFormatter._EncodeString(line)
            return len(self._fLine)
        
        else:
        
            self._fLine = None
            return 0


    def Write(self, stream:BytesIO) -> None:
        """
        Overridden. Writes a previously compiled packet to the supplied stream.
        
        Args:
            stream (BytesIO):
                The stream to write the packet to.

        Raises:
            IOException:
                An I/O error occurred while trying to write the compiled packet.

        This method writes the previously computed text representation
        of a packet (see Compile) to the supplied stream object.
        If the return value of the Compile method was 0, nothing is written.
        """
        if (self._fLine != None):

            stream.write(self._fLine)
