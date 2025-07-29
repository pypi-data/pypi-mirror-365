# external package imports.
# none

# our package imports.
from .sienumcomparable import SIEnumComparable
from .siviewerid import SIViewerId

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SISourceId(SIEnumComparable):
    """
    Used in the LogSource methods of the SISession class to specify
    the type of source code.
    """

    Html = SIViewerId.HtmlSource.value
    """
    Instructs the SISession.LogSource methods to use syntax highlighting for HTML.
    """

    JavaScript = SIViewerId.JavaScriptSource.value
    """
    Instructs the SISession.LogSource methods to use syntax highlighting for JavaScript.
    """

    VbScript = SIViewerId.VbScriptSource.value
    """
    Instructs the SISession.LogSource methods to use syntax highlighting for VBScript.
    """

    Perl = SIViewerId.PerlSource.value
    """
    Instructs the SISession.LogSource methods to use syntax highlighting for Perl.
    """

    Sql = SIViewerId.SqlSource.value
    """
    Instructs the SISession.LogSource methods to use syntax highlighting for SQL.
    """

    Ini = SIViewerId.IniSource.value
    """
    Instructs the SISession.LogSource methods to use syntax highlighting for INI file.
    """

    Python = SIViewerId.PythonSource.value
    """
    Instructs the SISession.LogSource methods to use syntax highlighting for Python.
    """

    Xml = SIViewerId.XmlSource.value
    """
    Instructs the SISession.LogSource methods to use syntax highlighting for XML.
    """
