import numpy as np
import pyqtgraph as pg
from pyqtgraph import ROI, PlotWidget
from PySide6 import QtCore
from PySide6.QtCore import Qt, Signal

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

        # Keep a reference to the scatter plot object
        self.scatter = None

        # ROI for localizations selection
        self.ROI = None
        self.__roi_start_point = None
        self.__roi_is_being_drawn = False

    def mousePressEvent(self, ev):
        """Override mouse press event."""

        # Is the user trying to initiate drawing an ROI?
        if (
            self.scatter is not None
            and ev.button() == Qt.MouseButton.LeftButton
            and ev.modifiers() == QtCore.Qt.ShiftModifier
        ):

            # Remove previous ROI if it exists
            if self.ROI is not None:
                self.removeItem(self.ROI)

            # Create ROI and keep track of position
            self.__roi_is_being_drawn = True
            self.__roi_start_point = (
                self.getPlotItem().getViewBox().mapSceneToView(ev.position())
            )
            self.ROI = ROI(
                pos=self.__roi_start_point,
                size=(0, 0),
                resizable=False,
                rotatable=False,
                pen=(255, 0, 0),
            )
            self.addItem(self.ROI)
            self.ROI.show()

            # Accept the event
            ev.accept()

        else:

            # Call the parent method
            ev.ignore()
            super().mousePressEvent(ev)

    def mouseMoveEvent(self, ev):

        # Is the user drawing an ROI?
        if (
            self.scatter is not None
            and ev.buttons() == Qt.MouseButton.LeftButton
            and ev.modifiers() == QtCore.Qt.ShiftModifier
            and self.__roi_is_being_drawn
        ):

            # Resize the ROI
            current_point = (
                self.getPlotItem().getViewBox().mapSceneToView(ev.position())
            )
            self.ROI.setSize(current_point - self.__roi_start_point)

            # Accept the event
            ev.accept()

        else:

            # Call the parent method
            ev.ignore()
            super().mouseMoveEvent(ev)

    def mouseReleaseEvent(self, ev):
        if (
            self.scatter is not None
            and ev.button() == Qt.MouseButton.LeftButton
            and ev.modifiers() == QtCore.Qt.ShiftModifier
            and self.__roi_is_being_drawn
        ):

            # Select points
            print("SELECT POINTS IN ROI!")

            # Emit point selection!

            # Reset flags
            self.__roi_start_point = None
            self.__roi_is_being_drawn = False

            # Accept the event
            ev.accept()

        else:

            # Call the parent method
            ev.ignore()
            super().mouseReleaseEvent(ev)

    def remove_points(self):
        self.setBackground("w")
        self.clear()

    def plot_localizations(self, tid, **coords):
        """Plot localizations in a 2D scatter plot."""

        if "z" in coords:
            print("3D scatter plot support will follow soon.")

        # Create the scatter plot
        self.scatter = pg.ScatterPlotItem(
            size=5,
            pen=self.pen,
            brush=self.brush,
            hoverable=True,
            hoverSymbol="s",
            hoverSize=5,
            hoverPen=pg.mkPen("w", width=2),
            hoverBrush=None,
        )
        self.scatter.sigClicked.connect(self.clicked)
        self.scatter.addPoints(
            x=coords["x"].values,
            y=coords["y"].values,
            data=tid.values,
            brush=self.set_colors_per_tid(tid.values),
        )
        self.addItem(self.scatter)
        self.showAxis("bottom")
        self.showAxis("left")
        self.setBackground("k")

    def customize_context_menu(self):
        """Remove some default context menu actions.

        See: https://stackoverflow.com/questions/44402399/how-to-disable-the-default-context-menu-of-pyqtgraph#44420152
        """

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
