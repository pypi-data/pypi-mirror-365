# external package imports.
from array import array
from datetime import datetime
from inspect import FrameInfo
from io import BufferedReader, BytesIO, StringIO, TextIOWrapper
from pprint import pformat
from threading import Thread, current_thread
from typing import Collection
from xml.etree.ElementTree import fromstring, Element
from xml.etree import ElementTree
import _threading_local
import datetime
import inspect
import logging
import os
import platform
import sqlite3
import sys
import tempfile

# our package imports.
from .sibinarycontext import SIBinaryContext
from .sibinaryformatter import SIBinaryFormatter
from .sibinaryviewercontext import SIBinaryViewerContext
from .sicolor import SIColor, SIColors
from .sicontrolcommand import SIControlCommand
from .sicontrolcommandtype import SIControlCommandType
from .sidataviewercontext import SIDataViewerContext
from .siinspectorviewercontext import SIInspectorViewerContext
from .silevel import SILevel
from .silistviewercontext import SIListViewerContext
from .silogentry import SILogEntry
from .silogentrytype import SILogEntryType
from .simethodparmlistcontext import SIMethodParmListContext
from .siobjectrenderer import SIObjectRenderer
from .siprocessflow import SIProcessFlow
from .siprocessflowtype import SIProcessFlowType
from .sisourceid import SISourceId
from .sitableviewercontext import SITableViewerContext
from .sitextcontext import SITextContext
from .siutils import DataTypeHelper
from .sivaluelistviewercontext import SIValueListViewerContext
from .siviewercontext import SIViewerContext
from .siviewerid import SIViewerId
from .siwatch import SIWatch
from .siwatchtype import SIWatchType

# the following causes a circular import error:
#from .smartinspect import SmartInspect

