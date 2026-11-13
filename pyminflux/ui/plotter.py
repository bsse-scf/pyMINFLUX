#  Copyright (c) 2022 - 2026 D-BSSE, ETH Zurich.
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
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import pyqtgraph as pg
from pyqtgraph import (
    ROI,
    ImageItem,
    PlotCurveItem,
    PlotWidget,
    TextItem,
    ViewBox,
    mkPen,
)
from PySide6 import QtCore
from PySide6.QtCore import QPoint, QPointF, Qt, Signal
from PySide6.QtGui import QAction, QPainter, QPainterPath, QPolygonF
from PySide6.QtWidgets import QDialog, QFileDialog, QInputDialog, QMenu

from pyminflux.ui.state import State

from ..reader import MSRReader
from .colors import ColorsToBrushes
from .custom_dialogs import TreeDialog
from .helpers import BottomLeftAnchoredScaleBar, export_plot_interactive


class LassoROI(ROI):
    """Freehand polygon ROI.

    Like the rectangular selection ROI, it can be dragged and is highlighted on
    hover (anywhere inside the polygon); it cannot be resized or rotated.
    Vertices are stored relative to the ROI position, so dragging just moves it.
    """

    def __init__(self, start, **kwargs):
        super().__init__(
            pos=start, size=(0, 0), resizable=False, rotatable=False, **kwargs
        )
        self._vertices = [QPointF(0.0, 0.0)]
        self._path = QPainterPath()

    def add_point(self, point):
        """Append a vertex (in data coordinates) to the polygon."""
        self._vertices.append(
            QPointF(point.x() - self.pos().x(), point.y() - self.pos().y())
        )
        path = QPainterPath()
        path.addPolygon(QPolygonF(self._vertices))
        path.closeSubpath()
        self.prepareGeometryChange()
        self._path = path
        self.update()

    def polygon(self) -> np.ndarray:
        """Return the (N, 2) polygon vertices in data coordinates."""
        offset = np.array([self.pos().x(), self.pos().y()])
        local = np.array([(v.x(), v.y()) for v in self._vertices], dtype=float)
        return local + offset

    def boundingRect(self):
        return self._path.boundingRect()

    def shape(self):
        return self._path

    def paint(self, p, opt, widget):
        p.setRenderHint(QPainter.RenderHint.Antialiasing, self._antialias)
        p.setPen(self.currentPen)
        p.drawPath(self._path)


