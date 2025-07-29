from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from io import BytesIO, BufferedWriter

# our package imports.
from .siargumentnullexception import SIArgumentNullException

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SICryptoStreamWriter(BytesIO):
    """
    Cryptographic stream writer class used to encrypt data and write to a destination
    stream.

    This class utilizes PyCryptodome cryptography support.  More info can be found here:
    https://pycryptodome.readthedocs.io/en/latest/index.html
    """

    def __init__(self, stream:BufferedWriter, cipher, padMethod:str='pkcs7') -> None:
        """
        Initializes a new instance of the class.

        Args:
            stream (BufferedWriter):
                Destination stream (BufferedWriter object) that encrypted data will be written to.
            cipher (object):
                AES Cipher object used to encrypt the data.
            padMethod (str):
                Method used for padding bytes to be encoded; possible values are 'pkcs7' (default), 'iso7816' or 'x923'.

        Raises:
            SIArgumentNullException:
                Thrown if the cipher or stream argument is null.
        """
        # validations.
        if (cipher == None):
            raise SIArgumentNullException("cipher")
        if (stream == None):
            raise SIArgumentNullException("stream")
        if (padMethod == None):
            padMethod = 'pkcs7'

        # init base class, using the cipher block size as the buffer size to allocate.
        super().__init__(bytes(cipher.block_size))

        # initialize instance.
        self._fCipher = cipher                         # cipher object used to encrypt data.
        self._fPadMethod = padMethod                   # padding method for cipher text (e.g. 'pkcs7', etc).
        self._fStream = stream                         # reference to the stream that we will write encrypted data to.
        self._fBufferPos:int = 0                       # the current position of the temporary buffer.
        self._fBuffer:memoryview = self.getbuffer()    # the temporary buffer.


    def flush(self) -> None:
        """
        Overridden.  Calls the same method on the destination stream specified at initialization.
        """
        self._fStream.flush()


    def tell(self) -> int:
        """
        Overridden.  Calls the same method on the destination stream specified at initialization.
        """
        return self._fStream.tell()


    def writable(self) -> bool:
        """
        Overridden.  Calls the same method on the destination stream specified at initialization.
        """
        return self._fStream.writable()


    def write(self, data) -> int:
        """
        Overridden.  Write encrypted data to the destination stream specified at initialization.

        Args:
            data (object):
                Data to write.

        The data to write is encrypted using a block size of the Cipher specified at 
        initialization, and written to the underlying stream.  If there is not enough 
        data to fill a block, then it is written to a temporary buffer to be processed 
        on the next write or close.
        """
        datalen:int = len(data)
        remaining:int = datalen
        dataptr:int = 0
        block_size:int = self._fCipher.block_size

        # process data until there is none left to process.
        while (remaining > 0):

            # are we about to overflow the buffer?
            if (self._fBufferPos > (block_size - 1)):

                # yes - encrypt the buffer contents.
                # note that there is no need to pad bytes, as we have a full block.
                dataPlain = self._fBuffer.tobytes()
                dataEncrypted = self._fCipher.encrypt(dataPlain)
                #dataEncrypted = self._fCipher.encrypt(self._fBuffer.tobytes())

                # write encrypted data to the log file stream.
                encbyteswritten:int = self._fStream.write(dataEncrypted)

                # reset buffer position.
                self._fBufferPos = 0

            else:

                # no - write a byte to the buffer.
                self._fBuffer[self._fBufferPos] = data[dataptr]

                # update pointers for next byte.
                self._fBufferPos = self._fBufferPos + 1
                dataptr = dataptr + 1
                remaining = remaining - 1

        # indicate we processed all bytes supplied.
        return datalen


    def close(self) -> None:
        """
        Overridden.  Calls the same method on the destination stream specified at initialization.

        Prior to closing the destination stream, it will encrypt and write out any remaining 
        bytes in the temporary buffer to the destination stream.
        """
        # if destination stream is not writable then don't bother!
        if (not self._fStream.writable()):
            return

        # anything left in the buffer to write?
        if (self._fBufferPos > 0):

            # yes - get the remaining bytes.
            dataPlain = self._fBuffer.tobytes()[0:self._fBufferPos]

            # do we need to pad data?
            if (self._fBufferPos < AES.block_size):
                dataPlainPadded = pad(dataPlain, AES.block_size, self._fPadMethod)
                dataEncrypted = self._fCipher.encrypt(dataPlainPadded)
            else:
                dataEncrypted = self._fCipher.encrypt(dataPlain)
            #dataEncrypted = self._fCipher.encrypt(pad(self._fBuffer.tobytes(), AES.block_size, self._fPadMethod))

            # write encrypted data to the log file stream.
            encbyteswritten:int = self._fStream.write(dataEncrypted)

            # also force a flush since we are closing the stream!
            self._fStream.flush()

            # reset buffer position.
            self._fBufferPos = 0

        # close the log file stream.
        self._fStream.close()


    # we don't care about implementing the following methods, since this should be
    # a BuffereWriter stream we are inheriting from.

    #@property
    #def name(self) -> str:
    #    """
    #    """
    #    return self._fStream.name


    #def detach(self) -> RawIOBase:
    #    """
    #    """
    #    return self._fStream.detach()


    #def fileno(self) -> int:
    #    """
    #    """
    #    return self._fStream.fileno()


    #def isatty(self) -> bool:
    #    """
    #    """
    #    return self._fStream.isatty()


    #def seek(self, offset:int, whence:int=0) -> int:
    #    """
    #    """
    #    return self._fStream.seek(offset, whence)

    #def readable(self) -> bool:
    #    """
    #    """
    #    return self._fStream.readable()
