# external package imports.
import _threading_local

# our package imports.
from .siargumentnullexception import SIArgumentNullException

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIProtocolVariables:
    """ 
    Manages connection variables.

    This class manages a list of connection variables. Connection
    variables are placeholders for strings in the Connections of the
    SmartInspect class. Please see SmartInspect.SetVariable for
    more information.
    
    Threadsafety:
        This class is fully thread-safe.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        self._fLock = _threading_local.RLock()
        self._fItems = {}


    @property
    def Count(self) -> int:
        """
        Returns the number of key/value pairs of this collection.
        """
        with self._fLock:

            return len(self._fItems)


    def Add(self, key:str, value:str) -> None:
        """
        Adds a new element with a specified key and value to the
        set of connection variables.

        Args:
            key (str):
                The key of the element.
            value (str):
                The value of the element.

        Raises:
            SIArgumentNullException:
                The key or value argument is null.

        This method adds a new element with a given key and value to
        the set of connection variables. If an element for the given
        key already exists, the original element's value is not updated.
        """
        if (key == None):
            raise SIArgumentNullException("key")

        with self._fLock:

            if (not self.Contains(key)):
                self.Put(key, value)


    def Clear(self) -> None:
        """
        Removes all key/value pairs of the collection.
        """
        with self._fLock:

            self._fItems.clear()


    def Contains(self, key:str) -> bool:
        """
        Tests if the collection contains a value for a given key. 

        Args:
            key (str):
                The key of the element to test.

        Raises:
            SIArgumentNullException:
                The key argument is null.

        True if a value exists for the given key and false
        otherwise.
        """
        if (key == None):
            raise SIArgumentNullException("key")

        with self._fLock:

            if key in self._fItems.keys():
                return True
            return False


    def Expand(self, connections:str) -> str:
        """
        Expands and returns a connections string.

        Args:
            connections (str):
                The connections string to expand and return.

        Returns:
            The expanded connections string.

        Raises:
            SIArgumentNullException:
                The connections argument is null.

        This method replaces all variables which have previously
        been added to this collection (with Add or Put) in the
        given connections string with their respective values and
        then returns it. Variables in the connections string must
        have the following form: $variable$.
        """
        if (connections == None):
            raise SIArgumentNullException("connections")

        with self._fLock:

            if (self.Count == 0):
                return connections

            value:str = ""

            for key in self._fItems.keys():

                keyrepl:str = "$" + key + "$"
                value = self._fItems[key]
                if (value == None):
                    connections = connections.replace(keyrepl, "")
                else:
                    connections = connections.replace(keyrepl, value)

            return connections


    def Get(self, key:str) -> str:
        """
        Returns a value of an element for a given key.

        Args:
            key (str):
                The key whose value to return.
        
        Raises:
            SIArgumentNullException:
                The key argument is null.

        Either the value for a given key if an element with the
        given key exists or null otherwise.
        """
        if (key == None):
            raise SIArgumentNullException("key")

        value:object = None

        with self._fLock:

            value = self._fItems[key]
            if (value != None):
                return str(value)
            return None


    def Put(self, key:str, value:str) -> None:
        """
        Adds or updates an element with a specified key and value
        to the set of connection variables.

        Args:
            key (str):
                The key of the element.
            value (str):
                The value of the element.

        Raises:
            SIArgumentNullException:
                The key or value argument is null.
        
        This method adds a new element with a given key and value to
        the set of connection variables. If an element for the given
        key already exists, the original element's value is updated.
        """
        if (key == None):
            raise SIArgumentNullException("key")
        if (value == None):
            raise SIArgumentNullException("value")
         
        with self._fLock:

            self._fItems[key] = value


    def Remove(self, key:str) -> None:
        """
        Removes an existing element with a given key from this set
        of connection variables.

        Args:
            key (str):
                The key of the element to remove.

        Raises:
            SIArgumentNullException:
                The key argument is null.

        This method removes the element with the given key from the
        internal set of connection variables. Nothing happens if no
        element with the given key can be found.
        """
        if (key == None):
            raise SIArgumentNullException("key")

        with self._fLock:

            if (self.Contains(key)):
                self._fItems.pop(key)
