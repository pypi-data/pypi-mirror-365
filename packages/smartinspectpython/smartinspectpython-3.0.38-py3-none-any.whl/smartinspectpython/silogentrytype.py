# our package imports.
from .sienumcomparable import SIEnumComparable

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SILogEntryType(SIEnumComparable):
    """
    Represents the type of a Log Entry packet. Instructs the Console
    to choose the correct icon and to perform additional actions,
    like, for example, enter a new method or draw a separator.
    """

    Separator = 0
    """
    Instructs the Console to draw a separator.
    """

    EnterMethod = 1
    """
    Instructs the Console to enter a new method.
    """

    LeaveMethod = 2
    """
    Instructs the Console to leave a method.
    """

    ResetCallstack = 3
    """
    Instructs the Console to reset the current call stack.
    """

    Message = 100
    """
    Instructs the Console to treat a Log Entry as simple message.
    """

    Warning = 101
    """
    Instructs the Console to treat a Log Entry as warning message.
    """

    Error = 102
    """
    Instructs the Console to treat a Log Entry as error message.
    """

    InternalError = 103
    """
    Instructs the Console to treat a Log Entry as internal error.
    """

    Comment = 104
    """
    Instructs the Console to treat a Log Entry as comment.
    """

    VariableValue = 105
    """
    Instructs the Console to treat a Log Entry as a variable value.
    """

    Checkpoint = 106
    """
    Instructs the Console to treat a Log Entry as checkpoint.
    """

    Debug = 107
    """
    Instructs the Console to treat a Log Entry as debug message.
    """

    Verbose = 108
    """
    Instructs the Console to treat a Log Entry as verbose message.
    """

    Fatal = 109
    """
    Instructs the Console to treat a Log Entry as fatal error message.
    """

    Conditional = 110
    """
    Instructs the Console to treat a Log Entry as conditional message.
    """

    Assert = 111
    """
    Instructs the Console to treat a Log Entry as assert message.
    """

    Text = 200
    """
    Instructs the Console to treat the Log Entry as Log Entry with text.
    """

    Binary = 201
    """
    Instructs the Console to treat the Log Entry as Log Entry with binary data.
    """

    Graphic = 202
    """
    Instructs the Console to treat the Log Entry as Log Entry
    with a picture as data.
    """

    Source = 203
    """
    Instructs the Console to treat the Log Entry as Log Entry
    with source code data.
    """

    Object = 204
    """
    Instructs the Console to treat the Log Entry as Log Entry
    with object data.
    """

    WebContent = 205
    """
    Instructs the Console to treat the Log Entry as Log Entry
    with web data.
    """

    System = 206
    """
    Instructs the Console to treat the Log Entry as Log Entry
    with system information.
    """

    MemoryStatistic = 207
    """
    Instructs the Console to treat the Log Entry as Log Entry
    with memory statistics.
    """

    DatabaseResult = 208
    """
    Instructs the Console to treat the Log Entry as Log Entry
    with a database result.
    """

    DatabaseStructure = 209
    """
    Instructs the Console to treat the Log Entry as Log Entry
    with a database structure.
    """
