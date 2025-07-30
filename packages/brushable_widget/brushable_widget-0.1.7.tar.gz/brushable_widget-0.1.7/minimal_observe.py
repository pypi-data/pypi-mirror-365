import marimo

__generated_with = "0.11.17"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    import anywidget
    import traitlets
    return anywidget, mo, traitlets


@app.cell
def _(anywidget, traitlets):
    class CounterWidget(anywidget.AnyWidget):
        _esm = """
        function render({ model, el }) {
          let count = () => model.get("value");
          let btn = document.createElement("button");
          btn.innerHTML = `count is ${count()}`;
          btn.addEventListener("click", () => {
            model.set("value", count() + 1);
            model.save_changes();
          });
          model.on("change:value", () => {
            btn.innerHTML = `count is ${count()}`;
          });
          el.appendChild(btn);
        }
        export default { render };
        """
        value = traitlets.Int(17).tag(sync=True)
    return (CounterWidget,)


@app.cell
def _(mo):
    get_value, set_value = mo.state(0)
    return get_value, set_value


@app.cell
def _(CounterWidget):
    m1 = CounterWidget()
    m2 = CounterWidget()
    return m1, m2


@app.cell
def _(m1, m2, set_value):
    m1.observe(lambda x: set_value(x["new"]), names="value")
    m2.observe(lambda x: set_value(x["new"]), names="value")
    return


@app.cell
def _(m1, mo):
    w1 = mo.ui.anywidget(m1)
    w1
    return (w1,)


@app.cell
def _(m2, mo):
    w2 = mo.ui.anywidget(m2)
    return (w2,)


@app.cell
def _(w1):
    w1.widget.value
    return


@app.cell
def _(w2):
    w2.value
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
