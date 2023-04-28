#  Copyright (c) 2022 - 2023 D-BSSE, ETH Zurich.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#   limitations under the License.
#

import numpy as np
import pyqtgraph.opengl as gl
from PySide6.QtGui import QQuaternion, Qt
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

        # Only hide on close by default
        self.hide_on_close = True

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
        range_z = 0.0
        spacing_x = range_x / 25
        spacing_y = range_y / 25
        spacing_z = 0.0
        center_x = 0.5 * (min_x + max_x)
        center_y = 0.5 * (min_y + max_y)
        center_z = 0.0
        distance = np.max((range_x, range_y, range_z))

        # Remove items if they already exist
        if self.grid is not None:
            self.view.removeItem(self.grid)
            self.grid.deleteLater()

        if self.scatter is not None:
            self.view.removeItem(self.scatter)
            self.scatter.deleteLater()

        # Create a grid and center it at the center of mass of the point cloud
        self.grid = gl.GLGridItem()
        self.grid.setSize(range_x, range_y, range_z)
        self.grid.setSpacing(spacing_x, spacing_y, spacing_z)
        self.view.addItem(self.grid)

        # Add the points
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

    def closeEvent(self, ev):
        """Hide the dialog instead of closing it."""
        if self.hide_on_close:
            ev.ignore()
            self.hide()
        else:
            ev.accept()
