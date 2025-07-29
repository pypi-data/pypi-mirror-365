# external package imports.
import _threading_local

# our package imports.
from .siargumentnullexception import SIArgumentNullException
from .siconfiguration import SIConfiguration
from .silevel import SILevel
from .sisession import SISession
from .sisessiondefaults import SISessionDefaults
from .sisessioninfo import SISessionInfo

from .siconst import (
    DEFAULT_COLOR_VALUE
)

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SISessionManager:
    """ 
    Manages and configures session instances.
    
    This class manages and configures a list of sessions. Sessions
    can be configured and added to the list with the Add method. To
    lookup a stored session, you can use Get. To remove an existing
    session from the list, call Delete.

    Stored sessions will be reconfigured if LoadConfiguration has
    been called and contains corresponding session entries.

    Threadsafety:
        This class is fully thread-safe.
    """

    # static constants.
    PREFIX:str = "session."
    PREFIX_LEN:int = len(PREFIX)

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        self._fLock:object = _threading_local.RLock()
        self._fDefaults:SISessionDefaults = SISessionDefaults()
        self._fSessions = {}
        self._fSessionInfos = {}


    @property
    def Defaults(self) -> SISessionDefaults:
        """
        Specifies the default property values for new sessions.

        This property lets you specify the default property values
        for new sessions which will be passed to the Add method.
        Please see the Add method for details. For information about
        the available session properties, please refer to the
        documentation of the Session class.
        """
        return self._fDefaults


    def Add(self, session:SISession, store:bool) -> None:
        """
        Configures a passed session instance and optionally saves it
        for later access.

        Args:
            session (SISession):
                The session to configure and to save for later access, if desired.
            store (bool):
                Indicates if the passed session should be stored for later access.

        This method configures the passed session with the default
        session properties as specified by the Defaults property.
        This default configuration can be overridden on a per-session
        basis by loading the session configuration with the
        LoadConfiguration method.

        If the 'store' parameter is true, the passed session is stored
        for later access and can be retrieved with the Get method. To
        remove a stored session from the internal list, call Delete. 

        If this method is called multiple times with the same session
        name, then the Get method operates on the session which got
        added last. If the session parameter is null, this method does nothing.
        """
        if (session == None):
            return

        with self._fLock:
        
            self._fDefaults.Assign(session)

            if (store):
                self._fSessions[session.Name] = session
                session.IsStored = True

            self.Configure(session, session.Name)


    def Assign(self, session:SISession, info:SISessionInfo) -> None:
        """
        Assigns property values to a session instance from stored session information.

        Args:
            session (SISession):
                Session to assign property values to.
            info (SISessionInfo):
                Session information to retrieve property values from.
        """
        if (info.Active):

            if (info.HasColor):
                session.ColorBG = info.ColorBG

            if (info.HasLevel):
                session.Level = info.Level

            if (info.HasActive):
                session.Active = info.Active
            
        else:
            
            if (info.HasActive):
                session.Active = info.Active

            if (info.HasLevel):
                session.Level = info.Level

            if (info.HasColor):
                session.ColorBG = info.ColorBG


    def Clear(self) -> None:
        """
        Clears the configuration of this session manager and removes
        all sessions from the internal lookup table.
        """
        with self._fLock:
            
            self._fSessions.clear()
            self._fSessionInfos.clear()


    def Configure(self, session:SISession, sessionName:str) -> None:
        """
        Configures the specified session from stored session information.

        Args:
            session (SISession):
                Session to configure.
            sessionName (str):
                Name to retrieve session information properties from.
        """
        info:SISessionInfo = None
        key:str = sessionName.lower()   # Session Info keys are always lower-case
        if (key in self._fSessionInfos.keys()):
            info = self._fSessionInfos[key]

        if (info != None):
            self.Assign(session, info)


    def Delete(self, session:SISession) -> None:
        """
        Removes a session from the internal list of sessions.

        Args:
            session (SISession):
                The session to remove from the lookup table of sessions. 

        This method removes a session which has previously been added
        with the Add method. After this method returns, the Get method
        returns null when called with the same session name unless a
        different session with the same name has been added.

        This method does nothing if the supplied session argument is null.
        """
        if (session == None):
            return

        with self._fLock:
        
            name:str = session.Name
            if (self._fSessions[name] == session):
                self._fSessions.pop(name)


    def Get(self, sessionName:str) -> SISession:
        """
        Returns a previously added session.
        
        Args:
             (str):
                The name of the session to lookup and return. 
        
        Returns:
            The requested session or null if the supplied name of the
            session is unknown.
        
        Raises:
            SIArgumentNullException:
                Thrown if the supplied sessionName is null, and a
                "Main" session does not exist.
        
        This method returns a session which has previously been
        added with the Add method and can be identified by the
        supplied name parameter. If the requested session is unknown
        then this method returns null.

        If sessionName is null, then the default "Main" session is
        returned if one exists.

        Note that the behavior of this method can be unexpected in
        terms of the result value if multiple sessions with the same
        name have been added. In this case, this method returns the
        session which got added last and not necessarily the session
        which you expect. 

        Adding multiple sessions with the same name should therefore be avoided.
        </para>
        """
        with (self._fLock):

            # if session name not supplied, then try to return the 
            # default "Main" session.
            if (sessionName == None):
                if "Main" in self._fSessions.keys():
                    return self._fSessions["Main"]
        
            # if session name not supplied then it's a problem.
            if (sessionName != None) and (len(sessionName) == 0):
                raise SIArgumentNullException("sessionName")

            # otherwise try to return the listed session name.
            if (sessionName in self._fSessions.keys()):
                return self._fSessions[sessionName]
            else:
                return None


    def LoadConfiguration(self, config:SIConfiguration) -> None:
        """
        Loads the configuration properties of this session manager.
        
        Args:
            config (SIConfiguration):
                The SIConfiguration object to load the configuration from.

        This method loads the configuration of this session manager
        from the passed SIConfiguration object. Sessions which have
        already been stored or will be added with Add will
        automatically configured with the new properties if the
        passed SIConfiguration object contains corresponding session
        entries. Moreover, this method also loads the default session
        properties which will be applied to all sessions which are
        passed to Add.

        Please see the SmartInspect.LoadConfiguration method for
        details on how session entries and session defaults look
        like.
        """
        with self._fLock:
         
            self._fSessionInfos.clear()
            self.LoadInfos(config)
            self.LoadDefaults(config)


    def LoadDefaults(self, config:SIConfiguration) -> None:
        """
        Loads the configuration session default properties of this session manager.
        
        Args:
            config (SIConfiguration):
                The SIConfiguration object to load the configuration from.

        This method will only process "SessionDefaults.x" lines, and will
        ignore the SmartInspect object configuration and "Session.x.x" lines.
        """
        self._fDefaults.Active = config.ReadBoolean("sessiondefaults.active", self._fDefaults.Active)
        self._fDefaults.Level = config.ReadLevel("sessiondefaults.level", self._fDefaults.Level)
        self._fDefaults.ColorBG = config.ReadColor("sessiondefaults.color", self._fDefaults.ColorBG)


    def LoadInfo(self, name:str, config:SIConfiguration) -> SISessionInfo:
        """
        Loads the configuration session instance properties of a defined
        session in this session manager.
        
        Args:
            name (str):
                The session name.
            config (SIConfiguration):
                The SIConfiguration object to load the configuration from.

        Returns:
            A SISessionInfo object with session information.
        """
        info:SISessionInfo = SISessionInfo()

        # use lower-case config name, just in case ".Name" property not defined.
        info.Name = name

        info.HasName = config.Contains(SISessionManager.PREFIX + name + ".name")
        if (info.HasName):
            info.Name = config.ReadString(SISessionManager.PREFIX + name + ".name", name)

        info.HasActive = config.Contains(SISessionManager.PREFIX + name + ".active")
        if (info.HasActive):
            info.Active = config.ReadBoolean(SISessionManager.PREFIX + name + ".active", True)

        info.HasLevel = config.Contains(SISessionManager.PREFIX + name + ".level")
        if (info.HasLevel):
            info.Level = config.ReadLevel(SISessionManager.PREFIX + name + ".level", SILevel.Debug)

        info.HasColor = config.Contains(SISessionManager.PREFIX + name + ".colorbg")
        if (info.HasColor):
            info.ColorBG = config.ReadColor(SISessionManager.PREFIX + name + ".colorbg", DEFAULT_COLOR_VALUE)

        return info


    def LoadInfos(self, config:SIConfiguration) -> None:
        """
        Loads the configuration session instance properties of all defined
        sessions in this session manager.
        
        Args:
             (SIConfiguration):
                The SIConfiguration object to load the configuration from.

        This method will only process the "session.x.x" configuration lines, and will
        ignore the SmartInspect object configuration and SessionDefaults lines.
        """

        for i in range(config.Count):

            key:str = config.ReadKey(i)

            # do we have a session here?
            if (key == None):
                continue

            # only process the "session.x.x" configuration lines.
            # session info should contain 3 parts: SESSIONPREFIX.NAME.PROPERTY.
            # for example: "session.MySessionName.Level".

            if (len(key) < SISessionManager.PREFIX_LEN):
                continue    # No, too short

            prefix:str = key[0:SISessionManager.PREFIX_LEN]

            if (not prefix.lower() == SISessionManager.PREFIX):
                continue    # No prefix match

            suffix:str = key[SISessionManager.PREFIX_LEN:]
            index:int = suffix.rindex('.')
            if (index == -1):
                continue

            # at this point we know the 3 parts are there - get the session name (middle) part.
            name:str = suffix[0:index]

            # duplicate session configuration entry?  if so, then don't add it.
            # this will occur in case multiple session properties are specified for
            # the same session name, as ALL properties for a session name are processed 
            # by the "LoadInfo()" method call below.  in this case, just ignore the 
            # property because it has already been processed.
            if (name in self._fSessionInfos.keys()):
                continue

            info:SISessionInfo = self.LoadInfo(name, config)
            self._fSessionInfos[name] = info

            # do we need to update a related session?
            # we have to check the list one at a time because the name value from the
            # configuration file is in lower-case, but the session keys are in mixed-case!
            for sessionkey in self._fSessions.keys():
                session:SISession = self._fSessions[sessionkey]
                if ((session != None) and (name == session.Name.lower())):
                    self.Assign(session, info)
                    break


    def Update(self, session:SISession, toName:str, fromName:str) -> None:
        """
        Updates an entry in the internal lookup table of sessions.

        Args:
            session (SISession):
                The session whose name has changed and whose entry should be updated.
            toName (str):
                The new name of the session.
            fromName (str):
                The old name of the session.

        Once the name of a session has changed, this method is called
        to update the internal session lookup table. The 'to' argument
        specifies the new name and 'from' the old name of the session.
        After this method returns, the new name can be passed to the
        Get method to lookup the supplied session.
        """
        if (session == None):
            return

        if (fromName == None) or (toName == None):
            return

        with self._fLock:
        
            if (self._fSessions[fromName] == session):
                self._fSessions.Remove(fromName)

            self.Configure(session, toName)
            self._fSessions[toName] = session
