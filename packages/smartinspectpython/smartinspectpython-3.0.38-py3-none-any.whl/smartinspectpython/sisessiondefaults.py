# external package imports.
import _threading_local

# our package imports.
from .sicolor import SIColor
from .silevel import SILevel
from .sisession import SISession

# our package constants.
from .siconst import (
    DEFAULT_COLOR_VALUE
)

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SISessionDefaults:
    """ 
    Specifies the default property values for newly created sessions.
    
    This class is used by the SmartInspect class to customize the
    default property values for newly created sessions. Sessions
    that will be created by or passed to the AddSession method of
    the SmartInspect class will be automatically configured with
    the values of the SmartInspect.SessionDefaults property.

    Threadsafety:
        This class is fully thread-safe.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        self._fLock = _threading_local.RLock()
        self._fActive:bool = True
        self._fColorBG:SIColor = SIColor(DEFAULT_COLOR_VALUE)
        self._fLevel:SILevel = SILevel.Debug


    @property
    def Active(self) -> bool:
        """ 
        Gets the Active property value.

        Represents the default Active property for newly created sessions.
        
        Please see SISession.Active for general information about the
        active status of sessions.
        """
        return self._fActive
    

    @Active.setter
    def Active(self, value: bool) -> None:
        """ 
        Sets the Active property value.
        """
        if value != None:
            self._fActive = value


    @property
    def ColorBG(self) -> SIColor:
        """
        Gets the ColorBG property value.

        Represents the default background color property for newly created sessions.
        
        Please see SISession.ColorBG for general information about the
        background color of sessions.
        """
        with self._fLock:

            return self._fColorBG;  # not atomic


    @ColorBG.setter
    def ColorBG(self, value: SIColor) -> None:
        """ 
        Sets the ColorBG property value.
        """
        with self._fLock:

            self._fColorBG = value   # Not atomic


    @property
    def Level(self) -> SILevel:
        """ 
        Gets the Level property value.

        Represents the default Level property for newly created
        sessions.

        Please see SISession.Level for general information about the
        log level of sessions.
        """
        return self._fLevel


    @Level.setter
    def Level(self, value:SILevel) -> None:
        """ 
        Sets the Level property value.
        """
        if value != None:
            self._fLevel = value


    def Assign(self, session:SISession) -> None:
        """
        Sets various properties of the specified session with like-named 
        properties of the session defaults.

        Args:
            session (SISession):
                Session whose properties will be set from session defaults.
        """
        session.Active = self.Active
        session.Level = self.Level
        session.ColorBG = self.ColorBG
