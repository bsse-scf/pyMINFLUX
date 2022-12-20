import numpy as np
import pyqtgraph as pg
from pyqtgraph import PlotWidget
from PySide6.QtCore import Signal

from ..state import State


class Plotter(PlotWidget):

    locations_selected = Signal(list, name="locations_selected")

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(600)
        self.setBackground("w")
        self.brush = pg.mkBrush(255, 255, 255, 128)
        self.pen = pg.mkPen(None)
        self.remove_points()
        self.customize_context_menu()
        self.hideAxis("bottom")
        self.hideAxis("left")
        self.show()

        # Set aspect ratio to 1.0 locked
        self.getPlotItem().getViewBox().setAspectLocked(lock=True, ratio=1.0)

        # Keep a reference to the singleton State class
        self.state = State()

    def remove_points(self):
        self.setBackground("w")
        self.clear()

    def plot_localizations(self, tid, **coords):
        """Plot localizations in a 2D scatter plot."""

        if "z" in coords:
            print("3D scatter plot support will follow soon.")

        # Create the scatter plot
        scatter = pg.ScatterPlotItem(
            size=5,
            pen=self.pen,
            brush=self.brush,
            hoverable=True,
            hoverSymbol="s",
            hoverSize=5,
            hoverPen=pg.mkPen("r", width=2),
            hoverBrush=None,
        )
        scatter.sigClicked.connect(self.clicked)
        scatter.addPoints(
            x=coords["x"].values,
            y=coords["y"].values,
            data=tid.values,
            brush=self.set_colors_per_tid(tid.values),
        )
        self.addItem(scatter)
        self.showAxis("bottom")
        self.showAxis("left")
        self.setBackground("k")

    def customize_context_menu(self):
        """Remove some default context menu actions.

        See: https://stackoverflow.com/questions/44402399/how-to-disable-the-default-context-menu-of-pyqtgraph#44420152
        """
        # All menu entries but the "Plot Options" menu can be accessed via:
        # viewbox = self.getPlotItem().getViewBox()
        # actions = viewbox.menu.actions()

        # Hide the "Plot Options" menu
        self.getPlotItem().ctrlMenu.menuAction().setVisible(False)

    def clicked(self, _, points):
        """Emit 'signal_selected_locations' when points are selected in the plot."""
        self.locations_selected.emit(points)

    def set_colors_per_tid(self, tids: np.ndarray, seed: int = 142) -> np.ndarray:
        """Creates a matrix of colors where same TIDs get the same color."""

        # Initialize random number generator
        rng = np.random.default_rng(seed)

        # Get unique TIDs
        u_tids = np.unique(tids)

        # Create a map to keep track of existing colors
        color_map = {}

        # Fill the map
        for tid in u_tids:
            clr = np.ones((4,), dtype=float)
            clr[1:] = rng.uniform(
                low=0.0,
                high=1.0,
                size=(3,),
            )
            color_map[tid] = clr

        # Now assign the colors
        colors = np.zeros((len(tids), 4))
        for i, tid in enumerate(tids):
            colors[i] = color_map[tid]

        return tids
