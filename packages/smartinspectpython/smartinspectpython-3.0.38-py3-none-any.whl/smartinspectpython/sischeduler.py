# external package imports.
import _threading_local
import threading

# our package imports.
from .sipacket import SIPacket
from .siprotocolcommand import SIProtocolCommand
from .sischeduleraction import SISchedulerAction
from .sischedulercommand import SISchedulerCommand
from .sischedulerqueue import SISchedulerQueue

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIScheduler:
    """
    Responsible for scheduling protocol operations and executing
    them asynchronously in a different thread of control.

    This class is used by the SIProtocol.IsValidOption to asynchronously execute
    protocol operations. New commands can be scheduled for execution with
    the Schedule method. The scheduler can be started and stopped
    with the Start and Stop methods. The scheduler uses a size
    limited queue to buffer scheduler commands. The maximum size of
    this queue can be set with the Threshold property. To influence
    the behavior of the scheduler if new commands are enqueued and
    the queue is currently considered full, you can specify the
    Throttle mode.

    Threadsafety:
        This class is guaranteed to be thread-safe.
    """

    _BUFFER_SIZE:int = 0x10

    def __init__(self, protocol) -> None:
        """
        Initializes a new instance of the class.

        Args:
            protocol (SIProtocol):
                The protocol object on which to execute the actual operations like
                connect, disconnect, write or dispatch.
        """
        # initialize instance.
        self._fMonitor = _threading_local.RLock()
        self._fMonitorCondition:threading.Condition = threading.Condition(self._fMonitor)
        self._fThread:threading.Thread = None
        self._fQueue:SISchedulerQueue = SISchedulerQueue()
        self._fBuffer = [None] * SIScheduler._BUFFER_SIZE
        self._fProtocol = protocol
        self._fThreshold:int = 0
        self._fThrottle:bool = False
        self._fStopped:bool = False
        self._fStarted:bool = False


    @property
    def Threshold(self) -> int:
        """ 
        Gets the Threshold property value.

        Represents the maximum size of the scheduler command queue.

        To influence the behavior of the scheduler if new commands
        are enqueued and the queue is currently considered full,
        you can specify the Throttle mode.
        """
        return self._fThreshold

    @Threshold.setter
    def Threshold(self, value:int):
        """ 
        Sets the Threshold property value.
        """
        if (value != None):
            self._fThreshold = value


    @property
    def Throttle(self) -> bool:
        """ 
        Gets the Throttle property value.

        Specifies if the scheduler should automatically throttle
        threads that enqueue new scheduler commands.

        If this property is true and the queue is considered full
        when enqueuing new commands, the enqueuing thread is
        automatically throttled until there is room in the queue
        for the new command. In non-throttle mode, the thread is
        not blocked but older commands are removed from the queue.
        """
        return self._fThrottle

    @Throttle.setter
    def Throttle(self, value:bool):
        """ 
        Sets the Throttle property value.
        """
        if (value != None):
            self._fThrottle = value


    def _Enqueue(self, command:SISchedulerCommand) -> bool:
        """
        Queues a new command for asynchronous execution.

        Args:
            command (SISchedulerCommand):
                The command to queue.</param>

        Returns:
            True if the command could be queued for asynchronous
            execution and false otherwise.

        This method adds the passed command to the internal queue
        of scheduler commands. The command is eventually executed
        by the internal scheduler thread. This method can block the
        caller if the scheduler operates in Throttle mode and the
        internal queue is currently considered full (see Threshold).
        """
        # has the scheduler threadtask been started yet?  
        # if not, then we are done.
        if (not self._fStarted):
            return False

        # if scheduler threadtask has stopped then we are done.
        if (self._fStopped):
            return False

        # any room in the queue for this command?  if not, then we are done.
        commandSize:int = command.Size
        if (commandSize > self._fThreshold):
            return False

        # lock the queue so only the main thread can access it.
        with (self._fMonitor):
        
            # is throttling disabled?  or did a protocol function fail?
            if ((not self._fThrottle) or (self._fProtocol.Failed)):
            
                # if so, then remove old commands from the queue until we have
                # enough room for the command we are about to add to the queue.
                if ((self._fQueue.Size + commandSize) > self._fThreshold):
                    self._fQueue.Trim(commandSize)
            
            else:
            
                # if throttling is enabled, then wait for the scheduler threadtask
                # to process enough items in the queue until room is made for the
                # command we are about to add to the queue.
                while ((self._fQueue.Size + commandSize) > self._fThreshold):

                    self._fMonitorCondition.wait()

            # add the command to the queue.
            self._fQueue.Enqueue(command)

            # signal the scheduler threadtask that we added an item to the queue.
            self._fMonitorCondition.notify_all()

        return True


    def Clear(self) -> None:
        """
        Removes all scheduler commands from this scheduler.

        This method clears the current queue of scheduler commands.
        If the Stop method is called after calling Clear and no new
        commands are stored between these two calls, the internal
        scheduler thread will exit as soon as possible (after the
        current command, if any, has been processed).
        """
        with (self._fMonitor):
        
            # clear the queue, and let the scheduler threadtask know about it.
            self._fQueue.Clear()
            self._fMonitorCondition.notify_all()


    def Schedule(self, command:SISchedulerCommand) -> bool:
        """
        Schedules a new command for asynchronous execution.

        Args:
            command (SISchedulerCommand):
                The command to schedule.</param>

        Returns:
            True if the command could be scheduled for asynchronous
            execution and false otherwise.

        This method adds the passed command to the internal queue
        of scheduler commands. The command is eventually executed
        by the internal scheduler thread. This method can block the
        caller if the scheduler operates in Throttle mode and the
        internal queue is currently considered full (see Threshold).
        """
        return self._Enqueue(command)


    def Start(self) -> None:
        """
        Starts this scheduler and the internal scheduler threadtask.

        This method must be called before scheduling new commands
        with the Schedule method. Call Stop to stop the internal
        thread when the scheduler is no longer needed. Note that
        this method starts the internal scheduler thread only once.
        This means that subsequent calls to this method have no
        effect.
        """
        with (self._fMonitor):
        
            # if scheduler already started then we are done.
            if (self._fStarted):
                return

            # start the scheduler threadtask on a new thread.
            self._fThread = threading.Thread(target=self._SchedulerThreadTask, args=(self,))
            self._fThread.name = "SiSchedulerThreadTask"
            self._fThread.start()
            self._fStarted = True


    def Stop(self) -> None:
        """
        Stops this scheduler and the internal scheduler threadtask.

        This is the matching method for Start. After calling this
        method, new commands will no longer be accepted by Schedule
        and are ignored. This method blocks until the internal
        thread has processed the current content of the queue.
        Call Clear before calling Stop to exit the internal thread
        as soon as possible.
        """
        with (self._fMonitor):

            # if scheduler has not started yet then we are done.
            if (not self._fStarted):
                return

            # indicate scheduler has stopped, and pulse the scheduler threadtask
            # to let it know that it can stop.
            self._fStopped = True
            self._fMonitorCondition.notify_all()

        # wait for the scheduler threadtask to finish up.
        if (self._fThread != None):
            self._fThread.join()


    ##################################################################################################################################
    # The following methods are ran on the SIScheduler threadtask!
    ##################################################################################################################################

    def _SchedulerThreadTask(self, instance) -> None:
        """
        SIScheduler thread task method.
        """
        while (True):
        
            count:int = self._Dequeue()

            # is scheduler stopped and no more commands to process?
            if (count == 0):
                break

            if (not self._RunCommands(count)):
                break   # stopped 

        # reset buffer.
        self._fBuffer = [None] * SIScheduler._BUFFER_SIZE


    def _Dequeue(self) -> int:
        """
        Removes a scheduler command from the queue, and places it into
        an command buffer for subsequent execution by the scheduler thread.

        Returns:
            The number of commands that were removed from the queue.

        This method adds the passed command to the internal queue
        of scheduler commands. The command is eventually executed
        by the internal scheduler thread. This method can block the
        caller if the scheduler operates in Throttle mode and the
        internal queue is currently considered full (see Threshold).

        This method is executed by the _SchedulerThreadTask.
        """
        count:int = 0
        length:int = len(self._fBuffer)

        # lock the queue so only the scheduler threadtask thread can access it.
        with (self._fMonitor):
        
            # anything in the queue to process?
            while (self._fQueue.Count == 0):
            
                # no - were we asked to stop?  if so, then we are done.
                if (self._fStopped):
                    break

                # is main thread still alive?  if not, then we are done.
                if (not threading.main_thread().is_alive()):
                    break

                # continue waiting until we receive a pulse from the main thread
                # that it added something to the queue (or asked us to stop).
                self._fMonitorCondition.wait()

            # ensure the queue has not been destroyed (in case of shutdown).
            if (self._fQueue != None):
            
                # pull as many items off of the queue that will fit in our buffer.
                # we will return how many items we pulled off of the queue.
                while (self._fQueue.Count > 0):
                
                    self._fBuffer[count] = self._fQueue.Dequeue()
                    count = count + 1

                    if (count >= length):
                        break

            # inform the main thread that it can process the buffer
            # of commands that we just dequeued.
            self._fMonitorCondition.notify_all()

        return count


    def _RunCommand(self, command:SISchedulerCommand) -> None:
        """
        Processes a dequeued command.

        Args:
            command (SISchedulerCommand):
                The dequeued command to run.

        This method is executed by the _SchedulerThreadTask.
        """
        # Process the dequeued command. The Impl methods cannot
        # throw an exception. Exceptions are reported with the
        # error event of the protocol in asynchronous mode.

        action:SISchedulerAction = command.Action

        if (action == SISchedulerAction.Connect):
            self._fProtocol._ImplConnect()
        elif (action == SISchedulerAction.WritePacket):
            packet:SIPacket = command.State
            self._fProtocol._ImplWritePacket(packet)
        elif (action == SISchedulerAction.Disconnect):
            self._fProtocol._ImplDisconnect()
        elif (action == SISchedulerAction.Dispatch):
            cmd:SIProtocolCommand = command.State
            self._fProtocol._ImplDispatch(cmd)


    def _RunCommands(self, count:int) -> bool:
        """
        Runs the specified number of commands in the queue.

        Args:
            count (int):
                The number of commands to run.

        Returns:
            True if all commands were run successfully, otherwise False.

        This method is executed by the _SchedulerThreadTask.
        """
        for i in range(count):
        
            stopped:bool = self._fStopped

            command:SISchedulerCommand = self._fBuffer[i]
            if (command != None):
                self._RunCommand(command)
            self._fBuffer[i] = None

            if (not stopped):
                continue

            # The scheduler has been stopped before the last
            # command has been processed. To shutdown this
            # thread as fast as possible we check if the last
            # command of the protocol has failed (or if the
            # last command has failed to change the previous
            # failure status, respectively). If this is the
            # case, we clear the queue and exit this thread
            # immediately.
            if (self._fProtocol.Failed):
            
                self.Clear()
                return False

        return True
