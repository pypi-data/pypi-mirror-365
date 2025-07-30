import importlib.metadata
import pathlib

import anywidget
import traitlets

try:
    __version__ = importlib.metadata.version("brushable_widget")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"


class BrushableWidget(anywidget.AnyWidget):
    _esm = pathlib.Path(__file__).parent / "static" / "widget.js"
    _css = pathlib.Path(__file__).parent / "static" / "widget.css"
    # _css = ".brushed { fill: green;}"
    # _css = traitlets.Unicode("svg { border: 1px solid; } .brushed { stroke: blue; }").tag(sync=True)
    svg = traitlets.Any().tag(sync=True)
    selected_ids = traitlets.List([]).tag(sync=True)