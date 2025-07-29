# external package imports.
# none

# our package imports.
from .silogentry import SILogEntry
from .silogentrytype import SILogEntryType
from .sitoken import SIToken
from .sitokenfactory import SITokenFactory

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIPatternParser:
    """
    Capable of parsing and expanding a pattern string as used in the
    SITextProtocol and SITextFormatter classes.

    The SIPatternParser class is capable of creating a text
    representation of a SILogEntry object (see Expand). The string
    representation can be influenced by setting a pattern string.
    Please see the Pattern property for a description.

    Threadsafety:
        This class is not guaranteed to be thread-safe.
    """

    _SPACES:str = "   "
    
    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        self._fPosition:int = 0
        self._fPattern:str = ""
        self._fTokens = []
        self._fIndent:bool = False
        self._fIndentLevel:int = 0
        self._fBuilder = ""


    @property
    def Indent(self) -> bool:
        """ 
        Gets the Indent property value.

        Indicates if the Expand method should automatically intend
        log packets like in the Views of the SmartInspect Console.

        Log Entry packets of type EnterMethod increase the indentation
        and packets of type LeaveMethod decrease it.
        """
        return self._fIndent
    

    @Indent.setter
    def Indent(self, value:bool) -> None:
        """ 
        Sets the Indent property value.
        """
        if value != None:
            self._fIndent = value


    @property
    def Pattern(self) -> str:
        """
        Gets the Pattern property value.

        Represents the pattern string for this SIPatternParser object.

        The pattern string influences the way a text representation of
        a SILogEntry object is created. A pattern string consists of a
        list of so called variable and literal tokens. When a string
        representation of a SILogEntry object is created, the variables
        are replaced with the actual values of the SILogEntry object.

        Variables have a unique name, are surrounded with '%' characters
        and can have an optional options string enclosed in curly
        braces like this: %name{options}%.

        You can also specify the minimum width of a value like this:
        %name,width%. Width must be a valid positive or negative
        integer. If the width is greater than 0, formatted values will
        be right-aligned. If the width is less than 0, they will be
        left-aligned.

        The following table lists the available variables together with
        the corresponding Log Entry property.

        Variable       | Corresponding Property
        -------------- | ------------------------------------------
        %appname%      | LogEntry.AppName
        %color%        | LogEntry.ColorBG
        %hostname%     | LogEntry.HostName
        %level%        | Packet.Level
        %logentrytype% | LogEntry.LogEntryType
        %process%      | LogEntry.ProcessId
        %session%      | LogEntry.SessionName
        %thread%       | LogEntry.ThreadId
        %timestamp%    | LogEntry.Timestamp
        %title%        | LogEntry.Title
        %viewerid%     | LogEntry.ViewerId

        For the time-stamp token, you can use the options string to
        pass a custom date/time format string. This can look as follows:
        %timestamp{HH:mm:ss.fff}%

        The format string must be a valid Python DateTime format
        string. The default format string used by the time-stamp token
        is "yyyy-MM-dd HH:mm:ss.fff".

        Literals are preserved as specified in the pattern string. When
        a specified variable is unknown, it is handled as literal.

        # Examples:
        `"[%timestamp%] %level,8%: %title%"`

        `"[%timestamp%] %session%: %title% (Level: %level%)"`
        """
        return self._fPattern

    @Pattern.setter
    def Pattern(self, value:str) -> None:
        """
        Sets the Pattern property value.
        """
        self._fPosition = 0
        self._fIndentLevel = 0

        if (value != None):
            self._fPattern = value.strip()
        else:
            self._fPattern = ""

        self._Parse()


    def _Next(self) -> SIToken:
        """
        Gets the next token in the list.

        Returns:
            A Token object that represents the next token found, or null 
            if no more tokens to process.
        """
        length:int = len(self._fPattern)

        if (self._fPosition < length):
        
            isVariable:bool = False
            pos:int = self._fPosition

            if (self._fPattern[pos] == '%'):
            
                isVariable = True
                pos = pos + 1

            while (pos < length):
            
                if (self._fPattern[pos] == '%'):
                
                    if (isVariable):

                        pos=pos + 1
                    
                    break
                
                pos = pos + 1
            
            value:str = self._fPattern[self._fPosition: pos]
            self._fPosition = pos

            return SITokenFactory.GetToken(value)
        
        else:
        
            return None
        

    def _Parse(self) -> None:
        """
        Creates a string representation of a variable or literal token.
        """
        self._fTokens.clear()
        token:SIToken = self._Next()
        while (token != None):
        
            self._fTokens.append(token)
            token = self._Next()


    def Expand(self, logEntry:SILogEntry) -> str:
        """
        Creates a text representation of a Log Entry by applying a
        user-specified Pattern string.

        Args:
            logEntry (LogEntry):
                The Log Entry whose text representation should be computed by
                applying the current Pattern string. All recognized variables
                in the pattern string are replaced with the actual values of
                this Log Entry.

        Returns:
            The text representation for the supplied Log Entry object.
        """
        if (len(self._fTokens) == 0):
            return ""

        self._fBuilder = ""
        if (logEntry.LogEntryType == SILogEntryType.LeaveMethod):
            if (self._fIndentLevel > 0):
                self._fIndentLevel = self._fIndentLevel - 1

        for tokenptr in range(len(self._fTokens)):

            token:SIToken = self._fTokens[tokenptr]

            if (self._fIndent and token.Indent):
                for i in range(self._fIndentLevel):
                    self._fBuilder += SIPatternParser._SPACES

            expanded:str = token.Expand(logEntry)
            if (expanded != None):

                if (token.Width < 0):
                    
                    # Left-aligned
                    self._fBuilder += expanded

                    pad:int = -token.Width - len(expanded)

                    for i in range(pad):
                        self._fBuilder += ' '
                    
                elif (token.Width > 0):
                    
                    pad:int = token.Width - len(expanded)

                    for i in range(pad):
                        self._fBuilder += ' '

                    # Right-aligned 
                    self._fBuilder += expanded
                    
                else:
                    
                    self._fBuilder += expanded
                    
        if (logEntry.LogEntryType == SILogEntryType.EnterMethod):
            self._fIndentLevel = self._fIndentLevel + 1

        return self._fBuilder
