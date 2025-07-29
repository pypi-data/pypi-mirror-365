# our package imports.
from .sienumcomparable import SIEnumComparable

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIFileRotate(SIEnumComparable):
    """
    Specifies the log rotate mode for the SIFileProtocol class and
    derived classes.
    """

    NoRotate = 0
    """
    Completely disables the log rotate functionality.
    """

    Hourly = 1
    """
    Instructs the file protocol to rotate log files hourly.
    """

    Daily = 2
    """
    Instructs the file protocol to rotate log files daily.
    """

    Weekly = 3
    """
    Instructs the file protocol to rotate log files weekly.
    """

    Monthly = 4
    """
    Instructs the file protocol to rotate log files monthly.
    """

    @classmethod
    def Parse(cls, value:str, defaultValue):
        """
        Returns an enum value for the given string representation if found,
        otherwise the default value.

        Args:
            value (str):
                The string representation of the enum value.
            defaultValue (object):
                The value to use if an enum could not be determined from the value.

        Both the Name and Value of the enum are compared for a match.
        """
        result:SIFileRotate = defaultValue

        if (value != None):
            valueIgnoreCase: str = value.lower().strip()
            for k, v in cls.__members__.items():
                if k.lower() == valueIgnoreCase:
                    result = v
                    break
                if v.value == valueIgnoreCase:
                    result = v
                    break

        return result
