# external package imports.
from datetime import datetime

# our package imports.
from .silistviewercontext import SIListViewerContext
from .siviewerid import SIViewerId

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIValueListViewerContext(SIListViewerContext):
    """ 
    Represents the value list viewer in the Console which can display data as a key/value list.

    The value list viewer in the Console interprets the Log Entry Data as a simple key/value list.
    Every line in the text data is interpreted as one key/value item of the list. This class 
    takes care of the necessary formatting and escaping required by the corresponding value 
    list viewer of the Console.
    
    You can use the SIValueListViewerContext class for creating custom log methods around 
    SISession.LogCustomContext for sending custom data organized as key/value lists.
    
    Threadsafety:
        This class is not guaranteed to be thread-safe.
    """

    def __init__(self, vi:SIViewerId=None) -> None:
        """
        Initializes a new instance of the class.

        Args:
            vi (SIViewerId):
                The viewer ID to use;  SIViewerId.ValueList will be used if value is null.
        """
        if (vi == None):
            vi = SIViewerId.ValueList

        # initialize base instance.
        super().__init__(vi)

        # initialize instance.
        # nothing to do.


    def _AppendKeyValueString(self, key:str, value:str) -> None:
        """
        Appends a string value and its key.
        
        Args:
            key (str):
                The key to use.
            value (str):
                The string value to use.
        """
        if (key != None):
        
            self.AppendText(self.EscapeItem(key));
            self.AppendText("=");
            if (value != None):
            
                self.AppendText(self.EscapeItem(value))
            
            self.AppendText("\r\n")


    def AppendKeyValue(self, key:str, value:str) -> None:
        """
        Adds an entry to the current row.

        Args:
            key (str):
                The key to use.
            value (str):
                The entry to add; must be able to be converted to a string
                via the "str(x)" syntax.
        """
        # since python does not support overloading, add based upon type checking.
        # I kept the type checking in this code for reference to the C# equivalent code; 
        # we could just use "self._AppendKeyValueString(key, str(value))" to do it as well.
        if isinstance(value, str):
            self._AppendKeyValueString(key, value)
        elif isinstance(value, int):
            self._AppendKeyValueString(key, str(value))
        elif isinstance(value, float):
            self._AppendKeyValueString(key, str(value))
        elif isinstance(value, datetime):
            self._AppendKeyValueString(key, str(value))
        elif isinstance(value, bool):
            self._AppendKeyValueString(key, str(value))
        elif isinstance(value, bytes):
            self._AppendKeyValueString(key, str(value))
        else:
            self._AppendKeyValueString(key, str(value))


    def EscapeItem(self, item:str) -> str:
        """
        Escapes a key or a value.

        Args:
            item (str):
                The key or value to escape.

        Returns:
            The escaped key or value.
        
        This method ensures that the escaped key or value does not
        contain any newline characters, such as the carriage return
        or linefeed characters. Furthermore, it escapes the '\' and
        '=' characters.
        """
        return SIListViewerContext.EscapeLine(item, "\\=")
