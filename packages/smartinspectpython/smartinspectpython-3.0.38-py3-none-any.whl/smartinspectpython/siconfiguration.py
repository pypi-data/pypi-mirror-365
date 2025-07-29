import _threading_local

# our package imports.
from .siargumentnullexception import SIArgumentNullException
from .siargumentoutofrangeexception import SIArgumentOutOfRangeException
from .sicolor import SIColor
from .silevel import SILevel
from .silookuptable import SILookupTable

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIConfiguration:
    """ 
    Responsible for handling the SmartInspect configuration and loading
    it from a file.
    
    This class is responsible for loading and reading values from a
    SmartInspect configuration file. For more information, please refer
    to the SmartInspect.LoadConfiguration method.

    Threadsafety:
        This class is not guaranteed to be thread-safe.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        self._fItems:SILookupTable = SILookupTable()
        self._fIndexedKeys = []
        self._fLock:object = _threading_local.RLock()


    @property
    def Count(self) -> int:
        """
        Returns the number of key/value pairs of this SmartInspect
        configuration.
        """
        return self._fItems.Count


    def Contains(self, key:str) -> bool:
        """
        Tests if the configuration contains a value for a given key. 

        Args:
            key (str):
                The key to test for.

        Returns:
            True if a value exists for the given key; otherwise, false.
        """
        return self._fItems.Contains(key)


    def Clear(self) -> None:
        """
        Removes all key/value pairs of the configuration.
        """
        self._fIndexedKeys.clear()
        self._fItems.Clear()


    def LoadFromFile(self, fileName:str) -> None:
        """
        Loads the configuration from a file.

        Args:
            fileName (str):
                The name of the file to load the configuration from.
        
        Raises:
            IOException:
                An I/O error occurred while trying to load the configuration or if the
                specified file does not exist.
            SIArgumentNullException:
                The fileName argument is null.

        This method loads key/value pairs separated with a '='
        character from a file. Empty, unrecognized lines or lines
        beginning with a ';' character are ignored.
        """
        if (fileName == None):
            raise SIArgumentNullException("fileName")

        # clear all configuration data.
        self.Clear()

        with open(fileName, 'r') as reader:

            # process the file line-by-line, ignoring any lines
            # that start with a semi-colon (comments).
            # The EOF char is an empty string.
            line:str = reader.readline()
            while line != '':

                line = line.strip()
                if (len(line) > 0) and (not line.startswith(";")):
                    self.Parse(line)

                line = reader.readline()


    def Parse(self, pair:str) -> None:
        """
        Parses a line read from a configuration file, adding the
        found key and value to the configuration variables table.

        Args:
            pair (str):
                String that contains a KEY=VALUE pair.
        """
        
        # is this a KEY=VALUE format?  if not, then we are done.
        index:int = pair.find('=')
        if (index == -1):
            return

        # get the key and value portions.
        key:str = pair[0:index].strip()
        value:str = pair[index + 1:].strip()

        # fold key value to lower-case for comparison later.
        key = key.lower()

        # does key already existin the index?  if not, then add it.
        if (not self._fItems.Contains(key)):
            self._fIndexedKeys.append((key,value))

        # add / update the item value.
        self._fItems.Put(key, value)


    def ReadBoolean(self, key:str, defaultValue:bool) -> bool:
        """
        Returns a boolean value of an element for a given key.

        Args:
            key (str):
                The key whose value to return.
            defaultValue (bool):
                The value to return if the given key is unknown.

        Returns:
            Either the value converted to a bool for the given key if an
            element with the given key exists or defaultValue otherwise.

        Raises:
            SIArgumentNullException:
                The key argument is null.

        This method returns a bool value of true if the found value
        of the given key matches either "true", "1" or "yes" and false
        otherwise. If the supplied key is unknown, the defaultValue
        argument is returned.
        """
        return self._fItems.GetBooleanValue(key, defaultValue)


    def ReadColor(self, key:str, defaultValue:SIColor) -> SIColor:
        """
        Returns a color value of an element for a given key.

        Args:
            key (str):
                The key whose value to return.
            defaultValue (SIColor):
                The value to return if the given key is unknown or if the
                found value has an invalid format.

        Returns:
            Either the value converted to a SIColor value for the given key
            if an element with the given key exists and the found value
            has a valid format or defaultValue otherwise.

        Raises:
            SIArgumentNullException:
                The key argument is null.
        
        The element value must be specified as hexadecimal string.
        To indicate that the element value represents a hexadecimal
        string, the element value must begin with "0x", "&amp;H" or "$".
        A '0' nibble is appended if the hexadecimal string has an odd
        length.
        
        The hexadecimal value must represent a three or four byte
        integer value. The hexadecimal value is handled as follows.

        Bytes |  Format
        ----- |  ----------
        3     |  RRGGBB
        4     |  AARRGGBB
        Other |  Ignored
        
        A stands for the alpha channel and R, G and B represent the
        red, green and blue channels, respectively. If the value is not
        given as hexadecimal value with a length of 6 or 8 characters
        excluding the hexadecimal prefix identifier or if the value
        does not have a valid hexadecimal format, this method returns
        defaultValue.
        """
        return self._fItems.GetColorValue(key, defaultValue)


    def ReadInteger(self, key:str, defaultValue:bool) -> bool:
        """
        Returns a integer value of an element for a given key.

        Args:
            key (str):
                The key whose value to return.
            defaultValue (bool):
                The value to return if the given key is unknown.

        Returns:
            Either the value converted to an int for the given key if an
            element with the given key exists and the found value is a
            valid int or defaultValue otherwise.

        Raises:
            SIArgumentNullException:
                The key argument is null.

        This method returns the defaultValue argument if either the
        supplied key is unknown or the found value is not a valid int.
        Only non-negative int values are recognized as valid. 
        """
        return self._fItems.GetIntegerValue(key, defaultValue)


    def ReadKey(self, index:int) -> str:
        """
        Returns a key of this SmartInspect configuration for a
        given index.

        Args:
            index (int):
                The index in this SmartInspect configuration.

        Returns:
            A key of this SmartInspect configuration for the given index.

        Raises:
            SIArgumentOutOfRangeException:
                The index argument is not a valid index of this SmartInspect configuration.

        To find out the total number of key/value pairs in this
        SmartInspect configuration, use Count. To get the value for
        a given key, use ReadString.
        """
        if (index > len(self._fIndexedKeys)):
            raise SIArgumentOutOfRangeException("index")

        for i in range(len(self._fIndexedKeys)):
            if (i == index):
                value:str = str(self._fIndexedKeys[index][0])
                return value
        return None


    def ReadLevel(self, key:str, defaultValue:SILevel) -> SILevel:
        """
        Returns a SILevel value of an element for a given key.

        Args:
            key (str):
                The key whose value to return.
            defaultValue (SILevel):
                The value to return if the given key is unknown.

        Returns:
            Either the value converted to the corresponding SILevel value for
            the given key if an element with the given key exists and the
            found value is a valid SILevel value or defaultValue otherwise.

        Raises:
            SIArgumentNullException:
                The key argument is null.

        This method returns the defaultValue argument if either the
        supplied key is unknown or the found value is not a valid SILevel
        value. Please see the SILevel enum for more information on the
        available values.  
        """
        return self._fItems.GetLevelValue(key, defaultValue)


    def ReadString(self, key:str, defaultValue:str) -> str:
        """
        Returns a string value of an element for a given key.

        Args:
            key (str):
                The key whose value to return.
            defaultValue (str):
                The value to return if the given key is unknown.

        Returns:
            Either the value for a given key if an element with the 
            given key exists or defaultValue otherwise.

        Raises:
            SIArgumentNullException:
                The key argument is null.
        """
        value:str = self._fItems.GetStringValue(key, defaultValue)
        if (value == None) or (len(value) == 0):
            value = defaultValue
        return value
