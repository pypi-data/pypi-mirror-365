# our package imports.
from .sitextcontext import SITextContext
from .siviewerid import SIViewerId

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIListViewerContext(SITextContext):
    """ 
    Represents the list viewer in the Console which can display simple lists of text data.

    The list viewer in the Console interprets the Log Entry Data as a list. 
    Every line in the text data is interpreted as one item of the list. 
    This class takes care of the necessary formatting and escaping required 
    by the corresponding list viewer in the Console.

    You can use the SIListViewerContext class for creating custom
    log methods around SISession.LogCustomContext
    for sending custom data organized as simple lists.
    
    Threadsafety:
        This class is not guaranteed to be thread-safe.
    """

    def __init__(self, vi:SIViewerId=None) -> None:
        """
        Initializes a new instance of the class.

        Args:
            vi (SIViewerId):
                The viewer ID to use; if None, then ViewId.List is used.
        """
        if (vi == None):
            vi = SIViewerId.List

        # initialize base instance.
        super().__init__(vi)

        # initialize instance.
        # nothing to do.


    @staticmethod
    def EscapeLine(line:str, toEscape:str=None) -> str:
        """
        Escapes a line.

        Args:
            line (str):
                The line to escape.
            toEscape (str):
                A set of characters which should be escaped in addition
                to the newline characters, or an empty string if there are none.

        Returns:
            The escaped line.

        This method ensures that the escaped line does not
        contain characters listed in the toEscape parameter plus
        any newline characters, such as the carriage return or
        linefeed characters.
        """
        # if line is null or empty then nothing to do.
        if ((line == None) or (len(line) == 0)):
            return line

        if (toEscape == None):
            toEscape = ""

        b:chr = '\u0000'
        result:str = ""
        
        for i in range(len(line)):

            c:chr = line[i]
            if ((c == '\r') or (c == '\n')):

                if ((b != '\r') and (b != '\n')):
                
                    # newline characters need to be removed, as
                    # they would break the list format.
                    result += ' '

            elif (toEscape.find(c) != -1):
                    
                # The current character needs to be escaped as
                # well (with the \ character).
                result += "\\"
                result += c
                    
            else:
            
                # This character is valid, so just append it.
                result += c
            
            b = c

        return result
