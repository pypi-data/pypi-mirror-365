import marimo

__generated_with = "0.14.13"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    from svg import SVG, Circle, G, Rect
    import random
    import traitlets
    return Circle, G, SVG, mo, random, traitlets


@app.cell
def _(random):
    datapoints = []
    for _i in range(20):
        datapoints.append({
            'x': random.randint(20,180),
            'y': random.randint(20,180),
            'z': random.randint(20,180),
            'id': _i
        })
    return (datapoints,)


@app.cell
def _(Circle, datapoints):
    circles1 = []
    for datapoint in datapoints:
        circles1.append(Circle(
                        cx=datapoint['x'],
                        cy=datapoint['y'],
                        r=5,
                        fill="steelblue",
                        fill_opacity=0.5,
                        stroke_width=1,
                        stroke="white",
                        class_="jfsi2 brushable plot1",
                        id=datapoint['id']))

    circles2 = []
    for datapoint in datapoints:
        circles2.append(Circle(
                        cx=datapoint['x'],
                        cy=datapoint['z'],
                        r=5,
                        fill="steelblue",
                        fill_opacity=0.5,
                        stroke_width=1,
                        stroke="white",
                        class_="jfsi2 brushable plot2",
                        id=datapoint['id']))
    return circles1, circles2


@app.cell
def _(SVG, circles1, circles2):
    svg1 = SVG(
        class_="notebook plot1",
        width=200,
        height=200,
        elements=[circles1]
    )
    svg2 = SVG(
        class_="notebook plot2",
        width=200,
        height=200,
        elements=[circles2]
    )
    return svg1, svg2


@app.cell
def _():
    from brushable_widget import BrushableWidget
    return (BrushableWidget,)


@app.cell
def _(BrushableWidget, svg1, svg2):
    brushable_1 = BrushableWidget(svg=svg1.as_str())
    brushable_2 = BrushableWidget(svg=svg2.as_str())
    return brushable_1, brushable_2


@app.cell
def _(brushable_1, brushable_2, traitlets):
    traitlets.link((brushable_1, "selected_ids"), (brushable_2, "selected_ids"))
    return


@app.cell
def _(brushable_1, brushable_2, mo):
    mo.hstack([mo.ui.anywidget(brushable_1), mo.ui.anywidget(brushable_2)],justify="start")
    return


@app.cell
def _(brushable_1):
    a = brushable_1.selected_ids
    return (a,)


@app.cell
def _(a):
    a
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ### Check if transform works correctly
    We create 2 plots with the same locations, but one is translated by a certain amount. The brush should take that into account.
    """
    )
    return


@app.cell
def _(G, SVG, circles1):
    svg3 = SVG(
        class_="notebook plot3",
        width=200,
        height=200,
        elements=[circles1]
    )
    svg4 = SVG(
        class_="notebook plot4",
        width=200,
        height=200,
        elements=[G(elements=[circles1], transform="translate(20,20)")]
    )
    return svg3, svg4


@app.cell
def _(BrushableWidget, svg3, svg4):
    brushable_3 = BrushableWidget(svg=svg3.as_str())
    brushable_4 = BrushableWidget(svg=svg4.as_str())
    return brushable_3, brushable_4


@app.cell
def _(brushable_3, brushable_4, traitlets):
    traitlets.link((brushable_3, "selected_ids"), (brushable_4, "selected_ids"))
    return


@app.cell
def _(brushable_3, brushable_4, mo):
    mo.hstack([mo.ui.anywidget(brushable_3), mo.ui.anywidget(brushable_4)],justify="start")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
