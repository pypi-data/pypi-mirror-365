# our package imports.
from .siargumentnullexception import SIArgumentNullException
from .sioptionfoundeventargs import SIOptionFoundEventArgs
from .siutils import Event
from .smartinspectexception import SmartInspectException

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIOptionsParser:
    """ 
    Responsible for parsing the options part of a SmartInspect
    connections string.

    This class offers a single method only, called Parse, which
    is responsible for parsing the options part of a connections
    string. This method informs the caller about found options
    by raising the OptionFound event.

    Threadsafety:
        This class is not guaranteed to be thread-safe.
    """

    def __init__(self) -> None:
        """ 
        Initializes a new instance of the class.
        """
   
        # define all events raised by this class.
        self.OptionFoundEvent:Event = Event()
        """
        Event raised when an option key=value pair has been found.
        """


    def _RaiseOptionFoundEvent(self, protocol:str, key:str, value:str) -> None:
        """
        Raises the OptionFoundEvent event with found option data.

        Args:
            protocol (str):
                The related protocol.
            key (str):
                The option key that was found.
            value (str):
                The option value that was found.

        This method is used to inform other objects that an option has been found for 
        a protocol configuration string.
        """
        try:

            args:SIOptionFoundEventArgs = SIOptionFoundEventArgs(protocol, key, value)
            self.OptionFoundEvent(self, args)

        except Exception as ex:

            raise  # pass exception on thru.


    def Parse(self, protocol:str, options:str) -> None:
        """
        Parses the options part of a connections string.

        Args:
            protocol (str):
                The related protocol. Not allowed to be null.
            options (str):
                The options to parse. Not allowed to be null.

        Raises:
            SIArgumentNullException:
                The protocol or options argument is null.
            SmartInspectException:
                Invalid options string syntax.

        This method parses the supplied options part of a connections
        string and informs the caller about found options via the
        OptionFound event.

        For information about the correct syntax of the options,
        please refer to the documentation of the SIProtocol.Options
        property.

        <details>
            <summary>Sample Code</summary>
        ``` python
        .. include:: ../docs/include/samplecode/SIOptionsParser/Parse.py
        ```
        </details>
        """
        if (protocol == None):
            raise SIArgumentNullException("protocol")
        if (options == None):
            raise SIArgumentNullException("options")
            
        options = options.strip()
        if (len(options) == 0):
            return

        i:int = 0
        c:chr
        key:str = ""
        value:str = ""
        parselen:int = len(options)

        # This code attempts to parse an option string of key=value pairs delimited by comma's.  
        # Examples:
        # 1) host=localhost,port=4228,timeout=30000				key=host, value=localhost
        # 2) host="localhost,host2",port=4228,timeout=30000		key=host, value="localhost,host2" (comma not treated as delimiter since it is in quotes!)

        while (i < parselen - 1):

            # process the KEY portion of the option.
            c = options[i]
            while (i < parselen - 1):
                i = i + 1
                key += c
                c = options[i]
                if (c == '='):
                    break

            # did we find the '=' delimiter? if not, then it's an error!
            if (c != '='):
                raise SmartInspectException("Missing \"=\" in " + protocol + " protocol!")

            # point to character after "=" delimiter.
            if (i < parselen):
                i = i + 1

            # process the VALUE portion of the option.
            quoted:bool = False
            while (i < parselen):
                c = options[i]
                i = i + 1
                if (c == '"'):
                    if (i < parselen):
                        if (options[i] != '"'):
                            quoted = (not quoted)
                            continue
                        else:
                            i = i + 1  # skip one quote
                    else:
                        quoted = (not quoted)
                        continue
                elif (c == ',' and not quoted):
                    break
                value = value + c

            # if the value was quoted, was closing quote provided?  if not, then it's an error!
            if (quoted):
                raise SmartInspectException("Quoted value not closed in " + protocol + " protocol!")

            # raise event to inform interested parties that we found an option.
            self._RaiseOptionFoundEvent(protocol, key.strip(), value.strip())

            # reset key and value for next option pair.
            key = ""
            value = ""
