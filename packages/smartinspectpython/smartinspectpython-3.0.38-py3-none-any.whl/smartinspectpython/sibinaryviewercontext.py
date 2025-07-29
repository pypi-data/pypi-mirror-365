# our package imports.
from .sibinarycontext import SIBinaryContext
from .siviewerid import SIViewerId

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIBinaryViewerContext(SIBinaryContext):
    """ 
    Represents the binary viewer in the Console which can display binary
    data in a read-only hex editor.

    The binary viewer in the Console interprets the Log Entry Data
    as binary data and displays it in a read-only hex editor.

    You can use the SIBinaryViewerContext class for creating custom log
    methods around SISession.LogCustomContext(string, SILogEntryType, SIViewerContext)
    for sending custom binary data.
    
    Threadsafety:
        This class is not guaranteed to be thread-safe.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class with a Binary SIViewerId value.
        """

        # initialize base instance.
        super().__init__(SIViewerId.Binary)

        # initialize instance.
        # nothing to do.
