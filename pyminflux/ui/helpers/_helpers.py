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

import time
from datetime import datetime
from pathlib import Path
from typing import Union

import numpy as np
import pyqtgraph as pg
from pyqtgraph import AxisItem, ViewBox
from PySide6.QtCore import QPointF, QRect, QRectF
from PySide6.QtGui import QImage, QPainter, Qt
from PySide6.QtWidgets import QApplication, QFileDialog
from vispy.scene import SceneCanvas

from pyminflux.analysis import get_robust_threshold
from pyminflux.state import State


def export_plot_interactive(item, parent=None):
    """Save the content of the current scene to a PNG image."""
    if isinstance(item, ViewBox):
        view_box = item
    elif isinstance(item, AxisItem):
        view_box = item.getViewBox()
    elif isinstance(item, pg.PlotItem):
        view_box = item.getViewBox()
    else:
        return

    # Get the State
    state = State()

    # Default to the input data path
    if state.last_selected_path is not None:
        save_path = str(state.last_selected_path)
    else:
        save_path = str(Path(".").absolute())

    # Ask the user to pick a file name
    filename, ext = QFileDialog.getSaveFileName(
        parent,
        "Export current plot",
        save_path,
        "PNG images (*.png)",
    )

    # Did the user cancel?
    if filename == "":
        return

    # Make sure to add the extension
    if not filename.lower().endswith(".png"):
        filename += ".png"

    # Save the scene to file
    export_to_image(view_box, filename, dpi=state.plot_export_dpi)


def export_all_plots_interactive(items: dict, parent=None):
    """Save the content of the current scene to a PNG image."""

    if len(items) == 0:
        return

    # Get the State
    state = State()

    # Default to the input data path
    if state.last_selected_path is not None:
        save_path = str(state.last_selected_path)
    else:
        save_path = str(Path(".").absolute())

    # Ask the user to pick a file name
    filename, ext = QFileDialog.getSaveFileName(
        parent,
        "Set plots common name",
        save_path,
        "PNG images (*.png)",
    )

    # Did the user cancel?
    if filename == "":
        return

    # Turn filename into a Path object
    filename = Path(filename)

    # Test if any of the output file names already exists
    timestamp = ""
    for name, item in items.items():
        # Build the filename
        test_filename = filename.parent / f"{filename.stem}_{name}.png"
        if test_filename.exists():
            timestamp = "_" + datetime.fromtimestamp(time.time()).strftime(
                "%Y%m%d_%H%M%S"
            )
            break

    for name, item in items.items():
        if isinstance(item, ViewBox):
            view_box = item
        elif isinstance(item, AxisItem):
            view_box = item.getViewBox()
        elif isinstance(item, pg.PlotItem):
            view_box = item.getViewBox()
        else:
            return

        # Build the filename
        out_filename = str(filename.parent / f"{filename.stem}_{name}{timestamp}.png")

        # Save the scene to file
        export_to_image(view_box, out_filename, dpi=state.plot_export_dpi)


def export_to_image(item: pg.ViewBox, out_file_name: Union[Path, str], dpi: int = 600):
    """Export current QGraphicsScene to file."""

    # Get the scene from the viewBox
    if isinstance(item, pg.ViewBox):
        plot_item = item.parentItem()
        plot_widget = plot_item.getViewWidget()
    elif isinstance(item, pg.PlotWidget):
        plot_widget = item
    else:
        return

    # Get primary screen resolution
    app = QApplication.instance()
    screen = app.primaryScreen()
    logical_dpi = screen.logicalDotsPerInch()

    # Final image size at given dpi
    dpi_scaling = dpi / logical_dpi
    img_size = plot_widget.size() * dpi_scaling

    # Create the image and painter
    image = QImage(img_size, QImage.Format_ARGB32)
    painter = QPainter()

    # Begin the QPainter operation
    painter.begin(image)

    # Set the viewport and window of the QPainter
    painter.setViewport(QRect(0, 0, img_size.width(), img_size.height()))

    # Paint the scene onto the image
    plot_widget.render(painter)

    # End the QPainter operation
    painter.end()

    # Save the image to a file
    image.save(out_file_name)

    # Inform
    print(f"Plot exported to {out_file_name}.")


def export_colorbar(colorbar_widget):
    """Save the colorbar to file."""

    # Get the State
    state = State()

    # Default to the input data path
    if state.last_selected_path is not None:
        save_path = str(state.last_selected_path)
    else:
        save_path = str(Path(".").absolute())

    # Ask the user to pick a file name
    filename, ext = QFileDialog.getSaveFileName(
        None,
        "Export colorbar",
        save_path,
        "PNG images (*.png)",
    )

    # Did the user cancel?
    if filename == "":
        return

    # Make sure to add the extension
    if not filename.lower().endswith(".png"):
        filename += ".png"

    # Save the colorbar to file
    export_colorbar_to_image(
        colorbar_widget, out_file_name=filename, dpi=state.plot_export_dpi
    )


