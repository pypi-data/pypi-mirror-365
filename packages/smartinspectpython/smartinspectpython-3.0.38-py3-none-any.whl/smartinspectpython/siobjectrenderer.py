# external package imports.
from array import array
from typing import Collection

# our package imports.
# none

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIObjectRenderer:
    """ 
    Responsible for creating a string representation of any arbitrary object.

    This class provides only one method, RenderObject, which is
    capable of creating a string representation of an object. It
    renders dictionaries, collections or any other object.

    Threadsafety:
        The public static members of this class are thread-safe.
    """

    def __init__(self) -> None:
        """ 
        Initializes a new instance of the class.
        """
        #self.__private SIObjectRenderer() {}  TODO - what is this?
        #private SIObjectRenderer() {}


    @staticmethod
    def _RenderCollection(oColl:Collection) -> str:
        """
        Creates a string representation of a collection object.

        Args:
            oColl (Collection):
                The collection object to render. Can be null.

        Returns:
            A string representation of the supplied object.

        This method is capable of creating a string representation of a collection object.
        It simply loops through the values of the collection, and calls RenderObject for each value.
        """
        sb = "["
        if (len(oColl) > 0):

            # append all keys and values in the dictionary.
            for obj in oColl:

                if (obj == oColl):
                    sb += "<cycle>"
                else:
                    sb += SIObjectRenderer.RenderObject(obj)

                sb += ", "

            # drop the ending comma-space delimiter from the built string.
            sb = sb[:-2]

        sb += "]"
        return sb


    @staticmethod
    def _RenderDictionary(oDict:dict) -> str:
        """
        Creates a string representation of a dictionary object.

        Args:
            oDict (dict):
                The dictionaty object to render. Can be null.

        Returns:
            A string representation of the supplied object.

        This method is capable of creating a string representation of a dictionaty object.
        It simply loops through the keys collection, and calls RenderObject for each key and its value.
        """
        sb = "{"
        if (len(oDict) > 0):

            # append all keys and values in the dictionary.
            for key in oDict.keys():

                val:object = oDict[key]

                if (key == oDict):
                    strKey = "<cycle>"
                else:
                    strKey = SIObjectRenderer.RenderObject(key)

                if (val == oDict):
                    strVal = "<cycle>"
                else:
                    strVal = SIObjectRenderer.RenderObject(val)

                sb += strKey + "=" + strVal + ", "

            # drop the ending comma-space delimiter from the built string.
            sb = sb[:-2]

        sb += "}"
        return sb


    @staticmethod
    def RenderObject(obj:object) -> str:
        """
        Creates a string representation of an object.

        Args:
            obj (object):
                The object to render. Can be null.

        Returns:
            A string representation of the supplied object.

        This method is capable of creating a string representation
        of an object. For most types this method simply calls the
        __str__ method of the supplied object. Some objects, like
        dictionaries or collections, are handled special.
        """
        if (obj == None):
            return "<null>"
        
        if (isinstance(obj, str)):
            value:str = str(obj)
            if (value != None):
                return value.strip()

        if (isinstance(obj, dict)):
            oDict:dict = obj
            return SIObjectRenderer._RenderDictionary(oDict)

        if (isinstance(obj, Collection)):
            oColl:Collection = obj
            return SIObjectRenderer._RenderCollection(oColl)
           
        if (isinstance(obj, array)):
            oArr:array = obj
            return SIObjectRenderer._RenderCollection(oArr)
           
        value:str = str(obj)
        if (value != None):
            return value.strip()

        return "<null>"
