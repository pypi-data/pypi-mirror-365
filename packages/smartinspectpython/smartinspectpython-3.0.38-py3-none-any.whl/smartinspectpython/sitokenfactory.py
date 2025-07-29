# external package imports.
# none

# our package imports.
from .sicolor import SIColor
from .silogentry import SILogEntry
from .sitoken import SIToken
from .siutils import static_init

# our package constants.
from .siconst import (
    DEFAULT_COLOR_OBJECT
)

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@static_init    # indicate we have a static init method.
@export
class SITokenFactory:
    """ 
    Creates instances of Token subclasses.

    This class has only one public method called GetToken, which
    is capable of creating Token objects depending on the given
    argument.
    
    Threadsafety:
        This class is not guaranteed to be thread-safe.
    """

    # static properties.
    _fTokenClassNames = {}
    _fTokenClasses = {}

    @classmethod
    def static_init(cls) -> None:
        """ 
        Initializes a new instance of the class.
        """
        # Note - at this point, you cannot call any of the static methods in this class,
        # as we are still in the initilization phase!
  
        tokenName:str = ""

        # register all token types.
        tokenName = "%appname%"
        cls._fTokenClasses[tokenName] = cls._AppNameToken
        cls._fTokenClassNames[tokenName] = cls._AppNameToken.__name__

        tokenName = "%session%"
        cls._fTokenClasses[tokenName] = cls._SessionToken
        cls._fTokenClassNames[tokenName] = cls._SessionToken.__name__

        tokenName = "%hostname%"
        cls._fTokenClasses[tokenName] = cls._HostNameToken
        cls._fTokenClassNames[tokenName] = cls._HostNameToken.__name__

        tokenName = "%title%"
        cls._fTokenClasses[tokenName] = cls._TitleToken
        cls._fTokenClassNames[tokenName] = cls._TitleToken.__name__

        tokenName = "%timestamp%"
        cls._fTokenClasses[tokenName] = cls._TimestampToken
        cls._fTokenClassNames[tokenName] = cls._TimestampToken.__name__

        tokenName = "%level%"
        cls._fTokenClasses[tokenName] = cls._LevelToken
        cls._fTokenClassNames[tokenName] = cls._LevelToken.__name__

        tokenName = "%color%"
        cls._fTokenClasses[tokenName] = cls._ColorToken
        cls._fTokenClassNames[tokenName] = cls._ColorToken.__name__

        tokenName = "%logentrytype%"
        cls._fTokenClasses[tokenName] = cls._LogEntryTypeToken
        cls._fTokenClassNames[tokenName] = cls._LogEntryTypeToken.__name__

        tokenName = "%viewerid%"
        cls._fTokenClasses[tokenName] = cls._ViewerIdToken
        cls._fTokenClassNames[tokenName] = cls._ViewerIdToken.__name__

        tokenName = "%thread%"
        cls._fTokenClasses[tokenName] = cls._ThreadIdToken
        cls._fTokenClassNames[tokenName] = cls._ThreadIdToken.__name__

        tokenName = "%_ProcessIdToken%"
        cls._fTokenClasses[tokenName] = cls._ProcessIdToken
        cls._fTokenClassNames[tokenName] = cls._ProcessIdToken.__name__


    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        pass


    class _AppNameToken(SIToken):
        def Expand(self, logEntry:SILogEntry) -> str:
            return logEntry.AppName

    class _SessionToken(SIToken):
        def Expand(self, logEntry:SILogEntry) -> str:
            return logEntry.SessionName

    class _HostNameToken(SIToken):
        def Expand(self, logEntry:SILogEntry) -> str:
            return logEntry.HostName

    class _TitleToken(SIToken):
        def Expand(self, logEntry:SILogEntry) -> str:
            return logEntry.Title
        @property
        def Indent(self) -> bool:
            return True

    class _LevelToken(SIToken):
        def Expand(self, logEntry:SILogEntry) -> str:
            return str(logEntry.Level.name)

    class _LogEntryTypeToken(SIToken):
        def Expand(self, logEntry:SILogEntry) -> str:
            return str(logEntry.LogEntryType)

    class _ViewerIdToken(SIToken):
        def Expand(self, logEntry:SILogEntry) -> str:
            return str(logEntry.ViewerId)

    class _ThreadIdToken(SIToken):
        def Expand(self, logEntry:SILogEntry) -> str:
            return str(logEntry.ThreadId)

    class _ProcessIdToken(SIToken):
        def Expand(self, logEntry:SILogEntry) -> str:
            return str(logEntry.ProcessId)

    class _LiteralToken(SIToken):
        def Expand(self, logEntry:SILogEntry) -> str:
            return self.Value

    class _TimestampToken(SIToken):
        def Expand(self, logEntry:SILogEntry) -> str:
            if ((self.Options != None) and (len(self.Options) > 0)):
                try:
                    # try to use a custom format string.
                    return logEntry.Timestamp.ToString(self.Options)
                except Exception as ex:
                    pass    # ignore exceptions.
            #return str.format("yyyy-MM-dd HH:mm:ss.fff", logEntry.Timestamp)
            return logEntry.Timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')   # [:-3] <- drop last 3 of milliseconds if desired.

    class _ColorToken(SIToken):
        def Expand(self, logEntry:SILogEntry) -> str:
            if (logEntry.ColorBG != DEFAULT_COLOR_OBJECT):
                return SIColor.ValueHex
            else:
                return "<default>"
    

    @staticmethod
    def _CreateInstance(tokenName:str, tokenType:type) -> SIToken:
        """
        Creates a new class instance of the selected token type.

        Args:
            tokenName (str):
                The token name.
            tokenType (type):
                The token type to search for.

        Returns:
            The token instance created.
        """
        try:

            oInstanceClass = SITokenFactory._fTokenClasses[tokenName]
            oInstanceClassName = SITokenFactory._fTokenClassNames[tokenName]
            oInstanceType = type(oInstanceClassName, (oInstanceClass, object), {})
            oInstance = oInstanceType.__call__()

            return oInstance
         
        finally:

            # exceptions will be handled by calling method.
            pass


    @staticmethod
    def CreateLiteral(value:str) -> SIToken:
        """
        Creates a LiteralToken instance.

        Args:
            value (str):
                The value to assign to the literal token.

        Returns:
            A LiteralToken object with the value assigned.
        """
        token:SIToken = SITokenFactory._LiteralToken()
        token.Options = ""
        token.Value = value
        return token


    @staticmethod
    def GetToken(value:str) -> SIToken:
        """
        Creates instance of Token subclasses.

        Args:
            value (str):
                The original string representation of the token.

        Returns:
            An appropriate Token object for the given string representation of a token.

        This method analyzes and parses the supplied representation of
        a token and creates an appropriate Token object. For example,
        if the value argument is set to "%session%", a Token object
        is created and returned which is responsible for expanding the
        %session% variable. For a list of available tokens and a
        detailed description, please have a look at the SIPatternParser
        class, especially the SIPatternParser.Pattern property.
        """
        if (value == None):
            return SITokenFactory.CreateLiteral("")

        length:int = len(value)
        if (length <= 2):
            return SITokenFactory.CreateLiteral(value)

        # if not a valid token id, then we are done.
        # token id's start and end with a percent sign.
        if ((value[0] != '%') or (value[length - 1] != '%')):
            return SITokenFactory.CreateLiteral(value)

        original:str = value
        options:str = ""

        # Extract the token options: %token{options}%
        # examples:
        #   %timestamp{HH:mm:ss.fff}%
        index:int = 0
        if (value[length - 2] == '}'):
        
            index = value.find('{')

            if (index > -1):
            
                index = index + 1
                options = value[index:length - 2]
                value = value.replace("{" + options + "}","")
                length = len(value)
            
        width:str = ""
        index = value.find(",") # .index(",")

        # Extract the token width: %token,width%
        # examples:
        #   %level,8%
        if (index != -1):
        
            index = index + 1
            width = value[index:length - 1]
            value = value.replace("," + width,"")
            length = len(value)

        value = value.lower()
        tokentype:type = SITokenFactory._fTokenClasses[value]

        if (tokentype == None):
            return SITokenFactory.CreateLiteral(original);

        token:SIToken = None
        try:
        
            # create the token and assign the properties.
            token = SITokenFactory._CreateInstance(value, tokentype)
            if (token != None):
            
                token.Options = options;
                token.Value = original;
                token.Width = SITokenFactory.ParseWidth(width);
        
        except Exception as ex:
        
            return SITokenFactory.CreateLiteral(original)

        return token


    @staticmethod
    def ParseWidth(value:str) -> int:
        """
        Parses the specified value for it's width.

        Args:
            value (str):
                The value to obtain the width of.

        Returns:
            The width of the value.
        """
        if (value == None):
            return 0

        value = value.strip()
        if (len(value) == 0):
            return 0

        width:int = 0

        try:
            width = int(value)
        except Exception as ex:
            width = 0

        return width
