# external package imports.
# none

# our package imports.
from .sienumcomparable import SIEnumComparable

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIPacketType(SIEnumComparable):
    """
    Represents the type of a packet. In the SmartInspect concept,
    there are multiple packet types each serving a special purpose.
    For a good starting point on packets, please have a look at the
    documentation of the SIPacket class.
    """

    ControlCommand = 1
    """
    Identifies a packet as Control Command. Please have a look
    at the documentation of the SIControlCommand class for more
    information about this packet type.
    """

    LogEntry = 4
    """
    Identifies a packet as Log Entry. Please have a look at the
    documentation of the SILogEntry class for information about
    this packet type.
    """

    Watch = 5
    """
    Identifies a packet as Watch. Please have a look at the
    documentation of the SIWatch class for information about
    this packet type.
    """

    ProcessFlow = 6
    """
    Identifies a packet as Process Flow entry. Please have a
    look at the documentation of the SIProcessFlow class for
    information about this packet type.
    """

    LogHeader = 7
    """
    Identifies a packet as Log Header. Please have a look
    at the documentation of the SILogHeader class for information
    about this packet type.
    """
