# our package imports.
from .silistviewercontext import SIListViewerContext
from .sivaluelistviewercontext import SIValueListViewerContext
from .siviewerid import SIViewerId

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIInspectorViewerContext(SIValueListViewerContext):
    """ 
    Represents the inspector viewer in the Console which displays key/value pairs in 
    an object inspector control.

    The inspector viewer in the Console interprets the Log Entry Data as a key/value list with
    group support like object inspectors from popular IDEs. This class takes care of the necessary 
    formatting and escaping required by the corresponding inspector viewer in the Console.

    You can use the SIInspectorViewerContext class for creating custom log methods around 
    SISession.LogCustomContext for sending custom data organized as grouped key/value pairs.
    
    Threadsafety:
        This class is not guaranteed to be thread-safe.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        # initialize base instance.
        super().__init__(SIViewerId.Inspector)

        # initialize instance.
        # nothing to do.


    def EscapeItem(self, item:str) -> str:
        """
        Overridden. Escapes a key or a value.

        Args:
            item (str):
                The key or value to escape.

        Returns:
            The escaped key or value.

        This method ensures that the escaped key or value does
        not contain any newline characters, such as the carriage
        return or linefeed characters. Furthermore, it escapes
        the '\', '=', '[' and ']' characters.
        """
        return SIListViewerContext.EscapeLine(item, "\\=[]")


    def StartGroup(self, group:str) -> None:
        """
        Starts a new group.

        Args:
            group (str):
                The name of the group to use.
        """
        if (group != None):
          
            self.AppendText("[")
            self.AppendText(self.EscapeItem(group))
            self.AppendText("]\r\n")
