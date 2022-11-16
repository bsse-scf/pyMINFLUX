import pyqtgraph as pg
from pyqtgraph import PlotWidget


class Plotter(PlotWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(600)
        self.setBackground("w")
        self.brush = pg.mkBrush(255, 255, 255, 128)
        self.pen = pg.mkPen(None)
        self.remove_points()
        self.hideAxis("bottom")
        self.hideAxis("left")
        self.show()

    def remove_points(self):
        self.setBackground("w")
        self.clear()

    def plot_localizations(self, **coords):
        if "z" in coords:
            print("3D scatter plot support will follow soon.")
        scatter = pg.ScatterPlotItem(
            size=3,
            pen=self.pen,
            brush=self.brush,
            hoverable=True,
            hoverSymbol="s",
            hoverSize=5,
            hoverPen=pg.mkPen("r", width=2),
            hoverBrush=pg.mkBrush("r"),
        )
        scatter.sigClicked.connect(self.clicked)
        scatter.setData(x=coords["x"], y=coords["y"])
        self.addItem(scatter)
        self.showAxis("bottom")
        self.showAxis("left")
        self.setBackground("k")

    def clicked(self, plot, points):
        for p in points:
            print(f"index = {p.index()}, position = {p.pos()}")
