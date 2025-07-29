# conditional import of the "pywin32" module.  this module utilizes
# the pywin32 module (for Win32 API calls), which is not defined on other systems!
# we only want to include this module if running on Windows.
import platform
if (platform.system().lower() == "windows"):
    import win32file, pywintypes

# external package imports.
from io import BytesIO, RawIOBase

# our package imports.
from .siargumentnullexception import SIArgumentNullException
from .smartinspectexception import SmartInspectException

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIPipeStream(BytesIO):
    """
    Stream class used to read from / write to a named pipe via Win32API calls.

    This class utilizes the Windows win32file support from the pywin32 module.
    More information can be found here:
    http://timgolden.me.uk/pywin32-docs/win32file__ReadFile_meth.html
    """

    def __init__(self, pipeHandle:int, initialSize:int=0x2000) -> None:
        """
        Initializes a new instance of the class.

        Args:
            pipeHandle (int):
                Handle to the named pipe that is open for reading / writing.
            initialSize (int):
                The initial size of the buffer to allocate for this stream.

        Raises:
            SIArgumentNullException:
                Thrown if the pipeHandle argument is null or an empty string.
        """
        # validations.
        if ((pipeHandle == None) or (pipeHandle == 0)):
            raise SIArgumentNullException("pipeHandle")

        # init base class, allocating a buffer using the supplied initial size.
        super().__init__(bytes(initialSize))

        # initialize instance.
        self._fPipeHandle:int = pipeHandle


    def flush(self) -> None:
        """
        Overridden.  Force bytes held in the buffer into the raw stream.
        Prior to flushing, buffered data will be written to the named pipe.
        """
        # get stream position (e.g. length of data to write to pipe).
        datalen:int = super().tell()

        data:memoryview = None
        try:

            # get direct access to the stream buffer.
            data:memoryview = self.getbuffer()

            # write data to the pipe; response is a tuple of (return-code, # bytes written).
            retcode, nBytesWritten = win32file.WriteFile(self._fPipeHandle, data[0:datalen])

        except pywintypes.error as ex:

            # pywintypes.error returns a tuple: (errno, methodname, errmsg)

            # destroy the reference to the underlying buffer (memoryview) in case it has to be re-sized.
            if (data != None):
                data = None

            # close the handle.
            if (self._fPipeHandle != None):
                win32file.CloseHandle(self._fPipeHandle)

            # throw new exception indicating an error.
            raise SmartInspectException(str.format("Failed to write data to named pipe.  ErrNo {0}: {1}", ex.args[0], ex.args[2]))

        finally:

            # destroy the reference to the underlying buffer (memoryview) in case it has to be re-sized.
            if (data != None):
                data = None

        # call base class method to keep the buffer in sync.
        super().flush()

        # reposition buffer for next write.
        # note that if we don't do this, the buffer position just keeps rising!
        super().seek(0)


    def tell(self) -> int:
        """
        Overridden.  Calls the same method on the destination stream specified at initialization.
        """
        return super().tell()


    def writable(self) -> bool:
        """
        Overridden.  Calls the same method on the destination stream specified at initialization.
        """
        return super().writable()


    def write(self, data) -> int:
        """
        Overridden.  Writes data to the internal buffer.  

        Args:
            data (Any):
                Bytes of data to write.

        Buffered data will only be written to the named pipe once a "flush()" is called.
        """
        # write data to the underlying stream.  we will read the stream in the "flush()"
        # method to write it to the pipe.
        nBytesWritten:int = super().write(data)

        #print("write.buffer[" + str(nBytesWritten) + "]")  # =" + data[0:datalen].hex())    # TEST TODO DEBUG

        # return number of bytes written.
        return nBytesWritten


    def close(self) -> None:
        """
        Overridden.  Closes the stream, as well as the named pipe.
        """

        # reposition buffer and truncate it to free memory.
        super().seek(0)
        super().truncate(0)

        # close the stream.
        super().close()

        # close the named pipe handle.
        win32file.CloseHandle(self._fPipeHandle)


    def read(self, size:int) -> bytes:
        """
        Overridden.  Read data from the named pipe, and moves it to our buffer.

        Args:
            size (int):
                Number of bytes to read.  This argument is ignored, as ALL available data is 
                read from the named-pipe.

        Raises:
            IOError:
                Thrown if the read failed for any reason.

        Returns:
            A byte array of data read.
        """
        # read from the pipe; response is a tuple of (return-code, data buffer)
        retcode, data = win32file.ReadFile(self._fPipeHandle, 0x2000)

        # if read failed, then raise an exception.
        if (retcode != 0):
            raise IOError(str.format("Failed to read data from named pipe.  ErrNo {0}", retcode))

        # return the read data.
        return data


    def readable(self) -> bool:
        """
        Overridden.  Calls the same method on the destination stream specified at initialization.
        """
        return super().readable()


    @property
    def name(self) -> str:
        """
        Overridden.  Calls the same method on the destination stream specified at initialization.
        """
        return super().name


    def detach(self) -> RawIOBase:
        """
        Overridden.  Calls the same method on the destination stream specified at initialization.
        """
        return super().detach()


    def fileno(self) -> int:
        """
        Overridden.  Calls the same method on the destination stream specified at initialization.
        """
        return super().fileno()


    def isatty(self) -> bool:
        """
        Overridden.  Calls the same method on the destination stream specified at initialization.
        """
        return super().isatty()


    def seek(self, offset:int, whence:int=0) -> int:
        """
        Overridden.  Calls the same method on the destination stream specified at initialization.
        """
        return super().seek(offset, whence)

