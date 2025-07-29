# system imports.
from datetime import datetime, timedelta

# our package imports.
from .sifilerotate import SIFileRotate

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIFileRotater:
    """
    Responsible for the log file rotate management as used by the
    SIFileProtocol class.

    This class implements a flexible log file rotate management
    system. For a detailed description of how to use this class,
    please refer to the documentation of the Initialize(DateTime)
    and Update(DateTime) methods and the Mode property.

    Threadsafety:
        This class is not guaranteed to be thread-safe.
    """

    _DATETIME_MIN_VALUE:datetime = datetime.min  # DateTime.MinValue;   # C# equivalent = 01/01/0001 12:00:00 AM

    def __init__(self) -> None:
        """ 
        Initializes a new instance of the class.
        """

        # initialize instance.
        self._fMode:SIFileRotate = SIFileRotate.NoRotate
        self._fTimeValue:int = 0


    @property
    def Mode(self) -> SIFileRotate:
        """ 
        Gets the FileRotate property value.

        Represents the SIFileRotate mode of this SIFileRotater object.
    
        Always call the Initialize method after changing this
        property to reinitialize this SIFileRotater object. For a
        complete list of available property values, please refer
        to the documentation of the SIFileRotate enum.
        """
        return self._fMode
    
    @Mode.setter
    def Mode(self, value:SIFileRotate) -> None:
        """ 
        Sets the FileRotate property value.
        """ 
        if value != None:
            self._fMode = value


    @staticmethod
    def _GetDays(date:datetime) -> int:
        """
        Returns the number of days between the specified date and the datetime minimum value.

        Args:
            date (datetime):
                Date to find the number of days from.

        Returns:
            The number of days between the specified date and the datetime minimum value.
        """
        return (date - SIFileRotater._DATETIME_MIN_VALUE).days


    @staticmethod
    def _GetMonday(date:datetime) -> datetime:
        """
        Returns a datetime value for the following Monday from the specified date value.

        Args:
            date (datetime):
                Date to find the next Monday from.

        Returns:
            A datetime value for the following Monday from the specified date value.
        """
        dayofweek:int = date.weekday

        daystoadd:int = 0
        if (dayofweek == 0):    # 0=monday
            daystoadd = 0
        elif (dayofweek == 1):  # 1=tuesday
            daystoadd = -1
        elif (dayofweek == 2):  # 2=wednesday
            daystoadd = -2
        elif (dayofweek == 3):  # 3=thursday
            daystoadd = -3
        elif (dayofweek == 4):  # 4=friday
            daystoadd = -4
        elif (dayofweek == 5):  # 5=saturday
            daystoadd = -5
        elif (dayofweek == 6):  # 6=sunday
            daystoadd = -6
    
        return date + timedelta(days=daystoadd)


    def Initialize(self, now:datetime) -> None:
        """
        Initializes this object with a user-supplied timestamp.

        Args:
            now (datetime):
                The user-specified timestamp to use to initialize this object.

        Always call this method after creating a new SIFileRotater
        object and before calling the Update method the first time.
        For additional information please refer to the Update method.
        """
        self._fTimeValue = self.GetTimeValue(now);


    def GetTimeValue(self, now:datetime) -> int:
        """
        Determines the amount of time between the specified date and when the next file
        rotation will take place.

        Args:
            now (datetime):
                The date the File Rotation event is calculated from.

        Returns:
            The amount of time between the specified date and when the next file
            rotation will take place.
        """
        timeValue:int = 0

        if (self._fMode == SIFileRotate.Hourly):
            timeValue = SIFileRotater._GetDays(now) * 24 + now.hour
        elif (self._fMode == SIFileRotate.Daily):
            timeValue = SIFileRotater._GetDays(now)
        elif (self._fMode == SIFileRotate.Weekly):
            timeValue = SIFileRotater._GetDays(SIFileRotater._GetMonday(now)) 
        elif (self._fMode == SIFileRotate.Monthly):
            timeValue = now.year * 12 + now.month
        else:
            timeValue = 0

        return timeValue


    def Update(self, now:datetime) -> bool:
        """
        Updates the date of this object and returns
        whether the rotate state has changed since the last call to
        this method or to Initialize.

        Args:
            now (datetime):
                The timestamp to update this object.

        Returns:
            True if the rotate state has changed since the last call to
            this method or to Initialize and false otherwise.

        This method updates the internal date of this SIFileRotater
        object and returns whether the rotate state has changed since
        the last call to this method or to Initialize. Before calling
        this method, always call the Initialize method.
        """
        timeValue:int = self.GetTimeValue(now)

        if (timeValue != self._fTimeValue):
        
            self._fTimeValue = timeValue
            return True
        
        else:
        
            return False
