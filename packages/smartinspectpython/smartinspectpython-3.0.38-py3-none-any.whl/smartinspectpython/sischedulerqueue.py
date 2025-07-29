# external package imports.
# none

# our package imports.
from .sischeduleraction import SISchedulerAction
from .sischedulercommand import SISchedulerCommand
from .sischedulerqueueitem import SISchedulerQueueItem

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SISchedulerQueue:
    """
    Manages a queue of scheduler commands.

    This class is responsible for managing a queue of scheduler
    commands. This functionality is needed by the
    SIProtocol.IsValidOption and the SIScheduler class. New commands can 
    be added with the Enqueue method. Commands can be dequeued with 
    Dequeue. This queue does not have a maximum size or count.

    Threadsafety:
        This class is not guaranteed to be thread-safe.
    """

    OVERHEAD:int = 24

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        # initialize instance.
        self._fSize:int = 0
        self._fCount:int = 0
        self._fHead:SISchedulerQueueItem = None
        self._fTail:SISchedulerQueueItem = None


    @property
    def Count(self) -> int:
        """ 
        Returns the current amount of scheduler commands in this queue.

        For each added scheduler command this counter is incremented
        by one and for each removed command (with Dequeue) this
        counter is decremented by one. If the queue is empty, this
        property returns 0.
        """
        return self._fCount


    @property
    def Size(self) -> int:
        """ 
        Returns the current size of this queue in bytes.

        For each added scheduler command this counter is incremented
        by the size of the command (plus some internal management
        overhead) and for each removed command (with Dequeue) this
        counter is then decremented again. If the queue is empty,
        this property returns 0.
        """
        return self._fSize


    def _Add(self, item:SISchedulerQueueItem) -> None:
        """
        Adds a new scheduler queue item to the queue.

        Args:
            item (SISchedulerQueueItem):
                A scheduler queue item to add.
        """
        if (self._fTail == None):
        
            self._fTail = item
            self._fHead = item
        
        else:
        
            self._fTail.Next = item
            item.Previous = self._fTail
            self._fTail = item

        self._fCount = self._fCount + 1
        if (item.Command != None):
            self._fSize = self._fSize + (item.Command.Size + SISchedulerQueue.OVERHEAD);


    def _Remove(self, item:SISchedulerQueueItem) -> None:
        """
        Removes a scheduler queue item from the queue.

        Args:
            item (SISchedulerQueueItem):
                A scheduler queue item to remove.
        """
        if (item == self._fHead): # head
        
            self._fHead = item.Next
            if (self._fHead != None):
                self._fHead.Previous = None
            else: # was also tail
                self._fTail = None
        
        else:
        
            if (item.Previous != None):
            
                item.Previous.Next = item.Next
                if (item.Next == None):  # tail
                    self._fTail = item.Previous
                else:
                    item.Next.Previous = item.Previous

        self._fCount = self._fCount - 1
        if (item.Command != None):
            self._fSize = self._fSize - (item.Command.Size + SISchedulerQueue.OVERHEAD)


    def Clear(self) -> None:
        """
        Removes all scheduler commands from this queue.

        Removing all scheduler commands of the queue is done by calling
        the Dequeue method for each command in the current queue.
        """
        while True:

            if (self.Dequeue() == None):
                break


    def Dequeue(self) -> SISchedulerCommand:
        """
        Returns a scheduler command and removes it from the queue.

        Returns:
            The removed scheduler command or null if the queue does not
            contain any packets.

        If the queue is not empty, this method removes the oldest
        scheduler command from the queue (also known as FIFO) and
        returns it. The total Size of the queue is decremented by
        the size of the returned command (plus some internal
        management overhead).
        """
        item:SISchedulerQueueItem = self._fHead

        if (item != None):
        
            self._Remove(item)
            return item.Command
        
        else:
            return None


    def Enqueue(self, command:SISchedulerCommand) -> None:
        """
        Adds a new scheduler command to the queue.

        Args:
            command (SISchedulerCommand):
                The command to add.

        This method adds the supplied scheduler command to the
        queue. The Size of the queue is incremented by the size of
        the supplied command (plus some internal management overhead).
        This queue does not have a maximum size or count.
        """
        item:SISchedulerQueueItem = SISchedulerQueueItem()
        item.Command = command
        self._Add(item)


    def Trim(self, size:int) -> bool:
        """
        Tries to skip and remove scheduler commands from this queue.

        Args:
            size (int):
                The minimum amount of bytes to remove from this queue.

        Returns:
            True if enough scheduler commands could be removed and false otherwise.

        This method removes the next WritePacket scheduler commands
        from this queue until the specified minimum amount of bytes
        has been removed. Administrative scheduler commands (connect,
        disconnect or dispatch) are not removed. If the queue is
        currently empty or does not contain enough WritePacket
        commands to achieve the specified minimum amount of bytes,
        this method returns false.
        """
        if (size <= 0):
            return True

        removedBytes:int = 0
        item:SISchedulerQueueItem = self._fHead

        while (item != None):
        
            if ((item.Command != None) and (item.Command.Action == SISchedulerAction.WritePacket)):
            
                removedBytes = removedBytes + (item.Command.Size + SISchedulerQueue.OVERHEAD)
                self._Remove(item)

                if (removedBytes >= size):
                    return True

            item = item.Next

        return False
