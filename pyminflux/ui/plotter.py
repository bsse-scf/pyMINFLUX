import pyqtgraph as pg
from pyqtgraph import PlotWidget
from PySide6.QtCore import Signal


class Plotter(PlotWidget):

    locations_selected = Signal(list, name="locations_selected")

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
        """Plot localizations in a 2D scatter plot."""

        if "z" in coords:
            print("3D scatter plot support will follow soon.")
        scatter = pg.ScatterPlotItem(
            size=5,
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

    def clicked(self, _, points):
        """Emit 'signal_selected_locations' when points are selected in the plot."""
        self.locations_selected.emit(points)
