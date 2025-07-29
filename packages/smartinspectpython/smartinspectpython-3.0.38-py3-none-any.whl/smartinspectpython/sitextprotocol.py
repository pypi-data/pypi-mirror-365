# external package imports.
from io import BytesIO

# our package imports.
from .siconnectionsbuilder import SIConnectionsBuilder
from .sifileprotocol import SIFileProtocol
from .siformatter import SIFormatter
from .sitextformatter import SITextFormatter

# our package constants.
from .siconst import (
    TEXTFILE_HEADER_BOM,
    TEXTFILE_INDENT_DEFAULT,
    TEXTFILE_PATTERN_DEFAULT
)

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SITextProtocol(SIFileProtocol):
    """
    Used for writing customizable plain text log files.

    This class is used for writing plain text log files. This class is used when 
    the 'text' protocol is specified in the SmartInspect.Connections. 
    
    For a list of available protocol options, please refer to the
    IsValidOption method.

    Threadsafety:
        The public members of this class are thread-safe.
    """
    
    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """

        # initialize instance.
        # note that we have to declare these BEFORE calling the base init, as
        # we are overriding the "Formatter" property and we have to define the
        # the underlying value (e.g. "__fFormatter") first!
        self._fIndent:bool = TEXTFILE_INDENT_DEFAULT
        self._fPattern:str = TEXTFILE_PATTERN_DEFAULT
        self._fFormatter:SIFormatter = None

        # initialize base classinstance.
        super().__init__()


    @property
    def DefaultFileName(self) -> str:
        """
        Returns the default filename for this log file protocol.

        The standard implementation of this method returns the string
        "log.txt" here. Derived classes can change this behavior by
        overriding this method.

        """
        return "log.txt"


    @property
    def Formatter(self) -> SIFormatter:
        """
        Returns the formatter for this log file protocol.

        The standard implementation of this method returns an instance
        of the SIBinaryFormatter class. Derived classes can change this
        behavior by overriding this method.
        """
        if (self._fFormatter == None):
            self._fFormatter = SITextFormatter()

        return self._fFormatter


    @property
    def Name(self) -> str:
        """ 
        Overridden.  Returns "text".
        """
        return "text"


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
        builder.AddOptionBool("indent", self._fIndent)
        builder.AddOptionString("pattern", self._fPattern)


    def IsValidOption(self, name:str) -> bool:
        """
        Overridden. Validates if a protocol option is supported.

        Args:
            name (str):
                The option name to validate.

        Returns:
            True if the option is supported and false otherwise.

        The following table lists all valid options, their default
        values and descriptions for the TEXT protocol.

        Valid Options (default value)              | Description
        ------------------------------------------ | -----------------------------------------------------------------
        indent (false)                             | Indicates if the logging output should automatically be indented like in the Console.
        pattern ("[%timestamp%] %level%: %title%") | Specifies the pattern used to create a text representation of a packet.

        Please note that this protocol DOES NOT support log file encryption.

        For further options which affect the behavior of this protocol, please have a look at the documentation of the
        SIProtocol.IsValidOption method of the parent class.

        <details>
            <summary>Sample Code</summary>
        ``` python
        .. include:: ../docs/include/samplecode/SITextProtocol/IsValidOption.py
        ```
        </details>
        """
        # encryption related options are NOT supported for text logging.
        if ((name == "encrypt") or (name == "key")):
            return False

        return \
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
        self._fPattern = self.GetStringOption("pattern", TEXTFILE_PATTERN_DEFAULT)
        self._fIndent = self.GetBooleanOption("indent", TEXTFILE_INDENT_DEFAULT)
        self.Formatter.Pattern = self._fPattern
        self.Formatter.Indent = self._fIndent


    def WriteFooter(self, stream:BytesIO) -> None:
        """
        Intended to write the footer of a log file.

        Args:
            stream (BytesIO):
                The stream to which the footer should be written to.

        The implementation of this method does nothing. Derived
        class may change this behavior by overriding this method.
        """
        pass


    def WriteHeader(self, stream:BytesIO, size:int) -> int:
        """
        Overridden.  Intended to write the header of a log file.

        Args:
            stream (BytesIO):
                The stream to which the header should be written to.
            size (int):
                Specifies the current size of the supplied stream.
        
        Returns:
            The new size of the stream after writing the header. If no
            header is written, the supplied size argument is returned.

        The implementation of this method writes the standard UTF8
        BOM (byte order mark) to the supplied stream in order to
        identify the log file as text file in UTF8 encoding. Derived
        classes may change this behavior by overriding this method.
        """
        if (size == 0):
            stream.write(TEXTFILE_HEADER_BOM)
            stream.flush()
            return len(TEXTFILE_HEADER_BOM)
        else:
            return size
