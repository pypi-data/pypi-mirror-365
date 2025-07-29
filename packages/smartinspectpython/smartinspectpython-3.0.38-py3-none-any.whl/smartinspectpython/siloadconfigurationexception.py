# external package imports.
# none

# our package imports.
# none

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SILoadConfigurationException(Exception):
    """
    Used to report errors concerning the SmartInspect.LoadConfiguration method.

    This exception is used to report errors concerning the
    SmartInspect.LoadConfiguration method. This method is able to load
    the SmartInspect properties from a file. Therefore errors can occur
    when trying to load properties from an inexistent file or when the
    file can not be opened for reading, for example.

    If such an error occurs, an instance of this class will be passed
    to the SmartInspect.Error event. Please note, that, if a connections
    string can be read while loading the configuration file, but is
    found to be invalid then this exception type will not be used. In
    this case, the SmartInspect.LoadConfiguration method will use the
    SIInvalidConnectionsException exception instead.

    Threadsafety:
        This class is not guaranteed to be thread-safe.
    """

    def __init__(self, message, fileName:str, *args, **kwargs) -> None:
        """
        Initializes a new instance of the class.

        Args:
            message (Any):
                The exception message.
            fileName (str):
                The filename that contained the configuration settings.
        """

        # initialize base class.
        super().__init__(message, *args, **kwargs)

        # initialize instance.
        self._fFileName:str = fileName
    

    @property
    def FileName(self) -> str:
        """ 
        Gets the FileName property value.

        Name of the file which caused this exception
        while trying to load the SmartInspect properties from it.
        """
        return self._fFileName
