# our package imports.
from .siargumentnullexception import SIArgumentNullException
from .sibinaryformatter import SIBinaryFormatter
from .sicolor import SIColor
from .sifilerotate import SIFileRotate
from .silevel import SILevel

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SILookupTable:
    """ 
    Represents a simple collection of key/value pairs.

    The SILookupTable class is responsible for storing and returning
    values which are organized by keys. Values can be added with
    the Put method. To query a String value for a given key, the
    GetStringValue method can be used. To query and automatically
    convert values to types other than String, please have a look
    at the Get method family.

    Threadsafety:
        This class is not guaranteed to be thread-safe.
    """

    _SECONDS_FACTOR:int = 1000;
    _MINUTES_FACTOR:int = _SECONDS_FACTOR * 60;
    _HOURS_FACTOR:int = _MINUTES_FACTOR * 60;
    _DAYS_FACTOR:int = _HOURS_FACTOR * 24;

    _KB_FACTOR:int = 1024;
    _MB_FACTOR:int = _KB_FACTOR * 1024;
    _GB_FACTOR:int = _MB_FACTOR * 1024;

    def __init__(self) -> None:
        """ 
        Initializes a new instance of the class.
        """
   
        # initialize instance.
        self._fItems = {}


    @property
    def Count(self) -> int:
        """
        Returns the number of key/value pairs of this collection.
        """
        return len(self._fItems)


    @staticmethod
    def _ConvertUnicodeValue(value:str) -> bytearray:
        """
        Encodes the value using UTF-8 encoding.

        Args:
            value (str):
                Value to encode.

        Returns:
            A byte array with the encoded string.
        """
        # normal Unicode string encoded in UTF-8.
        return SIBinaryFormatter._EncodeString(value)


    def Add(self, key:str, value:str) -> None:
        """
        Adds a new element with a specified key and value to the Lookup Table.
        
        Args:
            key (str):
                The key of the element.
            value (str):
                The value of the element.
        
        Raises:
            SIArgumentNullException:
                The key or value argument is null.

        This method adds a new element with a given key and value to
        the collection of key/value pairs. If an element for the
        given key already exists, the original element's value is
        not updated.
        """

        if (not self.Contains(key)):
            self.Put(key, value)


    def Clear(self) -> None:
        """
        Removes all key/value pairs of the collection.
        """
        self._fItems.clear()


    def Contains(self, key:str) -> bool:
        """
        Tests if the collection contains a value for a given key. 

        Args:
            key (str):
                The key to test for.
        
        Returns:
            True if a value exists for the given key and false otherwise.

        Raises:
            SIArgumentNullException:
                The key argument is null.
        """
        if (key == None):
            raise SIArgumentNullException("key")

        if key in self._fItems.keys():
            return True
        return False


    def GetBooleanValue(self, key:str, defaultValue:bool) -> bool:
        """
        Returns a value of an element converted to a bool for a
        given key.

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

        result:bool = defaultValue;
        value:str = self.GetStringValue(key, None);

        if (value != None):
            value = value.strip().lower()

            if (value == "1") or (value == "yes") or (value == "true"):
                result = True
            else:
                result = False

        return result;


    def GetBytesValue(self, key:str, size:int, defaultValue:bytearray) -> bytearray:
        """
        Returns a byte array value of an element for a given key.

        Args:
            key (str):
                The key whose value to return.
            size (int):
                The desired size in bytes of the returned byte array. If
                the element value does not have the expected size, it is
                shortened or padded automatically.
            defaultValue (bytearrau):
                The value to return if the given key is unknown or if the
                found value has an invalid format.
        
        Returns:
            Either the value converted to a byte array for the given key
            if an element with the given key exists and the found value
            has a valid format or defaultValue otherwise.
        
        Exception:
            SIArgumentNullException:
                The key argument is null.

        The returned byte array always has the desired length as
        specified by the size argument. If the element value does
        not have the required size after conversion, it is shortened
        or padded (with zeros) automatically. This method returns
        the defaultValue argument if either the supplied key is
        unknown or the found value does not have a valid format
        (e.g. invalid characters when using hexadecimal strings).
        """
        value:str = self.GetStringValue(key, None)

        if (value != None):
        
            valuebytes:bytearray = SILookupTable._ConvertUnicodeValue(value.strip())

            if (valuebytes == None):
                return defaultValue     # invalid hex format
            elif (len(valuebytes) == size):
                return valuebytes

            # initialize returned byte array to requested size filled with zeros.
            result:bytearray = bytearray([0] * size)

            # if value byte array exceeds the size, then truncate what is copied
            # so that we don't exceed the size.
            copylen:int = len(valuebytes)
            if (len(valuebytes) > size):
                copylen = len(result)
            for i in range(copylen):
                result[i] = valuebytes[i]

            return result

        return defaultValue;


    def GetColorValue(self, key:str, defaultValue:SIColor) -> SIColor:
        """
        Returns a color value of an element for a given key.

        Args:
            key (str):
                The key whose value to return.
            defaultValue (SIColor):
                The value to return if the given key is unknown or if the
                found value has an invalid format.

        Returns:
            Either the value converted to a Color value for the given key
            if an element with the given key exists and the found value
            has a valid format or defaultValue otherwise.
        
        Raises:
            SIArgumentNullException:
                The key argument is null.
            ArgumentError:
                The read value is not a valid color value representation.

        The element value must be specified as hexadecimal string.
        To indicate that the element value represents a hexadecimal
        string, the element value must begin with "0x", "&H" or "$".
        A '0' nibble is appended if the hexadecimal string has an odd
        length.

        The hexadecimal value must represent a three or four byte
        integer value. The hexadecimal value is handled as follows.
        
        Bytes  | Format
        -----  | --------
        3      | RRGGBB
        4      | AARRGGBB
        Other  | Ignored

        A stands for the alpha channel and R, G and B represent the
        red, green and blue channels, respectively. If the value is not
        given as hexadecimal value with a length of 6 or 8 characters
        excluding the hexadecimal prefix identifier or if the value
        does not have a valid hexadecimal format, this method returns
        defaultValue.
        """
        value:str = self.GetStringValue(key, None)

        if (value != None):

            # get rid of the special indicators, and always treat as base 16.
            value = value.lower()
            value = value.replace("0x","")
            value = value.replace("&h","")
            value = value.replace("$","")

            # convert to integer and initialize the SIColor object.
            # an ArgumentError will be thrown if the value is not a valid color value.
            valueInt:int = int(value, base=16)
            oColor:SIColor = SIColor(valueInt)

            # return the color object.
            return oColor

        return defaultValue;


    def GetIntegerValue(self, key:str, defaultValue:int) -> int:
        """
        Returns a value of an element converted to an integer for a
        given key.

        Args:
             (str):
                The key whose value to return.
            defaultValue (int):
                The value to return if the given key is unknown.

        Returns:
            Either the value converted to an integer for the given key if
            an element with the given key exists and the found value is a
            valid integer or defaultValue otherwise.

        Raises:
            SIArgumentNullException:
                The key argument is null.

        Only non-negative integer values are recognized as valid. 
        """

        result:int = defaultValue;
        value:str = self.GetStringValue(key, None);

        if (value != None):
            value = value.strip();
            if (SILookupTable.IsValidInteger(value)):
                try:
                    result = int(value)
                except Exception as e:
                    pass  # return default

        return result


    def GetLevelValue(self, key:str, defaultValue:SILevel) -> SILevel:
        """
        Returns a value of an element converted to a Level value for
        a given key.

        Args:
            key (str):
                The key whose value to return.
            defaultValue (SILevel):
                The value to return if the given key is unknown.

        Returns:
            Either the value converted to the corresponding Level value for
            the given key if an element with the given key exists and the
            found value is a valid Level value or defaultValue otherwise.

        Raises:
            SIArgumentNullException:
                The key argument is null.

        This method returns the defaultValue argument if either the
        supplied key is unknown or the found value is not a valid Level
        value. Please see the Level enum for more information on the
        available values.  
        """
        result:SILevel = defaultValue;
        value:str = self.GetStringValue(key, None);

        if (value != None):
            result = SILevel.Parse(value, defaultValue)
        return result;


    def GetRotateValue(self, key:str, defaultValue:SIFileRotate) -> SIFileRotate:
        """
        Returns a value of an element converted to a SIFileRotate value for
        a given key.

        Args:
            key (str):
                The key whose value to return.
            defaultValue (SIFileRotate):
                The value to return if the given key is unknown.

        Returns:
            Either the value converted to a SIFileRotate value for the
            given key if an element with the given key exists and the found
            value is a valid SIFileRotate or defaultValue otherwise.
    
        Raises:
            SIArgumentNullException:
                The key argument is null.

        This method returns the defaultValue argument if either the
        supplied key is unknown or the found value is not a valid SIFileRotate
        value. Please see the SIFileRotate enum for more information on the
        available values.  
        """
        result:SIFileRotate = defaultValue;
        value:str = self.GetStringValue(key, None);

        if (value != None):
            result = SIFileRotate.Parse(value, defaultValue)
        return result;


    def GetSizeValue(self, key:str, defaultValue:int) -> int:
        """
        Returns a value of an element converted to an integer for a
        given key. The integer value is interpreted as a byte size and
        it is supported to specify byte units.

        Args:
            key (str):
                The key whose value to return.
            defaultValue (int):
                The value to return if the given key is unknown.

        Returns:
            Either the value converted to an integer for the given key if
            an element with the given key exists and the found value is a
            valid integer or defaultValue otherwise.

        Raises:
            SIArgumentNullException:
                The key argument is null.

        This method returns the defaultValue argument if either the
        supplied key is unknown or the found value is not a valid
        integer or ends with an unknown byte unit. Only non-negative
        integer values are recognized as valid.

        It is possible to specify a size unit at the end of the value.
        If a known unit is found, this function multiplies the
        resulting value with the corresponding factor. For example, if
        the value of the element is "1KB", the return value of this
        function would be 1024.

        The following table lists the available units together with a
        short description and the corresponding factor.

        Unit Name / Factor | Description
        ------------------ | -----------
        KB / 1024          | KiloByte
        MB / 1024^2        | MegaByte
        GB / 1024^3        | GigaByte
        
        If no unit is specified, this function defaults to the KB unit.
        """

        result:int = defaultValue * SILookupTable._KB_FACTOR;
        value:str = self.GetStringValue(key, None);

        if (value != None):
            value = value.strip().lower()
            factor:int = SILookupTable._KB_FACTOR

            if (len(value) >= 2):
                unit = value[-2:]
                if (SILookupTable.IsValidSizeUnit(unit)):
                    value = value[0:len(value)-2]
                    if (unit == "kb"):
                        factor = SILookupTable._KB_FACTOR
                    elif (unit == "mb"):
                        factor = SILookupTable._MB_FACTOR
                    elif (unit == "gb"):
                        factor = SILookupTable._GB_FACTOR

            if (SILookupTable.IsValidInteger(value)):
                try:
                    result = factor * int(value)
                except Exception as ex:
                    pass  # return default

        return result


    def GetStringValue(self, key:str, defaultValue:str) -> str:
        """
        Returns a string value of an element for a given key.

        Args:
            key (str):
                The key whose value to return.
            defaultValue (str):
                The value to return if the given key is unknown.

        Returns:
            The value for a given key if an element with the given
            key exists; otherwise, the defaultValue.

        Raises:
            SIArgumentNullException:
                The key argument is null.
        """

        if (key == None):
            raise SIArgumentNullException("key")

        if (self.Contains(key)):
            value:str = self._fItems[key]
            return value 
        else:
            return defaultValue


    def GetTimespanValue(self, key:str, defaultValue:int) -> int:
        """
        Returns a value of an element converted to an integer for a
        given key. The integer value is interpreted as a time span
        and it is supported to specify time span units.

        Args:
            key (str):
                The key whose value to return.
            defaultValue (int):
                The value to return if the given key is unknown.

        Returns:
            Either the value converted to an integer for the given key if
            an element with the given key exists and the found value is a
            valid integer or defaultValue otherwise. The value is returned
            in milliseconds.

        Raises:
            SIArgumentNullException:
                The key argument is null.

        This method returns the defaultValue argument if either the
        supplied key is unknown or the found value is not a valid
        integer or ends with an unknown time span unit.

        It is possible to specify a time span unit at the end of the
        value. If a known unit is found, this function multiplies the
        resulting value with the corresponding factor. For example, if
        the value of the element is "1s", the return value of this
        function would be 1000.

        The following table lists the available units together with a
        short description and the corresponding factor.

        Unit Name / Factor | Description
        ------------------ | -----------
        s (seconds)        | 1000
        m (minutes)        | 60*s
        h (hours)          | 60*m
        d (days)           | 24*h
        
        If no unit is specified, this function defaults to the Seconds
        unit. Please note that the value is always returned in
        milliseconds.
        """

        result:int = defaultValue * SILookupTable._SECONDS_FACTOR;
        value:str = self.GetStringValue(key, None);

        if (value != None):
            value = value.strip().lower()
            factor:int = SILookupTable._SECONDS_FACTOR

            if (len(value) >= 1):
                unit = value[-1:]
                if (SILookupTable.IsValidTimespanUnit(unit)):
                    value = value[0:len(value)-1]
                    if (unit == "s"):
                        factor = SILookupTable._SECONDS_FACTOR
                    elif (unit == "m"):
                        factor = SILookupTable._MINUTES_FACTOR
                    elif (unit == "h"):
                        factor = SILookupTable._HOURS_FACTOR
                    elif (unit == "d"):
                        factor = SILookupTable._DAYS_FACTOR

            if (SILookupTable.IsValidInteger(value)):
                try:
                    result = factor * int(value)
                except Exception as ex:
                    pass  # return default

        return result



    @staticmethod
    def IsValidInteger(value:str) -> bool:
        """
        Checks to see if the supplied value is numeric or not.

        Args:
            value (str):
                The value to check.

        Returns:
            True if the value is numeric; otherwise, false.

        Only non-negative whole integer values are recognized as numeric. 
        """

        result:bool = False

        if (value != None):
            if (value.isnumeric()):
                try:
                    value:int = int(value)
                    result = True
                except Exception as e:
                    pass   # return default

        return result


    @staticmethod
    def IsValidSizeUnit(value:str) -> bool:
        """
        Checks to see if the supplied value is a valid size unit or not.
        Valid size units are: kb, mb, and gb.

        Args:
            value (str):
                The value to check.

        Returns:
            True if the value is valid; otherwise, false.
        """

        result:bool = False

        if (value != None):
            value = value.strip().lower()
            if (value == "kb") or (value == "mb") or (value == "gb"):
                result = True 

        return result


    @staticmethod
    def IsValidTimespanUnit(value:str) -> bool:
        """
        Checks to see if the supplied value is a valid timespan unit or not.
        Valid units are: s, m, h, and d.

        Args:
            value (str):
                The value to check.

        Returns:
            True if the value is valid; otherwise, false.
        """

        result:bool = False

        if (value != None):
            value = value.strip().lower()
            if (value == "s") or (value == "m") or (value == "h") or (value == "d"):
                result = True 

        return result


    def Put(self, key:str, value:str) -> None:
        """
        Adds or updates an element with a specified key and value
        to the Lookup Table.

        Args:
            key (str):
                The key of the element.
            value (str):
                The value of the element.
        
        Raises:
            SIArgumentNullException:
                The key or value argument is null.

        This method adds a new element with a given key and value to
        the collection of key/value pairs. If an element for the
        given key already exists, the original element's value is
        updated.
        """

        if (key == None):
            raise SIArgumentNullException("key")
        if (value == None):
            raise SIArgumentNullException("value")
        self._fItems[key] = value


    def Remove(self, key:str) -> None:
        """
        Removes an existing element with a given key from this lookup table.

        Args:
            key (str):
                The key of the element to remove.
        
        Raises:
            SIArgumentNullException:
                The key argument is null.
        
        This method removes the element with the given key from the
        internal list. Nothing happens if no element with the given
        key can be found.
        """

        if (key == None):
            raise SIArgumentNullException("key")

        if (self.Contains(key)):
            self._fItems.pop(key)
