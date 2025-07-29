# external package imports.
# none

# our package imports.
from .sienumcomparable import SIEnumComparable

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIProcessFlowType(SIEnumComparable):
    """
    Represents the type of a Process Flow packet. The type of Process Flow 
    entry specifies the way the Console interprets this packet.

    For example, if a Process Flow entry has a type of
    SIProcessFlowType.EnterThread, the Console interprets this packet as
    information about a new thread of your application.
    """

    EnterMethod = 0
    """
    Instructs the Console to enter a new method.
    """

    LeaveMethod = 1
    """
    Instructs the Console to leave a method.
    """

    EnterThread = 2
    """
    Instructs the Console to enter a new thread.
    """

    LeaveThread = 3
    """
    Instructs the Console to leave a thread.
    """

    EnterProcess = 4
    """
    Instructs the Console to enter a new process.
    """
        
    LeaveProcess = 5
    """
    Instructs the Console to leave a process.
    """
