# our package imports.
from .siargumentnullexception import SIArgumentNullException
from .siconnectionfoundeventargs import SIConnectionFoundEventArgs
from .siutils import Event
from .smartinspectexception import SmartInspectException

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIConnectionsParser:
    """ 
    Responsible for parsing a SmartInspect connections string.

    This class offers a single method only, called Parse, which is
    responsible for parsing a connections string. This method informs
    the caller about found protocols and connections by raising the
    ConnectionFoundEvent event.

    Threadsafety:
        This class is not guaranteed to be thread-safe.
    """

    def __init__(self) -> None:
        """ 
        Initializes a new instance of the class.
        """
   
        # define all events raised by this class.
        self.ConnectionFoundEvent = Event()
        """
        Event raised when a connections string has been found.
        """


    def _RaiseConnectionFoundEvent(self, name:str, options:str) -> None:
        """
        Raises the ConnectionFoundEvent event with found option data.

        Args:
            name (str):
                The protocol name which has been found.
            options (str):
                The options of the new protocol.

        This method is used to inform interested parties that a protocol connections string
        has been found.
        """
        try:

            args:SIConnectionFoundEventArgs = SIConnectionFoundEventArgs(name, options)
            self.ConnectionFoundEvent(self, args)

        except Exception as ex:

            raise  # pass exception on thru.


    def Parse(self, connections:str) -> None:
        """
        Parses the connections part of a connections string.

        Args:
            connections (str):
                The connections to parse. Not allowed to be null.

        Raises:
            SIArgumentNullException:
                The connections argument is null.
            SmartInspectException:
                Invalid connections string syntax.

        This method parses the supplied connections part of a connections
        string and informs the caller about found connections via the
        ConnectionFoundEvent event.

        For information about the correct syntax of the connections,
        please refer to the documentation of the SIProtocol.connections
        property.

        <details>
            <summary>Sample Code</summary>
        ``` python
        .. include:: ../docs/include/samplecode/SIConnectionsParser/Parse.py
        ```
        </details>
        """
        if (connections == None):
            raise SIArgumentNullException("connections")
            
        connections = connections.strip()
        if (len(connections) == 0):
            return

        i:int = 0
        c:chr
        name:str = ""
        options:str = ""
        parselen:int = len(connections)

        # This code attempts to parse connection strings for protocol definitions delimited by comma's.  
        # Examples:
        # 1) tcp(host=localhost,port=4228,timeout=30000)
        # 2) tcp(host=localhost,port=4228,timeout=30000),file(fileoption1=value)

        while (i < parselen - 1):

            # process the protocol NAME portion of the connection string.
            c = connections[i]
            while (i < parselen - 1):
                i = i + 1
                name += c
                c = connections[i]
                if (c == '('):
                    break

            # did we find the '(' delimiter? if not, then it's an error!
            if (c != '('):
                raise SmartInspectException("Missing \"(\" at position " + str(i + 1) + " in protocol connection string!")

            # point to character after "(" delimiter.
            if (i < parselen):
                i = i + 1

            # process the OPTIONS portion of the connection string.
            quoted:bool = False
            while (i < parselen):
                c = connections[i]
                i = i + 1
                if (c == '"'):
                    if (i < parselen):
                        if (connections[i] != '"'):
                            quoted = (not quoted)
                            continue
                        else:
                            i = i + 1  # skip one quote
                            options = options + '"'
                    else:
                        quoted = (not quoted)
                        continue
                elif (c == ')' and not quoted):
                    break
                options = options + c

            # if the options was quoted, was closing quote provided?  if not, then it's an error!
            if (quoted):
                raise SmartInspectException("Quoted options not closed in \"" + name + "\" protocol connection string!")

            if (c != ')'):
                raise SmartInspectException("Missing \")\" at position " + str(i + 1) + " in \"" + name + "\" protocol connection string!")

            # skip the ',' character.
            if (i < parselen and connections[i] == ','):
                i = i + 1

            # raise event to inform interested parties that we found a protocol connection string.
            self._RaiseConnectionFoundEvent(name, options)

            # reset protocol and options for next protocol connection string.
            name = ""
            options = ""