class Plotter(PlotWidget):
    # Signals
    locations_selected = Signal(list)
    # (x_param, y_param, polygon): polygon is an (N, 2) array of vertices in
    # data coordinates; rectangular selections are emitted as 4-vertex polygons
    locations_selected_by_polygon = Signal(str, str, object)
    crop_region_selected = Signal(str, str, object)
    added_confocal_image = Signal()
    removed_confocal_image = Signal()

    def __init__(self):
        super().__init__()
        self.setBackground("k")
        self.brush = pg.mkBrush(255, 255, 255, 128)
        self.pen = pg.mkPen(None)
        self.remove_points()
        self.hideAxis("bottom")
        self.hideAxis("left")
        self.show()

        # Disable default context menu
        self.setMenuEnabled(False)

        # Set aspect ratio to 1.0 locked
        view_box = self.getPlotItem().getViewBox()
        view_box.setAspectLocked(lock=True, ratio=1.0)

        # Keep a reference to the singleton State class
        self.state = State()

        # Keep track of the mapping between unique identifiers or fluorophore identifiers and cached QBrushes
        self._id_to_brush = None
        self._fid_to_brush = None

        # Keep a reference to the scatter plot/line plot and image item objects
        self.scatter_plot = None
        self.line_plot = None
        self.image_item = None

        # Selection of localizations: at most one at a time, either a
        # rectangular ROI or a freehand LassoROI (both draggable)
        self._selection = None
        self._selection_kind = None  # None, "rectangle" or "lasso"
        self._selection_is_being_drawn = False
        self._roi_start_point = None
        self._lasso_last_scene_pos = None

        # Line for distance measurements
        self.line = None
        self.line_text = None
        self._line_start_point = None
        self._line_is_being_drawn = False

        # Keep track of last plot
        self._last_x_param = None
        self._last_y_param = None

        # Keep track of the ScaleBar
        self.scale_bar = None

        # Remember previous parameters to avoid redrawing when not needed
        self.last_plot_parameters = {
            "color_column": None,
            "tid": None,
            "fid": None,
            "depth": None,
            "time": None,
            "brushes": None,
        }

    def enableAutoRange(self, enable: bool):
        """Enable/disable axes auto-range."""
        self.getViewBox().enableAutoRange(axis=ViewBox.XYAxes, enable=enable)

    def mousePressEvent(self, ev):
        """Override mouse press event."""

        # Is the user trying to initiate drawing an ROI?
        if (
            self.scatter_plot is not None
            and ev.button() == Qt.MouseButton.LeftButton
            and ev.modifiers() == QtCore.Qt.ShiftModifier
        ):
            # Replace the current selection (if any)
            self._remove_selection()

            # Create ROI and keep track of position
            self._roi_start_point = (
                self.getPlotItem().getViewBox().mapSceneToView(ev.position())
            )
            roi = ROI(
                pos=self._roi_start_point,
                size=(0, 0),
                resizable=False,
                rotatable=False,
                pen=(255, 0, 0),
            )
            self._add_selection(roi, "rectangle")

            # Accept the event
            ev.accept()

        elif (
            self.scatter_plot is not None
            and ev.button() == Qt.MouseButton.LeftButton
            and ev.modifiers() == QtCore.Qt.AltModifier
        ):
            # Is the user trying to initiate drawing a lasso?

            # Replace the current selection (if any)
            self._remove_selection()

            start = self.getPlotItem().getViewBox().mapSceneToView(ev.position())
            self._lasso_last_scene_pos = ev.position()
            self._add_selection(LassoROI(start, pen=(255, 0, 0)), "lasso")

            # Accept the event
            ev.accept()

        elif (
            self.scatter_plot is not None
            and ev.button() == Qt.MouseButton.LeftButton
            and ev.modifiers() == QtCore.Qt.ControlModifier
            and self.state.x_param in ("x", "y", "z")
            and self.state.y_param in ("x", "y", "z")
        ):
            # Is the user trying to initiate drawing a line?

            # Remove previous line if it exists
            if self.line is not None:
                self.removeItem(self.line)
                self.line.deleteLater()
                self.line = None

            if self.line_text is not None:
                self.removeItem(self.line_text)
                self.line_text.deleteLater()
                self.line_text = None

            # Create ROI and keep track of position
            self._line_is_being_drawn = True
            self._line_start_point = (
                self.getPlotItem().getViewBox().mapSceneToView(ev.position())
            )
            self.line = PlotCurveItem(
                x=[self._line_start_point.x(), self._line_start_point.x()],
                y=[self._line_start_point.y(), self._line_start_point.y()],
                pen=mkPen(color=(255, 0, 0), width=2),
            )
            self.addItem(self.line)
            self.line.show()

            # Accept the event
            ev.accept()

        else:
            # Is the user trying to open a context menu?
            if (
                self.scatter_plot is not None
                and ev.button() == Qt.MouseButton.RightButton
            ):
                menu = QMenu()
                if self._selection is not None:
                    crop_data_action = QAction("Crop data")
                    crop_data_action.triggered.connect(self.crop_data_by_selection)
                    menu.addAction(crop_data_action)
                    menu.addSeparator()
                set_scalebar_size_action = QAction("Set scale bar size")
                set_scalebar_size_action.triggered.connect(self.set_scalebar_size)
                menu.addAction(set_scalebar_size_action)
                if self.image_item is None:
                    add_confocal_image_action = QAction("Add confocal image")
                    add_confocal_image_action.triggered.connect(self.add_confocal_image)
                    menu.addAction(add_confocal_image_action)
                else:
                    replace_confocal_image_action = QAction("Replace confocal image")
                    replace_confocal_image_action.triggered.connect(
                        self.replace_confocal_image
                    )
                    menu.addAction(replace_confocal_image_action)
                    remove_confocal_image_action = QAction("Remove confocal image")
                    remove_confocal_image_action.triggered.connect(
                        lambda _: self.remove_confocal_image(redraw=True)
                    )
                    menu.addAction(remove_confocal_image_action)
                export_action = QAction("Export plot")
                export_action.triggered.connect(
                    lambda checked: export_plot_interactive(self.getPlotItem())
                )
                menu.addAction(export_action)
                pos = ev.screenPos()
                menu.exec(QPoint(int(pos.x()), int(pos.y())))
                ev.accept()
            else:
                # Call the parent method
                ev.ignore()
                super().mousePressEvent(ev)

    def mouseMoveEvent(self, ev):
        # Is the user drawing an ROI?
        if (
            self.scatter_plot is not None
            and ev.buttons() == Qt.MouseButton.LeftButton
            and self._selection_is_being_drawn
            and self._selection_kind == "rectangle"
        ):
            # Resize the ROI
            current_point = (
                self.getPlotItem().getViewBox().mapSceneToView(ev.position())
            )
            self._selection.setSize(current_point - self._roi_start_point)

            # Accept the event
            ev.accept()

        elif (
            self.scatter_plot is not None
            and ev.buttons() == Qt.MouseButton.LeftButton
            and self.line is not None
            and self._line_is_being_drawn
        ):
            # Is the user drawing a line?

            # Resize the ROI
            current_point = (
                self.getPlotItem().getViewBox().mapSceneToView(ev.position())
            )
            self.line.setData(
                x=[self._line_start_point.x(), current_point.x()],
                y=[self._line_start_point.y(), current_point.y()],
            )

            # Accept the event
            ev.accept()

        elif (
            self.scatter_plot is not None
            and ev.buttons() == Qt.MouseButton.LeftButton
            and self._selection_is_being_drawn
            and self._selection_kind == "lasso"
        ):
            # Is the user drawing a lasso? Append the point (if the cursor moved
            # far enough to matter, to keep the polygon small)
            pos = ev.position()
            delta = pos - self._lasso_last_scene_pos
            if abs(delta.x()) + abs(delta.y()) >= 2:
                self._lasso_last_scene_pos = pos
                self._selection.add_point(
                    self.getPlotItem().getViewBox().mapSceneToView(pos)
                )

            # Accept the event
            ev.accept()
        else:
            # Call the parent method
            ev.ignore()
            super().mouseMoveEvent(ev)

    def mouseReleaseEvent(self, ev):
        if self.scatter_plot is not None and ev.button() == Qt.MouseButton.LeftButton:
            if self._selection_is_being_drawn:
                self._selection_is_being_drawn = False
                self._roi_start_point = None
                self._lasso_last_scene_pos = None

                # Update the DataViewer with current selection (a degenerate
                # selection selects nothing)
                polygon = self._selection_polygon()
                self.locations_selected_by_polygon.emit(
                    self.state.x_param, self.state.y_param, polygon
                )

                # Discard degenerate selections (e.g., a click without drag)
                if self._is_degenerate(polygon):
                    self._remove_selection()

                # Accept the event
                ev.accept()

            elif self._line_is_being_drawn:
                if self.line:
                    # Display the measurement
                    x_data, y_data = self.line.getData()
                    if (
                        x_data is None
                        or len(x_data) < 2
                        or y_data is None
                        or len(y_data) < 2
                    ):  # Check if data is incomplete
                        return

                    center = np.array(
                        [0.5 * (x_data[0] + x_data[1]), 0.5 * (y_data[0] + y_data[1])]
                    )
                    delta_y = y_data[1] - y_data[0]
                    delta_x = x_data[1] - x_data[0]
                    v = np.array([-1.0 * delta_y, delta_x])
                    norm = np.linalg.norm(v)

                    if norm >= 1e-4:
                        v_norm = v / norm
                        length = np.sqrt(delta_x**2 + delta_y**2)
                        pos = center + 1.0 * v_norm
                        clr = (
                            (255, 255, 0)
                            if self.state.color_column is None
                            else (255, 255, 255)
                        )
                        self.line_text = TextItem(text=f"{length:.2f} nm", color=clr)
                        self.line_text.setPos(pos[0], pos[1])
                        self.addItem(self.line_text)
                    else:
                        self.removeItem(self.line)
                        self.line.deleteLater()
                        self.line = None

                    # Reset flags
                    self._line_start_point = None
                    self._line_is_being_drawn = False

                    # Accept the event
                    ev.accept()
                else:
                    # If line is None, safely ignore the operation
                    ev.ignore()

            else:
                # Call the parent method if no conditions are met
                super().mouseReleaseEvent(ev)
        else:
            # Properly ignore the event if conditions are not met
            ev.ignore()

    def reset(self):
        # Forget last plot
        self._last_x_param = None
        self._last_y_param = None
        self.remove_points()

        # Clear color caches
        self._id_to_brush = None
        self._fid_to_brush = None

        # Remove images
        self.remove_confocal_image(redraw=False)
        self.state.has_confocal = False

        # Forget last plot parameters
        self.last_plot_parameters = {
            "color_column": None,
            "tid": None,
            "fid": None,
            "depth": None,
            "time": None,
            "brushes": None,
        }

    def remove_points(self):
        self.setBackground("k")
        self.clear()

        # The selection item was removed from the plot by clear():
        # drop the stale reference
        self._forget_selection()

    def plot_parameters(
        self,
        x: pd.Series,
        y: pd.Series,
        x_param: str,
        y_param: str,
        tid: pd.Series,
        color_values: Optional[pd.Series] = None,
        color_column: Optional[str] = None,
        show_track_connectors: bool = False,
    ):
        """Plot localizations and other parameters in a 2D scatter plot.

        Parameters
        ----------

        x: pd.Series
            x coordinates to plot. x must be a Pandas Series.
        y: pd.Series
            y coordinates to plot. y must be a Pandas Series.
        x_param: str
            Name of the x parameter.
        y_param: str
            Name of the y parameter.
        tid: pd.Series
            Traces IDs for each of the (x, y) pairs. tid must be a Pandas Series.
        color_values: Optional[pd.Series] = None
            Values from the selected dataframe color column.
        color_column: Optional[str] = None
            Name of the selected dataframe color column.
        show_track_connectors: bool = False
            Whether to connect consecutive points with the same `tid` (spatial
            parameters only). Set by the active workflow.
        """

        # Make sure our inputs are Pandas Series
        assert x is not None and type(x) == pd.Series, "`x` must be a Pandas Series."
        assert y is not None and type(y) == pd.Series, "`y` must be a Pandas Series."
        assert (
            tid is not None and type(tid) == pd.Series
        ), "`tid` must be a Pandas Series."

        if color_values is not None:
            assert (
                type(color_values) == pd.Series
            ), "`color_values` must be a Pandas Series."

        # If we have an image, make sure to draw it first (but only if
        # x_param is "x" and y_param is "y"
        if self.state.show_confocal:
            if self.image_item is not None and x_param == "x" and y_param == "y":
                self.addItem(self.image_item)

        if self.state.show_localizations:
            # Do we need to recreate the colors?
            if self._need_to_recreate_colors(
                color_column=color_column,
                color_values=color_values,
                tid=tid,
            ):
                # Recreate colors
                brushes = ColorsToBrushes().get_brushes_for_values(color_values)
                self.last_plot_parameters["brushes"] = brushes
            else:
                brushes = self.last_plot_parameters["brushes"]

            # Create the scatter plot
            self.scatter_plot = pg.ScatterPlotItem(
                x=x,
                y=y,
                data=x.index,
                size=5,
                pen=None,
                brush=brushes,
                hoverable=True,
                hoverSymbol="s",
                hoverSize=5,
                hoverPen=pg.mkPen("w", width=2),
                hoverBrush=None,
            )
            self.scatter_plot.sigClicked.connect(self.clicked)
            self.addItem(self.scatter_plot)

            # If requested, add the connecting line_plot (for spatial parameters only)
            if show_track_connectors and (
                x_param in ["x", "y", "z"] and y_param in ["x", "y", "z"]
            ):
                # Add the line_plot within TIDs
                line_indices = np.concatenate(
                    (np.diff(tid.to_numpy()) == 0, [1])
                ).astype(np.int32)
                self.line_plot = pg.PlotDataItem(
                    x.to_numpy(),
                    y.to_numpy(),
                    connect=line_indices,
                    pen=mkPen(cosmetic=True, width=0.5, color="w"),
                    symbol=None,
                    brush=None,
                )
                self.addItem(self.line_plot)

            # Flip the vertical axis (imaging convention) only when it shows y
            self.getViewBox().invertY(y_param == "y")

            self.setLabel("bottom", text=x_param)
            self.setLabel("left", text=y_param)
            self.showAxis("bottom")
            self.showAxis("left")
            self.setBackground("k")

            # Fix aspect ratio (if needed)
            if (self._last_x_param is None or self._last_x_param != x_param) or (
                self._last_y_param is None or self._last_y_param != y_param
            ):
                # Update range
                self.getViewBox().enableAutoRange(axis=ViewBox.XYAxes, enable=True)

                if x_param in ["x", "y", "z"] and y_param in ["x", "y", "z"]:
                    # Set fixed aspect ratio
                    aspect_ratio = 1.0

                    # Add scale bar
                    if self.scale_bar is None:
                        self.scale_bar = BottomLeftAnchoredScaleBar(
                            size=self.state.scale_bar_size,
                            auto_resize=False,
                            viewBox=self.getViewBox(),
                            brush="w",
                            pen=None,
                            suffix="nm",
                            offset=(50, -15),
                        )
                    self.scale_bar.setEnabled(True)
                    self.scale_bar.setVisible(True)

                else:
                    # Calculate aspect ratio
                    x_min, x_max = np.nanpercentile(x, (1, 99))
                    x_scale = x_max - x_min
                    y_min, y_max = np.nanpercentile(y, (1, 99))
                    y_scale = y_max - y_min
                    aspect_ratio = y_scale / x_scale
                    if np.isnan(aspect_ratio):
                        aspect_ratio = 1.0

                    if self.scale_bar is not None:
                        self.scale_bar.setEnabled(False)
                        self.scale_bar.setVisible(False)

                self.getPlotItem().getViewBox().setAspectLocked(
                    lock=True, ratio=aspect_ratio
                )

        # Update last plotted parameters
        self._last_x_param = x_param
        self._last_y_param = y_param

    def _need_to_recreate_colors(
        self,
        color_column: Optional[str],
        color_values: Optional[pd.Series],
        tid: pd.Series,
    ):
        """Check if the colors need to be recreated (and store state)."""

        assert type(tid) == pd.Series, "`tid` must be a Pandas Series."
        if color_values is not None:
            assert (
                type(color_values) == pd.Series
            ), "`color_values` must be a Pandas Series."

        recreate_brushes = False
        if self.last_plot_parameters["color_column"] is None:
            # Fist time
            recreate_brushes = True
        else:
            # There were plots already
            if self.last_plot_parameters["color_column"] != color_column:
                # If the color column changed, we need to recreate the colors
                recreate_brushes = True

            else:
                if color_values is None:
                    if (
                        self.last_plot_parameters["tid"] is None
                        or len(tid) != len(self.last_plot_parameters["tid"])
                        or np.any(tid.index != self.last_plot_parameters["tid"].index)
                        or np.any(tid.values != self.last_plot_parameters["tid"].values)
                    ):
                        recreate_brushes = True
                else:
                    if (
                        self.last_plot_parameters["depth"] is None
                        or len(color_values) != len(self.last_plot_parameters["depth"])
                        or np.any(
                            color_values.index
                            != self.last_plot_parameters["depth"].index
                        )
                        or np.any(
                            color_values.values
                            != self.last_plot_parameters["depth"].values
                        )
                    ):
                        recreate_brushes = True

        # Remember the new parameters
        self.last_plot_parameters["color_column"] = color_column
        self.last_plot_parameters["tid"] = tid
        self.last_plot_parameters["fid"] = None
        self.last_plot_parameters["depth"] = color_values
        self.last_plot_parameters["time"] = None

        # Return
        return recreate_brushes

    def crop_data_by_selection(self, item):
        """Crop the data to the current selection (rectangle or lasso)."""

        if self._selection is None:
            return

        polygon = self._selection_polygon()
        self.crop_region_selected.emit(self.state.x_param, self.state.y_param, polygon)

        # Delete the selection after it has been used to crop
        self._remove_selection()

    def roi_moved(self):
        """Inform that the selection of localizations may have changed after the ROI was moved."""

        # If the selection is being drawn now, do nothing
        if self._selection is None or self._selection_is_being_drawn:
            return

        # Update the DataViewer with current selection
        self.locations_selected_by_polygon.emit(
            self.state.x_param, self.state.y_param, self._selection_polygon()
        )

    def clicked(self, _, points):
        """Emit 'signal_selected_locations' when points are selected in the plot."""
        self.locations_selected.emit(points)

        # Remove the selection if it exists
        self._remove_selection()

    def _add_selection(self, roi: ROI, kind: str):
        """Add `roi` to the plot as the current (being drawn) selection of type `kind`."""
        self._selection = roi
        self._selection_kind = kind
        self._selection_is_being_drawn = True

        # Right-clickable (for the context menu), draggable, highlighted on hover
        roi.setAcceptedMouseButtons(Qt.MouseButton.RightButton)
        self.addItem(roi)
        roi.show()

        # Make sure to react to ROI shifts
        roi.sigRegionChangeFinished.connect(self.roi_moved)

    def _remove_selection(self):
        """Remove the current selection from the plot (if it exists)."""
        if self._selection is not None:
            self.removeItem(self._selection)
            self._selection.deleteLater()
        self._forget_selection()

    def _forget_selection(self):
        """Reset the selection state without touching the plot items."""
        self._selection = None
        self._selection_kind = None
        self._selection_is_being_drawn = False
        self._roi_start_point = None
        self._lasso_last_scene_pos = None

    def _selection_polygon(self) -> np.ndarray:
        """Return the current selection as an (N, 2) array of vertices in data coordinates."""
        if self._selection_kind == "rectangle":
            x0, y0 = self._selection.pos()
            w, h = self._selection.size()
            return np.array(
                [[x0, y0], [x0 + w, y0], [x0 + w, y0 + h], [x0, y0 + h]], dtype=float
            )
        if self._selection_kind == "lasso":
            return self._selection.polygon()
        return np.empty((0, 2), dtype=float)

    @staticmethod
    def _is_degenerate(polygon: np.ndarray) -> bool:
        """Whether the polygon cannot contain any point (too few vertices or no extent)."""
        if len(polygon) < 3:
            return True
        extent = polygon.max(axis=0) - polygon.min(axis=0)
        return bool(np.any(extent < 1e-4))

    def set_scalebar_size(self):
        """Ask the user to specify the size of the scalebar."""
        size, ok = QInputDialog.getInt(
            self,
            "Scale bar",
            "Set scale bar length (nm):",
            self.state.scale_bar_size,
            minValue=1,
            maxValue=10000,
        )
        if ok:
            # Set the new value
            self.state.scale_bar_size = size

            # Update the bar
            self.scale_bar.setSize(self.state.scale_bar_size)

    def add_confocal_image(self):
        """Ask the user to pick an MSR file and choose the confocal image to add to the plot."""

        # Default path
        if self.state.last_selected_path is not None:
            load_path = str(self.state.last_selected_path)
        else:
            load_path = str(Path(".").absolute())

        # Ask the user to pick an MSR file
        res = QFileDialog.getOpenFileName(
            self,
            "Load MSR file",
            load_path,
            "All Supported Files (*.msr);;MSR file (*.pmx);;",
        )
        filename = res[0]
        if filename == "":
            return

        # Open the file
        msr_reader = MSRReader(filename)

        # Scan it
        msr_reader.scan()

        # Get the image info
        image_info = msr_reader.get_image_info_dict()

        # Build the options list
        options = {}

        for key in image_info:
            # Build the header
            header = f"{key} - {image_info[key]['metadata']}"

            # Add the detectors
            detectors = []
            for detector in image_info[key]["detectors"]:
                detectors.append(
                    {
                        f"{detector['detector']} - {detector['name']}": detector,
                    }
                )

            # Add current image and detectors
            options[header] = detectors

        if len(options) == 0:
            print("No images found.")
            return

        # Create and show the dialog
        dialog = TreeDialog(options=options, title="Select image")
        if dialog.exec_() == QDialog.Accepted:
            selected_option = dialog.selected_item_data
        else:
            return

        # Load the image
        image = msr_reader.get_data(selected_option["index"])
        if image is None:
            print("Could not open confocal image.")
            return

        # Create an ImageItem to add to the plot
        if self.image_item is None:
            self.image_item = pg.ImageItem(image)

        # Calculate the offsets in nm
        offsets_nm = np.array(selected_option["physical_offsets"]) * 1e9

        # Extract the image physical size in nm
        physical_size = np.array(selected_option["physical_lengths"]) * 1e9

        # If a previous image exists, remove it and delete it
        self.remove_confocal_image(redraw=False)

        # Add the new image
        self.image_item = ImageItem(image)

        # Shift the image by the specified offsets
        self.image_item.setRect(
            QtCore.QRectF(
                float(offsets_nm[0]),
                float(offsets_nm[1]),
                float(physical_size[0]),
                float(physical_size[1]),
            )
        )

        # Enable the has_confocal state
        self.state.has_confocal = True

        # Enable showing the confocal image
        self.state.show_confocal = True

        # Inform that the confocal image was added
        self.added_confocal_image.emit()

    def replace_confocal_image(self):
        """Replace confocal image."""

        # Set a new one (the previous one will be automatically removed)
        self.add_confocal_image()

    def remove_confocal_image(self, redraw: bool = False):
        """Remove confocal image."""

        # If a previous image exists, remove it and delete it
        if self.image_item is not None:
            self.removeItem(self.image_item)
            self.image_item.deleteLater()
            self.image_item = None

        # Flag that the confocal image is not set
        self.state.has_confocal = False

        if redraw:
            # Inform that the confocal image was removed
            self.removed_confocal_image.emit()
