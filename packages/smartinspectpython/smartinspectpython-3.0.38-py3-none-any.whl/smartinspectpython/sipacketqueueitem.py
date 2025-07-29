# external package imports.
# none

# our package imports.
from .sipacket import SIPacket

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIPacketQueueItem:
    """
    SIPacketQueue item class.
    """
    
    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        self.Packet:SIPacket = None
        """
        Packet stored by this queue item.
        """
        self.Next:SIPacketQueueItem = None
        """
        The next packet queue item in the queue.
        """
        self.Previous:SIPacketQueueItem = None
        """
        The previous packet queue item in the queue.
        """
   