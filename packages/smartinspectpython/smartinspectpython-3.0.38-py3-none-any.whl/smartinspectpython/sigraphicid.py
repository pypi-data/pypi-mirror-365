# our package imports.
from .sienumcomparable import SIEnumComparable
from .siviewerid import SIViewerId

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIGraphicId(SIEnumComparable):
    """
    Used by the SIGraphicViewerContext class to specify the desired
    picture type.
    """

    Bitmap = SIViewerId.Bitmap.value
    """
    Instructs the graphic viewer context class to treat the data as bitmap image.
    """

    Jpeg = SIViewerId.Jpeg.value
    """
    Instructs the graphic viewer context class class to treat the data as JPEG image.
    """

    Icon = SIViewerId.Icon.value
    """
    Instructs the graphic viewer context class class to treat the data as Window icon.
    """

    Metafile = SIViewerId.Metafile.value
    """
    Instructs the graphic viewer context class class to treat the data as Window Metafile image.
    """

    Png = SIViewerId.Png.value
    """
    Instructs the graphic viewer context class class to treat the data as PNG image.
    """