def export_colorbar_to_image(
    colorbar_widget, out_file_name: Union[Path, str], dpi: int = 600
):
    """Export the ColorBarWidget to an image file with the specified DPI."""

    # Local import to avoid circular import issues
    from pyminflux.ui.colorbar import ColorBarWidget

    # Ensure the widget is a ColorBarWidget
    if not isinstance(colorbar_widget, ColorBarWidget):
        return

    # Get the primary screen resolution
    app = QApplication.instance()
    screen = app.primaryScreen()
    logical_dpi = screen.logicalDotsPerInch()

    # Final image size at the given DPI
    dpi_scaling = dpi / logical_dpi
    img_size = colorbar_widget.size() * dpi_scaling

    # Create the image and painter
    image = QImage(img_size, QImage.Format_ARGB32)
    painter = QPainter()

    # Begin the QPainter operation
    painter.begin(image)

    # Set the viewport and window of the QPainter
    painter.setViewport(QRect(0, 0, img_size.width(), img_size.height()))

    # Paint the GraphicsLayoutWidget onto the image
    colorbar_widget.graphWidget.render(painter)

    # End the QPainter operation
    painter.end()

    # Save the image to a file
    image.save(out_file_name)

    # Inform the user
    print(f"ColorBar exported to {out_file_name}.")


def export_vispy_plot(canvas):
    """Save the VisPy plot to file."""

    # Get the State
    state = State()

    # Default to the input data path
    if state.last_selected_path is not None:
        save_path = str(state.last_selected_path)
    else:
        save_path = str(Path(".").absolute())

    # Ask the user to pick a file name
    filename, ext = QFileDialog.getSaveFileName(
        None,
        "Export plot",
        save_path,
        "PNG images (*.png)",
    )

    # Did the user cancel?
    if filename == "":
        return

    # Make sure to add the extension
    if not filename.lower().endswith(".png"):
        filename += ".png"

    # Save the colorbar to file
    export_vispy_plot_to_image(
        canvas, out_file_name=filename, dpi=state.plot_export_dpi
    )


def export_vispy_plot_to_image(
    canvas: SceneCanvas, out_file_name: Union[Path, str], dpi: int = 300
):
    """Export a VisPy canvas to an image file with the specified DPI."""

    if not isinstance(canvas, SceneCanvas):
        return

    # Get the primary screen resolution
    app = QApplication.instance()
    screen = app.primaryScreen()
    logical_dpi = screen.logicalDotsPerInch()

    # Final image size at the given DPI
    dpi_scaling = dpi / logical_dpi

    # Get current canvas size
    original_canvas_size = canvas.size

    # Final image size at given dpi
    render_width = int(original_canvas_size[0] * dpi_scaling)
    render_height = int(original_canvas_size[1] * dpi_scaling)

    # Resize the canvas viewport to match the desired size: importantly, we let
    # the canvas resize manage the viewport update on its own.
    canvas.size = (render_width, render_height)

    # Grab the scene rendered at the desired final size
    image = canvas.native.grabFramebuffer()

    # Reset the canvas to the original size
    canvas.size = original_canvas_size

    # Save the image with the specified filename
    image.save(out_file_name)

    # Inform
    print(f"3D plot exported to {out_file_name}.")


def add_median_line(
    plot: pg.PlotWidget,
    values: np.ndarray,
    label_pos: float = 0.95,
    unit: str = "nm",
    add_iqr: bool = True,
):
    """Add median line to plot (with median +/- mad as label)."""
    _, _, med, mad = get_robust_threshold(values, 0.0)
    unit_str = f" {unit}" if unit != "" else ""
    line = pg.InfiniteLine(
        pos=med,
        movable=False,
        angle=90,
        pen={"color": (200, 50, 50), "width": 3},
        label=f"median={med:.2f} ± {mad:.2f}{unit_str}",
        labelOpts={
            "position": label_pos,
            "color": (200, 50, 50),
            "fill": (200, 50, 50, 10),
            "movable": True,
        },
    )
    plot.addItem(line)
    if add_iqr:
        iqr = np.percentile(values, q=(25, 75))
        fp_line = pg.InfiniteLine(
            pos=iqr[0],
            movable=False,
            angle=90,
            pen={"color": (200, 50, 50), "width": 1, "style": Qt.DashLine},
            label="",
        )
        plot.addItem(fp_line)
        tp_line = pg.InfiniteLine(
            pos=iqr[1],
            movable=False,
            angle=90,
            pen={"color": (200, 50, 50), "width": 1, "style": Qt.DashLine},
            label="",
        )
        plot.addItem(tp_line)


