# conditional import of the "pywin32" module.  this module utilizes
# the pywin32 module (for Win32 API calls), which is not defined on other systems!
# we only want to include this module if running on Windows.
import platform
if (platform.system().lower() == "windows"):
    import win32file, pywintypes
    from pywintypes import HANDLE

# external package imports.
# none

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIPipeHandle:
    """
    Used to open a named-pipe connection.

    Threadsafety:
        The public members of this class are thread-safe.
    """

    def __init__(self, pipeName:str=None) -> None:
        """ 
        Initializes a new instance of the class with the specified named pipe.

        Args:
            pipeName (str):
                The named pipe to open.
        """
        # initialize instance.
        self._fIsInvalid:bool = True
        self._fHandle = SIPipeHandle.OpenPipe(pipeName)
        self._fHResult:int = 0

        # if we made it here, then the open pipe was successful.
        self._fIsInvalid:bool = False

    @property
    def IsInvalid(self) -> int:
        """ 
        Gets the IsInvalid property value.
        """
        return self._fIsInvalid


    @property
    def HResult(self) -> int:
        """ 
        Gets the HResult property value.
        """
        return self._fHResult


    @property
    def Handle(self) -> object:
        """ 
        Gets the named pipe file Handle.
        """
        return self._fHandle


    @staticmethod
    def OpenPipe(pipeName:str=None) -> object:
        """ 
        Calls win32api to create a named pipe file.

        Args:
            pipeName (str):
                The named pipe to open.

        Raises:
            Exception:
                Thrown if an exception occurs for any reason (pipe not found,
                broken pipe, etc).

        Returns:
            A win32api file handle to the named pipe.            
        """
        # initialize handle in case of exceptions below.
        handle = None

        try:

            # set pipe path to connect to.  
            # this must match what is specified in the SmartInspect Console settings.
            pipePath:str = str.format(r'\\.\pipe\{0}', pipeName)

            # set desired access property.
            dwDesiredAccess:int = win32file.GENERIC_READ | win32file.GENERIC_WRITE

            # open the named pipe file.
            handle = win32file.CreateFile(
                pipePath,                       # filename
                dwDesiredAccess,                # dwDesiredAccess
                0,                              # FileShare.None
                None, 
                win32file.OPEN_EXISTING,        # FileMode.Open
                0,
                None)

            # return win32 handle to caller.
            return handle

        except pywintypes.error as ex:

            # pywintypes.error returns a tuple: (errno, methodname, errmsg)

            # close the handle.
            if (handle != None):
                win32file.CloseHandle(handle)

            # process exception.
            if ex.args[0] == 2:         # pipe not found
                raise Exception(str.format("Could not create named pipe '{0}': ErrNo={1} {2}", pipePath, ex.args[0], ex.args[2]))
            elif ex.args[0] == 109:     # broken pipe
                raise Exception(str.format("Could not create named pipe '{0}': ErrNo={1} {2}", pipePath, ex.args[0], ex.args[2]))
            else:
                raise Exception(str.format("Could not create named pipe '{0}'.  Exception Message: {1}", pipePath, ex.__str__()))
