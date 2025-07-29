# external package imports.
from io import BytesIO

# our package imports.
from .siviewerid import SIViewerId

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIViewerContext():
    """ 
    Is the abstract base class for a viewer context. A viewer context
    is the library-side representation of a viewer in the Console.

    A viewer context contains a viewer ID and data which can be
    displayed in a viewer in the Console. Every viewer in the Console
    has a corresponding viewer context class in this library. A viewer
    context is capable of processing data and to format it in a way
    so that the corresponding viewer in the Console can display it.

    Viewer contexts provide a simple way to extend the functionality
    of the SmartInspect library. See the SISession.LogCustomContext
    method for a detailed example.

    Threadsafety:
        This class is not guaranteed to be thread-safe.
    """

    def __init__(self, vi:SIViewerId) -> None:
        """
        Initializes a new instance of the class.
        """
        # validations.
        if (vi == None):
            vi = SIViewerId.Data

        # initialize instance.
        self._fVi:SIViewerId = vi


    @property
    def ViewerData(self) -> BytesIO:
        """ 
        Returns the actual data which will be displayed in the
        viewer specified by the viewer id.

        This property must be overridden by inheriting class.
        """
        return None


    @property
    def ViewerId(self) -> SIViewerId:
        """ 
        Returns the viewer ID which specifies the viewer
        to use in the Console.
        """
        return self._fVi
        

    def Dispose(self, disposing:bool) -> None:
        """
        Releases any unmanaged (and optionally) managed resources of this viewer context.

        Args:
            disposing (bool):
                True if managed resources should be released and false otherwise.
        """
        # this method was kept for C# reference.

        # since there is no gargbage collector "GCSuppressFinalize" functionality
        # in Python, there is nothing to do here.
        pass
