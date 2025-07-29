# our package imports.
from .sienumcomparable import SIEnumComparable

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SILevel(SIEnumComparable):
    """
    Represents the log level in the SmartInspect Python3 library.
    
    Please see the Level and DefaultLevel properties for detailed 
    examples and more information on how to use the Level enum.
    """

    Debug = 0
    """
    Represents the Debug log level. 

    This log level is mostly intended to be used in the debug and development process.
    """

    Verbose = 1
    """
    Represents the Verbose log level. 
    
    This log level is intended to track the general progress of applications at a
    fine-grained level.
    """

    Message = 2
    """
    Represents the Message log level. 

    This log level is intended to track the general progress of applications at a coarse-grained level.
    """

    Warning = 3
    """
    Represents the Warning log level. 

    This log level designates potentially harmful events or situations.
    """

    Error = 4
    """
    Represents the Error log level. 

    This log level designates error events or situations which are not critical to the
    entire system. This log level thus describes recoverable or less important errors.
    """

    Fatal = 5
    """
    Represents the Fatal log level. 

    This log level designates errors which are not recoverable and eventually stop the
    system or application from working.
    """

    Control = 6
    """
    Represents the Control Command log level. 

    This log level represents a special log level which is only used by the SIControlCommand 
    class and is not intended to be used directly.
    """

    
    @classmethod
    def Parse(cls, value:str, defaultValue):
        """
        Returns an enum value for the given string representation if found,
        otherwise the default value.

        Args:
            value (str):
                The string representation of the enum value.
            defaultValue:
                The value to use if an enum could not be determined from the value.

        Returns:
            A new Level instance if Parse was successful; otherwise, the defaultValue Level.

        Both the Name and Value of the enum are compared for a match.
        """
        result:SILevel = defaultValue

        if (value != None):
            valueIgnoreCase:str = value.lower().strip()
            for k, v in cls.__members__.items():
                if k.lower() == valueIgnoreCase:
                    result = v
                    break
                if v.name.lower() == valueIgnoreCase:
                    result = v
                    break

        return result
