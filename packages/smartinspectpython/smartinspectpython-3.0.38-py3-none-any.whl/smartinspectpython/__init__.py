# include the README.md file for pdoc documentation generation.
"""
.. include:: ../README.md

_________________

<details>
  <summary>View Change Log</summary>
.. include:: ../CHANGELOG.md
</details>
"""

# our package imports.
from smartinspectpython.siargumentnullexception import SIArgumentNullException
from smartinspectpython.siauto import SIAuto
from smartinspectpython.siargumentoutofrangeexception import SIArgumentOutOfRangeException
from smartinspectpython.sicolor import SIColors
from smartinspectpython.siconfigurationtimer import SIConfigurationTimer
from smartinspectpython.sicontrolcommandeventargs import SIControlCommandEventArgs
from smartinspectpython.sierroreventargs import SIErrorEventArgs
from smartinspectpython.sifiltereventargs import SIFilterEventArgs
from smartinspectpython.siinfoeventargs import SIInfoEventArgs
from smartinspectpython.silevel import SILevel
from smartinspectpython.silogentryeventargs import SILogEntryEventArgs
from smartinspectpython.simethodparmlistcontext import SIMethodParmListContext
from smartinspectpython.siprocessfloweventargs import SIProcessFlowEventArgs
from smartinspectpython.sisession import SISession
from smartinspectpython.sisourceid import SISourceId
from smartinspectpython.siwatcheventargs import SIWatchEventArgs
from smartinspectpython.smartinspectexception import SmartInspectException

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
