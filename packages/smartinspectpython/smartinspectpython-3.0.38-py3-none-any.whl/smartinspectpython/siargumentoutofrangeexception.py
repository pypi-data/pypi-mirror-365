# external package imports.
# none

# our package imports.
# none

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIArgumentOutOfRangeException(Exception):
    """
    The exception that is thrown when the value of an argument is outside the 
    allowable range of values as defined by the invoked method.
    """

    def __init__(self, paramName:str) -> None:
        """
        Initializes a new instance of the class with the name of the parameter that causes this exception.
        """
        super().__init__(self)

        # initialize instance.
        self.__paramName = paramName
        self.__message = "The \"{0}\" parameter is outside the allowable range of values as defined by the invoked method.".format(paramName)


    @property
    def Message(self) -> str:
        """ 
        Gets the error message and the parameter name, or only the error message if no parameter name is set.
        """
        return self.__message
    

    @property
    def paramName(self) -> str:
        """ 
        Gets the name of the parameter that causes this exception.
        """
        return self.__paramName

    
    def __str__(self) -> str:
        """ 
        Gets the error message and the parameter name, or only the error message if no parameter name is set.
        """
        return "ArgumentNullException: " + self.__message
