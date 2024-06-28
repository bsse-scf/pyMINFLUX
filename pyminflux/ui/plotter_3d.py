#  Copyright (c) 2022 - 2024 D-BSSE, ETH Zurich.
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

from PySide6.QtCore import Slot

import numpy as np
from PySide6.QtWidgets import QVBoxLayout, QWidget
from vispy import scene
from vispy.visuals import transforms

from ..processor import MinFluxProcessor
from ..state import State
from .colors import ColorsToRGB


class Plotter3D(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize the reference to the processor
        self.processor = None

        # Initialize references to the graphical objects
        self.canvas = None
        self.view = None
        self.scatter = None

        # Create the layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Keep track of whether we have already plotted something
        self.scatter_is_empty = True

        # Keep a reference to the singleton State class
        self.state = State()

    @Slot()
    def on_show(self):
        # Initialize the canvas only when the main window is shown
        if self.canvas is None:
            # Initialize the canvas
            self.canvas = scene.SceneCanvas(
                keys=None,
                show=False,
                app="pyside6",
                create_native=True,
                decorate=False,
            )

            # Add the native widget
            self.layout.addWidget(self.canvas.native)

            # Set up the view
            self.view = self.canvas.central_widget.add_view()

            # Create the camera
            self.view.camera = scene.cameras.ArcballCamera(fov=0)

            # Create and add the scatter plot
            self.scatter = scene.visuals.Markers()
            self.view.add(self.scatter)

            # Show the canvas
            self.canvas.show()

    def set_processor(self, processor: MinFluxProcessor):
        """Set the processor."""
        self.processor = processor

    def clear(self):
        """Remove the current scatter plot from the view."""
        # Remove the data
        if self.scatter is None:
            return

        self.scatter.set_data(None)
        self.scatter_is_empty = True

        # Reset the camera
        self.view.camera.reset()

        # Force the canvas to update
        self.canvas.update()

    def reset(self):
        """Reset the plotter."""

        if self.scatter is None:
            return

        # Remove the dots from the scatter plot
        if not self.scatter_is_empty:
            self.clear()

    def plot(self, positions, tid, fid):
        """Plot localizations in a 3D scatter plot."""

        # Make sure to have the correct datatype
        positions = positions.to_numpy().astype(np.float32)

        # Get the colors singleton
        rgb = ColorsToRGB().get_rgb(self.state.color_code, tid, fid)

        # If the average locations are plotted, set the diameter to fit the worst localization precision
        if self.state.plot_average_localisations:
            sz = np.max(
                self.processor.filtered_dataframe_stats[["sx", "sy", "sz"]].to_numpy(),
                axis=1,
            )
        else:
            sz = 5

        # Plot the data
        self.scatter.set_data(positions, face_color=rgb, size=sz)

        # Reset scene
        if self.scatter_is_empty:
            self._reset_camera_and_axes(positions)

        # Update the scatter_is_empty flag
        self.scatter_is_empty = False

        # Show the canvas
        self.canvas.show()

    def contextMenuEvent(self, event):
        """Create and display a context menu."""
        event.ignore()

    def _reset_camera_and_axes(self, positions: np.ndarray):
        """Initializes or resets camera position and orientation based on data.

        Parameters
        ----------

        positions: np.ndarray
            Nx3 NumPy array with coordinates [x, y, z].
        """

        if self.scatter is None:
            return

        # Get data range and center
        x_range = [positions[:, 0].min(), positions[:, 0].max()]
        y_range = [positions[:, 1].min(), positions[:, 1].max()]
        z_range = [positions[:, 2].min(), positions[:, 2].max()]
        x_center = (x_range[0] + x_range[1]) / 2
        y_center = (y_range[0] + y_range[1]) / 2
        z_center = (z_range[0] + z_range[1]) / 2

        # Set the camera to view the data
        self.view.camera.center = (x_center, y_center, z_center)
        self.view.camera.scale_factor = max(
            x_range[1] - x_range[0], y_range[1] - y_range[0], z_range[1] - z_range[0]
        )
        self.view.camera.distance = 2 * self.view.camera.scale_factor
        self.view.camera.fov = 0
        self.view.camera.elevation = 30
        self.view.camera.azimuth = 30
        self.view.camera.up = "+z"

        # Apply a transformation to adjust the coordinate system around the data center
        transform = transforms.MatrixTransform()
        transform.reset()
        transform.translate((-x_center, -y_center, -z_center))  # Translate to origin
        transform.rotate(90, (1, 0, 0))  # Rotate 90 degrees around the x-axis
        transform.translate(
            (x_center, y_center, z_center)
        )  # Translate back to original position
        self.scatter.transform = transform

        # Force the canvas to update
        self.canvas.update()
