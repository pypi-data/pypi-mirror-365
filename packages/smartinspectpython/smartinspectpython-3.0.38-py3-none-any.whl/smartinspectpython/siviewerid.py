# external package imports.
# none

# our package imports.
from .sienumcomparable import SIEnumComparable

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIViewerId(SIEnumComparable):
    """
    Specifies the viewer for displaying the title or data of a Log
    Entry in the Console.

    There are many viewers available for displaying the data of a
    Log Entry in different ways. For example, there are viewers that
    can display lists, tables, binary dumps of data or even websites.

    Every viewer in the Console has a corresponding so called viewer
    context in this library which can be used to send custom logging
    information. To get started, please see the documentation of the
    SISession.LogCustomContext method and SIViewerContext class.
    """

    NoViewer = -1
    """
    Instructs the Console to use no viewer at all.
    """

    Title = 0
    """
    Instructs the Console to display the title of a Log Entry
    in a read-only text field.
    """

    Data = 1
    """
    Instructs the Console to display the data of a Log Entry
    in a read-only text field.
    """

    List = 2
    """
    Instructs the Console to display the data of a Log Entry
    as a list.
    """

    ValueList = 3
    """
    Instructs the Console to display the data of a Log Entry
    as a key/value list.
    """

    Inspector = 4
    """
    Instructs the Console to display the data of a Log Entry
    using an object inspector.
    """

    Table = 5
    """
    Instructs the Console to display the data of a Log Entry
    as a table.
    """

    Web = 100
    """
    Instructs the Console to display the data of a Log Entry
    as a website.
    """

    Binary = 200
    """
    Instructs the Console to display the data of a Log Entry
    as a binary dump using a read-only hex editor.
    """

    HtmlSource = 300 
    """
    Instructs the Console to display the data of a Log Entry
    as HTML source with syntax highlighting.
    """

    JavaScriptSource = 301
    """
    Instructs the Console to display the data of a Log Entry
    as Java Script source with syntax highlighting.
    """

    VbScriptSource = 302
    """
    Instructs the Console to display the data of a Log Entry
    as VBScript source with syntax highlighting.
    """

    PerlSource = 303
    """
    Instructs the Console to display the data of a Log Entry
    as Perl source with syntax highlighting.
    """

    SqlSource = 304
    """
    Instructs the Console to display the data of a Log Entry
    as SQL source with syntax highlighting.
    """

    IniSource = 305
    """
    Instructs the Console to display the data of a Log Entry
    as INI source with syntax highlighting.
    """

    PythonSource = 306
    """
    Instructs the Console to display the data of a Log Entry
    as Python source with syntax highlighting.
    """

    XmlSource = 307
    """
    Instructs the Console to display the data of a Log Entry
    as XML source with syntax highlighting.
    """

    Bitmap = 400
    """
    Instructs the Console to display the data of a Log Entry
    as bitmap image.
    """

    Jpeg = 401
    """
    Instructs the Console to display the data of a Log Entry
    as JPEG image.
    """

    Icon = 402
    """
    Instructs the Console to display the data of a Log Entry
    as a Windows icon.
    """

    Metafile = 403
    """
    Instructs the Console to display the data of a Log Entry
    as Windows Metafile image.
    """

    Png = 404
    """
    Instructs the Console to display the data of a Log Entry
    as PNG image.
    """

