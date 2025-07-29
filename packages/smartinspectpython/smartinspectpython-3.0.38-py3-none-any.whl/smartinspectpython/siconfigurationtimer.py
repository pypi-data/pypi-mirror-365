import _threading_local
from ctypes import ArgumentError
import os
import threading
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler, FileModifiedEvent, FileCreatedEvent, FileDeletedEvent

# our package imports.
from .siargumentnullexception import SIArgumentNullException
#from .smartinspect import SmartInspect   # cannot import this due to circular reference.

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIConfigurationTimer:
    """
    Monitors a SmartInspect configuration settings file for changes
    and reloads the configuration when it does.
    
    A watchdog `Observer` class is used to monitor the configuration filepath
    for changes (create, update, delete).
        
    The `SmartInspect.LoadConfiguration` method is called if the configuration 
    filepath is created or changed.  
        
    The `SmartInspect.Enabled` property is set to False if the configuration 
    filepath is deleted (e.g. disables SmartInspect logging).  
    
    For information about SmartInspect configuration files, please
    refer to the documentation of the SmartInspect.LoadConfiguration
    method.

    Threadsafety:
        This class is fully thread-safe.

    <details>
        <summary>Sample Code</summary>
    ``` python
    .. include:: ../docs/include/samplecode/SIConfigurationTimer/LoadConfiguration.py
    ```
    <br/>
    The following is the configuration settings file contents:
    ``` ini
    .. include:: ../docs/include/samplecode/smartinspect.cfg
    ```
    </details>
    """

    def __init__(self, smartInspect:object, filePath:str) -> None:
        """
        Initializes a new instance of the class.

        Args:
            smartInspect (SmartInspect):
                The SmartInspect object to configure.
            filePath (str):
                The path of the configuration file to monitor.

        Raises:
            SIArgumentNullException:
                The smartInspect or filePath parameter is null.

        The monitoring of the file begins immediately.
        """
        # validations:
        if (smartInspect == None):
            raise SIArgumentNullException("smartInspect")
        if (filePath == None):
            raise SIArgumentNullException("filePath")

        # initialize instance.
        self._fLock:object = _threading_local.RLock()
        self._fSmartInspect:object = smartInspect
        self._fFilePath:str = filePath
        self._fStarted = False
        self._fStopRequested = False

        # start monitoring the filepath for changes.
        self.Start()


    def __enter__(self) -> 'SIConfigurationTimer':
        # if called via a context manager (e.g. "with" statement).
        # start monitoring the filepath for changes.
        self.Start()
        return self


    def __exit__(self, etype, value, traceback) -> None:
        # if called via a context manager (e.g. "with" statement).
        # stop monitoring the filepath for changes.
        self.Stop()
        return False


    def _MonitorFileTask(self, instance) -> None:
        """
        Starts a watchdog `Observer` class to monitor the configuration filepath
        for changes (create,update,delete).
        
        The `SmartInspect.LoadConfiguration` method is called if the configuration 
        filepath is created or changed.  
        
        The `SmartInspect.Enabled` property is set to False if the configuration 
        filepath is deleted.  
        """
        fileObserver:Observer = None
        
        try:
            
            # the event handler is the object that will be notified when something happens 
            # on the filesystem we are monitoring.
            # the pattern array to match should be file base name(s) (e.g. name.extension).
            baseName:str = os.path.basename(self._fFilePath)   #filename.extension
            fileEventHandler = PatternMatchingEventHandler(patterns=[baseName], 
                                                           ignore_patterns=None, 
                                                           ignore_directories=True, 
                                                           case_sensitive=False)
            
            # add event handlers for various file operations.
            fileEventHandler.on_created = self._OnCreated
            fileEventHandler.on_deleted = self._OnDeleted
            fileEventHandler.on_modified = self._OnModified

            # create the observer, which will monitor the filesystem, looking for changes 
            # that will be handled by the event handler.
            # in our case, we are looking for changes to 1 file in a single directory.
            dirPath:str = os.path.dirname(self._fFilePath)
            if dirPath is None or len(dirPath) == 0:
                dirPath = "."
            fileObserver = Observer()
            fileObserver.schedule(fileEventHandler, dirPath, recursive=False)

            # start the observer.
            fileObserver.start()

            # process until we are asked to stop by main thread.
            while (True):

                with (self._fLock):
        
                    # were we asked to stop?  if so, then we are done.
                    if (self._fStopRequested):
                        break

                    # is main thread still alive?  if not, then we are done.
                    if (not threading.main_thread().is_alive()):
                        break

                    # sleep for a time, giving other threads a chance to do their thing.
                    time.sleep(5)

        except Exception as ex:
        
            # ignore exceptions.
            pass
        
        finally:
        
            # if observer was started, then stop it.
            if fileObserver is not None:
                fileObserver.stop()
                fileObserver.join()
    
            # indicate we are not monitoring.
            self._fStarted = False

            # reset stop requested status.
            self._fStopRequested = False


    def _OnCreated(self, event:FileCreatedEvent):
        """ 
        Called when a configuration filepath has been created. 
        """
        self._fSmartInspect.RaiseInfoEvent("SI Configuration File was created: \"{0}\"".format(event.src_path))
        # we won't reload it here, since an `_OnChanged` event will be fired 
        # immediately after to issue the reload.


    def _OnDeleted(self, event:FileDeletedEvent):
        """ 
        Called when a configuration filepath has been deleted. 
        
        SmartInspect logger will be disabled when the monitored configuration file is deleted.
        """
        self._fSmartInspect.RaiseInfoEvent("SI Configuration File was deleted; disabling SmartInspect logger for file \"{0}\"".format(event.src_path))
        self._fSmartInspect.Enabled = False


    def _OnModified(self, event:FileModifiedEvent):
        """ 
        Called when a configuration filepath has been modified. 
        
        """
        self._fSmartInspect.RaiseInfoEvent("SI Configuration File was changed; reloading configuration from file \"{0}\"".format(event.src_path))

        # use the file path value from the constructor, instead of the event source path.
        # the LoadConfiguration method is expecting the exact same name that it passed to the 
        # constructor, which can vary slightly depending on operating system; for example, 
        # the constructor file is "./test/si.cfg", while the event source  is "./test\si.cfg".
        self._fSmartInspect.LoadConfiguration(self._fFilePath, True)
    

    def Start(self) -> None:
        """
        Starts monitoring the configuration file for changes.

        This method is called automatically when a new instance of the class 
        is created.  It can also be called after issuing a "Stop" method
        call, to restart monitoring of the configuration file.

        It will start a new thread named "SiConfigFileMonitorTask" that will
        execute the watchdog Observer that monitors the specified configuration 
        filepath for changes.
        """
        with (self._fLock):

            # if threadtask is already running then don't bother.
            if (self._fStarted):
                return

            # reset stop requested status.
            self._fStopRequested = False

            # start the thread task to monitor the file.
            self._fThread = threading.Thread(target=self._MonitorFileTask, args=(self,))
            self._fThread.name = "SiConfigFileMonitorTask"
            self._fThread.start()
                    
            # indicate we are monitoring.
            self._fStarted = True


    def Stop(self) -> None:
        """
        Stops monitoring the configuration file for changes.
        """
        with (self._fLock):

            # if threadtask has not started yet then we are done.
            if (not self._fStarted):
                return

            # inform the thread task we want it to stop.
            self._fStopRequested = True

        # wait for the monitoring threadtask to finish up.
        if (self._fThread != None):
            self._fThread.join()

        # reset threadtask object.
        self._fThread = None
