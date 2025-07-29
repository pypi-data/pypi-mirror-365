# external package imports.
from datetime import datetime
import sys

# our package imports.
# none

def static_init(cls):
    """
    Define the decorator used to call an initializer for a class with all static methods.
    This allows static variables to be initialized one time for the class.
    """
    if getattr(cls, "static_init", None):
        cls.static_init()
    #if hasattr(cls, '__static_init__',):
    #    cls.__static_init__(cls)
    return cls


def export(fn):
    """
    Define the decorator used to modify a module's "__all__" variable.
    This avoids us having to manually modify a module's "__all__" variable when adding new classes.
    """
    mod = sys.modules[fn.__module__]
    if hasattr(mod, '__all__'):
        mod.__all__.append(fn.__name__)
    else:
        mod.__all__ = [fn.__name__]

    return fn
    

class Event:
    """
    C# like event processing in Python3.

    <details>
        <summary>Sample Code</summary>
    ``` python
    .. include:: ../docs/include/samplecode/SIUtils/Event.py
    ```
    </details>
    """

    def __init__(self, *args) -> None:
        """
        Initializes a new instance of the class.
        """
        self.handlers = set()

    def fire(self, *args, **kargs):
        """
        Calls (i.e. "fires") all method handlers defined for this event.
        """
        for handler in self.handlers:
            handler(*args, **kargs)

    def getHandlerCount(self):
        """
        Returns the number of method handlers defined for this event.
        """
        return len(self.handlers)

    def handle(self, handler):
        """
        Adds a method handler for this event.
        """
        self.handlers.add(handler)
        return self

    def unhandle(self, handler):
        """
        Removes the specified method handler for this event.

        Args:
            handler (object):
                The method handler to remove.

        This method will not throw an exception.
        """
        try:
            self.handlers.remove(handler)
        except:
            #raise ValueError("Handler is not handling this event, so cannot unhandle it.")
            pass   # ignore exceptions.
        return self

    def unhandle_all(self):
        """
        Removes all method handlers (if any) for this event.

        This method will not throw an exception.
        """
        try:
            self.handlers.clear()
        except:
            #raise ValueError("Handler is not handling this event, so cannot unhandle all.")
            pass   # ignore exceptions.
        return self

    # alias method definitions.
    __iadd__ = handle
    __isub__ = unhandle
    __call__ = fire
    __len__  = getHandlerCount


class DataTypeHelper:
    """
    Helper class used for processing different types of data.
    """

    @staticmethod
    def BoolToStringYesNo(value:bool) -> str:
        """
        Converts a boolean value to a "Yes" (true) or "No" (false) string.

        Args:
            value (bool):
                Boolean value to convert.

        Returns:
            A "Yes" or "No" string value.
        """
        if (value):
            return "Yes"
        else:
            return "No"


class DateHelper:
    """
    Helper class used for processing date and time data.
    """
    @staticmethod
    def Ticks(dt:datetime) -> int:
        """
        Returns the number of ticks for a given datetime.
        """
        return int((dt - datetime(1, 1, 1)).total_seconds() * 10000000)