# our package constants.
from .siconst import (
    DEFAULT_COLOR_VALUE,
    UNKNOWN_VALUE
)

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SISession:
    """
    Logs all kind of data and variables to the SmartInspect Console
    or to a log file.
    
    The SISession class offers dozens of useful methods for sending
    any kind of data with the assistance of its SISession.Parent.
    Sessions can send simple messages, warnings, errors and
    more complex things like pictures, objects, exceptions, system
    information and much more. They are even able to send variable
    watches, generate illustrated process and thread information
    or control the behavior of the SmartInspect Console. It is
    possible, for example, to clear the entire log in the Console by
    calling the ClearLog method.

    Please note that log methods of this class do nothing and return
    immediately if the session is currently not active (Active=False),
    its parent is disabled (Parent.Enabled=False), or the Level is not
    sufficient.

    Threadsafety:
        This class is fully thread-safe.
    """

    def __init__(self, parent, name:str) -> None:
        """
        Initializes a new SISession instance with the
        default color and the specified parent and name.

        Args:
            parent (SmartInspect):
                The parent of the new session.
            name (str):
                The name of the new session.
        """

        #  initialize instance.
        self._fLock = _threading_local.RLock()
        self._fParent = parent
        self._fLevel:SILevel = SILevel.Message
        self._fName:str = ""
        self._fActive:bool = True  # active by default
        self._fIsStored:bool = False
        self._fColorBG = SIColor(DEFAULT_COLOR_VALUE)
        self._fCounters = {}
        self._fCheckpoints = {}
        self._fSystemLogger:logging.Logger = None

        if (name != None):
            self._fName = name

        self.ResetColor()

        # configure temporary logger and stream to capture exception message logging.
        # note that propagate = False is set so logged messages are not propagated to other loggers.
        self._fTempLogger = logging.getLogger('smartinspectpython_temp_log')
        self._fTempLogger.setLevel(logging.ERROR)
        self._fTempLoggingStream = StringIO()
        handler = logging.StreamHandler(stream=self._fTempLoggingStream)
        self._fTempLogger.addHandler(handler)
        self._fTempLogger.propagate = False


    @property
    def _IsStored(self) -> bool:
        """ 
        Gets the _IsStored property value.

        Returns:
            True if this session is stored in the session tracking list
            and false otherwise.

        Indicates if this session is stored in the session tracking
        list of its Parent.

        See the SmartInspect.GetSession and SmartInspect.AddSession
        methods for more information about session tracking.
        """
        return self._fIsStored
    

    @_IsStored.setter
    def _IsStored(self, value:bool) -> None:
        """ 
        Sets the _IsStored property value.
        """
        if value != None:
            self._fIsStored = value


    @property
    def Active(self) -> bool:
        """ 
        Gets the Active property value.

        Returns:
            True if this session can send log message data to the active
            protocols; otherwise, False to suspend logging activity.

        Specifies if the session is currently active.  

        If this property is set to false, all logging methods of this
        class will return immediately and do nothing. Please note that
        the Parent of this session also needs to be SmartInspect.Enabled
        in order to log information.

        This property is especially useful if you are using multiple
        sessions at once and want to deactivate a subset of these
        sessions. To deactivate all your sessions, you can use the
        SmartInspect.Enabled property of the Parent.
        """
        return self._fActive
    

    @Active.setter
    def Active(self, value:bool) -> None:
        """ 
        Sets the Active property value.
        """
        if value != None:
            self._fActive = value


    @property
    def ColorBG(self) -> SIColor:
        """ 
        Gets the ColorBG property value.

        Returns:
            The background color used for this session in the SmartInspect Console.

        The session color helps you to identify Log Entries from
        different sessions in the SmartInspect Console by changing
        the background color.
        """
        return self._fColorBG
    
    @ColorBG.setter
    def ColorBG(self, value:SIColor) -> None:
        """ 
        Sets the ColorBG property value.
        """
        if value != None:
            if (value.A != 0):
                # ensure it is transparent.
                self._fColorBG = SIColor.FromArgb(0, value.R, value.G, value.B)
            else:
                self._fColorBG = value


    @property
    def Level(self) -> SILevel:
        """ 
        Gets the Level property value.

        Returns:
            The log level of this session.

        Each SISession object can have its own log level. A log message
        is only logged if its log level is greater than or equal to
        the log level of a session AND the session Parent. Log levels
        can thus be used to limit the logging output to important
        messages only.
        """
        if (self._fLevel == None):
            return self._fParent.DefaultLevel
        return self._fLevel
    

    @Level.setter
    def Level(self, value:SILevel) -> None:
        """ 
        Sets the Level property value.
        """
        if value != None:
            self._fLevel = value


    @property
    def SystemLogger(self) -> logging.Logger:
        """ 
        A system Logger object, which can be used to write messages
        to a system-based log file as well as the SmartInspect log.

        Returns:
            The SystemLogger property value.

        This can be useful when adding logging to third-party products
        that require a common logging mechanism, but also allows you to
        capture extended logging information to a SmartInspect console.
        
        The following methods will write information to a Logger object
        assigned to the SystemLogger property:  
        LogDebug - calls `_LOGGER.debug(msg)` to log a message.  
        LogVerbose - calls `_LOGGER.debug(msg)` to log a message.  
        LogMessage - calls `_LOGGER.info(msg)` to log a message.  
        LogWarning - calls `_LOGGER.warning(msg)` to log a message.  
        LogError - calls `_LOGGER.error(msg)` to log a message.  
        LogException - calls `_LOGGER.exception(ex)` to log an exception message.  
        LogFatal - calls `_LOGGER.critical(msg)` to log a message.  
        
        <details>
          <summary>Sample Code</summary>
        ``` python
        .. include:: ../docs/include/samplecode/SISession/SystemLogger.py
        ```
        <br/>
        Create A New Session For Each Module
        ``` python
        .. include:: ../docs/include/samplecode/SISession/SystemLogger_02.py
        ```
        </details>
        """
        return self._fSystemLogger
    

    @SystemLogger.setter
    def SystemLogger(self, value:logging.Logger) -> None:
        """ 
        Sets the SystemLogger property value.
        """
        if value != None:
            if isinstance(value, (logging.Logger)):
                self._fSystemLogger = value


    @property
    def Name(self) -> str:
        """ 
        Gets the Name property value.

        Returns:
            The session name used for Log Entries.
        
        The session name helps you to identify Log Entries from
        different sessions in the SmartInspect Console. If you set
        this property to null, the session name will be empty when
        sending Log Entries.
        """
        return self._fName
    

    @Name.setter
    def Name(self, value:str) -> None:
        """ 
        Sets the Name property value.
        """
        name:str = ""

        if (value != None):
            name = value

        if (self._fIsStored):
            self._fParent._UpdateSession(self, name, self._fName)

        self._fName = name


    @property
    def Parent(self):
        """ 
        Gets the Name property value.

        Returns:
            The parent SmartInspect instance that owns the session.

        The parent of a session is a SmartInspect instance. It is
        responsible for sending the packets to the SmartInspect Console
        or for writing them to a file. If the SmartInspect.Enabled
        property of the parent is false, all logging methods
        of this class will return immediately and do nothing.
        """
        return self._fParent
    

    ###################################################################################
    # Internal methods follow after this.
    #
    # NOTE - Keep them in alphabetical order for Documentation generator!
    ###################################################################################


    def _GetThreadTitle(self, thread:Thread, titlePrefix:str=None) -> str:
        """
        Formulates a thread title if one was not supplied by the user.
        
        Args:
            thread (Thread):
                Thread to obtain titling information from.
            titlePrefix (str):
                Title prefix to add thread-derived title to.

        Returns:
            The thread title in the form of "prefix: thread.name (id = thread.id)".
        """
        # if no thread object supplied then don't bother.
        if (thread == None):
            return "No Thread Object"

        title:str = titlePrefix

        # if thread name not set, then use the thread id value.
        name:str = thread.name
        if ((name == None) or (len(name) == 0)):
            name = "Id = " + str(thread.ident)
        else:
            name += " (Id = " + str(thread.ident) + ")"

        # if title not set, then use default title.
        if ((title == None) or (len(title) == 0)):
            title = "Thread info:"

        return title + " " + name


    def _LogObjectBuildContext(self, groupTitle:str, instance:object, members, ctx:SIInspectorViewerContext, excludeNonPublic:bool, excludeBuiltIn:bool, excludeMethods:bool=False, excludeProperties:bool=False) -> None:
        """
        Adds inspect.getmember() data block to a context viewer for logging.

        Args:
            groupTitle (str):
                The block title to display in the Console.
            instance (object):
                The object whose fields and properties should be logged.
            members (object):
                Data returned from the call to inspect.getmembers() function.
            ctx (SIInspectorViewerContext):
                Inspector viewer context instance.
            excludeNonPublic (bool):
                Specifies if non public member items (e.g. "_x" prefix) should 
                be excluded from the log data.
            excludeBuiltIn (bool):
                Specifies if non public "built-in" member items (e.g. "__x" prefix) should 
                be excluded from the log data.
            excludeMethods (bool):
                Specifies if method or function member items (e.g. "<bound method" or "<function " prefixes)
                should be excluded from the log data.
            excludeProperties (bool):
                Specifies if members decorated with a "@property" attribute should be 
                excluded from the log data.
        """
        # Example of inspect.getmembers() output:
        # - PropertyBool : True
        # - PropertyString : 'This is a string property value'
        # - PublicEvent : <bound method InstanceGetMembersTestClass.PublicEvent of <__main__.InstanceGetMembersTestClass object at 0x0000026B84569AC0>>
        # - PublicFunctionString : <bound method InstanceGetMembersTestClass.PublicFunctionString of <__main__.InstanceGetMembersTestClass object at 0x0000026B84569AC0>>
        # - PublicMethod : <bound method InstanceGetMembersTestClass.PublicMethod of <__main__.InstanceGetMembersTestClass object at 0x0000026B84569AC0>>
        # - PublicStaticFunction : <function InstanceGetMembersTestClass.PublicStaticFunction at 0x0000026B859F1EE0>
        # - PublicStaticMethod : <function InstanceGetMembersTestClass.PublicStaticMethod at 0x0000026B859F1E50>
        # - STATIC_VAR_BOOL : True
        # - STATIC_VAR_INT : 69
        # - STATIC_VAR_STRING : 'Static String'
        # - _InstanceGetMembersTestClass__fPropertyBool : True
        # - _InstanceGetMembersTestClass__fPropertyBoolDynamic : True
        # - _InstanceGetMembersTestClass__fPropertyString : 'This is a string property value'
        # - _InstanceGetMembersTestClass__fPropertyStringDynamic : 'This is a INTERNAL string property value'

        iList:list[str] = []

        # add member data to context viewer.
        for name, data in members:

            # are we excluding nonpublic members?
            if (excludeNonPublic) and (name.startswith('_')):
                continue

            # are we excluding built-in members?
            if (excludeBuiltIn) and (name.startswith('__')):
                continue

            # exclude functions and methods - just looking for field or property values here.
            if ((excludeMethods) and (str(data).startswith("<"))):
                continue

            # are we excluding @property methods?
            if (excludeProperties):
                attr = getattr(type(instance), name, None)
                if (attr != None): 
                    if (isinstance(attr, property)):
                        continue

            sb:str = ""

            try:
            
                sb += ctx.EscapeItem(name)
                sb += "="
                sb += ctx.EscapeItem(SIObjectRenderer.RenderObject(data))
            
            except Exception as ex:
            
                sb += "<not accessible>"

            # add context entry to the list.
            iList.append(sb)
            sb = ""

        # sort context items - the member name is the first thing displayed
        # in the item, so the list is sorted by member name.
        # note that in Python, UPPER-case items are sorted above lower-case items,
        # so we use the "key=str.lower) syntax to force the case-insensitive sort.
        iList.sort(key=str.lower)

        # begin a new group and append the list to the inspector context.
        ctx.StartGroup(groupTitle)
        for line in iList:
            ctx.AppendLine(str(line))

        # clear list.
        iList.clear()


    def _SendContext(self, level:SILevel, title:str, lt:SILogEntryType, ctx:SIViewerContext, colorValue:SIColors=None) -> None:
        """
        Sends a Log Entry packet of information that contains viewer context.

        Args:
            level (SILevel):
                Level to set in the Log Entry.
            title (str):
                Title to set in the Log Entry.
            lt (SILogEntryType):
                Log Entry Type to set in the Log Entry.
            ctx (SIViewerContext):
                Viewer Context to set in the Log Entry.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
        """
        self._SendLogEntry(level, title, lt, ctx.ViewerId, colorValue, ctx.ViewerData)


    def _SendControlCommand(self, ct:SIControlCommandType, data:BytesIO) -> None:
        """
        Sends a ControlCommand packet of information.

        Args:
            ct
                SIControlCommandType to set in the ControlCommand.
            data
                Data to set in the ControlCommand.
        """
        controlCommand:SIControlCommand = SIControlCommand(ct)
        controlCommand.Data = data
        controlCommand.Level = SILevel.Control
        self._fParent.SendControlCommand(controlCommand)


    def _SendLogEntry(self, level:SILevel, title:str, lt:SILogEntryType, vi:SIViewerId, colorValue:SIColors=None, data:BytesIO=None) -> None:
        """
        Sends a Log Entry packet of information.

        Args:
            level (SILevel):
                Level to set in the Log Entry.
            title (str):
                Title to set in the Log Entry.
            lt (SILogEntryType):
                Log Entry Type to set in the Log Entry.
            vi (SIViewerId):
                Viewer Id to set in the Log Entry.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
            data
                Data to set in the Log Entry.
        """
        # validations.
        if (title == None):
            title = ""

        logEntry:SILogEntry = SILogEntry(lt, vi)

        # set the properties we already know.
        logEntry.Timestamp = self._fParent.Now()
        logEntry.Title = title
        logEntry.SessionName = self._fName # our session name
        logEntry.Level = level

        if (data != None):
            logEntry.Data = data

        # was a background color specified?
        # if no, then use default (white) background color assigned to this session.
        # if yes, then ensure it is transparent.
        if (colorValue == None):
            logEntry.ColorBG = self._fColorBG
        elif (isinstance(colorValue, SIColors)):
            colorObj:SIColor = SIColor(colorValue.value)
            logEntry.ColorBG = colorObj
        else:
            colorObj:SIColor = SIColor(colorValue)
            if (colorObj.A != 0):
                colorObj = SIColor.FromArgb(0, colorObj.R, colorObj.G, colorObj.B)
            logEntry.ColorBG = colorObj

        # send the new Log Entry.
        self._fParent.SendLogEntry(logEntry)


    def _SendProcessFlow(self, level:SILevel, title:str, pt:SIProcessFlowType) -> None:
        """
        Sends a Process Flow packet of information.

        Args:
            level (SILevel):
                Level to set in the Log Entry.
            title (str):
                Title to set in the Log Entry.
            pt (SIProcessFlowType):
                ProcessFlowType to set in the Log Entry.
        """
        processFlow:SIProcessFlow = SIProcessFlow(pt)
        processFlow.Timestamp = self._fParent.Now()
        processFlow.Title = title
        processFlow.Level = level
        self._fParent.SendProcessFlow(processFlow)


    def _SendWatch(self, level:SILevel, name:str, value:str, wt:SIWatchType) -> None:
        """
        Sends a Watch packet of information.

        Args:
            level (SILevel):
                Level to set in the Log Entry.
            name (str):
                Name to set in the Log Entry.
            value (str):
                Value to set in the Log Entry.
            wt (SIWatchType):
                WatchType to set in the Log Entry.
        """
        watch:SIWatch = SIWatch(wt)
        watch.Timestamp = self._fParent.Now()
        watch.Name = name
        watch.Value = value
        watch.Level = level
        self._fParent.SendWatch(watch)


    def _UpdateCheckpoint(self, name:str, increment:bool) -> int:
        """
        Updates a named checkpoint counter in a thread-safe manner.
        
        Args:
            name
                Checkpoint counter name to update.
            increment
                True to increment the named counter; False to decrement.

        Returns:
            The updated named checkpoint counter value.
        """
        value:int = 0

        with self._fLock:

            if name in self._fCheckpoints.keys():
                value = int(self._fCheckpoints[name])
            else:
                value = 0

            if (increment):
                value = value + 1
            else:
                value = value - 1

            self._fCheckpoints[name] = value

        return value


    def _UpdateCounter(self, name:str, increment:bool) -> int:
        """
        Updates a named counter in a thread-safe manner.
        
        Args:
            name
                Counter name to update.
            increment
                True to increment the named counter; False to decrement.

        Returns:
            The updated named counter value.
        """
        value:int = 0

        with self._fLock:

            if name in self._fCounters.keys():
                value = int(self._fCounters[name])
            else:
                value = 0

            if (increment):
                value = value + 1
            else:
                value = value - 1

            self._fCounters[name] = value

        return value


    ###################################################################################
    # Public Log methods follow after this.
    #
    # NOTE - Keep them in alphabetical order for Documentation generator!
    ###################################################################################


    def AddCheckpoint(self, level:SILevel=None, name:str=None, details:str=None, colorValue:SIColors=None) -> None:
        """
        Increments the counter of a named checkpoint and logs a
        message with a custom log level and an optional message.

        Args:
            level (SILevel):
                The log level of this method call.
            name (str):
                The name of the checkpoint to increment.
            details (str):
                An optional message to include in the resulting log entry.
                Can be null / None.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method increments the counter for the given checkpoint
        and then logs a message using "%checkpoint% #N" as title where
        %checkpoint% stands for the name of the checkpoint and N for
        the incremented counter value. The initial value of the counter
        for a given checkpoint is 0. Specify the details parameter to
        include an optional message in the resulting log entry. You
        can use the ResetCheckpoint method to reset the counter to 0
        again. 
        """
        if (not self.IsOn(level)):
            return
        
        # validations.
        if (name == None):
            name = "Checkpoint"
        
        try:

            # update checkpoint value.                
            value:int = self._UpdateCheckpoint(name, True)

            # format checkpoint message details.
            subtitle:str = ""
            if (details != None):
                subtitle = str.format(" ({0})", details)
            title:str = str.format("{0} #{1}{2}", name, str(value), subtitle)

            # send log entry packet.
            self._SendLogEntry(level, title, SILogEntryType.Checkpoint, SIViewerId.Title, colorValue)

        except Exception as ex:
                
            self.LogInternalError("AddCheckpoint: " + str(ex))


    def ClearAll(self, level:SILevel=None) -> None:
        """
        Resets the whole Console.

        Args:
            level (SILevel):
                The log level of this method call.

        This method resets the whole Console. This means that all
        Watches, Log Entries, Process Flow entries and AutoViews
        will be deleted.
        """
        if (not self.IsOn(level)):
            return

        try:
                
            # send control command.
            self._SendControlCommand(SIControlCommandType.ClearAll, None)

        except Exception as ex:
                
            self.LogInternalError("ClearAll: " + str(ex))


    def ClearAutoViews(self, level:SILevel=None) -> None:
        """
        Clears all AutoViews in the Console.

        Args:
            level (SILevel):
                The log level of this method call.
        """
        if (not self.IsOn(level)):
            return

        try:
                
            # send control command.
            self._SendControlCommand(SIControlCommandType.ClearAutoViews, None)

        except Exception as ex:
                
            self.LogInternalError("ClearAutoViews: " + str(ex))


    def ClearLog(self, level:SILevel=None) -> None:
        """
        Clears all Log Entries in the Console.

        Args:
            level (SILevel):
                The log level of this method call.
        """
        if (not self.IsOn(level)):
            return

        try:
                
            # send control command.
            self._SendControlCommand(SIControlCommandType.ClearLog, None)

        except Exception as ex:
                
            self.LogInternalError("ClearLog: " + str(ex))


    def ClearProcessFlow(self, level:SILevel=None) -> None:
        """
        Clears all Process Flow entries in the Console.

        Args:
            level (SILevel):
                The log level of this method call.
        """
        if (not self.IsOn(level)):
            return

        try:
                
            # send control command.
            self._SendControlCommand(SIControlCommandType.ClearProcessFlow, None)

        except Exception as ex:
                
            self.LogInternalError("ClearProcessFlow: " + str(ex))


    def ClearWatches(self, level:SILevel=None) -> None:
        """
        Clears all Watches in the Console.

        Args:
            level (SILevel):
                The log level of this method call.
        """
        if (not self.IsOn(level)):
            return

        try:
                
            # send control command.
            self._SendControlCommand(SIControlCommandType.ClearWatches, None)

        except Exception as ex:
                
            self.LogInternalError("ClearWatches: " + str(ex))


    @staticmethod
    def CurrentMethodName() -> str:
        """ 
        Returns the fully-qualified method name of the current stack level in the
        form of "MethodName".

        Returns:
            The fully-qualified method name of the current stack level in the
            form of "MethodName".

        Reflection is used to determine the method name.
        If method info could not be queried, "&lt;Unknown&gt;" is returned.
        
        No exception will be thrown by this method.
        """
        return SISession.GetMethodName(1, False)


    @staticmethod
    def CurrentMethodNameClass() -> str:
        """ 
        Returns the fully-qualified method name of the current stack level in the
        form of "ClassName.MethodName".

        Returns:
            The fully-qualified method name of the current stack level in the
            form of "ClassName.MethodName".

        Reflection is used to determine the method name.
        If method info could not be queried, "&lt;Unknown&gt;" is returned.
        
        No exception will be thrown by this method.
        """
        return SISession.GetMethodName(1, True)


    @staticmethod
    def CurrentMethodNameClassNamespace() -> str:
        """ 
        Returns the fully-qualified method name of the current stack level in the
        form of "Namespace.ClassName.MethodName".

        Returns:
            The fully-qualified method name of the current stack level in the
            form of "Namespace.ClassName.MethodName".

        Reflection is used to determine the method name.
        If method info could not be queried, "&lt;Unknown&gt;" is returned.
        
        No exception will be thrown by this method.
        """
        return SISession.GetMethodName(1, True)


    def DecCounter(self, level:SILevel=None, name:str=None) -> None:
        """
        Decrements a named counter by one and automatically
        sends its name and value as integer watch with a custom log
        level.

        Args:
            level (SILevel):
                The log level of this method call.
            name (str):
                The name of the counter to log.

        The SISession class tracks a list of so called named counters.
        A counter has a name and a value of type integer. This method
        decrements the value for the specified counter by one and then
        sends a normal integer watch with the name and value of the
        counter. The initial value of a counter is 0. To reset the
        value of a counter to 0 again, you can call ResetCounter.

        See IncCounter for a method which increments the value of a
        named counter instead of decrementing it.
        """
        if (not self.IsOn(level)):
            return

        # validations.
        if (name == None):
            self.LogInternalError("DecCounter: name argument is null.")
            return
        
        try:
                
            # send watch packet.
            value:int = self._UpdateCounter(name, False)
            self._SendWatch(level, name, str(value), SIWatchType.Integer)

        except Exception as ex:
                
            self.LogInternalError("DecCounter: " + str(ex))


    def EnterMethod(self, level:SILevel=None, methodName:str=None, colorValue:SIColors=None) -> None:
        """
        Enters a method by using a custom log level.
        The resulting method name consists of the FullName of the
        type of the supplied instance parameter, followed by a dot
        and the supplied methodName argument.
        
        Args:
            level (SILevel):
                The log level of this method call.
            methodName (str):
                The name of the method; otherwise null to retrieve the 
                current method name from inspect data.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
        
        The EnterMethod method notifies the Console that a new
        method has been entered. The Console includes the method in
        the method hierarchy. If this method is used consequently, a
        full call stack is visible in the Console which helps locating
        bugs in the source code. Please see the LeaveMethod method as 
        the counter piece to EnterMethod.
        
        If the methodName is null, then the currently executing method name
        is derived from calling inspect.stack.  The function name, module name,
        and source line number are displayed.
        
        This method uses the SmartInspect.DefaultLevel value if the level
        parameter is set to None (default).  Otherwise, the specified level
        is utilized.
        """
        if (not self.IsOn(level)):
            return

        # if method name was not specified then get it from the stack frame.
        if (methodName is None):
            methodName = SISession.GetMethodName(1, True)  # start=1 excludes our EnterMethod
        
        try:
                
            # send two packets: one log entry, and one process flow entry.
            self._SendLogEntry(level, methodName, SILogEntryType.EnterMethod, SIViewerId.Title, colorValue)
            self._SendProcessFlow(level, methodName, SIProcessFlowType.EnterMethod)

        except Exception as ex:
                
            self.LogInternalError("EnterMethod: " + str(ex))


    def EnterMethodParmList(self, level:SILevel=None, methodName:str=None, colorValue:SIColors=None) -> SIMethodParmListContext:
        """
        Logs method name entry and creates a custom view context for method input parameteres
        when placed at the start of a method by using the specified log level.  
        Reflection is used to retrieve the current method's name if the `method` argument is null.
        
        Args:
            level (SILevel):
                The log level of this method call.
            methodName (str):
                The name of the method; otherwise null to retrieve the 
                current method name from inspect data.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
                
        Returns:
            A `SIMethodParmListContext` trace viewer context used to log method input parameters.
        
        The EnterMethodParmList method notifies the Console that a new
        method has been entered. The Console includes the method in
        the method hierarchy. If this method is used consequently, a
        full call stack is visible in the Console which helps locating
        bugs in the source code. Please see the LeaveMethod method as 
        the counter piece to EnterMethod.
        
        If the methodName is null, then the currently executing method name
        is derived from calling inspect.stack.  The function name, module name,
        and source line number are displayed.
        
        This method uses the SmartInspect.DefaultLevel value if the level
        parameter is set to None (default).  Otherwise, the specified level
        is utilized.
        """
        if (not self.IsOn(level)):
            return SIMethodParmListContext(methodName or '')

        # if method name was not specified then get it from the stack frame.
        if (methodName is None):
            methodName = SISession.GetMethodName(1, True)  # start=1 excludes our EnterMethodParmList
        
        try:
                
            # send two packets: one log entry, and one process flow entry.
            self._SendLogEntry(level, methodName, SILogEntryType.EnterMethod, SIViewerId.Title, colorValue)
            self._SendProcessFlow(level, methodName, SIProcessFlowType.EnterMethod)

            return SIMethodParmListContext(methodName)

        except Exception as ex:
                
            self.LogInternalError("EnterMethodParmList: " + str(ex))


    def EnterProcess(self, level:SILevel=None, processName:str=None) -> None:
        """
        Enters a new process by using a custom log level.
        
        Args:
            level (SILevel):
                The log level of this method call.
            processName (str):
                The name of the process.
        
        The EnterProcess method notifies the Console that a new
        process has been entered. The Console displays this process
        in the Process Flow toolbox. Please see the LeaveProcess
        method as the counter piece to EnterProcess.
        
        This method uses the SmartInspect.DefaultLevel value if the level
        parameter is set to None (default).  Otherwise, the specified level
        is utilized.
        """
        if (not self.IsOn(level)):
            return

        # validations.
        if (processName == None):
            processName = ""
        
        try:
                
            # send two packets: one for process name entry, and one for process thread entry.
            self._SendProcessFlow(level, processName, SIProcessFlowType.EnterProcess)
            self._SendProcessFlow(level, "Main Thread", SIProcessFlowType.EnterThread)

        except Exception as ex:
                
            self.LogInternalError("EnterProcess: " + str(ex))


    def EnterThread(self, level:SILevel=None, threadName:str=None) -> None:
        """
        Enters a new thread by using a custom log level.
        
        Args:
            level (SILevel):
                The log level of this method call.
            threadName (str):
                The name of the thread.
        
        The EnterThread method notifies the Console that a new
        thread has been entered. The Console displays this thread
        in the Process Flow toolbox. Please see the LeaveThread
        method as the counter piece to EnterThread.
        
        This method uses the SmartInspect.DefaultLevel value if the level
        parameter is set to None (default).  Otherwise, the specified level
        is utilized.
        """
        if (not self.IsOn(level)):
            return

        # validations.
        if (threadName == None):
            threadName = ""
        
        try:
                
            # send process thread entry packet.
            self._SendProcessFlow(level, threadName, SIProcessFlowType.EnterThread)

        except Exception as ex:
                
            self.LogInternalError("EnterThread: " + str(ex))


    @staticmethod
    def GetMethodName(stackLevel:int=0, includeNameSpace:bool=False, includeClassName:bool=False) -> str:
        """
        Returns the callers method name for the specified stack level.
        
        Args:
            stackLevel (int):
        	    The Stack Frame level to query - defaults to 1 if zero is specified.
            includeSourcePos (bool):
                True to append the module name and source line # to the method name; 
                otherwise False (default) to return only the method name.
            includeNameSpace (bool):
                True to prefix the returned method name with the name-space identifier; otherwise False to
                not return the name-space identifier.
            includeClassName (bool):
                True to prefix the returned method name with the class name; otherwise False to
                not return the class name.
        
        Returns:
            The callers method name.
        
        Reflection is used to determine the method name for the specified stack level.  
        If method info could not be queried, "&lt;Unknown&gt;" is returned.
        
        No exception will be thrown by this method.
        """   
        
        UNKNOWN: str = "<Unknown>"
        methodName: str = UNKNOWN
        className: str = None

        try:

            # the call stack.
            stack:list[FrameInfo] = inspect.stack(0)

            # bypass the 0 frame index, as that would be the function we are currently in.
            stackLevel = stackLevel + 1

            # validations.
            if (stackLevel < 1):
                stackLevel = 1
            if (stackLevel > len(stack) - 1):
                stackLevel = len(stack) - 1

            # get the stack frame the caller is interested in.
            stackFrame:FrameInfo = stack[stackLevel]
            if (stackFrame == None):
                return methodName

            # extract the parts of the stack frame.
            filepath, line, funcname, context = stackFrame[1:5]
            methodName = funcname.strip()

            # if not including source position info then we are done.
            if (not includeNameSpace):
                return methodName

            # drop the path and extension from the file name.
            moduleName = os.path.basename(filepath)
            #moduleNameNoExt = os.path.splitext(os.path.basename(filepath))[0]

            # add source position to method name.
            if (includeNameSpace) and (moduleName != None):
                methodName += " ({0}, line {1})".format(moduleName, line)

            # return to caller.
            return methodName

        except Exception as ex:

            return UNKNOWN


    def IncCounter(self, level:SILevel=None, name:str=None) -> None:
        """
        Increments a named counter by one and automatically
        sends its name and value as integer watch with a custom log
        level.

        Args:
            level (SILevel):
                The log level of this method call.
            name (str):
                The name of the counter to log.
        
        The SISession class tracks a list of so called named counters.
        A counter has a name and a value of type integer. This method
        increments the value for the specified counter by one and then
        sends a normal integer watch with the name and value of the
        counter. The initial value of a counter is 0. To reset the
        value of a counter to 0 again, you can call ResetCounter.

        See DecCounter for a method which decrements the value of a
        named counter instead of incrementing it.
        """
        if (not self.IsOn(level)):
            return

        # validations.
        if (name == None):
            self.LogInternalError("IncCounter: name argument is null.")
            return
        
        try:
                
            # send watch packet.
            value:int = self._UpdateCounter(name, True)
            self._SendWatch(level, name, str(value), SIWatchType.Integer)

        except Exception as ex:
                
            self.LogInternalError("IncCounter: " + str(ex))


    def IsOn(self, level:SILevel=None) -> bool:
        """ 
        Indicates if information can be logged for a certain log level or not.  

        Args:
            level (SILevel):
                The log level to check for.

        Returns:
            True if information can be logged and false otherwise.
        
        This method is used by the logging methods in this class
        to determine if information should be logged or not. When
        extending the SISession class by adding new log methods to a
        derived class it is recommended to call this method first.
        """
        # use the session level if level not specified on the method call.
        if (level == None):
            level = self._fParent.DefaultLevel

        return self._fActive and \
                self._fParent.Enabled and \
                (level >= self._fLevel) and \
                (level >= self._fParent.Level)


    def LeaveMethod(self, level:SILevel=None, methodName:str=None, colorValue:SIColors=None) -> None:
        """
        Leaves a method by using a custom log level.
        
        Args:
            level (SILevel):
                The log level of this method call.
            methodName (str):
                The name of the method; otherwise null to retrieve the 
                current method name from inspect data.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
        
        The LeaveMethod method notifies the Console that a method
        has been left. The Console closes the current method in the
        method hierarchy. If this method is used consequently, a full
        call stack is visible in the Console which helps locating bugs
        in the source code. Please see the EnterMethod method as the 
        counter piece to EnterMethod.
       
        This method uses the SmartInspect.DefaultLevel value if the level
        parameter is set to None (default).  Otherwise, the specified level
        is utilized.
        """
        if (not self.IsOn(level)):
            return

        # if method name was not specified then get it from the stack frame.
        if (methodName is None):
            methodName = SISession.GetMethodName(1, True)  # start=1 excludes our EnterMethod
        
        try:
                
            # send two packets: one log entry, and one process flow entry.
            self._SendLogEntry(level, methodName, SILogEntryType.LeaveMethod, SIViewerId.Title, colorValue)
            self._SendProcessFlow(level, methodName, SIProcessFlowType.LeaveMethod)

        except Exception as ex:
                
            self.LogInternalError("LeaveMethod: " + str(ex))


    def LeaveProcess(self, level:SILevel=None, processName:str=None) -> None:
        """
        Leaves a process by using a custom log level.
        
        Args:
            level (SILevel):
                The log level of this method call.
            processName (str):
                The name of the process.
        
        The LeaveProcess method notifies the Console that a process
        has finished. The Console displays this change in the Process
        Flow toolbox. Please see the EnterProcess method as the
        counter piece to LeaveProcess.
        
        This method uses the SmartInspect.DefaultLevel value if the level
        parameter is set to None (default).  Otherwise, the specified level
        is utilized.
        """
        if (not self.IsOn(level)):
            return

        # validations.
        if (processName == None):
            processName = ""
        
        try:
                
            # send two packets: one for process thread exit, and one for process name exit.
            self._SendProcessFlow(level, "Main Thread", SIProcessFlowType.LeaveThread)
            self._SendProcessFlow(level, processName, SIProcessFlowType.LeaveProcess)

        except Exception as ex:
                
            self.LogInternalError("LeaveProcess: " + str(ex))


    def LeaveThread(self, level:SILevel=None, threadName:str=None) -> None:
        """
        Leaves a thread by using a custom log level.
        
        Args:
            level (SILevel):
                The log level of this method call.
            threadName (str):
                The name of the thread.
        
        The LeaveThread method notifies the Console that a thread
        has finished. The Console displays this change in the Process
        Flow toolbox. Please see the EnterThread method as the
        counter piece to LeaveThread.
        
        This method uses the SmartInspect.DefaultLevel value if the level
        parameter is set to None (default).  Otherwise, the specified level
        is utilized.
        """
        if (not self.IsOn(level)):
            return

        # validations.
        if (threadName == None):
            threadName = ""
        
        try:
                
            # send process thread exit packet.
            self._SendProcessFlow(level, threadName, SIProcessFlowType.LeaveThread)

        except Exception as ex:
                
            self.LogInternalError("LeaveThread: " + str(ex))


    def LogAppDomain(self, level:SILevel=None, title:str=None, colorValue:SIColors=None) -> None:
        """
        Logs information about an application and its setup with a custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method logs information about the current application and its setup.
        This is not quite the same as the C# equivalent, but it does log similar properties.
        """
        if (not self.IsOn(level)):
            return

        ctx:SIInspectorViewerContext = SIInspectorViewerContext()
        try:

            # default title if one was not supplied.
            if (title == None) or (len(title) == 0):
                title = "Application Domain details"

            basename:str = UNKNOWN_VALUE
            dirname:str = UNKNOWN_VALUE

            if (len(sys.argv) > 0):
                basename = os.path.basename(sys.argv[0])
                dirname = os.path.dirname(sys.argv[0])

            ctx.StartGroup("General")
            ctx.AppendKeyValue("Executable Name", basename)
            ctx.AppendKeyValue("Executable Directory", dirname)
            ctx.AppendKeyValue("Arguments (sys.argv)", str(sys.argv))

            ctx.StartGroup("Setup")
            ctx.AppendKeyValue("Current Working Directory", os.getcwd())
            ctx.AppendKeyValue("Python Version", platform.python_version())

            # send the packet.
            self._SendContext(level, title, SILogEntryType.Text, ctx, colorValue)
        
        except Exception as ex:
        
            self.LogInternalError("LogAppDomain: " + str(ex))


    def LogArray(self, level:SILevel=None, title:str=None, oArray:array=None, colorValue:SIColors=None) -> None:
        """
        Logs the content of an array with a custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console - "Current stack trace" is used if one is not supplied.
            oArray (array):
                The array to log.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method iterates through the supplied array and calls SIObjectRenderer.RenderObject to
        render every element into a string. These elements will be displayed in a listview in the Console.
        """
        self.LogCollection(level, title, oArray, colorValue)


    def LogAssert(self, condition:bool=None, title:str=None, colorValue:SIColors=None) -> None:
        """
        Logs an assert message if a condition is false with
        a log level of SILevel.Error.
        
        Args:
            condition (bool):
                The condition to check.
            title (str):
                The title of the Log Entry.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        An assert message is logged if this method is called with a
        condition parameter of the value false. No Log Entry
        is generated if this method is called with a
        condition parameter of the value true.

        A typical usage of this method would be to test if a variable
        is not set to null before you use it. To do this, you just need
        to insert a LogAssert call to the code section in question with
        "instance != null" as first parameter. If the reference is null
        and thus the expression evaluates to false, a message is logged.
        """
        if (not self.IsOn(SILevel.Error)):
            return

        try:

            if (not condition):

                # send the packet.
                self._SendLogEntry(SILevel.Error, title, SILogEntryType.Assert, SIViewerId.Title, colorValue)

        except Exception as ex:
                
            self.LogInternalError("LogAssert: " + str(ex))


    def LogAssigned(self, level:SILevel=None, name:str=None, value:object=None, colorValue:SIColors=None) -> None:
        """
        Logs whether a variable is assigned or not with a custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            name (str):
                The name of the variable.
            value (object):
                The variable value which should be checked for null.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        If the value argument is null, then ": Not assigned",
        otherwise ": Assigned" will be appended to the name before
        the Log Entry is sent.

        This method is useful to check source code for null references
        in places where you experienced or expect problems and want to
        log possible null references.
        """
        if (not self.IsOn(level)):
            return

        # validations.
        if (name is None):
            name = "<null name>"

        # not sure why SI authors chose to use "LogMessage" here, since a "level" was 
        # passed and an "IsOn(level)" check is performed.
        # this will only log a message if the level is Message or less!

        try:

            # send log entry packet.
            if (value != None):
                self.LogMessage(str.format("{0}: Assigned", name), colorValue=colorValue)
                #self.LogText(level, str.format("{0}: Assigned", name), "", colorValue)
            else:
                self.LogMessage(str.format("{0}: Not assigned", name), colorValue=colorValue)
                #self.LogText(level, str.format("{0}: Not assigned", name), "", colorValue)

        except Exception as ex:
                
            self.LogInternalError("LogAssigned: " + str(ex))


    def LogBinary(self, level:SILevel=None, title:str=None, buffer:bytes=None, offset:int=None, count:int=None, colorValue:SIColors=None) -> None:
        """
        Logs a byte array with a custom log level and
        displays it in a hex viewer.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            buffer (bytes):
                The byte array to display in the hex viewer.
            offset (int):
                The byte offset (zero-based) of buffer at which to display data from.
            count (int):
                The amount of bytes to display.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
        """
        if (not self.IsOn(level)):
            return

        # validations.
        if (offset == None) and (count != None):
            self.LogInternalError("LogBinary: count argument is required if offset argument is not null.")
            return

        if (offset != None) and (count == None):
            self.LogInternalError("LogBinary: offset argument is required if count argument is not null.")
            return

        if (offset != None) and (count != None) and (buffer != None):
            if ((offset + count) > len(buffer)):
                self.LogInternalError("LogBinary: offset + count arguments exceed the length of the buffer.")
                return

        ctx:SIBinaryViewerContext = SIBinaryViewerContext()
        try:

            if ((offset == None) and (count == None)):                
                ctx.AppendBytes(buffer)
            else:
                ctx.AppendBytes(buffer[offset:offset + count])

            # send the packet.
            self._SendContext(level, title, SILogEntryType.Binary, ctx, colorValue)
                
        except Exception as ex:
                
            self.LogInternalError("LogBinary: " + str(ex))
                

    def LogBinaryFile(self, level:SILevel=None, title:str=None, fileName:str=None, colorValue:SIColors=None) -> None:
        """
        Logs a binary file and displays its content in
        a hex viewer using a custom title and custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            fileName (str):
                The binary file to display in a hex viewer.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
        """
        self.LogCustomFile(level, title, fileName, SILogEntryType.Binary, SIViewerId.Binary, colorValue)


    def LogBinaryStream(self, level:SILevel=None, title:str=None, stream:BufferedReader=None, colorValue:SIColors=None) -> None:
        """
        Logs a binary stream with a custom log level and
        displays its content in a hex viewer.
        
        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            stream (BufferedReader):
                The binary stream to display in a hex viewer.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
        """
        self.LogCustomStream(level, title, stream, SILogEntryType.Binary, SIViewerId.Binary, colorValue)


    def LogBitmapFile(self, level:SILevel=None, title:str=None, fileName:str=None, colorValue:SIColors=None) -> None:
        """
        Logs a bitmap file and displays it in the Console
        using a custom title and custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            fileName (str):
                The bitmap file to display in the Console.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
        """
        self.LogCustomFile(level, title, fileName, SILogEntryType.Graphic, SIViewerId.Bitmap, colorValue)


    def LogBitmapStream(self, level:SILevel=None, title:str=None, stream:BufferedReader=None, colorValue:SIColors=None) -> None:
        """
        Logs a stream with a custom log level and
        interprets its content as a bitmap.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            stream (BufferedReader):
                The stream to display as bitmap.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
        """
        self.LogCustomStream(level, title, stream, SILogEntryType.Graphic, SIViewerId.Bitmap, colorValue)


    def LogBool(self, level:SILevel=None, name:str=None, value:bool=None, colorValue:SIColors=None) -> None:
        """
        Logs a bool value with a custom log level.
        
        Args:
            level (SILevel):
                The log level of this method call.
            name (str):
                The variable name.
            value (bool):
                The variable value.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method logs the name and value of a boolean variable.
        A title like "name = True" will be displayed in the Console.
        """
        if (not self.IsOn(level)):
            return

        # validations.
        if (name is None):
            name = "<null name>"

        try:

            # use "True"/"False" in case other boolean values passed (e.g. 0/1, yes/no, on/off, etc).
            v:str
            if (value == True):
                v:str = "True"
            else:
                v:str = "False"

            # send log entry packet.
            title:str = str.format("{0} = {1}", name, v)
            self._SendLogEntry(level, title, SILogEntryType.VariableValue, SIViewerId.Title, colorValue)

        except Exception as ex:
                
            self.LogInternalError("LogBool: " + str(ex))


    def LogByte(self, level:SILevel=None, name:str=None, value:int=None, includeHex:bool=False, colorValue:SIColors=None) -> None:
        """
        Logs a byte value with an optional hexadecimal representation 
        and custom log level.
        
        Args:
            level (SILevel):
                The log level of this method call.
            name (str):
                The variable name.
            value (int):
                The variable value.
            includeHex (bool):
                Indicates if a hexadecimal representation should be included (True) or not (False).
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method logs the name and value of a single byte variable.
        A title like "name = 10" will be displayed in the Console.
        """
        if (not self.IsOn(level)):
            return

        # validations.
        if (name is None):
            name = "<null name>"

        try:

            vhex:str = ""
            if (includeHex):
                vhex = " (" + hex(value).upper() + ")"
                if (value < 0):
                    vhex = vhex.replace("-","")     # remove minus sign for negative values.
                vhex = vhex.replace("0X","0x")      # make "0X" lower-case since hex values will be in upper-case

            # send log entry packet.
            title:str = str.format("{0} = {1}{2}", name, str(value), vhex)
            self._SendLogEntry(level, title, SILogEntryType.VariableValue, SIViewerId.Title, colorValue)

        except Exception as ex:
                
            self.LogInternalError("LogByte: " + str(ex))


    def LogChar(self, level:SILevel=None, name:str=None, value:chr=None, colorValue:SIColors=None) -> None:
        """
        Logs a chr value with a custom log level.
        
        Args:
            level (SILevel):
                The log level of this method call.
            name (str):
                The variable name.
            value (chr):
                The variable value.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method logs the name and value of a chr variable.
        A title like "name = 'c'" will be displayed in the Console.
        """
        if (not self.IsOn(level)):
            return

        # validations.
        if (name is None):
            name = "<null name>"

        try:

            # send log entry packet.
            title:str = str.format("{0} = '{1}'", name, str(value))
            self._SendLogEntry(level, title, SILogEntryType.VariableValue, SIViewerId.Title, colorValue)

        except Exception as ex:
                
            self.LogInternalError("LogChar: " + str(ex))


    def LogCollection(self, level:SILevel=None, title:str=None, oColl:Collection=None, colorValue:SIColors=None) -> None:
        """
        Logs the content of a collection with a custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console; "Current stack trace" is used if one is not supplied.
            oColl (Collection):
                The collection to log.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method iterates through the supplied collection and calls SIObjectRenderer.RenderObject to
        render every value into a string. These values will be displayed in a listview in the Console.
        """
        self.LogEnumerable(level, title, oColl, colorValue)


    def LogColored(self, level:SILevel=None, colorValue:SIColors=None, title:str=None) -> None:
        """
        Logs a colored message with a custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
            title (str):
                The message to log.
        """
        if (not self.IsOn(level)):
            return

        try:
                
            # send the packet.
            self._SendLogEntry(level, title, SILogEntryType.Message, SIViewerId.Title, colorValue, None)

        except Exception as ex:
                
            self.LogInternalError("LogColored: " + str(ex))


    def LogComplex(self, level:SILevel=None, name:str=None, value:complex=None, colorValue:SIColors=None) -> None:
        """
        Logs a complex value with a custom log level.
        
        Args:
            level (SILevel):
                The log level of this method call.
            name (str):
                The variable name.
            value (float):
                The variable value.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method logs the name and value of a complex variable.
        A title like "name = 3.14159" will be displayed in the Console.
        """
        if (not self.IsOn(level)):
            return

        # validations.
        if (name is None):
            name = "<null name>"

        try:

            # send log entry packet.
            title:str = str.format("{0} = {1}", name, str(value))
            self._SendLogEntry(level, title, SILogEntryType.VariableValue, SIViewerId.Title, colorValue)

        except Exception as ex:
                
            self.LogInternalError("LogComplex: " + str(ex))


    def LogConditional(self, level:SILevel=None, condition:bool=None, title:str=None, colorValue:SIColors=None) -> None:
        """
        Logs a conditional message with a custom log level. The message 
        is created with a format string and a related array of arguments.

        Args:
            level (SILevel):
                The log level of this method call.
            condition (bool):
                The condition to evaluate.
            title (str):
                The title of the conditional message.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
        
        This method only sends a message if the passed 'condition'
        argument evaluates to true. If 'condition' is false, this
        method has no effect and nothing is logged. This method is
        thus the counter piece to LogAssert.

        This version of the method accepts a format string and a
        related array of arguments. These parameters will be passed to
        the String.Format method and the resulting string will be the
        conditional message.
        """
        if (not self.IsOn(level)):
            return

        try:

            if (condition):

                # send the packet.
                self._SendLogEntry(level, title, SILogEntryType.Conditional, SIViewerId.Title, colorValue)

        except Exception as ex:
                
            self.LogInternalError("LogConditional: " + str(ex))


    def LogCurrentAppDomain(self, level:SILevel=None, title:str=None, colorValue:SIColors=None) -> None:
        """
        Logs information about the current application and its setup with a custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method logs information about the current application and its setup.
        This is not quite the same as the C# equivalent, but it does log similar properties.
        """
        self.LogAppDomain(level, title, colorValue)


    def LogCurrentStackTrace(self, level:SILevel=None, title:str=None, limit:int=None, colorValue:SIColors=None) -> None:
        """
        Logs the current stack trace with a custom title and custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console; "Current stack trace" is used if one is not supplied.
            limit (int):
                The number of frames to print (specify None to print all remaining frames).
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method logs the current stack trace. The resulting Log Entry contains all methods including the
        related classes that are currently on the stack. Furthermore, the filename, line and columns numbers are included.

        Please note that the stack frame information results will NOT include 2 frames that are used
        by the SmartInspect API to process the frame data.
        """
        if (not self.IsOn(level)):
            return

        # default title if one was not supplied.
        if ((title == None) or (len(title) == 0)):
            title = "Current stack trace"

        try:

            # get current stack trace.
            strace:list[FrameInfo] = inspect.stack()

            # skip our "LogCurrentStackTrace" method and start at the caller to this function.
            startFrame:int = 1

            # call overloaded method.
            self.LogStackTrace(level, title, strace, startFrame, limit, colorValue)

        except Exception as ex:
            
            self.LogInternalError("LogCurrentStackTrace: " + str(ex))


    def LogCurrentThread(self, level:SILevel=None, title:str=None, colorValue:SIColors=None) -> None:
        """
        Logs information about the current thread with a custom title and custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method logs information about the current thread. This
        includes its name, its current state and more.

        LogCurrentThread is especially useful in a multi-threaded
        program like in a network server application. By using this
        method you can easily track all threads of a process and
        obtain detailed information about them.

        See LogThread for a more general method which can handle any thread.
        public void LogCurrentThread(Level level, string title)
        """
        if (not self.IsOn(level)):
            return

        # get reference to the current thread.
        thread:Thread = current_thread() 

        # set default title if one was not supplied.
        if ((title == None) or (len(title) == 0)):
            title = self._GetThreadTitle(thread, "Current thread info:")

        # call LogThread method to do the rest.
        self.LogThread(level, title, thread, colorValue)


    def LogCustomContext(self, level:SILevel=None, title:str=None, lt:SILogEntryType=None, ctx:SIViewerContext=None, colorValue:SIColors=None) -> None:
        """
        Logs a custom viewer context with a custom log level.
        viewer ID and custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            lt (SILogEntryType):
                The custom Log Entry type.
            ctx (SIViewerContext):
                The viewer context which holds the actual data and the appropriate viewer ID.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
        """
        if (not self.IsOn(level)):
            return
        
        try:
           
            if (ctx == None):
                self.LogInternalError("LogCustomContext: ctx argument is null.");
            else:
                self._SendContext(level, title, lt, ctx, colorValue)
            
        except Exception as ex:
            
            self.LogInternalError("LogCustomContext: " + str(ex))


    def LogCustomFile(self, level:SILevel=None, title:str=None, fileName:str=None, lt:SILogEntryType=None, vi:SIViewerId=None, colorValue:SIColors=None) -> None:
        """
        Logs the content of a file using a custom
        Log Entry type, viewer ID and title and custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            fileName (str):
                The file to log.
            lt (SILogEntryType)
                The custom Log Entry type.
            vi (SIViewerId):
                The custom viewer ID which specifies the way the Console
                handles the file content.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method logs the content of the supplied file using a
        custom Log Entry type and viewer ID. The parameters control
        the way the content of the file is displayed in the Console.
        Thus you can extend the functionality of the SmartInspect
        library with this method.
        """
        if (not self.IsOn(level)):
            return
        
        ctx:SIBinaryContext = SIBinaryContext(vi)
        try:
            
            ctx.LoadFromFile(fileName)
            self._SendContext(level, title, lt, ctx, colorValue)
            
        except Exception as ex:
            
            self.LogInternalError("LogCustomFile: " + str(ex))


    def LogCustomReader(self, level:SILevel=None, title:str=None, reader:TextIOWrapper=None, lt:SILogEntryType=None, vi:SIViewerId=None, colorValue:SIColors=None) -> None:
        """
        Logs the content of a text reader using a custom Log
        Entry type and viewer ID and custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            reader (TextIOWrapper):
                The text reader to log.
            lt (SILogEntryType):
                The custom Log Entry type.
            vi (SIViewerId):
                The custom viewer ID which specifies the way the Console
                handles the reader content.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method logs the content of the supplied reader using 
        custom Log Entry type and viewer ID. The parameters control
        the way the content of the reader is displayed in the Console.
        Thus you can extend the functionality of the SmartInspect
        library with this method.
        """
        if (not self.IsOn(level)):
            return
        
        ctx:SITextContext = SITextContext(vi)
        try:
            
            ctx.LoadFromReader(reader)
            self._SendContext(level, title, lt, ctx, colorValue)
            
        except Exception as ex:
            
            self.LogInternalError("LogCustomReader: " + str(ex))


    def LogCustomStream(self, level:SILevel=None, title:str=None, stream:BufferedReader=None, lt:SILogEntryType=None, vi:SIViewerId=None, colorValue:SIColors=None) -> None:
        """
        Logs the content of a stream using a custom Log
        Entry type and viewer ID and custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            stream (BufferedReader):
                The stream to log (BufferedReader).
            lt (SILogEntryType):
                The custom Log Entry type.
            vi (SIViewerId):
                The custom viewer ID which specifies the way the Console
                handles the stream content.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method logs the content of the supplied stream using a
        custom Log Entry type and viewer ID. The parameters control
        the way the content of the stream is displayed in the Console.
        Thus you can extend the functionality of the SmartInspect
        Python library with this method.
        """
        if (not self.IsOn(level)):
            return
        
        ctx:SIBinaryContext = SIBinaryContext(vi)
        try:
            
            ctx.LoadFromStream(stream)
            self._SendContext(level, title, lt, ctx, colorValue)
            
        except Exception as ex:
            
            self.LogInternalError("LogCustomStream: " + str(ex))


    def LogCustomText(self, level:SILevel=None, title:str=None, text:str=None, lt:SILogEntryType=None, vi:SIViewerId=None, colorValue:SIColors=None) -> None:
        """
        Logs custom text using a custom Log Entry type and
        viewer ID and custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            text (str):
                The text to log.
            lt (SILogEntryType):
                The custom Log Entry type.
            vi (SIViewerId):
                The custom viewer ID which specifies the way the Console
                handles the text content.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
        """
        if (not self.IsOn(level)):
            return
        
        ctx:SITextContext = SITextContext(vi)
        try:
            
            ctx.LoadFromText(text)
            self._SendContext(level, title, lt, ctx, colorValue)
            
        except Exception as ex:
            
            self.LogInternalError("LogCustomText: " + str(ex))


    def LogDateTime(self, level:SILevel=None, name:str=None, value:datetime=None, colorValue:SIColors=None) -> None:
        """
        Logs a datetime value with a custom log level.
        
        Args:
            level (SILevel):
                The log level of this method call.
            name (str):
                The variable name.
            value (str):
                The variable value.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method logs the name and value of a datetime variable.
        A title like "name = 05/15/2023 02:15:30 PM" will be displayed in the Console.
        """
        if (not self.IsOn(level)):
            return

        # validations.
        if (name is None):
            name = "<null name>"

        try:

            # send log entry packet.
            title:str = str.format("{0} = {1}", name, str(value))
            self._SendLogEntry(level, title, SILogEntryType.VariableValue, SIViewerId.Title, colorValue)

        except Exception as ex:
                
            self.LogInternalError("LogDateTime: " + str(ex))


    def LogDebug(self, title:str, *args, colorValue:SIColors=None, logToSystemLogger:bool=True) -> None:
        """
        Logs a debug message with a log level of SILevel.Debug.

        Args:
            title (str):
                The message to log.
            *args:
                Format arguments for the title argument.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
                
        This method will also log a message to the system log if the `SystemLogger` property is set.
        """
        # is system logging enabled?  if so, then log the message there.
        if (self._fSystemLogger != None) and (logToSystemLogger):
            self._fSystemLogger.debug(title, *args)

        if (not self.IsOn(SILevel.Debug)):
            return 

        try:
                
            # format title if *args was supplied.
            if (title) and (args):
                title = (title % args)
                
            # send the packet.
            self._SendLogEntry(SILevel.Debug, title, SILogEntryType.Debug, SIViewerId.Title, colorValue)

        except Exception as ex:
                
            self.LogInternalError("LogDebug: " + str(ex))
            

    def LogDictionary(self, level:SILevel=None, title:str=None, oDict:dict=None, colorValue:SIColors=None, 
                      prettyPrint:bool=False
                      ) -> None:
        """
        Logs the content of a dictionary with a custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console; "Current stack trace" is used if one is not supplied.
            oDict (dict):
                The dictionary to log.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
            prettyPrint (bool):
                True to format the dictionary with pprint before logging; otherwise, just log
                the dictionary using a custom context viewer (e.g. `SIValueListViewerContext`).

        This method iterates through the supplied dictionary and calls SIObjectRenderer.RenderObject to
        render every key/value pair into a string. These pairs will be displayed in a key/value viewer 
        in the Console.
        """
        if (not self.IsOn(level)):
            return
        
        if (prettyPrint == True) and (oDict is not None):
            
            try:
            
                # if using pretty print, then format the dictionary and log it as text.
                dictText:str = pformat(oDict,indent=2,width=132,sort_dicts=False)
                self.LogCustomText(level, title, dictText, SILogEntryType.Text, SIViewerId.Data, colorValue)
                return
            
            except Exception as ex:
            
                self.LogInternalError("LogDictionary (pretty print): " + str(ex))
                
        ctx:SIValueListViewerContext = SIValueListViewerContext()

        try:
            
            # was an object to log supplied?
            if (oDict is None):
                    
                # no - just append a line to the context viewer.
                ctx.AppendLine("<The dictionary argument to log was null>")

            else:
                    
                # add all keys and values to the context viewer.
                for key in oDict.keys():

                    val:object = oDict[key]

                    if (key == oDict):
                        strKey = "<cycle>"
                    else:
                        strKey = SIObjectRenderer.RenderObject(key)

                    if (val == oDict):
                        strVal = "<cycle>"
                    else:
                        strVal = SIObjectRenderer.RenderObject(val)

                    ctx.AppendKeyValue(strKey, strVal)

            # send the packet.
            self._SendContext(level, title, SILogEntryType.Text, ctx, colorValue)
            
        except Exception as ex:
            
            self.LogInternalError("LogDictionary: " + str(ex))


    def LogEnumerable(self, level:SILevel=None, title:str=None, oList:list=None, colorValue:SIColors=None) -> None:
        """
        Logs the content of a list with a custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console; "Current stack trace" is used if one is not supplied.
            oList (list):
                The list to log.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method iterates through the supplied list and calls SIObjectRenderer.RenderObject to
        render every element into a string. These elements will be displayed in a listview in the Console.
        """
        if (not self.IsOn(level)):
            return

        ctx:SIListViewerContext = SIListViewerContext()

        try:
            
            # was an object to log supplied?
            if (oList is None):
                    
                # no - just append a line to the context viewer.
                ctx.AppendLine("<The list argument to log was null>")

            else:
                    
                # add all items to the context viewer.
                for item in oList:

                    if (item == oList):
                        ctx.AppendLine("<cycle>")
                    else:
                        ctx.AppendLine(SIObjectRenderer.RenderObject(item))

            # send the packet.
            self._SendContext(level, title, SILogEntryType.Text, ctx, colorValue)
            
        except Exception as ex:
            
            self.LogInternalError("LogEnumerable: " + str(ex))


    def LogError(self, title:str, *args, colorValue:SIColors=None, logToSystemLogger:bool=True) -> None:
        """
        Logs a error message with a log level of SILevel.Error.

        Args:
            title (str):
                The message to log.
            *args:
                Format arguments for the title argument.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
            logToSystemLogger (bool):
                True to log the exception to the SystemLogger instance (if one was supplied);  
                otherwise, False to not log the exception to the SystemLogger instance.  
                Default is True.
                
        This method will also log a message to the system log if the `SystemLogger` property is set.
        """
        # is system logging enabled?  if so, then log the message there.
        if (self._fSystemLogger != None) and (logToSystemLogger):
            self._fSystemLogger.error(title, *args)

        if (not self.IsOn(SILevel.Error)):
            return

        try:
                
            # format title if *args was supplied.
            if (title) and (args):
                title = (title % args)

            # send the packet.
            self._SendLogEntry(SILevel.Error, title, SILogEntryType.Error, SIViewerId.Title, colorValue)

        except Exception as ex:
                
            self.LogInternalError("LogError: " + str(ex))


    def LogException(self, title:str=None, ex:Exception=None, colorValue:SIColors=None, logToSystemLogger:bool=True):
        """
        Logs the content of an exception with a custom
        title and a log level of SILevel.Error.
        
        Args:
            title (str):
                The title to display in the Console.
            ex (Exception):
                The exception to log.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
            logToSystemLogger (bool):
                True to log the exception to the SystemLogger instance (if one was supplied);  
                otherwise, False to not log the exception to the SystemLogger instance.  
                Default is True.
        
        This method extracts the exception message and stack trace
        from the supplied exception and logs an error with this data.
        It is especially useful if you place calls to this method in
        exception handlers. See LogError for a more general method
        with a similar intention.

        This method will also automatically log the exception to the 
        system log if the `SystemLogger` property is set and the 
        logToSystemLogger argument is True.
        
        <details>
            <summary>Sample Code</summary>
        ``` python
        .. include:: ../docs/include/samplecode/SISession/LogException.py
        ```
        </details>
        """
        # is system logging enabled?  if so, then log the message there.
        if (self._fSystemLogger != None) and (logToSystemLogger) and (ex != None):
            self._fSystemLogger.exception(ex)

        if (not self.IsOn(SILevel.Error)):
            return
            
        if (ex == None):
            self.LogInternalError("LogException: ex argument is null.")
        else:

            try:

                # capture exception details to string via standard Python (temporary) logger.
                # we first clear the stream, then capture the recent exception details.
                self._fTempLoggingStream.seek(0)
                self._fTempLoggingStream.truncate(0)
                self._fTempLogger.exception(ex,exc_info=True)
                self._fTempLoggingStream.flush()
                errdtls:str = self._fTempLoggingStream.getvalue()

                # if title not specified, then use the exception string as a title.                    
                if (title == None):
                    title = str(ex)

                # prepare a custom context with the exception details and traceback info.
                ctx:SIDataViewerContext = SIDataViewerContext()
                ctx.LoadFromText(errdtls)

                # send the packet.
                self._SendContext(SILevel.Error, title, SILogEntryType.Error, ctx, colorValue)
                    
            except Exception as ex2:
                    
                self.LogInternalError("LogException: " + str(ex2))


    def LogFatal(self, title:str, *args, colorValue:SIColors=None, logToSystemLogger:bool=True) -> None:
        """
        Logs a fatal error message with a log level of SILevel.Fatal.

        Args:
            title (str):
                The message to log.
            *args:
                Format arguments for the title argument.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
            logToSystemLogger (bool):
                True to log the exception to the SystemLogger instance (if one was supplied);  
                otherwise, False to not log the exception to the SystemLogger instance.  
                Default is True.

        This method is ideally used in error handling code such as
        exception handlers. If this method is used consequently, it
        is easy to troubleshoot and solve bugs in applications or
        configurations. See LogError for a method which does not
        describe fatal but recoverable errors.

        This method will also log a message to the system log if the `SystemLogger` property is set.
        
        <details>
            <summary>Sample Code</summary>
        ``` python
        .. include:: ../docs/include/samplecode/SISession/LogFatal.py
        ```
        </details>
        """
        # is system logging enabled?  if so, then log the message there.
        if (self._fSystemLogger != None) and (logToSystemLogger):
            self._fSystemLogger.critical(title, *args)

        if (not self.IsOn(SILevel.Fatal)):
            return

        try:
                
            # format title if *args was supplied.
            if (title) and (args):
                title = (title % args)

            # send the packet.
            self._SendLogEntry(SILevel.Fatal, title, SILogEntryType.Fatal, SIViewerId.Title, colorValue)
                    
        except Exception as ex:
                
            self.LogInternalError("LogFatal: " + str(ex))


    def LogFloat(self, level:SILevel=None, name:str=None, value:float=None, colorValue:SIColors=None) -> None:
        """
        Logs a float value with a custom log level.
        
        Args:
            level (SILevel):
                The log level of this method call.
            name (str):
                The variable name.
            value (float):
                The variable value.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method logs the name and value of a float variable.
        A title like "name = 3.14159" will be displayed in the Console.
        """
        if (not self.IsOn(level)):
            return

        # validations.
        if (name is None):
            name = "<null name>"

        try:

            # send log entry packet.
            title:str = str.format("{0} = {1}", name, str(value))
            self._SendLogEntry(level, title, SILogEntryType.VariableValue, SIViewerId.Title, colorValue)

        except Exception as ex:
                
            self.LogInternalError("LogFloat: " + str(ex))


    def LogHtml(self, level:SILevel=None, title:str=None, html:str=None, colorValue:SIColors=None) -> None:
        """
        Logs HTML code with a custom log level and
        displays it in a web browser.
        
        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            html (str):
                The HTML source code to display.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
        
        This method logs the supplied HTML source code. The source
        code is displayed as a website in the web viewer of the Console.
        """
        self.LogCustomText(level, title, html, SILogEntryType.WebContent, SIViewerId.Web, colorValue)


    def LogHtmlFile(self, level:SILevel=None, title:str=None, fileName:str=None, colorValue:SIColors=None) -> None:
        """
        Logs an HTML file and displays the content in a
        web browser using a custom title and custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            fileName (str):
                The HTML file to display.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method logs the HTML source code of the supplied file. The
        source code is displayed as a website in the web viewer of the Console. 
        """
        self.LogCustomFile(level, title, fileName, SILogEntryType.WebContent, SIViewerId.Web, colorValue)


    def LogHtmlReader(self, level:SILevel=None, title:str=None, reader:TextIOWrapper=None, colorValue:SIColors=None) -> None:
        """
        Logs a text reader with a custom log level and displays
        the content in a web browser.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            reader (TextIOWrapper):
                The text reader to display (TextReader).
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method logs the HTML source code of the supplied reader.
        The source code is displayed as a website in the web viewer of
        the Console.
        """
        self.LogCustomReader(level, title, reader, SILogEntryType.WebContent, SIViewerId.Web, colorValue)


    def LogHtmlStream(self, level:SILevel=None, title:str=None, stream:BufferedReader=None, colorValue:SIColors=None) -> None:
        """
        Logs a stream with a custom log level and displays
        the content in a web browser.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            stream (BufferedReader):
                The stream to display.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method logs the HTML source code of the supplied stream.
        The source code is displayed as a website in the web viewer of
        the Console. 
        """
        self.LogCustomStream(level, title, stream, SILogEntryType.WebContent, SIViewerId.Web, colorValue)


    def LogIconFile(self, level:SILevel=None, title:str=None, fileName:str=None, colorValue:SIColors=None) -> None:
        """
        Logs a Windows icon file and displays it in the
        Console using a custom title and custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            fileName (str):
                The Windows icon file to display in the Console.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
        """
        self.LogCustomFile(level, title, fileName, SILogEntryType.Graphic, SIViewerId.Icon, colorValue)


    def LogIconStream(self, level:SILevel=None, title:str=None, stream:BufferedReader=None, colorValue:SIColors=None) -> None:
        """
        Logs a stream with a custom log level and
        interprets its content as Windows icon.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            stream (BufferedReader):
                The stream to display as Windows icon.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
        """
        self.LogCustomStream(level, title, stream, SILogEntryType.Graphic, SIViewerId.Icon, colorValue)


    def LogInt(self, level:SILevel=None, name:str=None, value:int=None, includeHex:bool=False, colorValue:SIColors=None) -> None:
        """
        Logs an integer value with an optional hexadecimal representation 
        and custom log level.
        
        Args:
            level (SILevel):
                The log level of this method call.
            name (str):
                The variable name.
            value (int):
                The variable value.
            includeHex (bool):
                Indicates if a hexadecimal representation should be included (True) or not (False).
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method logs the name and value of a integer variable.
        A title like "name = 10" will be displayed in the Console.
        """
        if (not self.IsOn(level)):
            return

        # validations.
        if (name is None):
            name = "<null name>"

        try:

            vhex:str = ""
            if (includeHex):
                vhex = " (" + hex(value).upper() + ")"
                if (value < 0):
                    vhex = vhex.replace("-","")     # remove minus sign for negative values.
                vhex = vhex.replace("0X","0x")      # make "0X" lower-case since hex values will be in upper-case

            # send log entry packet.
            title:str = str.format("{0} = {1}{2}", name, str(value), vhex)
            self._SendLogEntry(level, title, SILogEntryType.VariableValue, SIViewerId.Title, colorValue)

        except Exception as ex:
                
            self.LogInternalError("LogInt: " + str(ex))


    def LogInternalError(self, title:str, colorValue:SIColors=None) -> None:
        """
        Logs an internal error with a log level of SILevel.Error.

        Args:
            title (str):
                A string which describes the internal error.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method logs an internal error. Such errors can occur
        if session methods are invoked with invalid arguments. For
        example, if you pass an invalid format string to LogMessage,
        the exception will be caught and an internal error with the
        exception message will be sent.

        This method is also intended to be used in derived classes
        to report any errors in your own methods.
        """
        if (not self.IsOn(SILevel.Error)):
            return
        
        self._SendLogEntry(SILevel.Error, title, SILogEntryType.InternalError, SIViewerId.Title, colorValue)


    def LogJpegFile(self, level:SILevel=None, title:str=None, fileName:str=None, colorValue:SIColors=None) -> None:
        """
        Logs a JPEG file and displays it in the Console
        using a custom title and custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            fileName (str):
                The JPEG file to display in the Console.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
        """
        self.LogCustomFile(level, title, fileName, SILogEntryType.Graphic, SIViewerId.Jpeg, colorValue)


    def LogJpegStream(self, level:SILevel=None, title:str=None, stream:BufferedReader=None, colorValue:SIColors=None) -> None:
        """
        Logs a stream with a custom log level and
        interprets its content as JPEG image.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            stream (BuffereReader):
                The stream to display as JPEG image.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
        """
        self.LogCustomStream(level, title, stream, SILogEntryType.Graphic, SIViewerId.Jpeg, colorValue)


    def LogMessage(self, title:str, *args, colorValue:SIColors=None, logToSystemLogger:bool=True) -> None:
        """
        Logs a message with a log level of SILevel.Message.

        Args:
            title (str):
                The message to log.
            *args:
                Format arguments for the title argument.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
            logToSystemLogger (bool):
                True to log the exception to the SystemLogger instance (if one was supplied);  
                otherwise, False to not log the exception to the SystemLogger instance.  
                Default is True.

        This method will also log a message to the system log if the `SystemLogger` property is set.
        """
        # is system logging enabled?  if so, then log the message there.
        if (self._fSystemLogger != None) and (logToSystemLogger):
            self._fSystemLogger.info(title, *args)

        if (not self.IsOn(SILevel.Message)):
            return

        try:
                
            # format title if *args was supplied.
            if (title) and (args):
                title = (title % args)

            # send the packet.
            self._SendLogEntry(SILevel.Message, title, SILogEntryType.Message, SIViewerId.Title, colorValue)

        except Exception as ex:
                
            self.LogInternalError("LogMessage: " + str(ex))
                

    def LogMetafileFile(self, level:SILevel=None, title:str=None, fileName:str=None, colorValue:SIColors=None) -> None:
        """
        Logs a Windows Metafile file and displays it in
        the Console using a custom title and custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            fileName (str):
                The Windows Metafile file to display in the Console.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
        """
        self.LogCustomFile(level, title, fileName, SILogEntryType.Graphic, SIViewerId.Metafile, colorValue)


    def LogMetafileStream(self, level:SILevel=None, title:str=None, stream:BufferedReader=None, colorValue:SIColors=None) -> None:
        """
        Logs a stream with a custom log level and
        interprets its content as Windows Metafile image.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            stream (BufferedReader):
                The stream to display as Windows Metafile image.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
        """
        self.LogCustomStream(level, title, stream, SILogEntryType.Graphic, SIViewerId.Metafile, colorValue)


    def LogMethodParmList(self, level:SILevel=None, title:str=None, parmlistContext:SIMethodParmListContext=None, colorValue:SIColors=None) -> None:
        """
        Logs a method input parameter list view context with a custom log level and title.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            parmlistContext (SIMethodParmListContext):
                The method input parameter list view context to log.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
        """
        if (self.IsOn(level)):
        
            if title is None:
                title = parmlistContext.Title
            self.LogCustomContext(level, title, SILogEntryType.Object, parmlistContext, colorValue)


    def LogObject(self, level:SILevel=None, title:str=None, instance:object=None, excludeNonPublic:bool=False, excludeBuiltIn:bool=True, excludeFunctions:bool=True, colorValue:SIColors=None) -> None:
        """
        Logs fields and properties of an object with a custom log level. 
        Lets you specify if non public members should also be logged.
        
        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            instance (object):
                The object whose fields and properties should be logged.
            excludeNonPublic (bool):
                Specifies if non public member items (e.g. "_x" prefix) should 
                be excluded from the log data.
            excludeBuiltIn (bool):
                Specifies if non public "built-in" member items (e.g. "__x" prefix) should 
                be excluded from the log data.
            excludeFunctions (bool):
                Specifies if routine, function, and method data is included in the log data.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method logs all field and property names and their
        current values of an object. These key/value pairs will be
        displayed in the Console in an object inspector like viewer.

        You can specify if non public or only public members should
        be logged by setting the excludeNonPublic argument to true or false,
        respectively.
        """
        if (not self.IsOn(level)):
            return

        try:

            ctx:SIInspectorViewerContext = SIInspectorViewerContext()
            
            # was an object to log supplied?
            if (instance is None):
                    
                # no - just append a line to the context viewer.
                ctx.StartGroup("<The instance argument to log was null>")

            else:
                    
                #instanceType = type(instance)
                iList:list[str] = []

                # Example of inspect.getmembers(instance, None) output:
                # - PropertyBool : True
                # - PropertyString : 'This is a string property value'
                # - PublicEvent : <bound method InstanceGetMembersTestClass.PublicEvent of <__main__.InstanceGetMembersTestClass object at 0x0000026B84569AC0>>
                # - PublicFunctionString : <bound method InstanceGetMembersTestClass.PublicFunctionString of <__main__.InstanceGetMembersTestClass object at 0x0000026B84569AC0>>
                # - PublicMethod : <bound method InstanceGetMembersTestClass.PublicMethod of <__main__.InstanceGetMembersTestClass object at 0x0000026B84569AC0>>
                # - PublicStaticFunction : <function InstanceGetMembersTestClass.PublicStaticFunction at 0x0000026B859F1EE0>
                # - PublicStaticMethod : <function InstanceGetMembersTestClass.PublicStaticMethod at 0x0000026B859F1E50>
                # - STATIC_VAR_BOOL : True
                # - STATIC_VAR_INT : 69
                # - STATIC_VAR_STRING : 'Static String'
                # - _InstanceGetMembersTestClass__fPropertyBool : True
                # - _InstanceGetMembersTestClass__fPropertyBoolDynamic : True
                # - _InstanceGetMembersTestClass__fPropertyString : 'This is a string property value'
                # - _InstanceGetMembersTestClass__fPropertyStringDynamic : 'This is a INTERNAL string property value'

                # --------------------------------------------------------------------------------------------------
                # get all members of the instance and add field types to the context viewer.
                # --------------------------------------------------------------------------------------------------
                members = inspect.getmembers(instance, None)
                self._LogObjectBuildContext("Fields", instance, members, ctx, excludeNonPublic, excludeBuiltIn, True, True)

                # --------------------------------------------------------------------------------------------------
                # get all properties decorated with "@property" attribute.
                # --------------------------------------------------------------------------------------------------
                members = inspect.getmembers(type(instance), lambda o: isinstance(o, property)) 

                # add member data to context viewer.
                for name, data in members:

                    sb:str = ""

                    try:

                        # map the property object.
                        propobj:property = data

                        # try to determine if this is a "private" property.  if the "fget()"
                        # method of the property definition contains a "._" value then it usually
                        # indicates a "private" property. 
                        # Example fget, private property: '<function SISession._IsStored at 0x000001FCEDE96550>'
                        # Example fget, public  property: '<function SISession.Active at 0x000001FCEDE75650>'

                        propobjfgetdef = str(propobj.fget)
                        if (propobjfgetdef != None):
                            if (propobjfgetdef.find("._") != -1):
                                if (excludeNonPublic):
                                    continue
            
                        sb += ctx.EscapeItem(name)
                        sb += "="
                        sb += ctx.EscapeItem(SIObjectRenderer.RenderObject(propobj.fget(instance)))
            
                    except Exception as ex:
            
                        sb += "<not accessible>"

                    # add context entry to the list.
                    iList.append(sb)
                    sb = ""

                # sort context items - the member name is the first thing displayed
                # in the item, so the list is sorted by member name.
                # note that in Python, UPPER-case items are sorted above lower-case items,
                # so we use the "key=str.lower) syntax to force the case-insensitive sort.
                iList.sort(key=str.lower)

                # begin a new group and append the list to the inspector context.
                ctx.StartGroup("Properties")
                for line in iList:
                    ctx.AppendLine(str(line))

                iList.clear()

                # --------------------------------------------------------------------------------------------------
                # get everything else about the instance.
                # --------------------------------------------------------------------------------------------------

                # are we including routines, functions, and methods?
                if (not excludeFunctions):

                    # get routine members (e.g. non-static methods) of the instance and add field types to the context viewer.
                    members = inspect.getmembers(instance, predicate=inspect.isroutine)
                    self._LogObjectBuildContext("Routines", instance, members, ctx, excludeNonPublic, excludeBuiltIn, False)

                    # get function members (e.g. static methods) of the instance and add field types to the context viewer.
                    members = inspect.getmembers(instance, predicate=inspect.isfunction)
                    self._LogObjectBuildContext("Functions", instance, members, ctx, excludeNonPublic, excludeBuiltIn, False)

                    # get method members (e.g. non-static methods) of the instance and add field types to the context viewer.
                    members = inspect.getmembers(instance, predicate=inspect.ismethod)
                    self._LogObjectBuildContext("Methods", instance, members, ctx, excludeNonPublic, excludeBuiltIn, False)

            # send the packet.
            self._SendContext(level, title, SILogEntryType.Object, ctx, colorValue);

        except Exception as ex:
                
            self.LogInternalError("LogObject: " + str(ex))


    def LogObjectValue(self, level:SILevel=None, name:str=None, value:object=None, colorValue:SIColors=None) -> None:
        """
        Logs a object value with a custom log level.
        
        Args:
            level (SILevel):
                The log level of this method call.
            name (str):
                The variable name.
            value (object):
                The variable value.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method logs the name and value of a object variable.
        A title like "name = My Object" will be displayed in the Console.
        If the value is null, then a title like "name = null" will be displayed in the Console.
        """
        if (not self.IsOn(level)):
            return

        # validations.
        if (name is None):
            name = "<null name>"

        try:

            # send log entry packet.
            title:str = ""
            if (value == None):
                title = str.format("{0} = null", name)
            else:
                title = str.format("{0} = {1}", name, str(value))
            self._SendLogEntry(level, title, SILogEntryType.VariableValue, SIViewerId.Title, colorValue)

        except Exception as ex:
                
            self.LogInternalError("LogObject: " + str(ex))


    def LogPngFile(self, level:SILevel=None, title:str=None, fileName:str=None, colorValue:SIColors=None) -> None:
        """
        Logs a PNG file and displays it in the Console
        using a custom title and custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            fileName (str):
                The PNG file to display in the Console.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        Note that this method is only supported in the SI Console Viewer v3.4+.  Previous versions
        of the Si Console will display "A viewer for the selected Log Entry could not be found" error.
        """
        self.LogCustomFile(level, title, fileName, SILogEntryType.Graphic, SIViewerId.Png, colorValue)


    def LogPngStream(self, level:SILevel=None, title:str=None, stream:BufferedReader=None, colorValue:SIColors=None) -> None:
        """
        Logs a stream with a custom log level and
        interprets its content as PNG image.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            stream (BuffereReader):
                The stream to display as PNG image.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        Note that this method is only supported in the SI Console Viewer v3.4+.  Previous versions
        of the Si Console will display "A viewer for the selected Log Entry could not be found" error.
        """
        self.LogCustomStream(level, title, stream, SILogEntryType.Graphic, SIViewerId.Png, colorValue)


    def LogReader(self, level:SILevel=None, title:str=None, reader:TextIOWrapper=None, colorValue:SIColors=None) -> None:
        """
        Logs a reader with a custom log level and
        displays the content in a read-only text field.
        
        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            reader (TextIOWrapper):
                The text reader to log.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
        """
        self.LogCustomReader(level, title, reader, SILogEntryType.Text, SIViewerId.Data, colorValue)


    def LogSeparator(self, level:SILevel=None, colorValue:SIColors=None) -> None:
        """
        Logs a simple separator with a custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method instructs the Console to draw a separator.
        A separator is intended to group related Log Entry
        and to separate them visually from others. This
        method can help organizing Log Entries in the Console.
        """
        if (not self.IsOn(level)):
            return

        self._SendLogEntry(level, "", SILogEntryType.Separator, SIViewerId.NoViewer, colorValue)


    def LogSource(self, level:SILevel=None, title:str=None, source:str=None, id:SISourceId=None, colorValue:SIColors=None) -> None:
        """
        Logs source code that is displayed with syntax
        highlighting in the Console using a custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            source (str):
                The source code to log.
            id (SISourceId):
                Specifies the type of source code.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method displays the supplied source code with syntax
        highlighting in the Console. The type of the source code can be
        specified by the 'id' argument. Please see the SISourceId enum for
        information on the supported source code types.
        """
        self.LogCustomText(level, title, source, SILogEntryType.Source, id, colorValue)


    def LogSourceFile(self, level:SILevel=None, title:str=None, fileName:str=None, id:SISourceId=None, colorValue:SIColors=None) -> None:
        """
        Logs the content of a file as source code with
        syntax highlighting using a custom title and custom log
        level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            fileName (str):
                The name of the file which contains the source code.
            id (SISourceId):
                Specifies the type of source code.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method displays the source file with syntax highlighting
        in the Console. The type of the source code can be specified by
        the 'id' argument. Please see the SISourceId enum for information
        on the supported source code types.
        """
        self.LogCustomFile(level, title, fileName, SILogEntryType.Source, id, colorValue)        


    def LogSourceReader(self, level:SILevel=None, title:str=None, reader:TextIOWrapper=None, id:SISourceId=None, colorValue:SIColors=None) -> None:
        """
        Logs the content of a text reader as source code with
        syntax highlighting using a custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            reader (TextIOWrapper):
                The text reader which contains the source code.
            id (SISourceId):
                Specifies the type of source code.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method displays the content of a reader with syntax
        highlighting in the Console. The type of the source code can be
        specified by the 'id' argument. Please see the SISourceId enum for
        information on the supported source code types.
        """
        self.LogCustomReader(level, title, reader, SILogEntryType.Source, id, colorValue)


    def LogSourceStream(self, level:SILevel=None, title:str=None, stream:BufferedReader=None, id:SISourceId=None, colorValue:SIColors=None) -> None:
        """
        Logs the content of a stream as source code with
        syntax highlighting using a custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            stream (BufferedReader):
                The stream which contains the source code.
            id (SISourceId):
                Specifies the type of source code.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method displays the content of a stream with syntax
        highlighting in the Console. The type of the source code can be
        specified by the 'id' argument. Please see the SISourceId enum for
        information on the supported source code types.
        """
        self.LogCustomStream(level, title, stream, SILogEntryType.Source, id, colorValue)


    def LogSql(self, level:SILevel=None, title:str=None, source:str=None, colorValue:SIColors=None) -> None:
        """
        Logs a string containing SQL source code with a
        custom log level. The SQL source code is displayed with syntax
        highlighting in the Console.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            source (str):
                The SQL source code to log.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method displays the supplied SQL source code with syntax
        highlighting in the Console.

        It is especially useful to debug or track dynamically generated
        SQL source code.
        """
        self.LogSource(level, title, source, SISourceId.Sql, colorValue)


    def LogSqliteDbCursorData(self, level:SILevel=None, title:str=None, cursor:sqlite3.Cursor=None, colorValue:SIColors=None) -> None:
        """
        Logs the contents of a Sqlite Cursor with a custom title and custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            cursor (Cursor):
                The cursor data to log.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method logs all data of the supplied cursor, using a "for row in cursor:" statement.
        Note that this WILL move the position of the cursor, and the position is not restored.
        """
        if (not self.IsOn(level)):
            return

        methodName:str = "LogSqliteDbCursorData"

        if (cursor == None):
            self.LogInternalError("{0}: cursor argument is null.".format(methodName))
            return

        # default title if one was not supplied.
        if (title == None) or (len(title) == 0):
            title = "Sqlite Cursor Data"

        # sqllite cursor description is a tuple (of 7 items) containing the description of columns.
        # as of this writing, only the first tuple index item is populated, which is the column name.
        columns:list[(str,None,None,None,None,None,None)] = cursor.description
        if (columns == None):
            self.LogInternalError("{0}: cursor did not return any rows.".format(methodName))
            return;

        ctx:SITableViewerContext = SITableViewerContext()

        try:
        
            # formulate column header (e.g. "Col1", "Col2", etc).
            sb:str = ""
            for column in columns:
                sb += "\"{0}\", ".format(column[0])

            # drop the ending comma-space delimiter from the built string.
            sb = sb[:-2]

            # write the column header.
            ctx.AppendHeader(sb)

            # write all rows in the cursor.
            rowcnt:int = 0
            for row in cursor:

                # add column data for the row to the context view.
                ctx.BeginRow()
                for i in range(len(columns)):
                    ctx.AddRowEntry(str(row[i]))
                ctx.EndRow()
                rowcnt = rowcnt + 1

            # modify the title with the data row count.
            title += " ({0} rows)".format(str(rowcnt))

            # send the packet.
            self._SendContext(level, title, SILogEntryType.DatabaseStructure, ctx, colorValue)
        
        except Exception as ex:
            
            self.LogInternalError("{0}: {1}".format(methodName, str(ex)))


    def LogSqliteDbSchemaCursor(self, level:SILevel=None, title:str=None, cursor:sqlite3.Cursor=None, colorValue:SIColors=None) -> None:
        """
        Logs the schema of a Sqlite Cursor with a custom title and custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            cursor (Cursor):
                The cursor schema to log.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method logs the schema of the supplied cursor, by querying its "description" property value.  
        It does not move the position of the cursor.

        A cursor schema contains the name of every column in the cursor.
        Note that this data could be different than what is actually defined in the database table that
        the schema is derived from, as the SELECT statement used to query the database could limit the 
        columns returned.
        """
        if (not self.IsOn(level)):
            return

        ctx:SITableViewerContext = SITableViewerContext()

        try:
        
            # default title if one was not supplied.
            if (title == None) or (len(title) == 0):
                title = "Sqlite Cursor Schema"

            # was an object to log supplied?
            if (cursor is None):
                    
                # no - just append a line to the context viewer.
                ctx.BeginRow()
                ctx.AddRowEntry("<The cursor argument to log was null>")
                ctx.EndRow()

            else:

                # sqllite cursor description is a list (7 items) containing the description of columns.
                # as of this writing, only the first (of 7) list items is populated, which is the column name.
                columns:list[(str,None,None,None,None,None,None)] = cursor.description
                if (columns is None):
                    ctx.BeginRow()
                    ctx.AddRowEntry("<The cursor table is empty>")
                    ctx.EndRow()
                else:

                    # write the header first.
                    ctx.AppendHeader("\"Column Name\"")

                    # write the columns.
                    for column in columns:

                        # map the column schema.
                        sColName:str = str(column[0])

                        # add column info to the context view.
                        ctx.BeginRow()
                        ctx.AddRowEntry(sColName)
                        ctx.EndRow()

            # send the packet.
            self._SendContext(level, title, SILogEntryType.DatabaseStructure, ctx, colorValue)
        
        except Exception as ex:
            
            self.LogInternalError("LogSqliteCursorSchema: " + str(ex))


    def LogSqliteDbSchemaForeignKeyList(self, level:SILevel=None, title:str=None, conn:sqlite3.Connection=None, tableName:str=None, sortByName:bool=False, colorValue:SIColors=None) -> None:
        """
        Logs the schema of a Sqlite DB Table Foreign Key List with a custom title and custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            conn (Connection):
                Sqlite database connection object.
            tableName (str):
                The name of the table to obtain schema information for.
            sortByName (bool):
                Sorts the log data by Table Name (True) or by ID (False, default).
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method queries the schema information by executing the following SQL statement:
        "SELECT * FROM pragma_foreign_key_list('<tablename>');"

        This will log the following details returned from the schema information query:
        ID, Sequence, Table, From, To, On Update, On Delete, Match
        """
        if (not self.IsOn(level)):
            return

        methodName:str = "LogSqliteDbSchemaForeignKeyList"

        if (conn == None):
            self.LogInternalError("{0}: conn argument is null.".format(methodName))
            return

        if ((tableName == None) or (len(tableName) == 0)):
            self.LogInternalError("{0}: tableName argument is null or an empty string.".format(methodName))
            return

        # default title if one was not supplied.
        if (title == None) or (len(title) == 0):
            title = "Sqlite DB Schema Information: Table \"{0}\" - Foreign Key List".format(tableName)
            if (sortByName):
                title += " (sorted by table name)"

        tblSchema:list = None

        try:

            # more info on the return results of this schema query can be found here:
            # https://www.sqlite.org/pragma.html#pragma_foreign_key_list

            # sql to query db for schema info.
            sql:str = "SELECT * FROM pragma_foreign_key_list('{0}');".format(tableName)

            # execute sql.
            cursor:sqlite3.Cursor = conn.execute(sql)
            tblSchema = cursor.fetchall()

            # results contain information about the table foreign key list:
            # id, seq, table, from, to, on_update, on_delete, match
            if ((tblSchema == None) or (len(tblSchema)) == 0):
                self.LogInternalError("{0}: table name \"{1}\" does not exist.".format(methodName, tableName));
                return;

            # sort schema info by colum name if requested.
            if (sortByName):
                tblSchema.sort(key=lambda x: x[2])
            
        except Exception as ex:
            
            self.LogInternalError("{0}: DB Schema Foreign Key List Error for table \"{1}\" - {2}".format(methodName, tableName, str(ex)))
            return

        ctx:SITableViewerContext = SITableViewerContext()

        try:
        
            # write the header first.
            ctx.AppendHeader("ID, Sequence, Table, From, To, \"On Update\", \"On Delete\", Match")

            # write the columns.
            for column in tblSchema:

                # map the column schema.
                sColId:str = str(column[0])
                sColSeq:str = str(column[1])
                sColTable:str = str(column[2])
                sColFrom:str = str(column[3])
                sColTo:str = str(column[4])
                sColOnUpdate:str = str(column[5])
                sColOnDelete:str = str(column[6])
                sColMatch:str = str(column[7])

                # add column info to the context view.
                ctx.BeginRow()
                ctx.AddRowEntry(sColId)
                ctx.AddRowEntry(sColSeq)
                ctx.AddRowEntry(sColTable)
                ctx.AddRowEntry(sColFrom)
                ctx.AddRowEntry(sColTo)
                ctx.AddRowEntry(sColOnUpdate)
                ctx.AddRowEntry(sColOnDelete)
                ctx.AddRowEntry(sColMatch)
                ctx.EndRow()

            # send the packet.
            self._SendContext(level, title, SILogEntryType.DatabaseStructure, ctx, colorValue)
        
        except Exception as ex:
            
            self.LogInternalError("{0}: {1}".format(methodName, str(ex)))


    def LogSqliteDbSchemaIndexList(self, level:SILevel=None, title:str=None, conn:sqlite3.Connection=None, tableName:str=None, sortByName:bool=False, colorValue:SIColors=None) -> None:
        """
        Logs the schema of a Sqlite DB Table Index List with a custom title and custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            conn (Connection):
                Sqlite database connection object.
            tableName (str):
                The name of the table to obtain schema information for.
            sortByName (bool):
                Sorts the log data by Index Name (True) or by ID (False, default).
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method queries the schema information by executing the following SQL statement:
        "SELECT * FROM pragma_index_list('<tablename>');"

        This will log the following details returned from the schema information query:
        Sequence, Name, Unique, Origin, Partial
        """
        if (not self.IsOn(level)):
            return

        methodName:str = "LogSqliteDbSchemaIndexList"

        if (conn == None):
            self.LogInternalError("{0}: conn argument is null.".format(methodName))
            return

        if ((tableName == None) or (len(tableName) == 0)):
            self.LogInternalError("{0}: tableName argument is null or an empty string.".format(methodName))
            return

        # default title if one was not supplied.
        if (title == None) or (len(title) == 0):
            title = "Sqlite DB Schema Information: Table \"{0}\" - Index List".format(tableName)
            if (sortByName):
                title += " (sorted by index name)"

        tblSchema:list = None

        try:

            # more info on the return results of this schema query can be found here:
            # https://www.sqlite.org/pragma.html#pragma_index_list

            # sql to query db for schema info.
            sql:str = "SELECT * FROM pragma_index_list('{0}');".format(tableName)

            # execute sql.
            cursor:sqlite3.Cursor = conn.execute(sql)
            tblSchema = cursor.fetchall()

            # results contain information about the table foreign key list:
            # id, seq, table, from, to, on_update, on_delete, match
            if ((tblSchema == None) or (len(tblSchema)) == 0):
                self.LogInternalError("{0}: table name \"{1}\" does not exist.".format(methodName, tableName));
                return;

            # sort schema info by colum name if requested.
            if (sortByName):
                tblSchema.sort(key=lambda x: x[1])
            
        except Exception as ex:
            
            self.LogInternalError("{0}: DB Schema Index List Error for table \"{1}\" - {2}".format(methodName, tableName, str(ex)))
            return

        ctx:SITableViewerContext = SITableViewerContext()

        try:
        
            # write the header first.
            ctx.AppendHeader("Sequence, Name, \"Is Unique?\", Origin, \"Is Partial?\"")

            # write the columns.
            for column in tblSchema:

                # map the column schema.
                sColSeq:str = str(column[0])
                sColName:str = str(column[1])
                sColUnique:str = str(column[2])
                sColOrigin:str = str(column[3])
                sColPartial:str = str(column[4])

                # the "origin" column value signifies one of the following:
                # c  = index was created by a CREATE INDEX statement.
                # u  = index was created by a UNIQUE constraint.
                # pk = index was created by a PRIMARY KEY constraint.
                if (sColOrigin == "c"):
                    sColOrigin += " (CREATE INDEX)"
                elif (sColOrigin == "u"):
                    sColOrigin += " - (UNIQUE constraint)"
                elif (sColOrigin == "pk"):
                    sColOrigin += " - (PRIMARY KEY constraint)"

                # add column info to the context view.
                ctx.BeginRow()
                ctx.AddRowEntry(sColSeq)
                ctx.AddRowEntry(sColName)
                ctx.AddRowEntry(DataTypeHelper.BoolToStringYesNo(sColUnique))
                ctx.AddRowEntry(sColOrigin)
                ctx.AddRowEntry(DataTypeHelper.BoolToStringYesNo(sColPartial))
                ctx.EndRow()

            # send the packet.
            self._SendContext(level, title, SILogEntryType.DatabaseStructure, ctx, colorValue)
        
        except Exception as ex:
            
            self.LogInternalError("{0}: {1}".format(methodName, str(ex)))


    def LogSqliteDbSchemaTableInfo(self, level:SILevel=None, title:str=None, conn:sqlite3.Connection=None, tableName:str=None, sortByName:bool=False, colorValue:SIColors=None) -> None:
        """
        Logs the schema of a Sqlite DB Table with a custom title and custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            conn (Connection):
                Sqlite database connection object.
            tableName (str):
                The name of the table to obtain schema information for.
            sortByName (bool):
                Sorts the log data by Table Name (True) or by ID (False, default).
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method queries the schema information by executing the following SQL statement:
        "SELECT * FROM pragma_table_info('<tablename>');"

        This will log the following details returned from the schema information query:
        - id, name, data type, not null, default value, primary key, hidden column.
        """
        if (not self.IsOn(level)):
            return

        methodName:str = "LogSqliteDbSchemaTableInfo"

        if (conn == None):
            self.LogInternalError("{0}: conn argument is null.".format(methodName))
            return

        if ((tableName == None) or (len(tableName) == 0)):
            self.LogInternalError("{0}: tableName argument is null or an empty string.".format(methodName))
            return

        # default title if one was not supplied.
        if (title == None) or (len(title) == 0):
            title = "Sqlite DB Schema Information: Table \"{0}\" - Table Info".format(tableName)
            if (sortByName):
                title += " (sorted by name)"

        tblSchema:list = None

        try:

            # more info on the return results of this schema query can be found here:
            # https://www.sqlite.org/pragma.html#pragma_table_xinfo

            # sql to query db for schema info.
            sql:str = "SELECT * FROM pragma_table_xinfo('{0}');".format(tableName)

            # execute sql.
            cursor:sqlite3.Cursor = conn.execute(sql)
            tblSchema = cursor.fetchall()

            # results contain information about the table.
            # 'cid', 'name', 'type', 'notnull', 'dflt_value', 'pk', 'hidden'
            if ((tblSchema == None) or (len(tblSchema)) == 0):
                self.LogInternalError("{0}: table name \"{1}\" does not exist.".format(methodName, tableName));
                return;

            # sort schema info by colum name if requested.
            if (sortByName):
                tblSchema.sort(key=lambda x: x[1])
            
        except Exception as ex:
            
            self.LogInternalError("{0}: DB Schema Table Info Error for table \"{1}\" - {2}".format(methodName, tableName, str(ex)))
            return

        ctx:SITableViewerContext = SITableViewerContext()

        try:
        
            # write the header first.
            ctx.AppendHeader("ID, \"Column Name\", Type, \"Not NULL?\", \"Default Value\", \"Is Primary Key?\", Hidden")

            # write the columns.
            for column in tblSchema:

                # map the column schema.
                sColId:str = str(column[0])
                sColName:str = str(column[1])
                sColType:str = str(column[2])
                sColNotNull:bool = bool(column[3])
                sColDefaultValue:str = ""
                if (column[4] != None):
                    sColDefaultValue = str(column[4])                   
                sColPrimaryKey:bool = bool(column[5])
                sColHidden:str = str(column[6])

                # the "hidden" column value signifies one of the following:
                # 0 = normal column
                # 1 = hidden column in a virtual table
                # 2 = dynamic column
                # 3 = stored generated column 
                if (sColHidden == "0"):
                    sColHidden += " (normal)"
                elif (sColHidden == "1"):
                    sColHidden += " - (virtual)"
                elif (sColHidden == "2"):
                    sColHidden += " - (dynamic)"
                elif (sColHidden == "3"):
                    sColHidden += " - (stored generated)"
                else:
                    sColHidden += " - unknown"

                # add column info to the context view.
                ctx.BeginRow()
                ctx.AddRowEntry(sColId)
                ctx.AddRowEntry(sColName)
                ctx.AddRowEntry(sColType)
                ctx.AddRowEntry(DataTypeHelper.BoolToStringYesNo(sColNotNull))
                ctx.AddRowEntry(sColDefaultValue)
                ctx.AddRowEntry(DataTypeHelper.BoolToStringYesNo(sColPrimaryKey))
                ctx.AddRowEntry(sColHidden)
                ctx.EndRow()

            # send the packet.
            self._SendContext(level, title, SILogEntryType.DatabaseStructure, ctx, colorValue)
        
        except Exception as ex:
            
            self.LogInternalError("{0}: {1}".format(methodName, str(ex)))


    def LogSqliteDbSchemaTables(self, level:SILevel=None, title:str=None, conn:sqlite3.Connection=None, sortByName:bool=False, colorValue:SIColors=None) -> None:
        """
        Logs the schema table names defined in a Sqlite DB with a custom title and custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            conn (Connection):
                Sqlite database connection object.
            sortByName (bool):
                Sorts the log data by Table Name (True) or by entry order (False, default).
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method queries the schema information by executing the following SQL statement:
        "SELECT * FROM sqlite_schema WHERE type ='table';"

        This will log the following details returned from the schema information query:
        - type, name, tbl_name, rootpage, sql
        """
        if (not self.IsOn(level)):
            return

        methodName:str = "LogSqliteDbSchemaTables"

        if (conn == None):
            self.LogInternalError("{0}: conn argument is null.".format(methodName))
            return

        # default title if one was not supplied.
        if (title == None) or (len(title) == 0):
            title = "Sqlite DB Schema Information: Tables"
            if (sortByName):
                title += " (sorted by name)"

        tblSchema:list = None

        try:

            # more info on the return results of this schema query can be found here:
            # https://www.sqlitetutorial.net/sqlite-show-tables/

            # sql to query db for schema info.
            sql:str = "SELECT * FROM sqlite_schema WHERE type IN ('table','view');"

            # execute sql.
            cursor:sqlite3.Cursor = conn.execute(sql)
            tblSchema = cursor.fetchall()

            # results contain information about the table.
            # type, name, tbl_name, rootpage, sql
            if ((tblSchema == None) or (len(tblSchema)) == 0):
                self.LogInternalError("{0}: table list could not be queried.".format(methodName));
                return;

            # sort schema info by colum name if requested.
            if (sortByName):
                tblSchema.sort(key=lambda x: x[1])
            
        except Exception as ex:
            
            self.LogInternalError("{0}: DB Schema Table List Error - {1}".format(methodName, str(ex)))
            return

        ctx:SITableViewerContext = SITableViewerContext()

        try:
        
            # write the header first.
            ctx.AppendHeader("Type, Name, \"Table Name\", \"Root Page\", \"SQL\"")

            # write the columns.
            for column in tblSchema:

                # map the column schema.
                sColType:str = str(column[0])
                sColName:str = str(column[1])
                sColTableName:str = str(column[2])
                sColRootPage:str = str(column[3])
                sColSql:str = str(column[4])

                # add column info to the context view.
                ctx.BeginRow()
                ctx.AddRowEntry(sColType)
                ctx.AddRowEntry(sColName)
                ctx.AddRowEntry(sColTableName)
                ctx.AddRowEntry(sColRootPage)
                ctx.AddRowEntry(sColSql)
                ctx.EndRow()

            # send the packet.
            self._SendContext(level, title, SILogEntryType.DatabaseStructure, ctx, colorValue)
        
        except Exception as ex:
            
            self.LogInternalError("{0}: {1}".format(methodName, str(ex)))


    def LogStackTrace(self, level:SILevel=None, title:str=None, strace:list[FrameInfo]=None, startFrame:int=0, limit:int=None, colorValue:SIColors=None) -> None:
        """
        Logs a stack trace with a custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            strace (object):
                 StackTrace instance to log.
            startFrame (int):
                The offset of the first frame preceding the caller to print (default 0).
            limit (int):
                The number of frames to print (specify None to print all remaining frames).
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method logs the supplied stack trace. The resulting Log Entry contains all methods including the
        related classes lists. Furthermore the filename, line and columns numbers are included.
        """
        if (not self.IsOn(level)):
            return

        if (strace == None):
            self.LogInternalError("LogStackTrace: strace argument cannot be null.")
            return

        if (startFrame == None):
            startFrame = 0

        # default title if one was not supplied.
        if ((title == None) or (len(title) == 0)):
            title = "Stack trace"

        try:

            # create the context viewer.
            ctx:SIListViewerContext = SIListViewerContext()

            HEADER_FMT = "Call stack at {0}, line {1} in function {2}, frames {3} to {4} of {5}:"
            STACK_FMT = "{0}, line {1} in function {2}."

            # the caller stack frame is the specified starting frame in the list, as they control
            # what they want the starting point to be.
            callerFrame = strace[startFrame]

            # index of the first frame to print.
            begin = startFrame
    
            # index of the last frame to print.
            if limit:
                end = min(begin + limit, len(strace))
            else:
                end = len(strace)
    
            # write the caller stack frame header to the context viewer.
            file, line, func = callerFrame[1:4]
            sbhdr = str.format(HEADER_FMT, file, line, func, startFrame, end - 1, len(strace))
            ctx.AppendLine(sbhdr)

            # write the remaining stack frames to the context viewer (up to the specified limit).
            for frame in strace[begin:end]:

                file, line, func = frame[1:4]
                sbframe = str.format(STACK_FMT, file, line, func)
                ctx.AppendLine(sbframe)

            # send the packet.
            self._SendContext(level, title, SILogEntryType.Text, ctx, colorValue)

        except Exception as ex:
            
            self.LogInternalError("LogStackTrace: " + str(ex))


    def LogStream(self, level:SILevel=None, title:str=None, stream:BufferedReader=None, colorValue:SIColors=None) -> None:
        """
        Logs a stream with a custom log level and displays
        the content in a read-only text field.
        
        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            stream (BufferedStream):
                The stream to log.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
        """
        self.LogCustomStream(level, title, stream, SILogEntryType.Text, SIViewerId.Data, colorValue)


    def LogString(self, level:SILevel=None, name:str=None, value:str=None, colorValue:SIColors=None) -> None:
        """
        Logs a string value with a custom log level.
        
        Args:
            level (SILevel):
                The log level of this method call.
            name (str):
                The variable name.
            value (str):
                The variable value.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method logs the name and value of a string variable.
        A title like "name = \"Value\"" will be displayed in the Console.
        """
        if (not self.IsOn(level)):
            return

        # validations.
        if (name is None):
            name = "<null name>"

        try:

            # send log entry packet.
            title:str = str.format("{0} = \"{1}\"", name, value)
            self._SendLogEntry(level, title, SILogEntryType.VariableValue, SIViewerId.Title, colorValue)

        except Exception as ex:
                
            self.LogInternalError("LogString: " + str(ex))


    def LogSystem(self, level:SILevel=None, title:str=None, colorValue:SIColors=None) -> None:
        """
        Logs information about the system using a custom title and custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        The logged information include the version of the operating
        system, the Python version and more. This method is
        useful for logging general information at the program startup.
        This guarantees that the support staff or developers have
        general information about the execution environment.
        """
        if (not self.IsOn(level)):
            return

        # set default title if one was not supplied.
        if ((title == None) or (len(title) == 0)):
            title = "System Information"

        # get operating system bit depth.
        osbitdepth:str = "32-bit"
        if (sys.maxsize > 2**32):
            osbitdepth:str = "64-bit"

        ctx:SIInspectorViewerContext = SIInspectorViewerContext()

        try:
             
            ctx.StartGroup("Operating System Information");
            ctx.AppendKeyValue("Name", platform.system())
            ctx.AppendKeyValue("Version", platform.version())
            ctx.AppendKeyValue("Release", platform.release())
            ctx.AppendKeyValue("Platform", platform.platform())
            ctx.AppendKeyValue("Machine Architecture", platform.machine())
            ctx.AppendKeyValue("Bit Depth", osbitdepth)

            ctx.StartGroup("Machine Information");
            ctx.AppendKeyValue("Machine Name", platform.node())
            try:
                ctx.AppendKeyValue("User Login", os.getlogin())
            except Exception as ex:
                ctx.AppendKeyValue("User Login", "Error: " + str(ex))
            ctx.AppendKeyValue("Current directory", os.getcwd())

            ctx.StartGroup("Python Environment");
            ctx.AppendKeyValue("Version", platform.python_version())
            ctx.AppendKeyValue("Revision", platform.python_revision())
            ctx.AppendKeyValue("Build Date", str(platform.python_build()[1]))
            ctx.AppendKeyValue("Branch", platform.python_branch())
            ctx.AppendKeyValue("Compiler", platform.python_compiler())
            ctx.AppendKeyValue("Implementation", platform.python_implementation())

            # send the packet.
            self._SendContext(level, title, SILogEntryType.System, ctx, colorValue)
            
        except Exception as ex:
            
            self.LogInternalError("LogSystem: " + str(ex))


    def LogText(self, level:SILevel=None, title:str=None, text:str=None, colorValue:SIColors=None) -> None:
        """
        Logs a string with a custom log level and displays
        it in a read-only text field.
        
        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            text (str):
                The text to log.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
        """
        self.LogCustomText(level, title, text, SILogEntryType.Text, SIViewerId.Data, colorValue)


    def LogTextFile(self, level:SILevel=None, title:str=None, fileName:str=None, colorValue:SIColors=None) -> None:
        """
        Logs a text file and displays the content in a
        read-only text field using a custom title and custom log
        level.
        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            fileName (str):
                The file to log.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
        """
        self.LogCustomFile(level, title, fileName, SILogEntryType.Text, SIViewerId.Data, colorValue)


    def LogTextReader(self, level:SILevel=None, title:str=None, reader:TextIOWrapper=None, colorValue:SIColors=None) -> None:
        """
        Logs a text reader with a custom log level and
        displays the content in a read-only text field.
        
        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            reader (TextIOWrapper):
                The text reader to log.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
        """
        self.LogCustomReader(level, title, reader, SILogEntryType.Text, SIViewerId.Data, colorValue)


    def LogTextStream(self, level:SILevel=None, title:str=None, stream:BufferedReader=None, colorValue:SIColors=None) -> None:
        """
        Logs a stream with a custom log level and displays
        the content in a read-only text field.
        
        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            stream (BufferedStream):
                The stream to log.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
        """
        self.LogCustomStream(level, title, stream, SILogEntryType.Text, SIViewerId.Data, colorValue)


    def LogThread(self, level:SILevel=None, title:str=None, thread:Thread=None, colorValue:SIColors=None) -> None:
        """
        Logs information about a thread with a custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            thread (Thread):
                The thread to log.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method logs information about the supplied thread. This
        includes its name, its current state and more.

        LogThread is especially useful in a multi-threaded program
        like in a network server application. By using this method you
        can easily track all threads of a process and obtain detailed
        information about them.
        """
        if (not self.IsOn(level)):
            return

        ctx:SIValueListViewerContext = SIValueListViewerContext()
        
        try:
                
            # was an object to log supplied?
            if (thread is None):
                    
                # no - just append a line to the context viewer.
                ctx.AppendLine("<The thread argument to log was null>")

            else:
                    
                # set default title if one was not supplied.
                if ((title == None) or (len(title) == 0)):
                    title = self._GetThreadTitle(thread, None)

                # gather information about the thread.           
                ctx.AppendKeyValue("Thread Name", thread.name)
                ctx.AppendKeyValue("Is Alive?", str(thread.is_alive()))

                if (thread.is_alive):
                
                    #ctx.AppendKeyValue("Priority", thread. .Priority.ToString())
                    ctx.AppendKeyValue("ID", str(thread.ident))
                    ctx.AppendKeyValue("Native ID", str(thread.native_id))
                    ctx.AppendKeyValue("Is Daemon?", str(thread.daemon))

            # send the packet.
            self._SendContext(level, title, SILogEntryType.Text, ctx, colorValue)
            
        except Exception as ex:
            
            self.LogInternalError("LogThread: " + str(ex))


    def LogValue(self, level:SILevel=None, name:str=None, value=None, colorValue:SIColors=None) -> None:
        """
        Logs the name and value of a variable with a custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            name (str):
                The variable name.
            value (object):
                The variable value.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method just calls the appropriate "LogX" method (e.g. LogString, LogInt, etc) 
        based upon the type of value as determined by isinstance.  Note that it is faster to
        call the "LogX" method directly - this method is provided for C# SI compatibility.
        """
        if (not self.IsOn(level)):
            return

        if (value == None):
            self.LogObjectValue(level, name, value, colorValue)
        elif isinstance(value, str):
            self.LogString(level, name, value, colorValue)
        elif isinstance(value, bool):
            self.LogBool(level, name, value, colorValue)
        elif isinstance(value, int):
            self.LogInt(level, name, value, colorValue)
        elif isinstance(value, float):
            self.LogFloat(level, name, value, colorValue)
        elif isinstance(value, complex):
            self.LogComplex(level, name, value, colorValue)
        elif isinstance(value, datetime.datetime):
            self.LogDateTime(level, name, value, colorValue)
        #elif isinstance(value, chr):               # <- force user to call LogChar directly, as this was causing exceptions in testing!
        #    self.LogChar(level, name, value)
        else:
            self.LogObjectValue(level, name, value, colorValue)


    def LogVerbose(self, title:str, *args, colorValue:SIColors=None, logToSystemLogger:bool=True) -> None:
        """
        Logs a verbose message with a log level of SILevel.Verbose.

        Args:
            title (str):
                The message to log.
            *args:
                Format arguments for the title argument.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
            logToSystemLogger (bool):
                True to log the exception to the SystemLogger instance (if one was supplied);  
                otherwise, False to not log the exception to the SystemLogger instance.  
                Default is True.

        This method will also log a message to the system log if the `SystemLogger` property is set.
        """
        # is system logging enabled?  if so, then log the message there.
        if (self._fSystemLogger != None) and (logToSystemLogger):
            self._fSystemLogger.debug(title, *args)

        if (not self.IsOn(SILevel.Verbose)):
            return

        try:
                
            # format title if *args was supplied.
            if (title) and (args):
                title = (title % args)

            # send the packet.
            self._SendLogEntry(SILevel.Verbose, title, SILogEntryType.Verbose, SIViewerId.Title, colorValue)

        except Exception as ex:
                
            self.LogInternalError("LogVerbose: " + str(ex))


    def LogWarning(self, title:str, *args, colorValue:SIColors=None, logToSystemLogger:bool=True) -> None:
        """
        Logs a warning message with a log level of SILevel.Warning.

        Args:
            title (str):
                The message to log.
            *args:
                Format arguments for the title argument.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
            logToSystemLogger (bool):
                True to log the exception to the SystemLogger instance (if one was supplied);  
                otherwise, False to not log the exception to the SystemLogger instance.  
                Default is True.

        This method will also log a message to the system log if the `SystemLogger` property is set.
        """
        # is system logging enabled?  if so, then log the message there.
        if (self._fSystemLogger != None) and (logToSystemLogger):
            self._fSystemLogger.warning(title, *args)

        if (not self.IsOn(SILevel.Warning)):
            return

        try:
                
            # format title if *args was supplied.
            if (title) and (args):
                title = (title % args)

            # send the packet.
            self._SendLogEntry(SILevel.Warning, title, SILogEntryType.Warning, SIViewerId.Title, colorValue)

        except Exception as ex:
                
            self.LogInternalError("LogWarning: " + str(ex))
                

    def LogXml(self, level:SILevel=None, title:str=None, xml:str=None, colorValue:SIColors=None,
               prettyPrint:bool=False
               ) -> None:
        """
        Logs XML source code that is displayed with syntax
        highlighting in the Console using a custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            xml (str):
                The XML source code to log.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
            prettyPrint (bool):
                True to format the xml with ElementTree before logging; otherwise, just log
                the xml using a custom text viewer (e.g. Xml Source).

        This method displays the supplied XML source code with syntax
        highlighting in the Console. 
        """
        if (prettyPrint == True) and (xml is not None):
            
            try:
            
                # if using pretty print, then format the xml and log it as text.
                addXmlDeclare:bool = False
                if len(xml) > 5:
                    if xml[0:5].lower().startswith('<?xml'):
                        addXmlDeclare = True
                elmPrettyXml:Element = fromstring(xml)
                ElementTree.indent(elmPrettyXml)  
                strPrettyXml:str = ElementTree.tostring(elmPrettyXml, encoding='unicode', xml_declaration=addXmlDeclare)
                self.LogCustomText(level, title, strPrettyXml, SILogEntryType.Source, SISourceId.Xml, colorValue)
            
            except Exception as ex:
            
                self.LogInternalError("LogXml (pretty print): " + str(ex))
                
                # log the xml as-is.
                self.LogCustomText(level, title, xml, SILogEntryType.Source, SISourceId.Xml, colorValue)

        else:

            # no pretty print - log it as-is.
            self.LogCustomText(level, title, xml, SILogEntryType.Source, SISourceId.Xml, colorValue)


    def LogXmlFile(self, level:SILevel=None, title:str=None, fileName:str=None, colorValue:SIColors=None) -> None:
        """
        Logs the content of a file as XML source code with syntax
        highlighting using a custom title and custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title to display in the Console.
            fileName (str):
                The name of the file which contains the XML source code.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.

        This method displays the XML source file with syntax highlighting
        in the Console. 
        """
        self.LogCustomFile(level, title, fileName, SILogEntryType.Source, SISourceId.Xml, colorValue)        


    def ResetCallstack(self, level:SILevel=None) -> None:
        """
        Resets the call stack by using a custom log level.
        
        Args:
            level (SILevel):
                The log level of this method call.
        
        This method instructs the Console to reset the call stack
        generated by the EnterMethod and LeaveMethod methods. It
        is especially useful if you want to reset the indentation
        in the method hierarchy without clearing all log entries.
        """
        if (not self.IsOn(level)):
            return

        try:

            # send log entry packet.
            self._SendLogEntry(level, "", SILogEntryType.ResetCallstack, SIViewerId.NoViewer)

        except Exception as ex:
                
            self.LogInternalError("ResetCallstack: " + str(ex))


    def ResetCheckpoint(self, name:str=None) -> None:
        """
        Resets a named checkpoint counter.
        
        Args:
            name (str):
                The name of the checkpoint to reset.

        This method resets the counter of the given named checkpoint.
        Named checkpoints can be incremented and logged with the
        AddCheckpoint method.
        """
        # validations.
        if (name == None):
            name = "Checkpoint"

        with self._fLock:

            if name in self._fCheckpoints.keys():
                self._fCheckpoints.pop(name)


    def ResetColor(self) -> None:
        """
        Resets the session background color to its default value.

        The default background color of a session is white transparent.
        """
        self._fColorBG = SIColor(DEFAULT_COLOR_VALUE)


    def ResetCounter(self, name:str=None) -> None:
        """
        Resets a named counter to its initial value of 0.
        
        Args:
            name (str):
                The name of the counter to reset.

        This method resets the integer value of a named counter to 0
        again. If the supplied counter is unknown, this method has no
        effect. Please refer to the IncCounter and DecCounter methods
        for more information about named counters.
        """
        # validations.
        if (name == None):
            self.LogInternalError("ResetCounter: name argument is null.")
            return

        with self._fLock:

            if name in self._fCounters.keys():
                self._fCounters.pop(name)


    def SendCustomControlCommand(self, level:SILevel, ct:SIControlCommandType, data:BytesIO=None) -> None:
        """
        Logs a custom Control Command with a custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            ct (SIControlCommandType):
                The Control Command type to use.
            data (BytesIO):
                Optional data stream which can be null.               
        """
        if (not self.IsOn(level)):
            return

        try:

            if (data == None):
                self._SendControlCommand(ct, None)
                return

            oldPosition:int = 0

            # save original stream position (if possible).
            if (data.seekable):
                    
                oldPosition = data.tell()
                data.Position = 0

            try:
                    
                # send the packet.
                self._SendControlCommand(ct, data)
                    
            finally:
                    
                # restore stream position (if possible).
                if (data.seekable):
                    data.seek(oldPosition)
                    
        except Exception as ex:
                
            self.LogInternalError("SendCustomControlCommand: " + str(ex))


    def SendCustomLogEntry(self, level:SILevel, title:str, lt:SILogEntryType, vi:SIViewerId, colorValue:SIColors=None, data:BytesIO=None) -> None:
        """
        Logs a custom Log Entry with a custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title of the new Log Entry.
            lt (SILogEntryType):
                The Log Entry type to use.
            vi (SIViewerId):
                The Viewer ID to use.
            colorValue (SIColors):
                Background color value (SIColors enum, or ARGB integer form) for the message.
                Refer to the SIColors enum in the sicolor module for common color values.
                Specify None to use default background color.
            data
                Optional data stream which can be null (or None).

        This method is useful for implementing custom Log Entry
        methods. For example, if you want to display some information
        in a particular way in the Console, you can just create a
        simple method which formats the data in question correctly and
        logs them using this SendCustomLogEntry method.
        """
        if (not self.IsOn(level)):
            return

        try:

            if (data != None):
                
                # Use the LogCustomStream method, because the
                # supplied stream needs to be processed correctly.
                self.LogCustomStream(level, title, data, lt, vi)
                
            else:
                
                # send log entry packet.
                self._SendLogEntry(level, title, lt, vi, colorValue, None)

        except Exception as ex:
                
            self.LogInternalError("SendCustomLogEntry: " + str(ex))


    def SendCustomProcessFlow(self, level:SILevel, title:str, pt:SIProcessFlowType) -> None:
        """
        Logs a custom Process Flow entry with a custom log level.

        Args:
            level (SILevel):
                The log level of this method call.
            title (str):
                The title of the new Process Flow entry.
            pt (SIProcessFlowType):
                The Process Flow type to use.
        """
        if (not self.IsOn(level)):
            return

        try:

            # send process flow packet.
            self._SendProcessFlow(level, title, pt)

        except Exception as ex:
                
            self.LogInternalError("SendCustomProcessFlow: " + str(ex))


    def SendCustomWatch(self, level:SILevel=None, name:str=None, value=None, watchType:SIWatchType=None) -> None:
        """
        Logs a custom Watch with a custom log level.
        
        Args:
            level (SILevel):
                The log level of this method call.
            name (str):
                The name of the Watch.
            value (object):
                The value of the Watch.
            watchType (SIWatchType):
                The Watch type to use
        
        This method is useful for implementing custom Watch methods.
        For example, if you want to track the status of an instance of
        a specific class, you can just create a simple method which
        extracts all necessary information about this instance and logs
        them using this SendCustomWatch method.
        """
        # just invoke the Watch method, since they are the same calling parameters.
        # the SendCustomWatch method is provided for C# SI compatibility.
        self.Watch(level, name, value, watchType)


    def Watch(self, level:SILevel=None, name:str=None, value=None, watchType:SIWatchType=None) -> None:
        """
        Logs a Watch value by using the specified (or default) log level.
        
        Args:
            level (SILevel):
                The log level of this method call.
            name (str):
                The name of the Watch.
            value:
                The bool value to display as Watch value.
            watchType (SIWatchType):
                WatchType to set in the Log Entry.

        "null" will be displayed if value=None.
        
        This method uses the SmartInspect.DefaultLevel value if the level
        parameter is set to None (default).  Otherwise, the specified level
        is utilized.
        """
        if (not self.IsOn(level)):
            return

        try:

            title:str = ""
            wt:SIWatchType = None

            # validations.
            if (name == None):
                name = ""

            if (value == None):
                value = "null"

            if (watchType != None):
                wt = watchType

            # determine the value format and watch type to use, based on the type
            # of the value. The latter can be overridden via the `watchType`
            # argument, which can also affect formatting (e.g. SIWatchType.Address).
            if isinstance(value, str):
                wt = SIWatchType.String
                title = str.format("{0}", value)
            elif isinstance(value, bool):
                wt = SIWatchType.Boolean
                title = value and 'True' or 'False'
            elif isinstance(value, int):
                wt = SIWatchType.Integer
                title = str.format("{0}", str(value))
            elif isinstance(value, float):
                wt = SIWatchType.Float
                title = str.format("{0}", str(value))
            elif isinstance(value, complex):
                wt = SIWatchType.String
                title = str.format("{0}", str(value))
            elif watchType == SIWatchType.Address:
                wt = watchType
                title = str.format("{0}", str(id(value)))
            elif isinstance(value, bytes):
                wt = SIWatchType.Integer
                title = str.format("{0}", str(int.from_bytes(value, byteorder='big')))
            elif isinstance(value, datetime.datetime):
                wt = SIWatchType.Timestamp
                title = str.format("{0}", str(value))
            else:
                wt = SIWatchType.String
                title = str.format("{0}", value)

            # send watch entry.
            self._SendWatch(level, name, title, wt)

        except Exception as ex:
                
            self.LogInternalError("Watch: " + str(ex))


    def WatchBool(self, level:SILevel=None, name:str=None, value:bool=False) -> None:
        """
        Logs a boolean Watch with a custom log level.
        
        Args:
            level (SILevel):
                The log level of this method call.
            name (str):
                The name of the Watch.
            value (bool):
                The bool value to display as Watch value.
        
        This method uses the SmartInspect.DefaultLevel value if the level
        parameter is set to None (default).  Otherwise, the specified level
        is utilized.
        """
        if (not self.IsOn(level)):
            return

        # use "True"/"False" in case other boolean values passed (e.g. 0/1, yes/no, on/off, etc).
        if (value == True):
            v:str = "True"
        else:
            v:str = "False"
        self._SendWatch(level, name, v, SIWatchType.Boolean)


    def WatchByte(self, level:SILevel=None, name:str=None, value:int=0, includeHex:bool=False) -> None:
        """
        Logs a byte Watch with an optional hexadecimal representation and custom log level.
        
        Args:
            level (SILevel):
                The log level of this method call.
            name (str):
                The name of the Watch.
            value (int):
                The byte value to display as Watch value.
            includeHex (bool):
                Indicates if a hexadecimal representation should be included.
        
        This method logs a byte Watch. You can specify if a
        hexadecimal representation should be included as well
        by setting the includeHex parameter to true.

        This method uses the SmartInspect.DefaultLevel value if the level
        parameter is set to None (default).  Otherwise, the specified level
        is utilized.
        """
        if (not self.IsOn(level)):
            return

        v:str = str(value)
        if (includeHex):
            vhex:str = " (" + hex(value).upper() + ")"
            vhex = vhex.replace("0X","0x")      # make "0X" lower-case since hex values will be in upper-case
            v += vhex
            
        self._SendWatch(level, name, v, SIWatchType.Integer)


    def WatchChar(self, level:SILevel=None, name:str=None, value:chr=0) -> None:
        """
        Logs a chr Watch with a custom log level.
        
        Args:
            level (SILevel):
                The log level of this method call.
            name (str):
                The name of the Watch.
            value (chr):
                The chr value to display as Watch value.
        
        This method uses the SmartInspect.DefaultLevel value if the level
        parameter is set to None (default).  Otherwise, the specified level
        is utilized.
        """
        if (not self.IsOn(level)):
            return

        v:str = str(value)
        self._SendWatch(level, name, v, SIWatchType.Char)


    def WatchComplex(self, level:SILevel=None, name:str=None, value:complex=None) -> None:
        """
        Logs a complex Watch with a custom log level.
        
        Args:
            level (SILevel):
                The log level of this method call.
            name (str):
                The name of the Watch.
            value (complex):
                The complex value to display as Watch value.
        
        This method uses the SmartInspect.DefaultLevel value if the level
        parameter is set to None (default).  Otherwise, the specified level
        is utilized.
        """
        if (not self.IsOn(level)):
            return

        v:str = str(value)
        self._SendWatch(level, name, v, SIWatchType.Integer)


    def WatchDateTime(self, level:SILevel=None, name:str=None, value:datetime=None) -> None:
        """
        Logs a datetime Watch with a custom log level.
        
        Args:
            level (SILevel):
                The log level of this method call.
            name (str):
                The name of the Watch.
            value (datetime)
                The datetime value to display as Watch value.
        
        This method uses the SmartInspect.DefaultLevel value if the level
        parameter is set to None (default).  Otherwise, the specified level
        is utilized.
        """
        if (not self.IsOn(level)):
            return

        v:str = str(value)
        self._SendWatch(level, name, v, SIWatchType.Timestamp)


    def WatchFloat(self, level:SILevel=None, name:str=None, value:float=0) -> None:
        """
        Logs a float Watch with a custom log level.
        
        Args:
            level (SILevel):
                The log level of this method call.
            name (str):
                The name of the Watch.
            value (float):
                The float value to display as Watch value.
        
        This method uses the SmartInspect.DefaultLevel value if the level
        parameter is set to None (default).  Otherwise, the specified level
        is utilized.
        """
        if (not self.IsOn(level)):
            return

        v:str = str(value)
        self._SendWatch(level, name, v, SIWatchType.Integer)


    def WatchInt(self, level:SILevel=None, name:str=None, value:int=0, includeHex:bool=False) -> None:
        """
        Logs an integer Watch with an optional hexadecimal representation and custom log level.
        
        Args:
            level (SILevel):
                The log level of this method call.
            name (str):
                The name of the Watch.
            value (int):
                The integer value to display as Watch value.
            includeHex (bool):
                Indicates if a hexadecimal representation should be included.
        
        This method logs a integer Watch. You can specify if a
        hexadecimal representation should be included as well
        by setting the includeHex parameter to true.

        This method uses the SmartInspect.DefaultLevel value if the level
        parameter is set to None (default).  Otherwise, the specified level
        is utilized.
        """
        if (not self.IsOn(level)):
            return

        v:str = str(value)
        if (includeHex):
            vhex:str = " (" + hex(value).upper() + ")"
            if (value < 0):
                vhex = vhex.replace("-","")     # remove minus sign for negative values.
            vhex = vhex.replace("0X","0x")      # make "0X" lower-case since hex values will be in upper-case
            v += vhex
            
        self._SendWatch(level, name, v, SIWatchType.Integer)


    def WatchObject(self, level:SILevel=None, name:str=None, value:object=None) -> None:
        """
        Logs an object Watch with a custom log level.
        
        Args:
            level (SILevel):
                The log level of this method call.
            name (str):
                The name of the Watch.
            value (object):
                The object value to display as Watch value.

        The value of the resulting Watch is the return value of the
        "str(value)" method of the supplied object.
        
        This method uses the SmartInspect.DefaultLevel value if the level
        parameter is set to None (default).  Otherwise, the specified level
        is utilized.
        """
        if (not self.IsOn(level)):
            return

        if (value != None):
            v = "" + str(value)
            self._SendWatch(level, name, v, SIWatchType.Object)
        else:
            self.LogInternalError(str.format("WatchObject: value argument is null for watch name \"{0}\".", "" + name));


    def WatchString(self, level:SILevel=None, name:str=None, value:str=None) -> None:
        """
        Logs a string Watch with a custom log level.
        
        Args:
            level (SILevel):
                The log level of this method call.
            name (str):
                The name of the Watch.
            value (str):
                The string value to display as Watch value.
        
        This method uses the SmartInspect.DefaultLevel value if the level
        parameter is set to None (default).  Otherwise, the specified level
        is utilized.
        """
        if (not self.IsOn(level)):
            return

        self._SendWatch(level, name, value, SIWatchType.String)


    #def Track(self, func):
    #    """
    #    Decorator to add process flow tracking around the wrapped function.
    #    """
    #    def wrapped(*args, **kwargs):
    #        self.EnterMethod(func.__name__)
    #        try:
    #            return func(*args, **kwargs)
    #        finally:
    #            self.LeaveMethod(func.__name__)
    #    return wrapped

    #__Logging process flow using the decorator:__

    #``` python
    #>>> @logger.track
    #>>> def append(self, obj):
    #>>>     pass   # do something
    #```
