# external package imports.
# none

# our package imports.
from .sicolor import SIColor
from .silevel import SILevel

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SISessionInfo:
    """ 
    Contains session information (internal use only).
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        self.HasName:bool = False
        self.Name:str = ""
        self.HasColor:bool = False
        self.ColorBG:SIColor = None
        self.HasLevel:bool = False
        self.Level:SILevel = None
        self.HasActive:bool = False
        self.Active:bool = False
