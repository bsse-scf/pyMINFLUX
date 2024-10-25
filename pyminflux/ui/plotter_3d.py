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
#  limitations under the License.

import numpy as np
from PySide6.QtCore import QPoint, Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QVBoxLayout, QWidget
from vispy import scene
from vispy.visuals import transforms

from ..processor import MinFluxProcessor
from ..state import State
from .colors import ColorsToRGB
from .helpers import export_vispy_plot


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
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        # Keep track of whether we have already plotted something
        self.scatter_is_empty = True

        # Keep a reference to the singleton State class
        self.state = State()

        # Keep track of original distance
        self.original_distance = 1.0

        # Store the previous camera distance
        self.previous_camera_distance = 1.0

        # Keep track of the initial camera rotation
        self.original_rotation = None

        # Keep track of current point size
        self.current_point_sizes = None

        # Un-weighted point size
        self.fixed_point_size = 5.0

        # Keep track of current point colors
        self.current_colors = None

        # Keep track of surrent sizes
        self.current_sizes = None

        # Keep track of last plotted positions
        self.positions = None

    @Slot()
    def on_show(self):
        # Initialize the canvas only when the main window is shown
        if self.canvas is None:
            # Initialize the canvas
            self.canvas = CustomSceneCanvas(plotter_3d=self)

            # Add the native widget
            self.layout.addWidget(self.canvas.native)

            # Set up the view
            self.view = self.canvas.central_widget.add_view()

            # Create the camera
            self.view.camera = scene.cameras.ArcballCamera(
                fov=0 if self.state.plot_3d_orthogonal else 45
            )

            # Store the original camera rotation
            self.original_rotation = self.view.camera._quaternion.copy()

            # Create and add the scatter plot
            self.scatter = scene.visuals.Markers()
            self.view.add(self.scatter)

            # Connect the update function to the view_changed event
            self.canvas.events.draw.connect(self.update_point_size)

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

    def reset_camera(self):
        """Reset the camera."""
        if self.positions is None:
            return
        self._reset_camera_and_axes(self.positions)

        # Reset the camera rotation to the original rotation
        if self.original_rotation is not None:
            self.view.camera._quaternion = self.original_rotation.copy()

        # Update the view
        self.view.camera.view_changed()
        self.canvas.update()

    def plot(self, positions, tid, fid, depth, time):
        """Plot localizations in a 3D scatter plot."""

        # Make sure to have the correct datatype
        self.positions = positions.to_numpy().astype(np.float32)

        # Get the colors singleton
        self.current_colors = ColorsToRGB().get_rgb(
            self.state.color_code, tid, fid, depth, time
        )

        # If the average locations are plotted, set the diameter to fit the worst localization precision
        if self.state.plot_average_localisations:
            # @TODO Temporarily disable until a better solution is in place
            # sz = np.max(
            #     self.processor.filtered_dataframe_stats[["sx", "sy", "sz"]].to_numpy(),
            #     axis=1,
            # )
            #
            # # Keep track of current sizes
            # self.current_point_sizes = sz
            sz = self.fixed_point_size
        else:
            sz = self.fixed_point_size

        # Plot the data
        self.scatter.set_data(
            self.positions,
            edge_color=self.current_colors,
            face_color=self.current_colors,
            size=sz,
        )

        # Reset scene
        requested_fov = 0 if self.state.plot_3d_orthogonal else 45
        if self.scatter_is_empty or self.view.camera.fov != requested_fov:
            self._reset_camera_and_axes(self.positions)

        # Update the scatter_is_empty flag
        self.scatter_is_empty = False

        # Show the canvas
        self.canvas.show()

    def update_point_size(self, event):
        """Update point sizes based on camera distance."""

        # This only applies when plotting the localization precision
        if not self.state.plot_average_localisations:
            return

        # Get new camera distance
        camera_distance = self.view.camera.distance

        # Check if the camera distance has changed
        if (
            self.previous_camera_distance is None
            or self.previous_camera_distance == camera_distance
        ):
            return

        # Resize points
        if camera_distance != 0:
            scale_factor = self.previous_camera_distance / camera_distance
        else:
            scale_factor = 1.0

        # Update last camera position
        self.previous_camera_distance = camera_distance

        # Update current point size
        self.current_point_sizes *= scale_factor

        # Update the spot sizes
        self.scatter.set_data(
            self.positions,
            edge_color=self.current_colors,
            face_color=self.current_colors,
            size=self.current_point_sizes,
        )

    def _reset_camera_and_axes(self, positions: np.ndarray):
        """Initializes or resets camera position and orientation based on data.

        Parameters
        ----------

        positions: np.ndarray
            Nx3 NumPy array with coordinates [x, y, z].
        """

        if self.scatter is None:
            return

        if positions is None:
            if self.positions is None:
                return
            positions = self.positions

        # Position camera to look at the data center from a fixed distance
        self._position_camera(positions=positions)

        # Adjust the camera distance as a function of the fov
        self._adjust_camera_distance(new_fov=0 if self.state.plot_3d_orthogonal else 45)

        # Force the canvas to update
        self.canvas.update()

    @Slot()
    def toggle_projection(self):
        if self.view.camera.fov == 0:
            # Switch to perspective projection
            new_fov = 45.0
        else:
            # Switch to orthographic projection
            new_fov = 0

        # Adjust the camera distance for the new fov
        self._adjust_camera_distance(new_fov)

    def _adjust_camera_distance(self, new_fov):
        """Adjust the camera distance based on the new field of view."""
        if new_fov == 0:
            # Switch to orthographic projection
            # Calculate the new distance to maintain the same view
            if self.view.camera.fov == 45:
                scale_factor = np.tan(np.radians(self.view.camera.fov) / 2)
            else:
                scale_factor = 1.0
            self.view.camera.distance = self.previous_camera_distance / scale_factor
        else:
            # Switch to perspective projection
            if self.view.camera.fov == 0:
                # Multiply by an additional factor 1.4 to compensate for perspective change (heuristic)
                scale_factor = np.tan(np.radians(new_fov) / 2) * 1.4
            else:
                scale_factor = 1.0
            self.view.camera.distance = self.previous_camera_distance * scale_factor
        self.view.camera.fov = new_fov

    def _position_camera(self, positions):
        """Position camera and coordinate system."""

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
        # Multiply by a factor 2.1 to keep all data points in the view (heuristic)
        self.view.camera.distance = 2.1 * self.view.camera.scale_factor
        self.previous_camera_distance = self.view.camera.distance

        # Apply a transformation to adjust the coordinate system around the data center
        transform = transforms.MatrixTransform()
        transform.reset()

        # First translate to origin
        transform.translate((-x_center, -y_center, -z_center))

        # Then rotate 90 degrees around the x-axis
        transform.rotate(90, (1, 0, 0))

        # Finally translate back to original position
        transform.translate((x_center, y_center, z_center))
        self.scatter.transform = transform


