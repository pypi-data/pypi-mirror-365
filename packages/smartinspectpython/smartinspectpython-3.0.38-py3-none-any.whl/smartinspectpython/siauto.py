"""
Module: siauto.py

<details>
  <summary>Revision History</summary>

| Date       | Version     | Description      |
| ---------- | ----------- | -----------------|
| 2023/09/27 | 3.0.21.0    | Updated documentation sample code and examples.
| 2023/05/30 | 3.0.0.0     | Initial Version. | 

</details>

Provides automatically created objects for using SmartInspect Python logging.  

The following classes are imported when `from smartinspectpython.siauto import *` is specified:  
- SIArgumentNullException
- SIArgumentOutOfRangeException
- SIAuto
- SIColors
- SIConfigurationTimer
- SIControlCommandEventArgs
- SIErrorEventArgs
- SIFilterEventArgs
- SIInfoEventArgs
- SILevel
- SILogEntryEventArgs
- SIMethodParmListContext
- SIProcessFlowEventArgs
- SISession
- SIWatchEventArgs
- SmartInspectException
"""

# all classes to import when "import *" is specified.
__all__ = [
    'SIArgumentNullException',
    'SIArgumentOutOfRangeException',
    'SIAuto',
    'SIColors',
    'SIConfigurationTimer',
    'SIControlCommandEventArgs',
    'SIErrorEventArgs',
    'SIFilterEventArgs',
    'SIInfoEventArgs',
    'SILevel',
    'SILogEntryEventArgs',
    'SIMethodParmListContext',
    'SIProcessFlowEventArgs',
    'SISession',
    'SISourceId',
    'SIWatchEventArgs',
    'SmartInspectException'
]

import os

# our package imports.
from .siargumentnullexception import SIArgumentNullException
from .siargumentoutofrangeexception import SIArgumentOutOfRangeException
from .sicolor import SIColors
from .siconfigurationtimer import SIConfigurationTimer
from .sicontrolcommandeventargs import SIControlCommandEventArgs
from .sierroreventargs import SIErrorEventArgs
from .sifiltereventargs import SIFilterEventArgs
from .siinfoeventargs import SIInfoEventArgs
from .silevel import SILevel
from .silogentryeventargs import SILogEntryEventArgs
from .simethodparmlistcontext import SIMethodParmListContext
from .siprocessfloweventargs import SIProcessFlowEventArgs
from .sisession import SISession
from .sisourceid import SISourceId
from .siutils import static_init
from .siwatcheventargs import SIWatchEventArgs
from .smartinspect import SmartInspect
from .smartinspectexception import SmartInspectException


@static_init    # indicate we have a static init method.
class SIAuto:
    """
    Provides automatically created objects for using the SmartInspect and SISession classes.

    This class provides a static property called Si of type SmartInspect.
    Furthermore a SISession instance named Main with Si as parent is ready to use. The siauto module 
    is especially useful if you do not want to create SmartInspect and SISession instances by yourself.

    The SmartInspect.Connections property of Si is set to "tcp(host=localhost)", the
    SmartInspect.AppName property to "Auto" and the SISession.Name property to "Main".

    Threadsafety:
        The public static members of this class are thread-safe.

    <details>
        <summary>Sample Code</summary>
    ``` python
    .. include:: ../docs/include/samplecode/SIAuto/_class.py
    ```
    <br/>
    The following is the configuration settings file contents:
    ``` ini
    .. include:: ../docs/include/samplecode/smartinspect.cfg
    ```
    </details>  
    """

    """
    ## Static Properties
    """

    # static properties.
    Si:SmartInspect = None   
    """ 
    SmartInspect logging instance (automatically created). 
    """


    Main:SISession = None
    """ 
    SmartInspect logging Session instance ('Main', automatically created). 

    The SISession.Name is set to "Main" and the SISession.Parent to SIAuto.Si.

    <details>
        <summary>Sample Code</summary>
    ``` python
    .. include:: ../docs/include/samplecode/SIAuto/Main.py
    ```
    </details>   
    """


    @classmethod
    def static_init(cls) -> None:
        """ 
        Initializes a new static instance of the class.
        """
        # Note - at this point, you cannot call any of the static methods in this class,
        # as we are still in the initilization phase!

        # create a new smartinspect instance, using the
        # entry point name as the appname.
        cls.Si = SmartInspect(os.path.basename(os.sys.argv[0]))

        # set default connections string, logging levels, and disable by default.
        cls.Si.Connections = 'tcp(host=localhost)'
        cls.Si.Enabled = False
        cls.Si.Level = SILevel.Debug
        cls.Si.DefaultLevel = SILevel.Debug

        # create new default session, named "Main".
        cls.Main = cls.Si.AddSession('Main', True)
        cls.Main.Level = SILevel.Debug
