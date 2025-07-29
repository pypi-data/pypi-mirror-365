from io import StringIO

# our package imports.
from .sitextcontext import SITextContext
from .siviewerid import SIViewerId

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIDataViewerContext(SITextContext):
    """ 
    Represents the data viewer in the Console which can display simple
    and unformatted text.

    The data viewer in the Console interprets the Log Entry Data as text
    and displays it in a read-only text field.

    You can use this class for creating custom log methods around 
    SISession.LogCustomContext(string, SILogEntryType, SIViewerContext)
    for sending custom text data.
    
    Threadsafety:
        This class is not guaranteed to be thread-safe.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class with a Data SIViewerId value.
        """

        # initialize base instance.
        super().__init__(SIViewerId.Data)

        # initialize instance.
        # nothing to do.
