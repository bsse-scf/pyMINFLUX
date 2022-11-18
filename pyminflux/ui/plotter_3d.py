import numpy as np
import pyqtgraph.opengl as gl
from PySide6.QtGui import QQuaternion, QVector3D
from PySide6.QtWidgets import QDialog

from pyminflux.ui.ui_plotter_3d import Ui_Plotter3D


class Plotter3D(QDialog, Ui_Plotter3D):
    def __init__(self, parent=None):
        """Constructor."""

        # Call the base class
        super().__init__(parent=parent)

        # Initialize the dialog
        self.ui = Ui_Plotter3D()
        self.ui.setupUi(self)

        # Initialize the OpenGL View
        self.view = gl.GLViewWidget()
        self.ui.mainLayout.addWidget(self.view)

        # Keep a reference to the grid and the plot
        self.grid = None
        self.scatter = None

        # Set color
        self.color = (1.0, 1.0, 1.0, 0.5)

    def plot(self, coords):
        """Plot the data in 3D."""

        if coords.shape[1] != 3:
            raise ValueError("coords must be an (Nx3) array.")

        # Calculate ranges and positions
        min_x, max_x = coords[:, 0].min(), coords[:, 0].max()
        min_y, max_y = coords[:, 1].min(), coords[:, 1].max()
        min_z, max_z = coords[:, 2].min(), coords[:, 2].max()
        range_x = max_x - min_x
        range_y = max_y - min_y
        range_z = max_z - min_z
        spacing_x = range_x / 25
        spacing_y = range_y / 25
        spacing_z = range_z / 25
        center_x = 0.5 * (min_x + max_x)
        center_y = 0.5 * (min_y + max_y)
        center_z = 0.5 * (min_z + max_z)
        distance = np.max((range_x, range_y, range_z))

        # Create a grid and center it at the center of mass of the point cloud
        if self.grid is not None:
            self.view.removeItem(self.grid)
            self.grid = None
        self.grid = gl.GLGridItem()
        self.grid.setSize(range_x, range_y, range_z)
        self.grid.setSpacing(spacing_x, spacing_y, spacing_z)
        self.view.addItem(self.grid)

        # Add the points
        if self.scatter is not None:
            self.view.removeItem(self.scatter)
            self.scatter = None
        self.scatter = gl.GLScatterPlotItem(
            pos=coords, size=5.0, color=self.color, pxMode=True
        )
        self.scatter.translate(-center_x, -center_y, -center_z)
        self.view.addItem(self.scatter)

        # Set the camera
        self.view.opts["distance"] = distance
        self.view.opts["fov"] = 60
        self.view.opts["elevation"] = 90
        self.view.opts["azimuth"] = 270
        self.view.opts["rotation"] = QQuaternion(1.000000, 0.000000, 0.000000, 0.000000)

        # Show
        self.view.show()
