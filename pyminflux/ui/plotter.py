import pyqtgraph as pg
from PySide6.QtGui import QColor
from pyqtgraph import PlotWidget


class Plotter(PlotWidget):

    def __init__(self):
        super().__init__()
        self.setBackground('w')
        self.brush = pg.mkBrush(240, 50, 20, 180)
        self.remove_points()
        self.hideAxis('bottom')
        self.hideAxis('left')
        self.show()

    def remove_points(self):
        self.clear()

    def plot_localizations(self, **coords):
        if "z" in coords:
            print("3D scatter plot support will follow soon.")
        scatter = pg.ScatterPlotItem(size=10, brush=self.brush)
        scatter.setData(coords["x"], coords["y"])
        self.addItem(scatter)
        self.showAxis('bottom')
        self.showAxis('left')
