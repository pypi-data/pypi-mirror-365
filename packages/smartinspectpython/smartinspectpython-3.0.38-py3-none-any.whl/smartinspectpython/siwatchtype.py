# external package imports.
# none

# our package imports.
from .sienumcomparable import SIEnumComparable

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIWatchType(SIEnumComparable):
    """
    Represents the type of a Watch packet. The type of a Watch
    specifies its variable type.

    For example, if a Watch packet has a type of SIWatchType.String,
    the represented variable is treated as string in the Console.
    """

    Char = 0
    """
    Instructs the Console to treat a Watch value as char.
    """

    String = 1
    """
    Instructs the Console to treat a Watch value as string.
    """

    Integer = 2
    """
    Instructs the Console to treat a Watch value as integer.
    """

    Float = 3
    """
    Instructs the Console to treat a Watch value as float.
    """

    Boolean = 4
    """
    Instructs the Console to treat a Watch value as boolean.
    """

    Address = 5
    """
    Instructs the Console to treat a Watch value as address.
    """

    Timestamp = 6
    """
    Instructs the Console to treat a Watch value as timestamp.
    """

    Object = 7
    """
    Instructs the Console to treat a Watch value as object.
    """
