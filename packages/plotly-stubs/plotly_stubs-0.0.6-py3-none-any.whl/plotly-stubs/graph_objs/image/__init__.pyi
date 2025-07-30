# NOTE: Some import statements are intentionally written as alias imports, i.e.
#       `import package.subpackage as subpackage`
#       This is necessary for subpackages for which no stubs have been created yet.
#       -> For these imports, DO NOT CHANGE the import statements to `from package import subpackage`.
#       Once stubs for these subpackages are created, the import statements can
#       be changed to their respective `from package import subpackage` form.

# Import of subpackages for which _no_ stubs have been created yet:
import plotly.graph_objs.image.hoverlabel as hoverlabel
import plotly.graph_objs.image.legendgrouptitle as legendgrouptitle

# Import of subpackages for which stubs have been created:
# -/-
#
# Direct import of names this subpackage exports:
from plotly.graph_objs.image._hoverlabel import Hoverlabel
from plotly.graph_objs.image._legendgrouptitle import Legendgrouptitle
from plotly.graph_objs.image._stream import Stream

__all__ = [
    "Hoverlabel",
    "Legendgrouptitle",
    "Stream",
    "hoverlabel",
    "legendgrouptitle",
]
