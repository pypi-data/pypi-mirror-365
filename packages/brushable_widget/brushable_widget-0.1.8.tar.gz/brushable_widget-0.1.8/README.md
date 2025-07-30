# brushable_widget
An anywidget that adds a brush to SVG plots.

## Installation

```sh
pip install brushable_widget
```

or with [uv](https://github.com/astral-sh/uv):

```sh
uv add brushable_widget
```

## Example
An example marimo script (available as `example.py` => run with `uv run marimo edit example.py`).

IMPORTANT: the SVG elements that should be brushable should:

* have "brushable" in their `class_`
* have an ID

```python
import marimo as mo
from svg import SVG, Circle
import random
import brushable_widget

datapoints = []
for _i in range(20):
    datapoints.append({
        'x': random.randint(20,180),
        'y': random.randint(20,180),
        'z': random.randint(20,180),
        'id': _i
    })

circles = []
for datapoint in datapoints:
    circles.append(Circle(
        cx=datapoint['x'],
        cy=datapoint['y'],
        r=10,
        fill="steelblue",
        fill_opacity=0.5,
        stroke_width=1,
        stroke="white",
        class_="jfsi2 brushable",
        id=datapoint['id']
    ))

svg = SVG(
    class_="notebook",
    width=200,
    height=200,
    elements=[circles]
)

x = mo.ui.anywidget(brushable_widget.BrushableWidget(svg=svg.as_str(), selected_ids = []))

x

x.selected_ids
```

## Development

We recommend using [uv](https://github.com/astral-sh/uv) for development.
It will automatically manage virtual environments and dependencies for you.

```sh
uv run jupyter lab example.ipynb
```
