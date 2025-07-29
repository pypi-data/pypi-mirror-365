# our package imports.
from .sibinarycontext import SIBinaryContext
from .sigraphicid import SIGraphicId

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIGraphicViewerContext(SIBinaryContext):
    """ 
    Represents the graphic viewer in the Console which can display images.

    The graphic viewer in the Console interprets the Log Entry Data as picture.

    Threadsafety:
        This class is not guaranteed to be thread-safe.
    """

    def __init__(self, id:SIGraphicId) -> None:
        """
        Initializes a new instance of the class.

        Args:
            id (SIGraphicId):
                The graphic ID to use.
        """

        # initialize base instance.
        super().__init__(id)

        # initialize instance.
        # nothing to do.
