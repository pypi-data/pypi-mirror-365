import _threading_local
from Crypto.Hash import MD5
from Crypto.Cipher import AES
from datetime import datetime
from io import BytesIO, BufferedWriter
import os

# our package imports.
from .sibinaryformatter import SIBinaryFormatter
from .siconnectionsbuilder import SIConnectionsBuilder
from .sicryptostreamwriter import SICryptoStreamWriter
from .sifilehelper import SIFileHelper
from .sifilerotate import SIFileRotate
from .sifilerotater import SIFileRotater
from .siformatter import SIFormatter
from .sipacket import SIPacket
from .siprotocol import SIProtocol
from .siprotocolexception import SIProtocolException
from .siutils import DateHelper
from .smartinspectexception import SmartInspectException

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIFileProtocol(SIProtocol):
    """
    The standard SmartInspect protocol for writing log packets to a log file.

    SIFileProtocol is the base class for all protocol classes which
    deal with log files. By default, it uses the binary log file format
    which is compatible to the Console. Derived classes can change this
    behavior. For example, for a simple protocol which is capable of
    creating plain text files, see the SITextProtocol class.

    The file protocol supports a variety of options, such as log
    rotation (by size and date), encryption and I/O buffers. 

    For a list of available protocol options, please refer to the
    IsValidOption method.

    If encryption is true, then a new log file will be created when the
    configuration settings are initially loaded from process start, or
    when the SIConfigurationTimer monitor thread task detects a change
    to the configuration settings file and the configuration is reloaded.
    This differs from un-encrypted logging behavior, which will log to the 
    same log file (within rotation boundaries).

    Threadsafety:
        The public members of this class are thread-safe.
    """
    
    _DEFAULT_BUFFER:int = 0x2000     # 8kb buffer if custom buffering not specified.
    _KEY_SIZE:int = 16               # 16 byte / 128 bit key size for AES encryption
    _BLOCK_SIZE:int = 16             # 16 byte / 128 bit block size for AES encryption

    _SILF:bytearray = SIBinaryFormatter._EncodeStringAscii("SILF")
    """ The SI Log File eye-cactcher identifier of "SILF" in an ASCII encoded bytearray form. """

    _SILE:bytearray = SIBinaryFormatter._EncodeStringAscii("SILE")
    """ The SI Encrypted Log File eye-cactcher identifier of "SILE" in an ASCII encoded bytearray form. """


    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """

        # initialize base classinstance.
        super().__init__()

        # initialize instance.
        self._fStream:BytesIO = BytesIO()
        self._fFormatter:SIFormatter = None
        self._fRotater:SIFileRotater = SIFileRotater()
        self._fRotate:SIFileRotate = SIFileRotate.NoRotate
        self._fIOBuffer:int = 0
        self._fIOBufferCounter:int = 0
        self._fFileName:str = "log.sil"
        self._fFileSize:int = 0
        self._fEncrypt:bool = False
        self._fKey = []
        self._fAppend: bool = False
        self._fMaxSize:int = 0
        self._fMaxParts:int = 5
        self._fLock:object = _threading_local.RLock()

        # set default options.
        self.LoadOptions()


    @property
    def DefaultFileName(self) -> str:
        """
        Gets the DefaultFileName property value.

        Returns the default filename for this log file protocol.

        The standard implementation of this method returns the string
        "log.sil" here. Derived classes can change this behavior by
        overriding this property method.
        """
        return "log.sil"


    @property
    def Formatter(self) -> SIFormatter:
        """
        Gets the Formatter property value.

        Returns the formatter for this log file protocol.

        The standard implementation of this method returns an instance
        of the SIBinaryFormatter class. Derived classes can change this
        behavior by overriding this property method.
        """
        if (self._fFormatter == None):
            self._fFormatter = SIBinaryFormatter()

        return self._fFormatter


    @property
    def Name(self) -> str:
        """ 
        Overridden.  Returns "file".
        """
        return "file"


    def _GetCipher(self, stream:BytesIO) -> BytesIO:
        """
        Creates a new encrypted stream from the stream argument, and returns it to the caller.

        Args:
            stream (BytesIO):
                Existing stream that will be encrypted.

        Returns:
            A new encrypted stream.
        """
        # get MD5 initialization vector for AES cryptographic functions.
        iv = SIFileProtocol.GetIVector()

        # add the encryption header ("SILE" eye-catcher + AES initialization vector).
        # note that the data that FOLLOWS the header will be encrypted, but the header itself is not encrypted.
        stream.write(SIFileProtocol._SILE)
        stream.write(iv)
        stream.flush()

        # create the AES cipher using Ciphertext Block Chaining (CBC) mode.
        AES.block_size = SIFileProtocol._BLOCK_SIZE
        cipher = AES.new(self._fKey, AES.MODE_CBC, iv)

        # wrap the passed stream.
        return SICryptoStreamWriter(stream, cipher, 'pkcs7')


    def _InternalAfterConnect(self, fileName:str) -> None:
        """
        Deletes any rotating log files that have exceeded the "MaxParts" value.

        Executed after a connection to the protocol has been established.

        Args:
            filename (str):
                Log file base path to process.
        """
        if (not self._IsRotating()):
            return  # Nothing to do

        if (self._fRotate != SIFileRotate.NoRotate):
        
            # We need to initialize our SIFileRotater object with
            # the creation time of the opened log file in order
            # to be able to correctly rotate the log by date in
            # InternalWritePacket. */

            fileDate:datetime = SIFileHelper.GetFileDate(self._fFileName, fileName)

            self._fRotater.Initialize(fileDate)

        if (self._fMaxParts == 0):  # Unlimited log files
            return

        # ensure that we have at most 'maxParts' files.
        SIFileHelper.DeleteFiles(self._fFileName, self._fMaxParts)


    def _InternalBeforeConnect(self) -> None:
        """
        Validates encryption key before connecting.

        Raises:
            SIProtocolException:
                Thrown if there is no encryption key, or if the key is an invalid size.
        """
        # Validate encryption key before connecting.
        if (self._fEncrypt):
        
            if (len(self._fKey) == 0):

                self.ThrowException("No encryption key!");

            else:

                if (len(self._fKey) != SIFileProtocol._KEY_SIZE):

                    self.ThrowException("Invalid encryption key size!");


    def _InternalDoConnect(self, append:bool) -> None:
        """
        Opens the log file for writing.

        Args:
            append (bool):
                Specifies if new packets should be appended to the destination file
                instead of overwriting the file first.
            
        Raises:
            SIProtocolException:
                Thrown if there is no encryption key, or if the key is an invalid size.
        """
        # make the following thread-safe, so we don't create multiple log files.
        # note - if encryption is true, then a new log file will be created when the
        # configuration settings are loaded (or reloaded).  this differs from un-encrypted 
        # logging behavior, which will log to the same file name.
        with (self._fLock):

            # validate encryption keys (if used).
            self._InternalBeforeConnect()

            # replace filename parameters.
            self._fFileName = self._fFileName.replace("%appname%", self.AppName)
            self._fFileName = self._fFileName.replace("%machinename%", self.HostName)

            # create destination directory if necessary (e.g. "C:\\logs").
            dirName:str = os.path.dirname(self._fFileName)
            if (dirName is not None) and (len(dirName) > 0):
                if (not os.path.isdir(dirName)):
                    os.makedirs(dirName, exist_ok=True)

            # get the log file name.
            # if it's a rotating log, then the filename will have a timestamp in it (e.g. "C:\\logs\\logfile-hourly-2023-05-22-12-00-00.txt").
            # if it's NOT a rotating log, then just use the specified property value.
            fileName:str = ""
            if (self._IsRotating()):
                fileName = SIFileHelper.GetFileName(self._fFileName, append)
            else:
                fileName = self._fFileName

            # set flags used to open file.
            fileFlags:str = 'wb'    # write binary
            if (append):
                fileFlags = 'ab'    # append binary

            try:

                # open the log file.
                self._fStream = open(fileName, fileFlags)

            except Exception as ex:

                raise SmartInspectException(str.format("Could not open log file.  Ensure it is a valid file name, and that it is not open in another application.  Log file path: \"{0}\"", fileName))

            # get the current file size (will be zero if not rotating).
            self._fFileSize = self._fStream.tell()

            # if encryption was selected, then creates a new encrypted stream
            # from the existing non-encrypted stream.
            if (self._fEncrypt):
                self._fStream = self._GetCipher(self._fStream)

            # get the stream reference and write the file header.
            # the file header informs the console that this is a SI Console file.
            self._fStream = self.GetStream(self._fStream)
            self._fFileSize = self.WriteHeader(self._fStream, self._fFileSize)

            # was a custom buffer size selected?
            # if so, then allocate the buffer and reset the buffer counter.
            # if not, then just allocate a single buffer of 8192 bytes.
            if (self._fIOBuffer > 0):
        
                self._fStream = BufferedWriter(self._fStream, self._fIOBuffer)
                self._fIOBufferCounter = 0     # reset buffer counter
        
            else:
        
                self._fStream = BufferedWriter(self._fStream, SIFileProtocol._DEFAULT_BUFFER)
                pass

            self._InternalAfterConnect(fileName)


    def _IsRotating(self) -> None:
        """
        Indicates if a rotating file was specified (True) or not (False).

        Returns:
            True if a rotating file was specified; otherwise, false.
        """
        return (self._fRotate != SIFileRotate.NoRotate) or (self._fMaxSize > 0)


    def _Rotate(self) -> None:
        """
        """
        self.InternalDisconnect()
        self._InternalDoConnect(False)   # always create a new file


    def BuildOptions(self, builder:SIConnectionsBuilder) -> None:
        """
        Overridden. Fills a SIConnectionsBuilder instance with the
        options currently used by this protocol.

        Args:
            builder (SIConnectionsBuilder):
                The SIConnectionsBuilder object to fill with the current options
                of this protocol.
        """
        # build base class options.
        super().BuildOptions(builder)

        # build options specific to our class.
        builder.AddOptionBool("append", self._fAppend)
        builder.AddOptionInteger("buffer", self._fIOBuffer / 1024)
        builder.AddOptionString("filename", self._fFileName)
        builder.AddOptionInteger("maxsize", self._fMaxSize / 1024)
        builder.AddOptionInteger("maxparts", self._fMaxParts)
        builder.AddOptionFileRotate("rotate", self._fRotate)

        # do not add encryption options for security.


    @staticmethod
    def GetIVector() -> bytes:
        """
        Returns a new MD5 hashed initialization vector for AES cryptographic functions.
        The vector is based on a current datetime ticks value.

        Returns:
            A new MD5 hashed initialization vector of 16 bytes (128-bits).</returns>
        """
        ticks:int = DateHelper.Ticks(datetime.now())
        resultHash = MD5.new()
        resultHash.block_size = SIFileProtocol._BLOCK_SIZE
        resultHash.update(SIBinaryFormatter._EncodeString(str(ticks)))
        return resultHash.digest()


    def GetStream(self, stream:BytesIO) -> None:
        """
        Intended to provide a wrapper stream for the underlying file stream.

        Args:
            stream (BytesIO):
                The underlying file stream.

        Returns:
            The wrapper stream.

        This method can be used by custom protocol implementers
        to wrap the underlying file stream into a filter stream.
        Such filter streams include
        System.Security.Cryptography.CryptoStream for encrypting
        or System.IO.Compression.DeflateStream for compressing log
        files, for example.

        By default, this method simply returns the passed stream argument.
        """
        return stream


    def InternalConnect(self) -> None:
        """
        Overridden. Opens the destination file.
        
        Raises:
            Exception:
                Opening the destination file failed.

        This method tries to open the destination file, which can
        be specified by passing the "filename" option to the Initialize
        method. For other valid options which might affect the
        behavior of this method, please see the IsValidOption method.
        """
        self._InternalDoConnect(self._fAppend);


    def InternalDisconnect(self) -> None:
        """
        Overridden. Closes the destination file.

        Raises:
            Exception:
                Closing the destination file failed.

        This method closes the underlying file handle if previously
        created and disposes any supplemental objects.
        """
        if (self._fStream.writable or self._fStream.readable):
        
            self.WriteFooter(self._fStream)
            self._fStream.close()
            #self._fStream.Dispose()


    def InternalWritePacket(self, packet:SIPacket) -> None:
        """
        Overridden. Writes a packet to the destination file.

        Args:
            packet (SIPacket):
                The packet to write.

        Raises:
            Exception:
                Writing the packet to the destination file failed.

        If the "maxsize" option is set and the supplied packet would
        exceed the maximum size of the destination file, then the 
        current log file is closed and a new file is opened.
        Additionally, if the "rotate" option is active, the log file
        is rotated if necessary. Please see the documentation of the
        IsValidOption method for more information.
        """
        formatter:SIFormatter = self.Formatter
        packetSize:int = formatter.Compile(packet)

        # if we are rotating logs and the rotation state has changed,
        # then call the Rotate method to open a new log file rotation.
        if (self._fRotate != SIFileRotate.NoRotate):
            if (self._fRotater.Update(datetime.utcnow())):
                self._Rotate()

        if (self._fMaxSize > 0):
        
            self._fFileSize += packetSize;
            if (self._fFileSize > self._fMaxSize):
            
                self._Rotate()

                if (packetSize > self._fMaxSize):
                    return

                self._fFileSize += packetSize

        formatter.Write(self._fStream)

        if (self._fIOBuffer > 0):
        
            self._fIOBufferCounter = self._fIOBufferCounter + packetSize
            if (self._fIOBufferCounter > self._fIOBuffer):
            
                self._fIOBufferCounter = 0
                self._fStream.flush()
        else:
        
            self._fStream.flush()
        

    def IsValidOption(self, name:str) -> bool:
        """
        Overridden. Validates if a protocol option is supported.

        Args:
            name (str):
                The option name to validate.

        Returns:
            True if the option is supported and false otherwise.

        The following table lists all valid options, their default
        values and descriptions for the FILE protocol.
        
        |Valid Options (default value)  | Description
        |-----------------------------  | -------------------------------------------------
        |append (false)                 | Specifies if new packets should be appended to the destination file instead of overwriting the file first.
        |buffer (0)                     | Specifies the I/O buffer size in kilobytes. It is possible to specify size units like this: "1 MB". Supported units are "KB", "MB" and "GB". A value of 0 disables this feature. Enabling the I/O buffering greatly improves the logging performance but has the disadvantage that log packets are temporarily stored in memory and are not immediately written to disk.
        |encrypt (false)                | Specifies if the resulting log file should be encrypted. Note that the 'append' option cannot be used with encryption enabled. If encryption is enabled the 'append' option has no effect.
        |filename ([varies])            | Specifies the filename of the log.
        |key ([empty])                  | Specifies the secret encryption key as string if the 'encrypt' option is enabled.
        |maxparts ([varies])            | Specifies the maximum amount of log files at any given time when log rotating is enabled or the maxsize option is set. Specify 0 for no limit. See below for information on the default value for this option.
        |maxsize (0)                    | Specifies the maximum size of a log file in kilobytes. When this size is reached, the current log file is closed and a new file is opened. The maximum amount of log files can be set with the maxparts option. It is possible to specify size units like this: "1 MB". Supported units are "KB", "MB" and "GB".  A value of 0 disables this feature.
        |rotate (none)                  | Specifies the rotate mode for log files. Please see below for a list of available values. A value of "none" disables this feature. The maximum amount of log files can be set with the maxparts option.  See the SIFileRotate enum for more info.

        When using the standard binary log file protocol ("file" in the SmartInspect.Connections, the default
        filename is set to "log.sil". When using text log files ("text" in the SmartInspect.Connections), the
        default filename is "log.txt".

        The append option specifies if new packets should be appended to the destination file instead of 
        overwriting the file. The default value of this option is "false". 

        The rotate option specifies the date log rotate mode for this file protocol. When this option is used, 
        the filename of the resulting log consists of the value of the filename option and
        an appended time stamp (the used time stamp format thereby is "yyyy-MM-dd-HH-mm-ss"). To avoid problems 
        with daylight saving time or time zone changes, the time stamp is always in UTC (Coordinated Universal Time). 
        The following table lists the available rotate modes together with a short description.

        As example, if you specify "log.sil" as value for the filename option and use the Daily rotate mode, the log file is rotated
        daily and always has a name of log-yyyy-MM-dd-HH-mm-ss.sil. In addition to, or instead of, rotating log files by date, you
        can also let the file protocol rotate log files by size. To enable this feature, set the maxsize option to the desired
        maximum size. Similar to rotating by date, the resulting log files include a time stamp. Note that starting with
        SmartInspect 3.0, it is supported to combine the maxsize and rotate options (i.e. use both options at the same time).

        To control the maximum amount of created log files for the rotate and/or maxsize options, you can use the maxparts option.
        The default value for maxparts is 2 when used with the maxsize option, 0 when used with rotate and 0 when both options,
        maxsize and rotate, are used.

        SmartInspect log files can be automatically encrypted by enabling the 'encrypt' option. The used cipher is Rijndael
        (AES) with a key size of 128 bit. The secret encryption key can be specified with the 'key' option. The specified
        key is automatically shortened or padded (with zeros) to a key size of 128 bit. Note that the 'append' option cannot be
        used in combination with encryption enabled. If encryption is enabled the 'append' option has no effect.

        For further options which affect the behavior of this protocol, please have a look at the documentation of the
        SIProtocol.IsValidOption method of the parent class.

        <details>
            <summary>Sample Code</summary>
        ``` python
        .. include:: ../docs/include/samplecode/SIFileProtocol/IsValidOption.py
        ```
        </details>
        """
        return \
            (name == "append") or \
            (name == "buffer") or \
            (name == "encrypt") or \
            (name == "filename") or \
            (name == "key") or \
            (name == "maxsize") or \
            (name == "maxparts") or \
            (name == "rotate") or \
            (super().IsValidOption(name))


    def LoadOptions(self) -> None:
        """
        Overridden. Loads and inspects specific options for this protocol.

        This method loads all relevant options and ensures their
        correctness. See IsValidOption for a list of options which
        are recognized by the protocol.
        """
        # load base class options.
        super().LoadOptions()

        # load options specific to our class.
        self._fFileName = self.GetStringOption("filename", self.DefaultFileName)
        self._fAppend = self.GetBooleanOption("append", False)
        self._fIOBuffer = self.GetSizeOption("buffer", 0)
        self._fRotate = self.GetRotateOption("rotate", SIFileRotate.NoRotate)
        self._fMaxSize = self.GetSizeOption("maxsize", 0)

        if ((self._fMaxSize > 0) and (self._fRotate == SIFileRotate.NoRotate)):
        
            # Backwards compatibility
            self._fMaxParts = self.GetIntegerOption("maxparts", 2)

        else:
        
            self._fMaxParts = self.GetIntegerOption("maxparts", 0)
        
        defValue:bytearray = bytes(0)
        key:bytearray = self.GetBytesOption("key", SIFileProtocol._KEY_SIZE, defValue)
        self._fEncrypt = self.GetBooleanOption("encrypt", False)
        if ((key != None) and (len(key) > 0)):
            self._fKey = key

        # append mode cannot be used with encryption!  if they are
        # both true, then force no appending mode.
        if (self._fEncrypt):
            self._fAppend = False  # Not applicable

        self._fRotater.Mode = self._fRotate


    def ThrowException(self, message:str) -> None:
        """
        Raises a new SIProtocolException exception

        Raises:
            SIProtocolException:
                Thrown when this method is called.
        """
        raise SIProtocolException(message)


    def WriteFooter(self, stream:BytesIO) -> None:
        """
        Intended to write the footer of a log file.

        Args:
            stream (BytesIO):
                The stream to which the footer should be written to.

        The implementation of this method does nothing. Derived
        class may change this behavior by overriding this method.
        """
        pass


    def WriteHeader(self, stream:BytesIO, size:int) -> int:
        """
        Intended to write the header of a log file.

        Args:
            stream (BytesIO):
                The stream to which the header should be written to.
            size (int):
                Specifies the current size of the supplied stream.
        
        Returns:
            The new size of the stream after writing the header. If no
            header is written, the supplied size argument is returned.

        This default implementation of this method writes the standard
        binary protocol header to the supplied Stream instance.
        Derived classes may change this behavior by overriding this method.
        """
        if (size == 0):
            stream.write(SIFileProtocol._SILF)
            stream.flush()
            return len(SIFileProtocol._SILF)
        else:
            return size
