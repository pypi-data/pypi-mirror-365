# external package imports.
# none

# our package imports.
from .sipacket import SIPacket
from .sipacketqueueitem import SIPacketQueueItem

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIPacketQueue:
    """
    Manages a memory size limited queue of packets.

    This class is responsible for managing a size limited queue
    of packets. This functionality is needed by the protocol
    SIProtocol.IsValidOption feature. The maximum
    total memory size of the queue can be set with the Backlog
    property. New packets can be added with the Push method. Packets
    which are no longer needed can be retrieved and removed from the
    queue with the Pop method.

    Threadsafety:
        This class is not guaranteed to be thread-safe.
    """

    _OVERHEAD:int = 24

    
    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        # initialize instance.
        self._fBacklog:int = 0
        self._fSize:int = 0
        self._fCount:int = 0
        self._fHead:SIPacketQueueItem = None
        self._fTail:SIPacketQueueItem = None


    @property
    def Backlog(self) -> int:
        """ 
        Gets the Backlog property value.

        Represents the total maximum memory size of this queue in bytes.

        Each time a new packet is added with the Push method, it will
        be verified that the total occupied memory size of the queue
        still falls below the supplied Backlog limit. To satisfy this
        constraint, old packets are removed from the queue when necessary.
        """
        return self._fBacklog
    
    @Backlog.setter
    def Backlog(self, value:int) -> None:
        """ 
        Sets the Backlog property value.
        """
        if value != None:

            self._fBacklog = value
            self._Resize()


    @property
    def Count(self) -> int:
        """ 
        Gets the Count property value.

        Returns the current amount of packets in this queue.

        For each added packet this counter is incremented by one
        and for each removed packet (either with the Pop method or
        automatically while resizing the queue) this counter is decremented
        by one. If the queue is empty, this property returns 0.
        """
        return self._fCount


    def _Resize(self) -> None:
        """
        Removes old packets from the queue (if necessary) when the Backlog
        property value is changed.
        """
        while (self._fBacklog < self._fSize):
        
            if (self.Pop() == None):
            
                self._fSize = 0
                break


    def Clear(self) -> None:
        """
        Removes all packets from this queue.

        Removing all packets of the queue is done by calling the Pop
        method for each packet in the current queue.
        """
        while True:

            if (self.Pop() == None):
                break


    def Pop(self) -> SIPacket:
        """
        Returns a packet and removes it from the queue.

        Returns:
            The removed packet or null if the queue does not contain any packets.

        If the queue is not empty, this method removes the oldest
        packet from the queue (also known as FIFO) and returns it.
        The total size of the queue is decremented by the size of
        the returned packet (plus some internal management overhead).
        """
        result:SIPacket = None
        item:SIPacketQueueItem = self._fHead

        if (item != None):
        
            result = item.Packet
            self._fHead = item.Next

            if (self._fHead != None):
                self._fHead.Previous = None
            else:
                self._fTail = None

            self._fCount = self._fCount - 1

            size:int = 0
            if (result.Size != None):
                size = result.Size
            self._fSize = self._fSize - (size + SIPacketQueue._OVERHEAD)
        
        return result


    def Push(self, packet:SIPacket) -> None:
        """
        Adds a new packet to the queue.

        Args:
            packet (SIPacket):
                The packet to add.

        This method adds the supplied packet to the queue. The size
        of the queue is incremented by the size of the supplied
        packet (plus some internal management overhead). If the total
        occupied memory size of this queue exceeds the Backlog limit
        after adding the new packet, then already added packets will
        be removed from this queue until the Backlog size limit is
        reached again.
        """
        item:SIPacketQueueItem = SIPacketQueueItem()
        item.Packet = packet

        if (self._fTail == None):
        
            self._fTail = item
            self._fHead = item
        
        else:
        
            self._fTail.Next = item
            item.Previous = self._fTail
            self._fTail = item
        
        self._fCount = self._fCount + 1
        self._fSize += packet.Size + SIPacketQueue._OVERHEAD
        self._Resize()
