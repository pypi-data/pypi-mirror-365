# external package imports.
# none

# our package imports.
from .silogentry import SILogEntry

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIToken:
    """ 
    Represents a token in the pattern string of the SITextProtocol protocol.

    This is the abstract base class for all available tokens. Derived
    classes are not documented for clarity reasons. To create a
    suitable token object for a given token string, you can use the
    SITokenFactory class.
    
    Threadsafety:
        This class is not guaranteed to be thread-safe.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        # initialize instance.
        self._fValue:str = None
        self._fOptions:str = None
        self._fWidth:int = 0


    @property
    def Indent(self) -> bool:
        """ 
        Gets the Indent property value.

        Indicates if this token supports indenting.

        This property always returns false unless this token represents
        the title token of a pattern string. This property is used
        by the SIPatternParser.Expand method to determine if a token
        allows indenting.
        """
        return False


    @property
    def Options(self) -> str:
        """ 
        Gets the Options property value.

        Represents the optional options string for this token.

        A variable token can have an optional options string. In the
        raw string representation of a token, an options string can be
        specified in curly braces after the variable name like this:
        %name{options}%. For a literal, this property is always set to
        an empty string. 
        """
        return self._fOptions

    @Options.setter
    def Options(self, value:str) -> None:
        """ 
        Sets the Options property value.
        """
        self._fOptions = value


    @property
    def Value(self) -> str:
        """ 
        Gets the Value property value.

        Represents the raw string value of the parsed pattern string for this token.

        This property represents the raw string of this token as found
        in the parsed pattern string. For a variable, this property is
        set to the variable name surrounded with '%' characters and an
        optional options string like this: %name{options}%. For a
        literal, this property can have any value.
        """
        return self._fValue

    @Value.setter
    def Value(self, value:str) -> None:
        """ 
        Sets the Value property value.
        """
        self._fValue = value


    @property
    def Width(self) -> int:
        """ 
        Gets the Width property value.

        Represents the minimum width of this token.

        A variable token can have an optional width modifier. In the
        raw string representation of a token, a width modifier can be
        specified after the variable name like this: %name,width%.
        Width must be a valid positive or negative integer.

        If the width is greater than 0, formatted values will be
        right-aligned. If the width is less than 0, they will be
        left-aligned.

        For a literal, this property is always set to 0. 
        """
        return self._fWidth

    @Width.setter
    def Width(self, value:int) -> None:
        """ 
        Sets the Width property value.
        """
        self._fWidth = value


    def Expand(self, logEntry:SILogEntry) -> str:
        """
        Creates a string representation of a variable or literal token.

        Args:
            logEntry (SILogEntry):
                The Log Entry to use to create the string representation.

        Returns:
            The text representation of this token for the supplied Log Entry object.

        With the help of the supplied Log Entry, this token is expanded into a string. 
        For example, if this token represents the %session% variable of a pattern string, 
        this Expand method simply returns the session name of the supplied Log Entry.
        
        For a literal token, the supplied Log Entry argument is ignored
        and the Value property is returned.
        """
        raise NotImplementedError()


    def __str__(self) -> str:
        """
        Returns a string representation of the objeect.
        """
        rslt:str = "Token Value=\"{0}\", Width={1}, Options=\"{2}\"".format(self._fValue, str(self._fWidth), self._fOptions)
        return rslt
