# external package imports.
# none

# our package imports.
from .sisourceid import SISourceId
from .sitextcontext import SITextContext

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SISourceViewerContext(SITextContext):
    """ 
    Represents the source viewer in the Console which can display text
    data as source code with syntax highlighting.

    The source viewer in the Console interprets the Log Entry Data
    as source code and displays it in a read-only
    text editor with syntax highlighting.
    
    Threadsafety:
        This class is not guaranteed to be thread-safe.
    """

    def __init__(self, id:SISourceId) -> None:
        """
        Initializes a new instance of the class.

        Args:
            id (SISourceId):
                The source ID to use.
        """

        # initialize base instance.
        super().__init__(id)

        # initialize instance.
        # nothing to do.
