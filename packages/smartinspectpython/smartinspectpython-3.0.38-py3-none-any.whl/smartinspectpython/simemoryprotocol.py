from io import BytesIO, BufferedWriter

# our package imports.
from .sibinaryformatter import SIBinaryFormatter
from .siconnectionsbuilder import SIConnectionsBuilder
from .sifileprotocol import SIFileProtocol
from .siformatter import SIFormatter
from .sipacket import SIPacket
from .sipacketqueue import SIPacketQueue
from .siprotocol import SIProtocol
from .siprotocolcommand import SIProtocolCommand
from .sitextformatter import SITextFormatter
from .smartinspectexception import SmartInspectException

# our package constants.
from .siconst import (
    TEXTFILE_HEADER_BOM,
    TEXTFILE_INDENT_DEFAULT,
    TEXTFILE_PATTERN_DEFAULT
)

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIMemoryProtocol(SIProtocol):
    """
    Used for writing log data to memory and saving it to a stream
    or another protocol object on request.
    To initiate such a request, use the InternalDispatch method.

    SITextProtocol is used for writing plain text log files. The SIMemoryProtocol class is used when 
    the 'mem' protocol is specified in the SmartInspect.Connections. See the 
    IsValidOption method for a list of available protocol options.
    
    For a list of available protocol options, please refer to the
    IsValidOption method.

    Threadsafety:
        The public members of this class are thread-safe.
    """

    _DEFAULT_MAXSIZE:int = 2048
    _DEFAULT_ASTEXT:bool = False
    
    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        # initialize base classinstance.
        super().__init__()

        # initialize instance.
        self._fMaxSize:int = SIMemoryProtocol._DEFAULT_MAXSIZE
        self._fIndent:bool = TEXTFILE_INDENT_DEFAULT
        self._fPattern:str = TEXTFILE_PATTERN_DEFAULT
        self._fAsText:bool = SIMemoryProtocol._DEFAULT_ASTEXT
        self._fFormatter:SIFormatter = None

        # use our own "_fMemQueue" object, so we don't confuse it with the base class "_fQueue" object!
        self._fMemQueue:SIPacketQueue = None

        # set default options.
        self.LoadOptions()


    @property
    def Name(self) -> str:
        """ 
        Overridden.  Returns "mem".
        """
        return "mem"


    def _FlushToProtocol(self, protocol:SIProtocol) -> None:
        """
        Args:
            protocol (SIProtocol):
                The protocol object to flush to.

        References the specified protocol object to call its WritePacket method 
        for each packet in the internal packet queue.
        """
        # write the current content of our queue.
        if (self._fMemQueue != None):
      
            packet:SIPacket = self._fMemQueue.Pop()
            while (packet != None):
                protocol.WritePacket(packet)
                packet = self._fMemQueue.Pop()


    def _FlushToStream(self, stream:BytesIO) -> None:
        """
        Args:
            stream (BytesIO):
                The stream object to flush to.

        References the specified stream object to call its formatters'
        Format method for each packet in the internal packet queue.
        The necessary header is written first and then the actual packets 
        are appended.

        The header and packet output format can be influenced with
        the "astext" protocol option (see IsValidOption). If the
        "astext" option is true, the header is a UTF8 Byte Order
        Mark and the packets are written in plain text format. If
        the "astext" option is false, the header is the standard
        header for SmartInspect log files and the packets are
        written in the default binary mode. In the latter case, the
        resulting log files can be loaded by the SmartInspect Console.
        """
        # write the necessary file header.
        if (self._fAsText):
            stream.write(TEXTFILE_HEADER_BOM)
        else:
            stream.write(SIFileProtocol._SILF)

        # write the current content of our queue using the appropriate formatter.
        if (self._fMemQueue != None):
      
            packet:SIPacket = self._fMemQueue.Pop()
            while (packet != None):
                if (self._fFormatter != None):
                    self._fFormatter.Format(packet, stream)
                packet = self._fMemQueue.Pop()


    def _InitializeFormatter(self) -> None:
        """
        Initializes formatter based upon the "astext" setting.
        """
        if (self._fAsText):
        
            self._fFormatter = SITextFormatter()
            self._fFormatter.Pattern = self._fPattern
            self._fFormatter.Indent = self._fIndent
        
        else:
        
            self._fFormatter = SIBinaryFormatter()


    def BuildOptions(self, builder:SIConnectionsBuilder) -> None:
        """
        Overridden. Fills a SIConnectionsBuilder instance with the
        options currently used by this protocol.

        Args:
            builder (SIConnectionsBuilder):
                The SIConnectionsBuilder object to fill with the current options
                of this protocol.
        """
        # build base class options.
        super().BuildOptions(builder)

        # build options specific to our class.
        builder.AddOptionInteger("maxsize", self._fMaxSize / 1024)
        builder.AddOptionBool("astext", self._fAsText)
        builder.AddOptionBool("indent", self._fIndent)
        builder.AddOptionString("pattern", self._fPattern)


    def InternalConnect(self) -> None:
        """
        Overridden. Creates and initializes the packet queue.

        This method creates and initializes a new packet queue with
        a maximum size as specified by the Initialize method. For
        other valid options which might affect the behavior of this
        method and protocol, please see the IsValidOption method.
        """
        self._fMemQueue = SIPacketQueue()
        self._fMemQueue.Backlog = self._fMaxSize


    def InternalDisconnect(self):
        """
        Overridden.  Clears the internal queue of packets.

        This method does nothing more than to clear the internal
        queue of packets. After this method has been called, the
        InternalDispatch method writes an empty log unless new
        packets are queued in the meantime.
        """
        if (self._fMemQueue != None):
        
            self._fMemQueue.Clear()
            self._fMemQueue = None


    def InternalDispatch(self, command:SIProtocolCommand) -> None:
        """
        Overridden. Implements a custom action for saving the current
        queue of packets of this memory protocol to a stream or
        protocol object.

        Args:
            command (SIProtocolCommand):
                The protocol command which is expected to provide the stream
                or protocol object.

        Raises:
            Exception:
                Writing the internal queue of packets to the supplied stream or protocol failed.

        Depending on the supplied command argument, this method does
        the following.

        If the supplied State object of the protocol command is of
        type Stream, then this method uses this stream to write the
        entire content of the internal queue of packets. The necessary
        header is written first and then the actual packets are
        appended.

        The header and packet output format can be influenced with
        the "astext" protocol option (see IsValidOption). If the
        "astext" option is true, the header is a UTF8 Byte Order
        Mark and the packets are written in plain text format. If
        the "astext" option is false, the header is the standard
        header for SmartInspect log files and the packets are
        written in the default binary mode. In the latter case, the
        resulting log files can be loaded by the SmartInspect Console.

        If the supplied State object of the protocol command is of
        type Protocol instead, then this method uses this protocol
        object to call its WritePacket method for each packet in the
        internal packet queue.

        The Action property of the command argument should currently
        always be set to 0. If the State object is not a stream or
        protocol command or if the command argument is null, then
        this method does nothing.
        """
        if (command == None):
            return

        # if supplied object is a protocol then flush queue contents to the protocol.
        if (issubclass(type(command.State), SIProtocol)):
            protocol:SIProtocol = command.State
            if (protocol != None):
                self._FlushToProtocol(protocol)
            return

        # if supplied object is a stream then flush queue contents to stream.
        if (issubclass(type(command.State), BufferedWriter)):
            stream:BytesIO = command.State
            if (stream != None):
                self._FlushToStream(stream)
            return

        # if none of the above then there is nothing to do!
        raise SmartInspectException("Dispatch State argument was neither a Protocol nor Stream type of object.")


    def InternalWritePacket(self, packet:SIPacket) -> None:
        """
        Overridden. Writes a packet to the packet queue.

        Args:
            packet (SIPacket):
                The packet to write.

        This method writes the supplied packet to the internal
        queue of packets. If the size of the queue exceeds the
        maximum size as specified by the Options property, the
        queue is automatically resized and older packets are
        discarded.
        """
        if (self._fMemQueue != None):
            self._fMemQueue.Push(packet)


    def IsValidOption(self, name:str) -> bool:
        """
        Overridden. Validates if a protocol option is supported.

        Args:
            name (str):
                The option name to validate.

        Returns:
            True if the option is supported and false otherwise.

        The following table lists all valid options, their default values and descriptions for the TEXT protocol.

        Valid Options (default value)              | Description
        ------------------------------------------ | ----------------------------------------------------------------------
        astext (false)                             | Specifies if logging data should be written as text instead of binary.
        indent (false)                             | Indicates if the logging output should automatically be indented like in the Console if 'astext' is set to true.
        maxsize (2048)                             | Specifies the maximum size of the packet queue of this protocol in kilobytes.  Specify size units like this: "1 MB".  Supported units are "KB", "MB" and "GB".
        pattern ("[%timestamp%] %level%: %title%") | Specifies the pattern used to create a text representation of a packet.
    
        If the "astext" option is used for creating a textual output instead of the default binary, the "pattern" string specifies
        the textual representation of a log packet. For detailed information of how a pattern string can look like, please
        have a look at the documentation of the PatternParser class, especially the PatternParser.Pattern property.

        Please note that this protocol DOES NOT support log data encryption.

        For further options which affect the behavior of this protocol, please have a look at the documentation of the
        SIProtocol.IsValidOption method of the parent class.

        <details>
            <summary>Sample Code</summary>
        ``` python
        .. include:: ../docs/include/samplecode/SIMemoryProtocol/IsValidOption.py
        ```
        </details>
        """
        # encryption related options are NOT supported for memory logging.
        if ((name == "encrypt") or (name == "key")):
            return False

        return \
            (name == "maxsize") or \
            (name == "astext") or \
            (name == "pattern") or \
            (name == "indent") or \
            (super().IsValidOption(name))


    def LoadOptions(self) -> None:
        """
        Overridden. Loads and inspects specific options for this protocol.

        This method loads all relevant options and ensures their
        correctness. See IsValidOption for a list of options which
        are recognized by the protocol.
        """
        # load base class options.
        super().LoadOptions()

        # load options specific to our class.
        self._fMaxSize = self.GetSizeOption("maxsize", SIMemoryProtocol._DEFAULT_MAXSIZE)
        self._fAsText = self.GetBooleanOption("astext", SIMemoryProtocol._DEFAULT_ASTEXT)
        self._fIndent = self.GetBooleanOption("indent", TEXTFILE_INDENT_DEFAULT)
        self._fPattern = self.GetStringOption("pattern", TEXTFILE_PATTERN_DEFAULT)

        # initialize formatter based upon the "astext" option value.
        self._InitializeFormatter()