class BottomLeftAnchoredScaleBar(pg.ScaleBar):
    """A ScaleBar that stays anchored in the bottom left corner of the view and resizes
    and repositions itself according to panning and zoom level."""

    def __init__(
        self,
        viewBox,
        size: int = None,
        auto_resize: bool = True,
        width: int = 5,
        brush=None,
        pen=None,
        suffix: str = "nm",
        offset: tuple = (20, -20),
    ):
        """Constructor."""
        super().__init__(
            size=size, width=width, brush=brush, pen=pen, suffix=suffix, offset=offset
        )

        # Store a reference to the ViewBox
        self.viewBox = viewBox

        # Enabled flag
        self._is_enabled = True

        # Autoresize flag
        self._auto_resize: bool = auto_resize

        # Current size
        self.currentSize = size
        self.initialSizePixels = None
        self.scaleBarLabel = f"{width} nm"
        self.ratio_step = 2.0

        # Keep a margin from the edge of the view when zooming in
        self.margin = 10.0

        # Set the ViewBox as parent item
        self.setParentItem(viewBox)

        # Offset from the bottom-left corner in pixels
        self.originalOffset = offset

        # Initially anchor the scale bar
        self.anchor(itemPos=(0, 1), parentPos=(0, 1), offset=self.originalOffset)

    def setEnabled(self, b: bool):
        """Enables/disables to scale bar.

        Important: disable it if the coordinate system of the ViewBox changes.
        """
        self._is_enabled = b

    def _calculateScaleBarRatio(self) -> float:
        """Calculate the ratio of the current size of the bar with the size at the
        beginning or after a resizing due to the zoom level passing a 2x or 0.5x threshold.
        """
        if not self._is_enabled:
            return 0

        view = self.parentItem()
        if view is None:
            return 0

        # Get current scal bar size in pixels
        currentSize = self._currentSizeInPixels()

        # Return the ratio to the initial scale bar size
        return currentSize / self.initialSizePixels

    def _adjustScaleBarSize(self):
        """Adjust the scale bar size based on the ratio calculated in `_calculateScaleBarRatio()`."""
        if not self._is_enabled:
            return

        if not self._auto_resize:
            return

        ratio = self._calculateScaleBarRatio()
        if ratio == 0:
            return

        # Halve or double the length of the scale bar depending on zoom level
        if ratio >= self.ratio_step:
            self.currentSize = int(self.currentSize / self.ratio_step)
            self.size = self.currentSize
            self.scaleBarLabel = f"{self.currentSize} nm"
            self.text.setText(self.scaleBarLabel)
            self.initialSizePixels = self._currentSizeInPixels()
        elif ratio <= 0.5:
            self.currentSize = int(self.currentSize * self.ratio_step)
            self.size = self.currentSize
            self.scaleBarLabel = f"{self.currentSize} nm"
            self.text.setText(self.scaleBarLabel)
            self.initialSizePixels = self._currentSizeInPixels()

    def _storeInitialSizePixels(self):
        """Store the initial size of the scale bar in pixels."""
        if not self._is_enabled:
            return 0

        self.initialSizePixels = self._currentSizeInPixels()

    def _currentSizeInPixels(self):
        """Return current size of the scale bar in pixels."""
        if not self._is_enabled:
            return 0

        view = self.parentItem()
        if view is None:
            return 0

        # Get the bounding rect of the scale bar
        rect = self.bar.boundingRect()

        # Map the corners of the rectangle to view coordinates
        topLeft = view.mapToScene(self.bar.mapToScene(rect.topLeft()))
        bottomRight = view.mapToScene(self.bar.mapToScene(rect.bottomRight()))

        # Calculate the width in pixels
        return abs(bottomRight.x() - topLeft.x())

    def setSize(self, size):
        """Set new scale bar size."""
        self.size = int(size)
        self.scaleBarLabel = f"{self.size} nm"
        self.text.setText(self.scaleBarLabel)
        self.updateBar()

    def updateBar(self):
        """Update the scale bar in size and position on the view."""
        if not self._is_enabled:
            return

        view = self.parentItem()
        if view is None:
            return

        # First, adjust the scale bar size depending on zoom ratio
        if self._auto_resize and self.initialSizePixels is not None:
            self._adjustScaleBarSize()

        # Calculate the width of the scale bar based on its size in the current view's coordinates
        p1 = view.mapFromViewToItem(self, QPointF(0, 0))
        p2 = view.mapFromViewToItem(self, QPointF(self.size, 0))
        w = (p2 - p1).x()

        # Determine the visible left edge in the item's coordinate system
        visibleLeftEdge = view.mapFromViewToItem(
            self, QPointF(view.viewRect().left(), 0)
        ).x()

        # The corrected logic for determining the initial and adjusted positions of the scale bar
        # This ensures the left edge of the scale bar aligns with the specified offset from the visible left edge
        initialLeftEdge = visibleLeftEdge + self.offset[0] - w

        # Check if the left edge of the scale bar, when considering the offset, is out of the visible area
        if initialLeftEdge <= visibleLeftEdge:
            # If out of view, adjust the scale bar's position to align its left edge with the visible left edge
            adjustedLeftEdge = visibleLeftEdge + self.margin
            self.bar.setRect(QRectF(adjustedLeftEdge, 0, w, self._width))
            self.text.setPos(adjustedLeftEdge + w / 2.0, 0)
        else:
            # Otherwise, position the scale bar using the corrected initial position
            self.bar.setRect(QRectF(initialLeftEdge, 0, w, self._width))
            self.text.setPos(initialLeftEdge + w / 2.0, 0)

        # Ensure the initial scale bar size in pixels has been stored.
        if self.initialSizePixels is None:
            self._storeInitialSizePixels()