class CustomSceneCanvas(scene.SceneCanvas):
    """Customize VisPy SceneCanvas."""

    def __init__(self, plotter_3d: Plotter3D):
        # Initialize State
        state = State()

        # Store reference to the Plotter3D object
        self.plotter_3d = plotter_3d

        super().__init__(
            keys=None,
            show=False,
            app="pyside6",
            create_native=True,
            decorate=False,
            dpi=state.plot_export_dpi,
        )

        # Connect the mouse release event to a custom handler
        self.events.mouse_release.connect(self.on_mouse_release)

    def on_mouse_release(self, event):
        """Mouse release handler."""

        # If the button is 2 (right-click), we open a context menu
        if event.button == 2:

            # Get the position of the cursor
            pos = event.pos
            qt_pos = QPoint(int(pos[0]), int(pos[1]))

            # Convert to global screen coordinates
            global_pos = self.native.mapToGlobal(qt_pos)

            # Open of the context menu
            self.open_context_menu(global_pos)

    def open_context_menu(self, global_pos):
        """Open context menu."""

        # Create the context menu
        context_menu = QMenu(None)

        # Add actions to the menu
        save_action = QAction("Export plot", None)
        context_menu.addAction(save_action)
        reset_action = QAction("Reset camera", None)
        context_menu.addAction(reset_action)

        # Connect triggered signals to slots
        save_action.triggered.connect(lambda _: export_vispy_plot(self))
        reset_action.triggered.connect(self.plotter_3d.reset_camera)

        # Open the context menu
        context_menu.exec(global_pos)
