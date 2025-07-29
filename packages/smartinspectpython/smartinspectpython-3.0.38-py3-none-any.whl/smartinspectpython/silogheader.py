# our package imports.
from .sipacket import SIPacket
from .sipackettype import SIPacketType

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SILogHeader(SIPacket):
    """ 
    Represents the Log Header packet type which is used for storing
    and transferring log metadata.
    
    The SILogHeader class is used to store and transfer log metadata.
    After the SIPipeProtocol or SITcpProtocol has established a connection,
    a Log Header packet with the metadata of the current logging
    context is created and written. Log Header packets are used by
    the SmartInspect Router application for its filter and trigger
    functionality.
    
    Threadsafety:
        This class is not guaranteed to be thread-safe. However, instances
        of this class will normally only be used in the context of a single thread.
    """

    _HEADER_SIZE:int = 4

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """

        # initialize the base class.
        super().__init__()

        # initialize instance.
        self._fHostName:str = ''
        self._fAppName:str = ''


    @property
    def AppName(self) -> str:
        """ 
        Gets the AppName property value.

        Represents the application name of this Log Header.

        The application name of a Log Header is usually set to the
        name of the application this Log Header is created in.
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
    def Content(self) -> str:
        """
        Gets the Content property value.

        Represents the entire content of this Log Header packet.

        The content of a Log Header packet is a key-value (syntax:
        key=value) list of the properties of this Log Header packet
        (currently only the AppName and the HostName strings).
        Key-value pairs are separated by carriage return and newline
        characters.
        """
        return str.format("hostname={0}\r\nappname={1}\r\n", self._fHostName, self._fAppName)


    @property
    def HostName(self) -> str:
        """ 
        Gets the HostName property value.

        Represents the hostname of this Log Header.

        The hostname of a Log Header is usually set to the name of
        the machine this Log Header is sent from.
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
    def PacketType(self) -> SIPacketType:
        """ 
        Overridden.  Returns SIPacketType.LogHeader. 
        """
        return SIPacketType.LogHeader


    @property
    def Size(self) -> int:
        """ 
        Overridden. Returns the total occupied memory size of this Log Header packet (including header length).
        
        The total occupied memory size of this Log Header is the size
        of memory occupied by all strings and any internal data
        structures of this Log Header.  Also note that the data
        is in UTF-8 encoding, so it takes up twice the storage as
        ASCII encoding.
        """
        result:int = (self._HEADER_SIZE +
                  SIPacket.GetStringSize(self.Content))
        return result
