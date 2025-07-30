# NOTE: Some import statements are intentionally written as alias imports, i.e.
#       `import package.subpackage as subpackage`
#       This is necessary for subpackages for which no stubs have been created yet.
#       -> For these imports, DO NOT CHANGE the import statements to `from package import subpackage`.
#       Once stubs for these subpackages are created, the import statements can
#       be changed to their respective `from package import subpackage` form.

# Import of subpackages for which _no_ stubs have been created yet:
import plotly.graph_objs.scatterternary.hoverlabel as hoverlabel
import plotly.graph_objs.scatterternary.legendgrouptitle as legendgrouptitle
import plotly.graph_objs.scatterternary.marker as marker
import plotly.graph_objs.scatterternary.selected as selected
import plotly.graph_objs.scatterternary.unselected as unselected

# Import of subpackages for which stubs have been created:
# -/-
#
# Direct import of names this subpackage exports:
from plotly.graph_objs.scatterternary._hoverlabel import Hoverlabel
from plotly.graph_objs.scatterternary._legendgrouptitle import Legendgrouptitle
from plotly.graph_objs.scatterternary._line import Line
from plotly.graph_objs.scatterternary._marker import Marker
from plotly.graph_objs.scatterternary._selected import Selected
from plotly.graph_objs.scatterternary._stream import Stream
from plotly.graph_objs.scatterternary._textfont import Textfont
from plotly.graph_objs.scatterternary._unselected import Unselected

__all__ = [
    "Hoverlabel",
    "Legendgrouptitle",
    "Line",
    "Marker",
    "Selected",
    "Stream",
    "Textfont",
    "Unselected",
    "hoverlabel",
    "legendgrouptitle",
    "marker",
    "selected",
    "unselected",
]
