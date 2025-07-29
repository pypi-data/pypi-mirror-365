from copy import copy
from datetime import datetime
from io import BytesIO

# our package imports.
from .sicolor import SIColor
from .silogentrytype import SILogEntryType
from .sipacket import SIPacket
from .sipackettype import SIPacketType
from .siviewerid import SIViewerId

# our package constants.
from .siconst import (
    DEFAULT_COLOR_VALUE
)

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SILogEntry(SIPacket):
    """
    Represents the Log Entry packet type which is used for nearly
    all logging methods in the SISession class.
    
    A Log Entry is the most important packet available in the
    SmartInspect concept. It is used for almost all logging methods
    in the SISession class, like, for example, SISession.LogMessage,
    SISession.LogObject or SISession.LogSql.

    A Log Entry has several properties which describe its creation
    context (like a thread ID, time-stamp or host name) and other
    properties which specify the way the Console interprets this packet
    (like the viewer ID or the background color). Furthermore a Log
    Entry contains the actual data which will be displayed in the
    Console.

    Threadsafety:
        This class is not guaranteed to be thread-safe. However, instances
        of this class will normally only be used in the context of a single
        thread.
    """

    # static variables.
    _HEADER_SIZE:int = 48
    
    def __init__(self, logEntryType:SILogEntryType, viewerId:SIViewerId) -> None:
        """ 
        Initializes a new SILogEntry instance with
        a custom log entry type and custom viewer ID.
        
        Args:
            logEntryType (SILogEntryType):
                The type of the new Log Entry describes the way the Console
                interprets this packet. Please see the SILogEntryType enum for
                more information.
            viewerId (SIViewerId):
                The viewer ID of the new Log Entry describes which viewer
                should be used in the Console when displaying the data of
                this Log Entry. Please see the SIViewerId enum for more information.
        """

        # initialize the base class.
        super().__init__()

        # initialize instance.
        self._fData:BytesIO = BytesIO()
        self._fLogEntryType:SILogEntryType = logEntryType
        self._fViewerid:SIViewerId = viewerId
        self._fColorBG:SIColor = SIColor(DEFAULT_COLOR_VALUE)
        self._fHostName:str = ''
        self._fAppName:str = ''
        self._fTitle:str = ''
        self._fSessionName:str = ''
        self._fTimestamp:datetime = None
        self._fProcessId:int = SIPacket.GetProcessId()
        self._fThreadId:int = SIPacket.GetThreadId()


    @property
    def AppName(self) -> str:
        """ 
        Gets the AppName property value.

        Represents the application name of this Log Entry.

        The application name of a Log Entry is usually set to the
        name of the application this Log Entry is created in. It will
        be empty in the SmartInspect Console when this property is set
        to null.
        """
        return self._fAppName
    
    @AppName.setter
    def AppName(self, value:str) -> None:
        """ 
        Sets the AppName property value.
        """
        if value != None:
            self._fAppName = value


    @property
    def ColorBG(self) -> SIColor:
        """ 
        Gets the ColorBG property value.

        Represents the background color of this Log Entry.
        
        The background color of a Log Entry is normally set to the
        color of the session which sent this Log Entry.
        """
        return self._fColorBG
    
    @ColorBG.setter
    def ColorBG(self, value:SIColor) -> None:
        """ 
        Sets the ColorBG property value.
        """
        if value != None:
            self._fColorBG = value


    @property
    def Data(self) -> BytesIO:
        """
        Gets the Data property value.

        This property contains an optional data stream of the Log Entry.
        This property can be null if this Log Entry does not
        contain additional data.

        <b>Important:</b> Treat this stream as read-only. This means,
        modifying this stream in any way is not supported. Additionally,
        only pass streams which support seeking. Streams which do not
        support seeking cannot be used by this class.
        """
        return self._fData

    @Data.setter
    def Data(self, value:BytesIO):
        """ 
        Sets the Data property value.
        """
        if value:
            self._fData = copy(value)
        else:
            self._fData.truncate(0)


    @property
    def DataLength(self) -> int:
        """
        Returns the number of bytes used in the Data property.
        Note that this is the actual # of bytes used, and not the # of bytes allocated!
        """
        if (self._fData != None):
            return self._fData.getbuffer().nbytes
        return 0


    @property
    def HasData(self) -> bool:
        """
        Returns true if this packet contains optional data; otherwise, false.
        """
        if (self._fData != None) & (self._fData.getbuffer().nbytes > 0):
            return True
        return False


    @property
    def HostName(self) -> str:
        """ 
        Gets the HostName property value.

        Represents the host name of this Log Entry.

        The host name of a Log Entry is usually set to the name of
        the machine this Log Entry is sent from. It will be empty in
        the SmartInspect Console when this property is set to null.
        """
        return self._fHostName
    
    @HostName.setter
    def HostName(self, value:str) -> None:
        """ 
        Sets the HostName property value.
        """
        if value != None:
            self._fHostName = value


    @property
    def LogEntryType(self) -> SILogEntryType:
        """ 
        Gets the LogEntryType property value.

        Represents the type of this Log Entry.

        The type of this Log Entry describes the way the Console
        interprets this packet. Please see the SILogEntryType enum for more
        information.
        """
        return self._fLogEntryType
    
    @LogEntryType.setter
    def LogEntryType(self, value:SILogEntryType) -> None:
        """ 
        Sets the LogEntryType property value.
        """ 
        if value != None:
            self._fLogEntryType = value


    @property
    def PacketType(self) -> SIPacketType:
        """ 
        Overridden.  Returns SIPacketType.LogEntry
        """
        return SIPacketType.LogEntry


    @property
    def ProcessId(self) -> int:
        """ 
        Gets the ProcessId property value.

        Represents the ID of the process this object was created in.
        """
        return self._fProcessId
    
    @ProcessId.setter
    def ProcessId(self, value:int) -> None:
        """ 
        Sets the ProcessId property value.
        """ 
        if value != None:
            self._fProcessId = value


    @property
    def SessionName(self) -> str:
        """ 
        Gets the SessionName property value.

        Represents the session name of this Log Entry.

        The session name of a Log Entry is normally set to the name
        of the session which sent this Log Entry. It will be empty in
        the SmartInspect Console when this property is set to null.
        """
        return self._fSessionName
    
    @SessionName.setter
    def SessionName(self, value:str) -> None:
        """ 
        Sets the SessionName property value.
        """
        if value != None:
            self._fSessionName = value


    @property
    def Size(self) -> int:
        """
        Overridden. Returns the total occupied memory size of this Log Entry packet.

        The total occupied memory size of this Log Entry is the size
        of memory occupied by all strings, the optional Data stream
        and any internal data structures of this Log Entry.
        """
        result = (self._HEADER_SIZE +
                SIPacket.GetStringSize(self._fTitle) +
                SIPacket.GetStringSize(self._fSessionName) +
                SIPacket.GetStringSize(self._fHostName) +
                SIPacket.GetStringSize(self._fAppName))

        if self.HasData:
            result += self._fData.getbuffer().nbytes
        return result


    @property
    def ThreadId(self) -> int:
        """ 
        Gets the ThreadId property value.

        Represents the ID of the thread this object was created in.
        """
        return self._fThreadId
    
    @ThreadId.setter
    def ThreadId(self, value:int) -> None:
        """ 
        Sets the ThreadId property value.
        """ 
        if value != None:
            self._fThreadId = value


    @property
    def Timestamp(self) -> datetime:
        """ 
        Gets the Timestamp property value.

        Represents the time-stamp of this Log Entry object.

        This property returns the creation time of this Log Entry object.
        """
        return self._fTimestamp
    
    @Timestamp.setter
    def Timestamp(self, value:datetime) -> None:
        """ 
        Sets the Timestamp property value.
        """
        if value != None:
            self._fTimestamp = value


    @property
    def Title(self) -> str:
        """ 
        Gets the Title property value.

        Represents the title of this Log Entry.

        The title of this Log Entry will be empty in the SmartInspect
        Console when this property is set to null.
        """
        return self._fTitle
    
    @Title.setter
    def Title(self, value:str) -> None:
        """ 
        Sets the Title property value.
        """
        if value != None:
            self._fTitle = value


    @property
    def ViewerId(self) -> SIViewerId:
        """ 
        Gets the ViewerId property value.

        Represents the viewer ID of this Log Entry.

        The viewer ID of the Log Entry describes which viewer should
        be used in the Console when displaying the data of this Log
        Entry. Please see the SIViewerId enum for more information.
        """
        return self._fViewerid
    
    @ViewerId.setter
    def ViewerId(self, value:SIViewerId) -> None:
        """ 
        Sets the ViewerId property value.
        """
        if value != None:
            self._fViewerid = value
