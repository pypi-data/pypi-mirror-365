# external package imports.
from datetime import datetime

# our package imports.
from .sipacket import SIPacket
from .sipackettype import SIPacketType
from .siwatchtype import SIWatchType

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIWatch(SIPacket):
    """
    Represents the Watch packet type which is used in the Watch
    methods in the SISession class.

    A Watch is responsible for sending variables and their values
    to the Console. These key/value pairs will be displayed in the
    Watches toolbox. If a Watch with the same name is sent twice,
    the old value is overwritten and the Watches toolbox displays
    the most current value.

    Threadsafety:
        This class is not guaranteed to be thread-safe. However, instances
        of this class will normally only be used in the context of a
        single thread.
    """

    # static variables.
    HEADER_SIZE:int = 20
    
    def __init__(self, watchType:SIWatchType) -> None:
        """ 
        Initializes a new SIWatch instance with a
        custom watch type.

        Args:
            watchType (SIWatchType):
                The type of the new Watch describes the variable type (String,
                Integer and so on). Please see the SIWatchType enum for more
                information.
        """

        # initialize the base class.
        super().__init__()

        self._fWatchType:SIWatchType = watchType
        self._fName:str = ''
        self._fValue:str = ''
        self._fTimestamp:datetime


    @property
    def Name(self) -> str:
        """ 
        Gets the Name property value.

        Represents the name of this Watch.

        If a Watch with the same name is sent twice, the old value is
        overwritten and the Watches toolbox displays the most current
        value. The name of this Watch will be empty in the SmartInspect
        Console when this property is set to null.
        """
        return self._fName
    
    @Name.setter
    def Name(self, value:str) -> None:
        """ 
        Sets the Name property value.
        """
        if value != None:
            self._fName = value


    @property
    def PacketType(self) -> SIPacketType:
        """ 
        Overridden.  Returns SIPacketType.Watch
        """
        return SIPacketType.Watch


    @property
    def Size(self) -> int:
        """
        Overridden. Returns the total occupied memory size of this Watch packet.

        The total occupied memory size of this Watch is the size of
        memory occupied by all strings and any internal data structures
        of this Watch.
        """
        result = (self.HEADER_SIZE +
              SIPacket.GetStringSize(self._fName) +
              SIPacket.GetStringSize(self._fValue))
        return result


    @property
    def Timestamp(self) -> datetime:
        """ 
        Gets the Timestamp property value.

        Represents the time-stamp of this Watch object.

        This property returns the creation time of this object.
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
    def Value(self) -> str:
        """ 
        Gets the Value property value.

        Represents the value of this Watch.

        The value of a Watch is always sent as String. To view the
        type of this variable Watch, please have a look at the
        WatchType property. The value of this Watch will be empty in
        the SmartInspect Console when this property is set to null.
        """
        return self._fValue
    
    @Value.setter
    def Value(self, value:str) -> None:
        """ 
        Sets the Value property value.
        """
        if value != None:
            self._fValue = value


    @property
    def WatchType(self) -> SIWatchType:
        """ 
        Gets the WatchType property value.

        Represents the type of this Watch.

        The type of this Watch describes the variable type (String,
        Integer and so on). Please see the SIWatchType enum for more
        information.
        """
        return self._fWatchType
    
    @WatchType.setter
    def WatchType(self, value:SIWatchType) -> None:
        """ 
        Sets the WatchType property value.
        """ 
        if value != None:
            self._fWatchType = value
