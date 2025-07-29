# external package imports.
# none

# our package imports.
from .sienumcomparable import *

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SISchedulerAction(Enum):
    """
    Represents a scheduler action to execute when a protocol is
    operating in asynchronous mode. For general information about
    the asynchronous mode, please refer to SIProtocol.IsValidOption.
    """

    Connect = 0
    """
    Represents a connect protocol operation. This action is
    enqueued when the SIProtocol.Connect method is called and
    the protocol is operating in asynchronous mode.
    """

    WritePacket = 1
    """
    Represents a write protocol operation. This action is
    enqueued when the SIProtocol.WritePacket method is called
    and the protocol is operating in asynchronous mode.
    """

    Disconnect = 2
    """
    Represents a disconnect protocol operation. This action
    is enqueued when the SIProtocol.Disconnect method is called
    and the protocol is operating in asynchronous mode.
    """

    Dispatch = 3
    """
    Represents a dispatch protocol operation. This action is
    enqueued when the SIProtocol.Dispatch method is called and
    the protocol is operating in asynchronous mode.
    """
