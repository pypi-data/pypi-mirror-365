# our package imports.
from .siinspectorviewercontext import SIInspectorViewerContext
from .silistviewercontext import SIListViewerContext
from .siviewerid import SIViewerId

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIMethodParmListContext(SIInspectorViewerContext):
    """ 
    Class that extends the `InspectorViewerContext` class, and is used to build method input 
    parameter lists for display in the trace viewer.

    Threadsafety:
        This class is not guaranteed to be thread-safe.
    """

    def __init__(self, methodName:str) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            methodName (str):
                Name of the method.
        """
        # initialize base instance.
        super().__init__()

        # validations.
        if methodName is None:
            methodName = ''

        # initialize instance.
        self._MethodName = str(methodName)
        self._Title = '"%s" Method Input Parameter List' % methodName

        # start new viewer group context.
        self.StartGroup(self._Title);


    @property
    def Title(self) -> str:
        """ 
        The trace viewer title.
        """
        return self._Title

    @Title.setter
    def Title(self, value:str) -> None:
        """ 
        Sets the _Title property value.
        """
        if value is None:
            value = ''
        self._Title = value


    @property
    def MethodName(self) -> str:
        """ 
        The method name specified on the class constructor.
        """
        return self._MethodName
