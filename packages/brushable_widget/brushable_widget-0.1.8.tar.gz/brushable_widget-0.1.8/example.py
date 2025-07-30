import marimo

__generated_with = "0.14.13"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    from svg import SVG, Circle, G, Rect
    import random
    import traitlets
    return Circle, G, Rect, SVG, mo, random


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
    return


@app.cell
def _():
    from brushable_widget import BrushableWidget
    return (BrushableWidget,)


@app.cell
def _():
    # brushable_1 = BrushableWidget(svg=svg1.as_str())
    # brushable_2 = BrushableWidget(svg=svg2.as_str())
    return


@app.cell
def _():
    # traitlets.link((brushable_1, "selected_ids"), (brushable_2, "selected_ids"))
    return


@app.cell
def _():
    # mo.hstack([mo.ui.anywidget(brushable_1), mo.ui.anywidget(brushable_2)],justify="start")
    return


@app.cell
def _():
    # a = brushable_1.selected_ids
    return


@app.cell
def _():
    # a
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
def _():
    # svg3 = SVG(
    #     class_="notebook plot3",
    #     width=200,
    #     height=200,
    #     elements=[circles1]
    # )
    # svg4 = SVG(
    #     class_="notebook plot4",
    #     width=200,
    #     height=200,
    #     elements=[G(elements=[circles1], transform="translate(20,20)")]
    # )
    return


@app.cell
def _():
    # brushable_3 = BrushableWidget(svg=svg3.as_str())
    # brushable_4 = BrushableWidget(svg=svg4.as_str())
    return


@app.cell
def _():
    # traitlets.link((brushable_3, "selected_ids"), (brushable_4, "selected_ids"))
    return


@app.cell
def _():
    # mo.hstack([mo.ui.anywidget(brushable_3), mo.ui.anywidget(brushable_4)],justify="start")
    return


@app.cell
def _(mo):
    mo.md(r"""### Rectangle borders are hidden behind the others?""")
    return


@app.cell
def _():
    rect_datapoints = []
    for _i in range(20):
        for _j in range(20):
            rect_datapoints.append({
                'x': _i*10,
                'y': _j*10,
                'id': str(_i) + '_' + str(_j)
            })
    return (rect_datapoints,)


@app.cell
def _(Rect, random, rect_datapoints):
    rectangles = []
    for _datapoint in rect_datapoints:
        rectangles.append(Rect(
                        x=_datapoint['x'],
                        y=_datapoint['y'],
                        width=8,
                        height=8,
                        fill="steelblue",
                        fill_opacity=random.randint(0,100)/100,
                        stroke_width=1,
                        stroke="white",
                        class_="fnms6 brushable plot_rect",
                        id=_datapoint['id']))
    return (rectangles,)


@app.cell
def _(G, SVG, rectangles):
    rect_svg = SVG(
        class_="notebook rect_plot",
        width=500,
        height=500,
        elements=[G(elements=[rectangles], transform="translate(173,21)")]
    )
    return (rect_svg,)


@app.cell
def _(rect_svg):
    rect_svg.as_str()
    return


@app.cell
def _(BrushableWidget, mo, rect_svg):
    mo.ui.anywidget(BrushableWidget(svg=rect_svg.as_str(), selected_ids = []))
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
