# system imports.
from datetime import datetime
from io import BytesIO
import struct

# our package imports.
from .sicolor import SIColor
from .sicontrolcommand import SIControlCommand
from .siformatter import SIFormatter
from .silogentry import SILogEntry
from .silogheader import SILogHeader
from .sipacket import SIPacket
from .sipackettype import SIPacketType
from .siprocessflow import SIProcessFlow
from .siwatch import SIWatch

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIBinaryFormatter(SIFormatter):
    """
    Responsible for formatting and writing a packet in the standard
    SmartInspect binary format.

    This class formats and writes a packet in the standard binary
    format which can be read by the SmartInspect Console. The
    Compile method preprocesses a packet and computes the required
    size of the packet. The Write method writes the preprocessed
    packet to the supplied stream.

    Threadsafety:
        This class is not guaranteed to be thread-safe.
    """

    MAX_STREAM_CAPACITY:int = 10 * 1024 * 1024
    MAX_BUFFER_SIZE:int = 8192

    TICKS_EPOCH:int = 621355968000000000   # number of seconds since 01/01/1970 (epoch date)
    MICROSECONDS_PER_DAY:int = 86400000000 # number of microseconds in 1 day
    DAY_OFFSET_DELPHI_DEFAULT:int = 25569  # number of days between 01/01/1970 (epoch date) and 12/30/1899 (Delphi default date)

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """

        # initialize instance.
        self._fSize:int = 0
        self._fBuffer:BytesIO = BytesIO(bytes(SIBinaryFormatter.MAX_BUFFER_SIZE))
        self._fStream:BytesIO = BytesIO()
        self._fPacket:SIPacket = None


    def _CompileControlCommand(self) -> None:
        """
        Compiles a ControlCommand packet, writing the packet's data to the data stream.
        """

        controlCommand:SIControlCommand = self._fPacket

        self._WriteInt(controlCommand.ControlCommandType.value)
        self._WriteStreamLength(controlCommand.Data)

        if controlCommand.HasData:
            self._CopyStream(self._fStream, controlCommand.Data, controlCommand.DataLength)


    def _CompileLogEntry(self) -> None:
        """
        Compiles a Log Entry packet, writing the packet's data to the data stream.
        """

        logEntry:SILogEntry = self._fPacket

        appName:bytes = SIBinaryFormatter._EncodeString(logEntry.AppName)
        sessionName:bytes = SIBinaryFormatter._EncodeString(logEntry.SessionName)
        title:bytes = SIBinaryFormatter._EncodeString(logEntry.Title)
        hostName:bytes = SIBinaryFormatter._EncodeString(logEntry.HostName)

        self._WriteInt(logEntry.LogEntryType.value)
        self._WriteInt(logEntry.ViewerId.value)
        self._WriteDataLength(appName)
        self._WriteDataLength(sessionName)
        self._WriteDataLength(title)
        self._WriteDataLength(hostName)
        self._WriteStreamLength(logEntry.Data)
        self._WriteUInt(logEntry.ProcessId)
        self._WriteUInt(logEntry.ThreadId)
        self._WriteTimestamp(logEntry.Timestamp)
        self._WriteColor(logEntry.ColorBG)
        self._WriteData(appName)
        self._WriteData(sessionName)
        self._WriteData(title)
        self._WriteData(hostName)

        if logEntry.HasData:
            self._CopyStream(self._fStream, logEntry.Data, logEntry.DataLength)


    def _CompileLogHeader(self) -> None:
        """
        Compiles a LogHeader packet, writing the packet's data to the data stream.
        """

        logHeader:SILogHeader = self._fPacket

        content = SIBinaryFormatter._EncodeString(logHeader.Content)
        self._WriteDataLength(content)
        self._WriteData(content)


    def _CompileProcessFlow(self) -> None:
        """
        Compiles a Process Flow packet, writing the packet's data to the data stream.
        """

        processFlow:SIProcessFlow = self._fPacket

        title:bytes = SIBinaryFormatter._EncodeString(processFlow.Title)
        hostname:bytes = SIBinaryFormatter._EncodeString(processFlow.HostName)

        self._WriteInt(processFlow.ProcessFlowType.value)
        self._WriteDataLength(title)
        self._WriteDataLength(hostname)
        self._WriteInt(processFlow.ProcessId)
        self._WriteInt(processFlow.ThreadId)
        self._WriteTimestamp(processFlow.Timestamp)
        self._WriteData(title)
        self._WriteData(hostname)


    def _CompileWatch(self) -> None:
        """
        Compiles a Watch packet, writing the packet's data to the data stream.
        """

        watch:SIWatch = self._fPacket

        name:bytes = SIBinaryFormatter._EncodeString(watch.Name)
        value:bytes = SIBinaryFormatter._EncodeString(watch.Value)

        self._WriteDataLength(name)
        self._WriteDataLength(value)
        self._WriteInt(watch.WatchType.value)
        self._WriteTimestamp(watch.Timestamp)
        self._WriteData(name)
        self._WriteData(value)


    def _CopyStream(self, toStream, fromStream, count) -> None:
        """
        Copies bytes from one stream to another.
        """
        # reset from stream position to zero
        fromStreamPos:int = fromStream.tell()
        fromStream.seek(0)

        while (count > 0):

            toRead:int = 0

            # set # of bytes to copy - limit max to size of our buffer.
            if (count > SIBinaryFormatter.MAX_BUFFER_SIZE):
                toRead = SIBinaryFormatter.MAX_BUFFER_SIZE
            else:
                toRead = count

            # copy bytes from the FROM stream to our temporary buffer.
            self._fBuffer = fromStream.read(toRead)

            # copy bytes from temporary buffer to the TO stream.
            if (toRead > 0):
                bytesWritten:int = toStream.write(self._fBuffer)
                count = count - toRead
            else:
                break


    @staticmethod
    def _EncodeString(value:str) -> bytes:
        """
        Encodes a string with UTF-8 encoding, returning a byte array.
        """
        if (value != None):
            return value.encode('utf-8')
        else:
            return None


    @staticmethod
    def _EncodeStringAscii(value:str) -> bytes:
        """
        Encodes a string with ASCII encoding, returning a byte array.
        """
        if (value != None):
            return value.encode('ascii')
        else:
            return None


    def _ResetStream(self) -> None:

        if self._fSize > SIBinaryFormatter.MAX_STREAM_CAPACITY:
            # Reset the stream capacity if the previous packet
            # was very big. This ensures that the amount of memory
            # can shrink again after a big packet has been sent.
            self._fStream.truncate(0)
        else:
            # Only reset the position. This should ensure better
            # performance since no reallocations are necessary.
            self._fStream.seek(0)


    def _WriteColor(self, value:SIColor) -> None:
        """
        Store color as Delphi Integer (32bit signed, little endian).
        """
        colorValue:int = value.R | value.G << 8 | value.B << 16 | value.A << 24
        self._WriteInt(colorValue)


    def _WriteData(self, value:bytes) -> None:
        """
        Store byte array.
        """
        if (value != None):
            self._fStream.write(value)


    def _WriteDataLength(self, value:bytes) -> None:
        """
        Store length of byte array as Delphi Integer (32bit signed, little endian).
        """
        if (value != None):
            self._WriteInt(len(value))
        else:
            self._WriteInt(0)


    def _WriteDouble(self, value:float) -> None:
        """
        Store as Delphi Integer (64bit unsigned, little endian) to internal stream.
        """
        self._WriteDoubleToStream(self._fStream, value)


    def _WriteDoubleToStream(self, stream:BytesIO, value:float) -> None:
        """
        Store as Delphi Double (64bit signed, little endian) to specified stream.
        """
        stream.write(struct.pack('<d', value))


    def _WriteInt(self, value:int) -> None:
        """
        Store as Delphi Integer (32bit signed, little endian) to internal stream.
        """
        self._WriteIntToStream(self._fStream, value)


    def _WriteIntToStream(self, stream:BytesIO, value:int) -> None:
        """
        Store as Delphi Integer (32bit signed, little endian) to specified stream.
        """
        # ensure we don't exceed the size range for 4 bytes of data!
        # this can happen for ThreadId and ProcessId values!
        if (value >= -2147483647) and (value <= 2147483648):
            stream.write(struct.pack('<l', value))
        elif (value >= 0) and (value <= 4294967295):
            stream.write(struct.pack('<L', value))
        else:
            # value would exceed the byte size the console is expecting - zero it out!
            stream.write(struct.pack('<L', 0))


    def _WriteShort(self, value:int) -> None:
        """
        Store as Delphi Word (16bit unsigned, little endian).
        """
        self._WriteShortToStream(self._fStream, value)


    def _WriteShortToStream(self, stream:BytesIO, value:int) -> None:
        """
        Store as Delphi Word (16bit unsigned, little endian) to specified stream.
        """
        stream.write(struct.pack('<H', value))


    def _WriteStreamLength(self, value:BytesIO) -> None:
        """
        Store length of stream as Delphi Integer (32bit signed, little endian).
        """
        if (value != None):
            self._WriteInt(value.getbuffer().nbytes)
        else:
            self._WriteInt(0)


    def _WriteTimestamp(self, value:datetime) -> None:
        """
        Store as Delphi TDatetime (8-byte double, little endian).
        """

        # Calculate current time-stamp:
        # A time-stamp is represented by a double. The integral
        # part of the from is the number of days that have
        # passed since 12/30/1899. The fractional part of the
        # from is the fraction of a 24 hour day that has elapsed.

        # Delphi is expecting a timestamp that is calculated from Delphi default time, which
        # is the number of seconds from a starting date of 12/30/1899.

        us:int = 0
        timestamp:float = 0
        timestamp2:float = 0

        # convert datetime value to raw ticks (# seconds since 1/1/0001).
        ticks:float = (value - datetime(1, 1, 1)).total_seconds() * 10000000

        # convert raw ticks value to epoch ticks (# seconds since 1/1/1970).
        us = int((ticks - SIBinaryFormatter.TICKS_EPOCH) / 10)

        # convert epoch ticks to Delphi default date ticks (# seconds since 12/30/1899).
        timestamp = int(us / SIBinaryFormatter.MICROSECONDS_PER_DAY + SIBinaryFormatter.DAY_OFFSET_DELPHI_DEFAULT)
        timestamp2 = timestamp + float((us % SIBinaryFormatter.MICROSECONDS_PER_DAY) / SIBinaryFormatter.MICROSECONDS_PER_DAY)

        # write timestamp to data stream.
        self._WriteDouble(timestamp2)


    def _WriteUInt(self, value:int) -> None:
        """
        Store as Delphi Cardinal (32bit unsigned, little endian).
        """
        #self._fStream.write(struct.pack('<L', value))
        self._WriteIntToStream(self._fStream, value)
    

    def Compile(self, packet:SIPacket) -> int:
        """
        Overridden. Preprocesses (or compiles) a packet and returns the
        required size for the compiled result.

        Args:
            packet (SIPacket):
                The packet to compile.

        Returns:
            The size for the compiled result.

        This method preprocesses the supplied packet and computes the
        required binary format size. To write this compiled packet,
        call the Write method.
        """

        self._ResetStream()
        self._fPacket = packet

        if packet.PacketType is SIPacketType.LogEntry:
            self._CompileLogEntry()
        elif packet.PacketType is SIPacketType.LogHeader:
            self._CompileLogHeader()
        elif packet.PacketType is SIPacketType.Watch:
            self._CompileWatch()
        elif packet.PacketType is SIPacketType.ControlCommand:
            self._CompileControlCommand()
        elif packet.PacketType is SIPacketType.ProcessFlow:
            self._CompileProcessFlow()

        self._fSize = self._fStream.tell()
        return self._fSize + SIPacket.PACKET_HEADER_SIZE


    def Write(self, stream:BytesIO) -> None:
        """
        Overridden. Writes a previously compiled packet to the supplied stream.
        
        Args:
            stream (BytesIO):
                The stream to write the packet to.

        Raises:
            IOException:
                An I/O error occurred while trying to write the compiled packet.

        This method writes the previously compiled packet (see Compile)
        to the supplied stream object. If the return value of the
        Compile method was 0, nothing is written.
        """

        if (self._fSize > 0):
            self._WriteShortToStream(stream, int(self._fPacket.PacketType.value))
            self._WriteIntToStream(stream, self._fSize)
            self._CopyStream(stream, self._fStream, self._fSize)
