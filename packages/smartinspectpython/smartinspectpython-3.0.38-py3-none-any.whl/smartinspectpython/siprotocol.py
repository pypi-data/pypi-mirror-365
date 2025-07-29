# external package imports.
import _threading_local
from datetime import datetime, timedelta 

# our package imports.
from .siconnectionsbuilder import SIConnectionsBuilder
from .sierroreventargs import SIErrorEventArgs
from .sifilerotate import SIFileRotate
from .siinfoeventargs import SIInfoEventArgs
from .silevel import SILevel
from .silogheader import SILogHeader
from .silookuptable import SILookupTable
from .sioptionfoundeventargs import SIOptionFoundEventArgs
from .sioptionsparser import SIOptionsParser
from .sipacket import SIPacket
from .sipacketqueue import SIPacketQueue
from .siprotocolcommand import SIProtocolCommand
from .siprotocolexception import SIProtocolException
from .sischeduler import SIScheduler
from .sischeduleraction import SISchedulerAction
from .sischedulercommand import SISchedulerCommand
from .siutils import Event
from .smartinspectexception import SmartInspectException

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIProtocol:
    """
    Is the abstract base class for a protocol. 
    A protocol is responsible for transporting packets.

    A protocol is responsible for the transport of packets. This
    base class offers all necessary methods to handle the protocol
    options and it declares several abstract protocol specific
    methods for handling protocol destinations like connecting or
    writing packets.

    The following table lists the available protocols together with
    their identifier in the SmartInspect.Connections and a short description.

    Protocol (Identifier)  | Description
    ---------------------  | ----------------------------------------------------------------
    SIFileProtocol ("file")  | Used for writing log files in the standard SmartInspect binary log file format which can be loaded into the Console.
    SIMemoryProtocol ("mem") | Used for writing log data to memory and saving it to a stream on request.
    SIPipeProtocol ("pipe")  | Used for sending log data over a named pipe directly to a local Console.
    SITcpProtocol ("tcp")    | Used for sending packets over a TCP connection directly to the Console.
    SITextProtocol ("text")  | Used for writing log files in a customizable text format.  Best suited for end-user notification purposes.

    There are several options which are IsValidOption
    and beyond that each protocol has its
    own set of additional options. For those protocol specific
    options, please refer to the documentation of the corresponding
    protocol class. Protocol options can be set with Initialize and
    derived classes can query option values using the Get methods.

    Threadsafety:
        The public members of this class are thread-safe.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        # initialize instance - options.
        self._fCaption:str = ''
        self._fLevel:SILevel = SILevel.Debug
        self._fReconnect:bool = False
        self._fReconnectInterval:int = 0
        self._fBacklogEnabled:bool = False
        self._fBacklogQueue:int = 0;
        self._fBacklogFlushOn:SILevel = SILevel.Debug
        self._fBacklogKeepOpen:bool = False
        self._fAsyncEnabled:bool = False
        self._fAsyncThrottle:bool = False
        self._fAsyncClearOnDisconnect:bool = False
        self._fAsyncQueue:int = 0

        # initialize instance - Internal data.
        self._fHostName:str = ''
        self._fAppName:str = ''
        self._fReconnectDateTime:datetime = None
        self._fKeepOpen:bool = False
        self._fFailed:bool = False
        self._fConnected:bool = False
        self._fInitialized:bool = False
        self._fLock:object = _threading_local.RLock()
        self._fOptions:SILookupTable = SILookupTable()
        self._fQueue:SIPacketQueue = SIPacketQueue()
        self._fScheduler:SIScheduler = None

        # define all events raised by this class.
        self.ErrorEvent:Event = Event()
        """
        Event raised when a protocol raises an exception.
        """
        self.InfoEvent:Event = Event()
        """
        Event raised when a protocol has an informational message to convey.
        """

        # wire up event handlers.
        self.ErrorEvent += self.OnErrorEvent
        self.InfoEvent += self.OnInfoEvent


    @property
    def AppName(self) -> str:
        """ 
        Gets the AppName property value.
        
        The application name of a protocol is usually set to the
        name of the application this protocol is created in. The
        application name can be used to write LogHeader packets
        after a successful protocol connect.
        """
        return self._fAppName
    
    @AppName.setter
    def AppName(self, value:str):
        """ 
        Sets the AppName property value.
        """
        if value != None:
            self._fAppName = value


    @property
    def Asynchronous(self) -> bool:
        """
        Gets the Asynchronous property value.

        Indicates if this protocol is operating in asynchronous protocol mode.

        If this property returns true, this protocol is operating
        in asynchronous protocol mode. Otherwise, it returns false.
        Asynchronous protocol mode can be enabled with the
        Initialize method. Also see IsValidOption for information
        on asynchronous logging and how to enable it.
        """
        return self._fAsyncEnabled


    @property
    def Caption(self) -> str:
        """
        Gets the Caption property value.

        Returns the caption of this protocol.

        The caption is used in the SmartInspect.Dispatch method to
        lookup a requested connection. The caption can be set with
        the Options property. If you use only one connection at once
        or does not use the SmartInspect.Dispatch method, the caption
        option can safely be ignored.

        For more information, please refer to the documentation of
        the Dispatch and SmartInspect.Dispatch methods.
        """
        return self._fCaption


    @property
    def Failed(self) -> bool:
        """
        Gets the Failed property value.

        Returns if the last executed connection-related operation of
        this protocol has failed. Indicates if the next operation is
        likely to block.
        """
        return self._fFailed


    @property
    def HostName(self) -> str:
        """ 
        Gets the HostName property value.
        
        The host name of a protocol is usually set to the name of
        the machine this protocol is created in. The host name can
        be used to write LogHeader packets after a successful
        protocol connect.
        """
        return self._fHostName
    
    @HostName.setter
    def HostName(self, value:str):
        """ 
        Sets the HostName property value.
        """
        if value != None:
            self._fHostName = value


    @property
    def Name(self) -> str:
        """
        Gets the Name property value.

        Specifies the name of a real protocol implementation.

        Raises:
            NotImplementedError:
                Thrown if the property method is not overridden in an inheriting class.
            
        Real implementations should return a meaningful name which
        represents the protocol. For example, the SIFileProtocol
        returns "file", the SITcpProtocol "tcp" and the SITextProtocol
        "text".
        """
        raise NotImplementedError()


    def _AddOption(self, sender:object, e:SIOptionFoundEventArgs) -> None:
        """
        Handles the SIOptionsParser.OptionFoundEvent.

        Args:
            sender (object):
                The object which fired the event.
            e (SIOptionFoundEventArgs):
                Arguments that contain detailed information related to the event.
        """
        if (self._MapOption(e.Key, e.Value)):
            return

        # is the option supported by the protocol?  if not, then it's an error!
        if (not self.IsValidOption(e.Key)):
            raise SmartInspectException(str.format("Option \"{0}\" is not available for protocol \"{1}\"", e.Key, e.Protocol))

        self._fOptions.Put(e.Key, e.Value)


    def _CreateOptions(self, options:str) -> None:
        """
        Parses options for this protocol, and adds them to a key-based lookup table.

        Args:
            options (str):
                Protocol options string.
        """
        parser:SIOptionsParser = None

        try:

            # wire up events, and parse the protocol options.
            parser = SIOptionsParser()
            parser.OptionFoundEvent += self._AddOption
            parser.Parse(self.Name, options)

        except Exception as ex:

            self._RemoveOptions()
            raise  # pass exception on thru.

        finally:

            if (parser != None):
                parser.OptionFoundEvent.unhandle_all()


    def _FlushQueue(self) -> None:
        """
        """
        packet:SIPacket = self._fQueue.Pop()

        while (packet != None):
            self._ForwardPacket(packet, False)
            packet = self._fQueue.Pop()


    def _ForwardPacket(self, packet:SIPacket, disconnect:bool) -> None:
        """
        """
        if (not self._fConnected):

            if (not self._fKeepOpen):
                self.InternalConnect()
                self._fConnected = True
                self._fFailed = False # Success
            else:
                self._Reconnect()

        if (self._fConnected):

            packet.Lock()

            try:

                self.InternalWritePacket(packet)

            finally:

                packet.Unlock()

            if (disconnect):
                self._fConnected = False
                self.InternalDisconnect()


    def _GetOptions(self) -> str:
        """
        Returns a string of options used by this protocol.
        """
        builder:SIConnectionsBuilder = SIConnectionsBuilder()
        self.BuildOptions(builder)
        return builder.Connections


    def _ImplConnect(self) -> None:
        """
        Internal function that will connect to the protocol destination.
        """
        if (not self._fConnected and self._fKeepOpen):

            try:

                try:

                    self.InternalConnect()
                    self._fConnected = True
                    self._fFailed = False

                except Exception as ex:

                    self.Reset()
                    raise  # pass exception on thru.

            except Exception as ex:

                self.HandleException(str(ex))


    def _ImplDisconnect(self) -> None:
        """
        Internal function that will disconnect from the protocol destination
        and reset itself to a consistent state.
        """
        if (self._fConnected):

            try:

                self.Reset()

            except Exception as ex:

                self.HandleException(str(ex))

        else:
            self._fQueue.Clear()


    def _ImplDispatch(self, command:SIProtocolCommand) -> None:
        """
        Executes a protocol specific custom action.

        Args:
            command (SIProtocolCommand):
                The protocol command which provides protocol specific
                information about the custom action. Can be null.
        """
        if (self._fConnected):

            try:

                self.InternalDispatch(command)

            except Exception as ex:

                self.HandleException(str(ex))


    def _ImplWritePacket(self, packet:SIPacket) -> None:
        """
        Writes a packet to the protocol specific destination.

        Args:
            packet (SIPacket):
                Packet to write.
        """
        if ((not self._fConnected) and (not self._fReconnect) and (self._fKeepOpen)):
            return

        if (packet == None):
            return

        try:

            try:

                skip:bool = False

                if (self._fBacklogEnabled):

                    if (packet.Level >= self._fBacklogFlushOn) and (packet.Level != SILevel.Control):
                        self._FlushQueue()
                    else:
                        self._fQueue.Push(packet)
                        skip = True

                if (not skip):
                    self._ForwardPacket(packet, not self._fKeepOpen)
            
            except Exception as ex:

                self.Reset()
                raise  # pass exception on thru.

        except Exception as ex:

            self.HandleException(str(ex))


    def _MapOption(self, key:str, value:str) -> bool:
        """
        This method is for backwards compatibility. In older
        SmartInspect versions the backlog options didn't have
        'backlog.' prefix. This has been changed in version
        3.0. This method does the mapping between the old and
        the new backlog options.

        Args:
            key (str):
                The option key string value.
            value (str):
                The option value string.
        """
        if (key == "backlog"):
            self._fOptions.Put(key, value)
            backlog:int = self._fOptions.GetSizeValue("backlog", 0)

            if (backlog > 0):
                self._fOptions.Add("backlog.enabled", "true")
                self._fOptions.Add("backlog.queue", value)
            else:
                self._fOptions.Add("backlog.enabled", "false")
                self._fOptions.Add("backlog.queue", "0")

            return True

        if (key == "flushon"):
            self._fOptions.Put(key, value)
            self._fOptions.Add("backlog.flushon", value)
            return True

        if (key == "keepopen"):
            self._fOptions.Put(key, value)
            self._fOptions.Add("backlog.keepopen", value)
            return True

        return False


    def _RaiseErrorEvent(self, ex:Exception) -> None:
        """
        Raises the ErrorEvent event with found exception data.

        Args:
            ex (Exception):
                The exception that caused the event.

        This method is used to inform other objects that an exception was caught for 
        a protocol function.
        """
        try:

            args:SIErrorEventArgs = SIErrorEventArgs(ex)
            self.ErrorEvent(self, args)

        except Exception as ex:

            # ignore exceptions.
            pass


    def _Reconnect(self) -> None:

        if (self._fReconnectInterval > 0):

            # get elapsed time between the last disconnect and now.
            elapsed:timedelta = (datetime.utcnow() - self._fReconnectDateTime)
            
            # convert to milliseconds to compare to reconnect interval (milliseconds value).
            elapsedms:int = round(elapsed.total_seconds() * 1000)

            # if elapsed time (in milliseconds) is less than our reconnect 
            # interval (in milliseconds), then the interval has not been
            # reached and we will not try to reconnect just yet.
            if (elapsedms < self._fReconnectInterval):
                return   # the interval has not been reached!

        try:

            if (self.InternalReconnect()):
                self._fConnected = True

        except:

            # Reconnect exceptions are not reported, but we
            # need to record that the last connection attempt
            # has failed (see below).
            pass

        self._fFailed = not self._fConnected

        if (self._fFailed):

            try:

                self.Reset()

            except:

                pass # Ignored


    def _RemoveOptions(self) -> None:
        self._fOptions.Clear()


    def _ScheduleConnect(self) -> None:
        """
        """
        command:SISchedulerCommand = SISchedulerCommand()
        command.Action = SISchedulerAction.Connect

        if (self._fScheduler != None):
            self._fScheduler.Schedule(command)


    def _ScheduleDisconnect(self) -> None:
        """
        """
        command:SISchedulerCommand = SISchedulerCommand()
        command.Action = SISchedulerAction.Disconnect
        if (self._fScheduler != None):
            self._fScheduler.Schedule(command)


    def _ScheduleDispatch(self, cmd:SIProtocolCommand) -> None:
        """
        """
        command:SISchedulerCommand = SISchedulerCommand()
        command.Action = SISchedulerAction.Dispatch
        command.State = cmd

        if (self._fScheduler != None):
            self._fScheduler.Schedule(command)


    def _ScheduleWritePacket(self, packet:SIPacket) -> None:
        """
        """
        command:SISchedulerCommand = SISchedulerCommand()
        command.Action = SISchedulerAction.WritePacket
        command.State = packet
        if (self._fScheduler != None):
            self._fScheduler.Schedule(command)


    def _StartScheduler(self) -> None:
        """
        Starts the scheduler and the internal scheduler thread
        that will process packets (if asynchronous mode is enabled).
        """
        self._fScheduler = SIScheduler(self)
        self._fScheduler.Threshold = self._fAsyncQueue
        self._fScheduler.Throttle = self._fAsyncThrottle

        try:

            self._fScheduler.Start()

        except Exception as ex:

            self._fScheduler = None
            raise  # pass exception on thru.


    def _StopScheduler(self) -> None:
        """
        Stops the scheduler and the internal scheduler thread
        that will process packets (if asynchronous mode is enabled).
        """
        if (self._fScheduler != None):
            self._fScheduler.Stop()
            self._fScheduler = None


    def _WriteLogHeaderPacket(self):
        """
        Writes a Log header packet that identifies us to the SmartInspect Console.
        """
        logHeader:SILogHeader = SILogHeader()
        logHeader.AppName = self._fAppName
        logHeader.HostName = self._fHostName
        self.InternalWritePacket(logHeader)


    def BuildOptions(self, builder:SIConnectionsBuilder) -> None:
        """
        Fills a SIConnectionsBuilder instance with the options currently
        used by this protocol.

        Args:
            builder (SIConnectionsBuilder):
                The SIConnectionsBuilder object to fill with the current options
                of this protocol.
        
        The filled options string consists of key, value option pairs
        separated by commas.
        
        This function takes care of the options (see IsValidOption).
        To include protocol specific options, override this function.
        """
        # Asynchronous options.
        builder.AddOptionBool("async.enabled", self._fAsyncEnabled)
        builder.AddOptionBool("async.clearondisconnect", self._fAsyncClearOnDisconnect)
        builder.AddOptionInteger("async.queue", self._fAsyncQueue / 1024)
        builder.AddOptionBool("async.throttle", self._fAsyncThrottle)

        # Backlog options.
        builder.AddOptionBool("backlog.enabled", self._fBacklogEnabled)
        builder.AddOptionLevel("backlog.flushon", self._fBacklogFlushOn)
        builder.AddOptionBool("backlog.keepopen", self._fBacklogKeepOpen)
        builder.AddOptionInteger("backlog.queue", self._fBacklogQueue / 1024)

        # General options.
        builder.AddOptionLevel("level", self._fLevel)
        builder.AddOptionString("caption", self._fCaption)
        builder.AddOptionBool("reconnect", self._fReconnect)
        builder.AddOptionInteger("reconnect.interval", self._fReconnectInterval)


    def Connect(self) -> None:
        """
        Connects to the protocol specific destination.
        
        Raises:
            SIProtocolException:
                Connecting to the destination failed.  Can only occur when operating in
                normal blocking mode. In asynchronous mode, the Error event is used for
                reporting exceptions instead.
        
        In normal blocking mode (see IsValidOption), this method
        does nothing more than to verify that the protocol is not
        already connected and does not use the IsValidOption
        and then calls the abstract protocol specific InternalConnect method in a thread-safe
        and exception-safe context.

        When operating in asynchronous mode instead, this method
        schedules a connect operation for asynchronous execution
        and returns immediately. Please note that possible
        exceptions which occur during the eventually executed
        connect are not thrown directly but reported with the
        Error event.
        """
        with self._fLock:

            if (self._fAsyncEnabled):

                # is the scheduler already running?  if so, then nothing to do!
                if (self._fScheduler != None):
                    return

                try:

                    self._StartScheduler()
                    self._ScheduleConnect()

                except Exception as ex:

                    self.HandleException(str(ex))

            else:

                self._ImplConnect()


    def Disconnect(self) -> None:
        """
        Disconnects from the protocol destination.

        Raises:
            SIProtocolException:
                Disconnecting from the destination failed. Can only occur when operating
                in normal blocking mode. In asynchronous mode, the Error event is used for
                reporting exceptions instead.

        In normal blocking mode (see IsValidOption), this method
        checks if this protocol has a working connection and then
        calls the protocol specific InternalDisconnect method in a
        thread-safe and exception-safe context.

        When operating in asynchronous mode instead, this method
        schedules a disconnect operation for asynchronous execution
        and then blocks until the internal protocol thread is done.
        Please note that possible exceptions which occur during
        the eventually executed disconnect are not thrown directly
        but reported with the Error event.
        """
        with self._fLock:

            if (self._fAsyncEnabled):

                # if scheduler is not running then there is nothing else to do.
                if (self._fScheduler == None):
                    return

                if (self._fAsyncClearOnDisconnect):
                    self._fScheduler.Clear()

                self._ScheduleDisconnect()
                self._StopScheduler()

            else:

                self._ImplDisconnect()


    def Dispatch(self, command:SIProtocolCommand) -> None:
        """
        Dispatches a custom action to a concrete implementation of
        a protocol.

        Args:
            command (SIProtocolCommand):
                The protocol command object which provides protocol specific
                information about the custom action. Can be null.
        Raises:
            SIProtocolException:
                An exception occurred in the custom action. Can only occur when operating
                in normal blocking mode. In asynchronous mode, the Error event is
                used for reporting exceptions instead.

        In normal blocking mode (see IsValidOption), this method
        does nothing more than to call the protocol specific
        InternalDispatch method with the supplied command argument
        in a thread-safe and exception-safe way. Please note that
        this method dispatches the custom action only if the protocol
        is currently connected.

        When operating in asynchronous mode instead, this method
        schedules a dispatch operation for asynchronous execution
        and returns immediately. Please note that possible
        exceptions which occur during the eventually executed
        dispatch are not thrown directly but reported with the
        Error event.
        """
        with self._fLock:

            if (self._fAsyncEnabled):

                if (self._fScheduler == None):
                    return  # Not running

                self._ScheduleDispatch(command)

            else:

                self._ImplDispatch(command)


    def Dispose(self) -> None:
        """
        Disconnects from the protocol destination.

        Raises:
            SIProtocolException:
                Disconnecting from the destination failed. Can only occur when operating
                in normal blocking mode. In asynchronous mode, the Error event is used for
                reporting exceptions instead.

        In normal blocking mode (see IsValidOption), this method
        checks if this protocol has a working connection and then
        calls the protocol specific InternalDisconnect method in a
        thread-safe and exception-safe context.

        When operating in asynchronous mode instead, this method
        schedules a disconnect operation for asynchronous execution
        and then blocks until the internal protocol thread is done.
        Please note that possible exceptions which occur during
        the eventually executed disconnect are not thrown directly
        but reported with the Error event.
        """
        try:

            self.Disconnect()

        finally:

            # unwire all event handlers.
            if (self.ErrorEvent != None):
                self.ErrorEvent.unhandle_all()
            if (self.InfoEvent != None):
                self.InfoEvent.unhandle_all()


    def GetBooleanOption(self, key:str, defaultValue:bool) -> bool:
        """
        Gets the boolean value of a key.

        Args:
            key (str):
                The key whose value to return.
            defaultValue (bool):
                The value to return if the key does not exist.
        
        Returns:
            Either the value if the key exists or defaultValue
            otherwise. Note that this method can throw an exception
            of type ArgumentNullException if you pass a null
            reference as key.

        Raises:
            ArgumentNullException:
                The key argument is null.

        A bool value will be treated as true if the value of the
        key matches either "true", "yes" or "1" and as false
        otherwise. Note that this method can throw an exception
        of type ArgumentNullException if you pass a null reference
        as key.
        """
        return self._fOptions.GetBooleanValue(key, defaultValue)


    def GetBytesOption(self, key:str, size:int, defaultValue:bytearray) -> bytearray:
        """
        Gets the byte array value of a key.

        Args:
            key (str):
                The key whose value to return.
            size (int):
                The desired size in bytes of the returned byte array. If
                the element value does not have the expected size, it is
                shortened or padded automatically.
            defaultValue (bytearray):
                The value to return if the given key is unknown or if the
                found value has an invalid format.
        
        Returns:
            Either the value converted to a byte array for the given key
            if an element with the given key exists and the found value
            has a valid format or defaultValue otherwise.

        Raises:
            ArgumentNullException:
                The key argument is null.

        The returned byte array always has the desired length as
        specified by the size argument. If the element value does
        not have the required size after conversion, it is shortened
        or padded (with zeros) automatically. This method returns
        the defaultValue argument if either the supplied key is
        unknown or the found value does not have a valid format
        (e.g. invalid characters when using hexadecimal strings).

        Note that this method can throw an exception of type
        ArgumentNullException if you pass a null reference as key.
        """
        return self._fOptions.GetBytesValue(key, size, defaultValue)


    def GetIntegerOption(self, key:str, defaultValue:int) -> int:
        """
        Gets the integer value of a key.

        Args:
            key (str):
                The key whose value to return.
            defaultValue (int):
                The value to return if the key does not exist.
        
        Returns:
            Either the value if the key exists or defaultValue
            otherwise. Note that this method can throw an exception
            of type ArgumentNullException if you pass a null
            reference as key.

        Raises:
            ArgumentNullException:
                The key argument is null.

        Please note that if a value could be found but is not a
        valid integer, the supplied default value will be returned.
        Only non-negative integers will be recognized as valid
        values. Also note that this method can throw an exception
        of type ArgumentNullException if you pass a null reference
        as key.
        """
        return self._fOptions.GetIntegerValue(key, defaultValue)


    def GetLevelOption(self, key:str, defaultValue:SILevel) -> SILevel:
        """
        Gets the Level value of a key.

        Args:
            key (str):
                The key whose value to return.
            defaultValue (SILevel):
                The value to return if the key does not exist.
        
        Returns:
            Either the value converted to the corresponding Level value
            for the given key if an element with the given key exists
            and the found value is a valid Level value or defaultValue
            otherwise.

        Raises:
            ArgumentNullException:
                The key argument is null.

        This method returns the defaultValue argument if either the
        supplied key is unknown or the found value is not a valid
        Level value. Please see the Level enum for more information
        on the available values. Note that this method can throw an
        exception of type ArgumentNullException if you pass a null
        reference as key.
        """
        return self._fOptions.GetLevelValue(key, defaultValue)


    def GetRotateOption(self, key:str, defaultValue:SIFileRotate) -> SIFileRotate:
        """
        Gets the FileRotate value of a key.

        Args:
            key (str):
                The key whose value to return.
            defaultValue (SIFileRotate):
                The value to return if the key does not exist.
        
        Returns:
            Either the value converted to a FileRotate value for the
            given key if an element with the given key exists and the
            found value is a valid FileRotate or defaultValue otherwise.
            Note that this method can throw an exception of type
            ArgumentNullException if you pass a null reference as key.

        Raises:
            ArgumentNullException:
                The key argument is null.

        This method returns the defaultValue argument if either the
        supplied key is unknown or the found value is not a valid
        Level value. Please see the Level enum for more information
        on the available values. Note that this method can throw an
        exception of type ArgumentNullException if you pass a null
        reference as key.
        """
        return self._fOptions.GetRotateValue(key, defaultValue)


    def GetSizeOption(self, key:str, defaultValue:int) -> int:
        """
        Gets an integer value of a key. The integer value is interpreted 
        as a byte size and it is supported to specify byte units.

        Args:
            key (str):
                The key whose value to return.
            defaultValue (int):
                The value to return if the key does not exist.
        
        Returns:
            Either the value converted to an integer for the given key if
            an element with the given key exists and the found value is a
            valid integer or defaultValue otherwise.

        Raises:
            ArgumentNullException:
                The key argument is null.

        This method returns the defaultValue argument if either the
        supplied key is unknown or the found value is not a valid
        integer or ends with an unknown byte unit. Only non-negative
        integer values are recognized as valid.
        
        It is possible to specify a size unit at the end of the value.
        If a known unit is found, this function multiplies the
        resulting value with the corresponding factor. For example, if
        the value of the element is "1KB", the return value of this
        function would be 1024.
        
        The following table lists the available units together with a
        short description and the corresponding factor.

        Unit Name / Factor | Description
        ------------------ | -----------
        KB / 1024          | KiloByte
        MB / 1024^2        | MegaByte
        GB / 1024^3        | GigaByte
        
        If no unit is specified, this function defaults to the KB
        unit. Note that this method can throw an exception of type
        ArgumentNullException if you pass a null reference as key.
        """
        return self._fOptions.GetSizeValue(key, defaultValue)


    def GetStringOption(self, key:str, defaultValue:str) -> str:
        """
        Gets the string value of a key.

        Args:
            key (str):
                The key whose value to return.
            defaultValue (str):
                The value to return if the key does not exist.
        
        Returns:
            Either the value if the key exists or defaultValue
            otherwise. Note that this method can throw an exception
            of type ArgumentNullException if you pass a null
            reference as key.

        Raises:
            ArgumentNullException:
                The key argument is null.
        """
        value:str = self._fOptions.GetStringValue(key, defaultValue)
        if (value == None):
            return ""
        return value


    def GetTimespanOption(self, key:str, defaultValue:float) -> float:
        """
        Gets an integer value of a key. The integer value is
        interpreted as a time span and it is supported to specify time
        span units.

        Args:
            key (str):
                The key whose value to return.
            defaultValue (float):
                The value to return if the key does not exist.
        
        Returns:
            Either the value converted to an integer for the given key if
            an element with the given key exists and the found value is a
            valid integer or defaultValue otherwise. The value is returned
            in milliseconds.

        Raises:
            ArgumentNullException:
                The key argument is null.

        This method returns the defaultValue argument if either the
        supplied key is unknown or the found value is not a valid
        integer or ends with an unknown time span unit.
        
        It is possible to specify a time span unit at the end of the
        value. If a known unit is found, this function multiplies the
        resulting value with the corresponding factor. For example, if
        the value of the element is "1s", the return value of this
        function would be 1000.
        
        The following table lists the available units together with a
        short description and the corresponding factor.
        
        Unit Name / Factor | Description
        ------------------ | -----------
        s (Seconds)        | 1000
        m (Minutes)        | 60*s
        h (Hours)          | 60*m
        d (Days)           | 24*h
        
        If no unit is specified, this function defaults to the Seconds
        unit. Please note that the value is always returned in
        milliseconds.
        """
        return self._fOptions.GetTimespanValue(key, defaultValue)


    def HandleException(self, message:str) -> None:
        """
        Handles a protocol exception.

        Args:
            message (str):
                The exception message.
        
        Raises:
            SIProtocolException:
                Always in normal blocking mode; never in asynchronous mode.
        
        This method handles an occurred protocol exception. It
        first sets the Failed flag and creates a SIProtocolException
        object with the name and options of this protocol. In
        normal blocking mode (see IsValidOption), it then throws
        this exception. When operating in asynchronous mode,
        it invokes the Error event handlers instead and does not
        throw an exception.
        """
        # indicate that the last operation has failed.
        self._fFailed = True

        # create exception object.
        ex:SIProtocolException = SIProtocolException(message, self.Name, self._GetOptions())

        if (self._fAsyncEnabled):

            # notify event handlers.
            self._RaiseErrorEvent(ex)

        else:

            raise ex


    def Initialize(self, options:str) -> None:
        """
        Sets and initializes the options of this protocol.
        
        Args:
            options (str):
                Protocol options, in string delimited format.

        Raises:
            SmartInspectException:
                Invalid options syntax or an unknown option key.
        
        This property expects an options string which consists
        of key, value pairs separated by commas like this:
        "filename=log.sil, append=true". To use a comma in a value,
        you can use quotation marks like in the following example:
        "filename=\\"log.sil\\", append=true".
        
        Please note that a SmartInspectException exception is thrown
        if an incorrect options string is assigned. An incorrect
        options string could use an invalid syntax or contain one or
        more unknown option keys. This method can be called only once.
        Further calls have no effect. Pass null or an empty string to
        use the default options of a particular protocol.
        """
        with (self._fLock):

            if (not self._fInitialized):

                if (options != None):
                    self._CreateOptions(options)

                self.LoadOptions()
                self._fInitialized = True


    def InternalConnect(self) -> None:
        """
        Connects to the protocol destination
        Abstract method - inheriting classes must override.

        Raises:
            Exception:
                Connecting to the destination failed.
        
        This method initiates a protocol specific connection attempt.
        The behavior of real implementations of this method can often
        be changed by setting protocol options with the Initialize
        method. This method is always called in a thread-safe and
        exception-safe context.
        """
        raise NotImplementedError()


    def InternalDisconnect(self) -> None:
        """
        Disconnects from the protocol destination.
        Abstract method - inheriting classes must override.

        Raises:
            Exception:
                Disconnecting from the destination failed.

        This method is intended for real protocol implementations
        to disconnect from the protocol specific source. This
        could be closing a file or disconnecting a TCP socket, for
        example. This method is always called in a thread-safe and
        exception-safe context.
        """
        raise NotImplementedError()


    def InternalDispatch(self, command:SIProtocolCommand) -> None:
        """
        Executes a protocol specific custom action.
        
        Args:
            command (SIProtocolCommand):
                The protocol command which provides protocol specific
                information about the custom action. Can be null.

        Raises:
            Exception:
                Executing the custom action failed.

        The default implementation does nothing. Derived protocol
        implementations can override this method to add custom
        actions. Please see the SIMemoryProtocol.InternalDispatch
        method for an example. This method is always called in a
        thread-safe and exception-safe way.
        """
        pass    # empty by default


    def InternalReconnect(self) -> bool:
        """
        Reconnects to the protocol specific destination.

        Returns:
            True if the reconnect attempt has been successful and false otherwise.
        
        Raises:
            Exception:
                Reconnecting to the destination failed.

        This method initiates a protocol specific reconnect attempt.
        The behavior of real method implementations can often be
        changed by setting protocol options with Initialize. This
        method is always called in a thread-safe and exception-safe
        context.

        The default implementation simply calls the protocol specific
        InternalConnect method. Derived classes can change this
        behavior by overriding this method. 
        """
        self.InternalConnect()
        return True


    def InternalWritePacket(self, packet:SIPacket) -> None:
        """
        Writes a packet to the protocol destination.

        Args:
            packet (SIPacket):
                The packet to write.

        Raises:
            Exception:
                Writing the packet to the destination failed.

        This method is intended for real protocol implementations
        to write the supplied packet to the protocol specific
        destination. This method is always called in a thread-safe
        and exception-safe context.
        """
        pass


    def IsValidOption(self, name:str) -> bool:
        """
        Overriddeable. Validates if a option is supported by this protocol.

        True if the option is supported and false otherwise.


        Args:
            name (str):
                The option name to validate.

        Returns:
            True if the option is supported and false otherwise.

        The following table lists all valid options, their default
        values and descriptions common to all protocols. See below
        for explanations.

        Option Name (Default Value)     | Description
        ---------------------------     | ----------------------------------------------------
        level (debug)                   | Specifies the log level of this protocol.
        reconnect (false)               | Specifies if a reconnect should be initiated when a connection gets dropped.
        reconnect.interval (0)          | If reconnecting is enabled, specifies the minimum time in seconds between two successive reconnect attempts. If 0 is specified, a reconnect attempt is initiated for each packet if needed. It is possible to specify time span units like this: "1s". Supported units are "s" (seconds), "m" (minutes), "h" (hours) and "d" (days).
        caption ([name])                | Specifies the caption of this protocol as used by SmartInspect.Dispatch. By default, it is set to the protocol identifier (e.g., "file" or "mem").
        async.enabled (false)           | Specifies if this protocol should operate in asynchronous instead of the default blocking mode.
        async.queue (2048)              | Specifies the maximum size of the asynchronous queue in kilobytes. It is possible to specify size units like this: "1 MB". Supported units are "KB", "MB" and "GB".
        async.throttle (true)           | Specifies if the application should be automatically throttled in asynchronous mode when more data is logged than the queue can handle.
        async.clearondisconnect (false) | Specifies if the current content of the asynchronous queue should be discarded before disconnecting. Useful if an application must not wait for the logging to complete before exiting.
        backlog.enabled (false)         | Enables the backlog feature (see below).
        backlog.queue (2048)            | Specifies the maximum size of the backlog queue in kilobytes. It is possible to specify size units like this: "1 MB". Supported units are "KB", "MB" and "GB".
        backlog.flushon (error)         | Specifies the flush level for the backlog functionality.
        backlog.keepopen (false)        | Specifies if the connection should be kept open between two successive writes when the backlog feature is used.
        
        With the log level of a protocol you can limit the amount of
        data being logged by excluding packets which don't have a
        certain minimum log level. For example, if you set the level
        to "message", all packets with a log level of "debug" or
        "verbose" are ignored. For a complete list of available log
        level values, please see the documentation of the Level enum.

        The caption option specifies the caption for this protocol
        as used by the SmartInspect.Dispatch method. This method
        can send and initiate custom protocol actions and the caption
        is used to lookup the requested connection. By default, the
        caption is set to the identifier of a protocol (e.g., "file"
        or "mem"). For more information about the dispatching of
        custom protocol actions, please refer to the documentation of
        the Dispatch and SmartInspect.Dispatch methods.

        If the backlog option is enabled, all packets whose log level
        is less than the flushon level and equal to or higher than the
        general log level of a protocol, will be written to a queue
        rather than directly to the protocol specific destination. When
        a packet arrives with a log level of at least the same value
        as the flushon option, the current content of the queue is
        written. The total amount of memory occupied by this queue
        can be set with the queue option. If the packet queue has
        been filled up with packets and a new packet is about to be
        stored, old packets are discarded.

        As an example, if the backlog queue is set to "2 MB" and the
        flushon level to "error", all packets with a log level less
        than error are written to a queue first. By specifying a queue
        option of "2 MB", the backlog queue is set to a maximum memory
        size of 2 megabyte. Now, when a packet with a log level of
        error arrives, the current content of the queue and then the
        error itself are written.

        With the keepopen option of the backlog feature you can specify
        if a connection should be kept open between two successive
        writes. When keepopen is set to false, a connection is only
        available during the actual write / flush. A connection is
        thus only created when absolutely necessary.

        A protocol can either operate in normal blocking (the default)
        or in asynchronous mode. In blocking mode, the operations of
        this protocol (Connect, Disconnect, Dispatch and WritePacket)
        are executed synchronously and block the caller until they are
        done. In asynchronous mode, these operations are not executed
        directly but scheduled for execution in a different thread 
        and return immediately. Asynchronous logging can increase the
        logging performance and reduce the blocking of applications.

        When operating in asynchronous mode, this protocol uses a
        queue to buffer the logging data. The total amount of memory
        occupied by this queue can be set with the queue option. The
        throttle option specifies if an application should be
        automatically throttled in asynchronous mode when more data
        is logged / generated than the queue can handle. If this
        option is disabled and the queue is currently full, old
        packets are discarded when new data is logged. The throttle
        option ensures that no logging data is lost but can be
        disabled if logging performance is critical.

        With the clearondisconnect option, you can specify if the
        current content of the asynchronous queue should be discarded
        before disconnecting. This can be useful if an application
        must not wait for the logging to complete before exiting.

        The reconnect option allows a protocol to reconnect
        automatically before a packet is being written. A reconnect
        might be necessary if a working connection has been unexpectedly
        disconnected or could not be established in the first place.
        Possible errors during a reconnect attempt will silently be
        ignored and not reported.

        Please note that the reconnect functionality causes a protocol
        by default to initiate a connection attempt for every packet
        until a connection has been successfully (re-) established.
        This can be a very time consuming process, especially when
        using a protocol which requires a complex connection process
        like SITcpProtocol, for example. This can slow down
        the logging performance. When using the reconnect option, it
        is thus recommended to also enable asynchronous logging to not
        block the application or to specify a reconnect interval to
        minimize the reconnect attempts.
        """
        return \
            (name == "caption") or \
            (name == "level") or \
            (name == "reconnect") or \
            (name == "reconnect.interval") or \
            (name == "backlog.enabled") or \
            (name == "backlog.flushon") or \
            (name == "backlog.keepopen") or \
            (name == "backlog.queue") or \
            (name == "async.enabled") or \
            (name == "async.queue") or \
            (name == "async.throttle") or \
            (name == "async.clearondisconnect")


    def LoadOptions(self) -> None:
        """
        Overriddeable. Loads and inspects protocol-specific options.

        This method is intended to give real protocol implementations
        the opportunity to load and inspect options. This method will
        be called automatically when the options have been changed.
        The default implementation of this method takes care of the
        options IsValidOption and  should thus always be called by 
        derived classes which override this method.
        """

        strvalue:str = None

        # General protocol options.
        self._fLevel = self.GetLevelOption("level", SILevel.Debug)
        self._fReconnect = self.GetBooleanOption("reconnect", False)
        self._fReconnectInterval = self.GetTimespanOption("reconnect.interval", 0)
        strvalue = self.GetStringOption("caption", self.Name)
        if (strvalue != None):
            self._fCaption = strvalue

        # Backlog protocol options.
        self._fBacklogEnabled = self.GetBooleanOption("backlog.enabled", False)
        self._fBacklogQueue = self.GetSizeOption("backlog.queue", 2048)
        self._fBacklogFlushOn = self.GetLevelOption("backlog.flushon", SILevel.Error)
        self._fBacklogKeepOpen = self.GetBooleanOption("backlog.keepopen", False)
        self._fQueue.Backlog = self._fBacklogQueue
        self._fKeepOpen = (not self._fBacklogEnabled) or (self._fBacklogKeepOpen)

        # Asynchronous protocol options.
        self._fAsyncEnabled = self.GetBooleanOption("async.enabled", False)
        self._fAsyncThrottle = self.GetBooleanOption("async.throttle", True)
        self._fAsyncQueue = self.GetSizeOption("async.queue", 2048)
        self._fAsyncClearOnDisconnect = self.GetBooleanOption("async.clearondisconnect", False)


    def OnErrorEvent(self, sender:object, e:SIErrorEventArgs) -> None:
        """
        Method that will handle the SIProtocol.ErrorEvent event.
        Inheriting classes can override this method to handle the event.

        Args:
            sender (object):
                The object which fired the event.
            e (SIErrorEventArgs):
                Arguments that contain detailed information related to the event.

        Derived classes can override this method to intercept the
        SIProtocol.Error event. Note that the Error event is only
        used in combination with asynchronous logging (please see
        IsValidOption for more information). In normal blocking
        mode, exceptions are reported by throwing.
        
        IMPORTANT: Keep in mind that adding SmartInspect log statements to the event 
        handlers can cause a presumably undesired recursive behavior!
        """
        pass


    def OnInfoEvent(self, sender:object, e:SIInfoEventArgs) -> None:
        """
        Method that will handle the SIProtocol.InfoEvent event.
        Inheriting classes can override this method to handle the event.

        Args:
            sender (object):
                The object which fired the event.
            e (SIInfoEventArgs):
                Arguments that contain detailed information related to the event.

        Derived classes can override this method to intercept the
        SIProtocol.Info event. 
        
        IMPORTANT: Keep in mind that adding SmartInspect log statements to the event 
        handlers can cause a presumably undesired recursive behavior!
        """
        pass


    def RaiseInfoEvent(self, message:str) -> None:
        """
        Raises the InfoEvent event with an informational message.

        Args:
            message (str)
                The message that caused the event.

        This method is used to inform other objects that an informational message was
        issued by a protocol function.
        """
        try:

            args:SIInfoEventArgs = SIInfoEventArgs(message)
            self.InfoEvent(self, args)

        except Exception as ex:

            # ignore exceptions.
            pass


    def Reset(self) -> None:
        """
        Resets the protocol and brings it into a consistent state.

        This method resets the current protocol state by clearing
        the internal backlog queue of packets, setting the connected
        status to false and calling the abstract InternalDisconnect
        method of a real protocol implementation to cleanup any
        protocol specific resources.
        """
        self._fConnected = False
        self._fQueue.Clear()
        
        try:

            self.InternalDisconnect()

        finally:

            # store current date for comparison later when trying to reconnect.
            self._fReconnectDateTime = datetime.utcnow()


    def WritePacket(self, packet:SIPacket) -> None:
        """
        Writes a packet to the protocol specific destination.

        Args:
            packet (SIPacket):
                The packet to write.

        Raises:
            SIProtocolException:
                Writing the packet to the destination failed. Can only occur when operating
                in normal blocking mode. In asynchronous mode, the Error event is
                used for reporting exceptions instead.
        
        This method first checks if the log level of the supplied
        packet is sufficient to be logged. If this is not the
        case, this method returns immediately.

        Otherwise, in normal blocking mode (see IsValidOption),
        this method verifies that this protocol is successfully
        connected and then writes the supplied packet to the
        IsValidOption or passes it directly to the protocol specific 
        destination by calling the InternalWritePacket method. 
        Calling InternalWritePacket is always done in a thread-safe 
        and exception-safe way.

        When operating in asynchronous mode instead, this method
        schedules a write operation for asynchronous execution and
        returns immediately. Please note that possible exceptions
        which occur during the eventually executed write are not
        thrown directly but reported with the Error event.
        """
        with self._fLock:

            if (packet.Level < self._fLevel):
                return

            if (self._fAsyncEnabled):

                if (self._fScheduler == None):
                    return  # Not running

                self._ScheduleWritePacket(packet)

            else:

                self._ImplWritePacket(packet)
