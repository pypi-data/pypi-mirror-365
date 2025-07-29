# external package imports.
from datetime import datetime

# our package imports.
from .silistviewercontext import SIListViewerContext
from .siviewerid import SIViewerId

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SITableViewerContext(SIListViewerContext):
    """ 
    Represents the table viewer in the Console which can display text data as a table.

    The table viewer in the Console interprets the Log Entry Data as a table. This class
    takes care of the necessary formatting and escaping required by the corresponding 
    table viewer in the Console.

    You can use the SITableViewerContext class for creating custom log methods around 
    SISession.LogCustomContext for sending custom data organized as tables.
    
    Threadsafety:
        This class is not guaranteed to be thread-safe.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        # initialize base instance.
        super().__init__(SIViewerId.Table)

        # initialize instance.
        self._fLineStart:bool = True


    def _AddRowEntryString(self, entry:str) -> None:
        """
        Adds a string entry to the current row.

        Args:
            entry (str):
                The string entry to add.
        """
        if (entry != None):
        
            if (self._fLineStart):
                self._fLineStart = False
            else:
                self.AppendText(", ")
            
            escentry:str = SITableViewerContext.EscapeCSVEntry(entry)
            if (escentry != None):
                self.AppendText(escentry)


    def AddRowEntry(self, entry) -> None:
        """
        Adds an entry to the current row.

        Args:
            entry (object):
                The entry to add; must be able to be converted to a string
                via the "str(x)" syntax.
        """
        # since python does not support overloading, add based upon type checking.
        # I kept the type checking in this code for reference to the C# equivalent code; 
        # we could just use "self._AddRowEntryString(str(entry))" to do it as well.
        if isinstance(entry, str):
            self._AddRowEntryString(entry)
        elif isinstance(entry, int):
            self._AddRowEntryString(str(entry))
        elif isinstance(entry, float):
            self._AddRowEntryString(str(entry))
        elif isinstance(entry, datetime):
            self._AddRowEntryString(str(entry))
        elif isinstance(entry, bool):
            self._AddRowEntryString(str(entry))
        elif isinstance(entry, chr):
            self._AddRowEntryString(str(entry))
        elif isinstance(entry, bytes):
            self._AddRowEntryString(str(entry))
        else:
            self._AddRowEntryString(str(entry))


    def AppendHeader(self, header:str) -> None:
        """
        Appends a header to the text data.

        Args:
             (str):
                The header to append.
        """
        self.AppendLine(header)
        self.AppendLine("")


    def BeginRow(self) -> None:
        """
        Begins a new row.
        """
        self._fLineStart = True


    def EndRow(self) -> None:
        """
        Ends the current row.
        """
        self.AppendLine("");


    @staticmethod
    def EscapeCSVEntry(entry:str) -> str:
        """
        Escapes a CSV (comma separated values) formatted entry.

        Args:
            entry (str):
                The CSV entry to escape.

        Returns:
            The escaped line.

        This method ensures that the escaped CSV entry does not
        contain whitespace characters, and that quoted values are
        escaped properly.
        """
        if ((entry == None) or (len(entry) == 0)):
            return entry

        sb:str = ""
        sb += "\""

        for i in range(len(entry)):

            c:chr = entry[i]

            if (c.isspace()):
            
                # whitespace characters need to be escaped,
                # they would break the table format.
                sb += " "
            
            elif (c == '"'):
            
                # '"' characters are used to surround entries
                # in the csv format, so they need to be escaped.
                sb += "\"\""
            
            else:
            
                # this character is valid, so just append it.
                sb += c
            
        sb += "\""
        return sb
