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
from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QDialog, QFileDialog, QInputDialog, QMenu

from pyminflux.ui.state import State

from ..reader import MSRReader
from .colors import ColorCode, ColorsToBrushes
from .custom_dialogs import TreeDialog
from .helpers import BottomLeftAnchoredScaleBar, export_plot_interactive


def compute_measurement_geometry(points: np.ndarray):
    """Compute PCA-based measurement geometry for a set of 2D points."""

    if points is None or len(points) < 3:
        return None

    points = np.asarray(points, dtype=float)
    center = points.mean(axis=0)
    centered = points - center

    _, _, vh = np.linalg.svd(centered, full_matrices=False)
    axis = vh[0]
    perp = np.array([-axis[1], axis[0]])

    along = centered @ axis
    orth = centered @ perp

    along_min = float(np.min(along))
    along_max = float(np.max(along))
    orth_min = float(np.min(orth))
    orth_max = float(np.max(orth))

    abs_orth = np.abs(orth)
    mean_thickness = float(2.0 * np.mean(abs_orth))
    median_thickness = float(2.0 * np.median(abs_orth))
    p95_thickness = float(2.0 * np.percentile(abs_orth, 95))

    box_local = np.array(
        [
            [along_min, orth_min],
            [along_max, orth_min],
            [along_max, orth_max],
            [along_min, orth_max],
            [along_min, orth_min],
        ],
        dtype=float,
    )
    box_xy = center + box_local[:, 0:1] * axis + box_local[:, 1:2] * perp

    mid_orth = 0.5 * (orth_min + orth_max)
    line_local = np.array(
        [[along_min, mid_orth], [along_max, mid_orth]],
        dtype=float,
    )
    line_xy = center + line_local[:, 0:1] * axis + line_local[:, 1:2] * perp

    return {
        "points": points,
        "center": center,
        "axis": axis,
        "perp": perp,
        "along_min": along_min,
        "along_max": along_max,
        "orth_min": orth_min,
        "orth_max": orth_max,
        "mean_thickness": mean_thickness,
        "median_thickness": median_thickness,
        "p95_thickness": p95_thickness,
        "max_negative_offset": float(-orth_min),
        "max_positive_offset": float(orth_max),
        "box_xy": box_xy,
        "line_xy": line_xy,
    }


class Plotter(PlotWidget):
    # Signals
    locations_selected = Signal(list)
    locations_selected_by_range = Signal(str, str, tuple, tuple)
    crop_region_selected = Signal(str, str, tuple, tuple)
    added_confocal_image = Signal()
    removed_confocal_image = Signal()

    def __init__(self):
        super().__init__()
        self.setBackground("k")
        self.brush = pg.mkBrush(255, 255, 255, 128)
        self.pen = pg.mkPen(None)

        # Initialize state used by remove_points() before the first reset call.
        self._plot_x_data = None
        self._plot_y_data = None
        self._measurements = []
        self._measurement_counter = 0
        self._selected_measurement_id = None
        self._measurement_roi = None
        self._measurement_start_point = None
        self._measurement_is_being_drawn = False
        self.ROI = None
        self.line = None
        self.line_text = None
        self._roi_start_point = None
        self._roi_is_being_drawn = False
        self._line_start_point = None
        self._line_is_being_drawn = False

        self.remove_points()
        self.hideAxis("bottom")
        self.hideAxis("left")
        self.show()

        # Disable default context menu
        self.setMenuEnabled(False)

        # Set aspect ratio to 1.0 locked
        view_box = self.getPlotItem().getViewBox()
        view_box.setAspectLocked(lock=True, ratio=1.0)
        view_box.invertY(True)

        # Keep a reference to the singleton State class
        self.state = State()

        # Keep track of the mapping between unique identifiers or fluorophore identifiers and cached QBrushes
        self._id_to_brush = None
        self._fid_to_brush = None

        # Keep a reference to the scatter plot/line plot and image item objects
        self.scatter_plot = None
        self.line_plot = None
        self.image_item = None

        # Keep track of last plot
        self._last_x_param = None
        self._last_y_param = None

        # Keep track of the ScaleBar
        self.scale_bar = None

        # Remember previous parameters to avoid redrawing when not needed
        self.last_plot_parameters = {
            "color_code": None,
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

        # Is the user trying to initiate drawing a measurement box?
        if (
            self.scatter_plot is not None
            and ev.button() == Qt.MouseButton.LeftButton
            and ev.modifiers() == QtCore.Qt.AltModifier
            and self.state.x_param in ("x", "y", "z")
            and self.state.y_param in ("x", "y", "z")
            and self._plot_x_data is not None
            and self._plot_y_data is not None
        ):
            if self._measurement_roi is not None:
                self.removeItem(self._measurement_roi)
                self._measurement_roi.deleteLater()
                self._measurement_roi = None

            self._measurement_is_being_drawn = True
            self._measurement_start_point = (
                self.getPlotItem().getViewBox().mapSceneToView(ev.position())
            )
            self._measurement_roi = ROI(
                pos=self._measurement_start_point,
                size=(0, 0),
                resizable=False,
                rotatable=False,
                pen=mkPen(color=(0, 255, 255), width=2, style=Qt.PenStyle.DashLine),
            )
            self._measurement_roi.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
            self.addItem(self._measurement_roi)
            self._measurement_roi.show()

            ev.accept()
            return

        # Is the user trying to initiate drawing an ROI?
        if (
            self.scatter_plot is not None
            and ev.button() == Qt.MouseButton.LeftButton
            and ev.modifiers() == QtCore.Qt.ShiftModifier
        ):
            # Remove previous ROI if it exists
            if self.ROI is not None:
                self.removeItem(self.ROI)
                self.ROI.deleteLater()
                self.ROI = None

            # Create ROI and keep track of position
            self._roi_is_being_drawn = True
            self._roi_start_point = (
                self.getPlotItem().getViewBox().mapSceneToView(ev.position())
            )
            self.ROI = ROI(
                pos=self._roi_start_point,
                size=(0, 0),
                resizable=False,
                rotatable=False,
                pen=(255, 0, 0),
            )
            self.ROI.setAcceptedMouseButtons(Qt.MouseButton.RightButton)
            self.addItem(self.ROI)
            self.ROI.show()

            # Make sure to react to ROI shifts
            self.ROI.sigRegionChangeFinished.connect(self.roi_moved)

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

        elif self.scatter_plot is not None and ev.button() == Qt.MouseButton.LeftButton:
            measurement = self._measurement_at_scene_pos(ev.position())
            if measurement is not None:
                self._select_measurement(measurement["id"])
                ev.accept()
                return

        else:

            # Is the user trying to open a context menu?
            if (
                self.scatter_plot is not None
                and ev.button() == Qt.MouseButton.RightButton
            ):
                menu = QMenu()
                measurement = self._measurement_at_scene_pos(ev.position())
                if measurement is None:
                    measurement = self._get_selected_measurement()
                if measurement is not None:
                    delete_measurement_action = QAction("Delete measurement")
                    delete_measurement_action.triggered.connect(
                        lambda _: self._delete_measurement(measurement["id"])
                    )
                    menu.addAction(delete_measurement_action)
                    menu.addSeparator()
                if self.ROI is not None:
                    crop_data_action = QAction("Crop data")
                    crop_data_action.triggered.connect(self.crop_data_by_roi_selection)
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
        if (
            self.scatter_plot is not None
            and ev.buttons() == Qt.MouseButton.LeftButton
            and self._measurement_roi is not None
            and self._measurement_is_being_drawn
        ):
            current_point = (
                self.getPlotItem().getViewBox().mapSceneToView(ev.position())
            )
            self._measurement_roi.setSize(current_point - self._measurement_start_point)
            ev.accept()
            return

        # Is the user drawing an ROI?
        if (
            self.scatter_plot is not None
            and ev.buttons() == Qt.MouseButton.LeftButton
            and self.ROI is not None
            and self._roi_is_being_drawn
        ):
            # Resize the ROI
            current_point = (
                self.getPlotItem().getViewBox().mapSceneToView(ev.position())
            )
            self.ROI.setSize(current_point - self._roi_start_point)

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
        else:
            # Call the parent method
            ev.ignore()
            super().mouseMoveEvent(ev)

    def mouseReleaseEvent(self, ev):
        if self.scatter_plot is not None and ev.button() == Qt.MouseButton.LeftButton:
            if self._measurement_is_being_drawn:
                self._measurement_is_being_drawn = False

                if self._measurement_roi is None:
                    ev.ignore()
                    return

                x_range, y_range = self._get_ranges_from_item(self._measurement_roi)
                if x_range is None or y_range is None:
                    self._remove_measurement_roi()
                    ev.accept()
                    return

                x_min, x_max = min(x_range), max(x_range)
                y_min, y_max = min(y_range), max(y_range)

                mask = (
                    (self._plot_x_data >= x_min)
                    & (self._plot_x_data <= x_max)
                    & (self._plot_y_data >= y_min)
                    & (self._plot_y_data <= y_max)
                )
                points = np.column_stack(
                    (self._plot_x_data[mask], self._plot_y_data[mask])
                )

                if points.shape[0] < 3:
                    self._remove_measurement_roi()
                    ev.accept()
                    return

                geometry = compute_measurement_geometry(points)
                if geometry is None:
                    self._remove_measurement_roi()
                    ev.accept()
                    return

                self._create_measurement(geometry)
                self._remove_measurement_roi()
                ev.accept()
                return

            if self._roi_is_being_drawn:
                # Extract the ranges
                x_range, y_range = self._get_ranges_from_roi()
                if x_range is None or y_range is None:
                    # Handle the case where ranges are None
                    return

                # Get current parameters
                x_param = self.state.x_param
                y_param = self.state.y_param

                # Update the DataViewer with current selection
                self.locations_selected_by_range.emit(
                    x_param, y_param, x_range, y_range
                )

                # Reset flags
                self._roi_start_point = None
                self._roi_is_being_drawn = False

                # Check if the ROI has 0 size
                if (
                    np.abs(x_range[1] - x_range[0]) < 1e-4
                    or np.abs(y_range[1] - y_range[0]) < 1e-4
                ):
                    if hasattr(self, "ROI") and self.ROI:
                        self.removeItem(self.ROI)
                        self.ROI.deleteLater()
                        self.ROI = None

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
                            if self.state.color_code == ColorCode.NONE
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
            "color_code": None,
            "tid": None,
            "fid": None,
            "depth": None,
            "time": None,
            "brushes": None,
        }

    def remove_points(self):
        self._clear_measurements()
        self._remove_measurement_roi()
        self._clear_drawn_roi()
        self.setBackground("k")
        self.clear()

    def plot_parameters(
        self,
        x: pd.Series,
        y: pd.Series,
        color_code: ColorCode,
        x_param: str,
        y_param: str,
        tid: pd.Series,
        fid: Optional[pd.Series] = None,
        depth: Optional[pd.Series] = None,
        time: Optional[pd.Series] = None,
    ):
        """Plot localizations and other parameters in a 2D scatter plot.

        Parameters
        ----------

        x: pd.Series
            x coordinates to plot. x must be a Pandas Series.
        y: pd.Series
            y coordinates to plot. y must be a Pandas Series.
        color_code: ColorCode
            Requested color coding.
        x_param: str
            Name of the x parameter.
        y_param: str
            Name of the y parameter.
        tid: pd.Series
            Traces IDs for each of the (x, y) pairs. tid must be a Pandas Series.
        fid: Optional[pd.Series] = None
            Fluorophore IDs for each of the (x, y) pairs. fid can be omitted, otherwise it must
            be a Pandas Series. If not None, it will be used to color-code the scatter plot points.
        depth: Optional[pd.Series] = None
            z value (depth) for each of the (x, y) pairs. depth can be omitted, otherwise it must
            be a Pandas Series. If not None, it will be used to color-code the scatter plot points.
        time: Optional[pd.Series]
            time for each of the (x, y) pairs. time can be omitted, otherwise it must
            be a Pandas Series. If not None, it will be used to color-code the scatter plot points.
        """

        # Make sure our inputs are Pandas Series
        assert x is not None and type(x) == pd.Series, "`x` must be a Pandas Series."
        assert y is not None and type(y) == pd.Series, "`y` must be a Pandas Series."
        assert (
            tid is not None and type(tid) == pd.Series
        ), "`tid` must be a Pandas Series."

        # Check consistency of arguments
        if color_code == ColorCode.BY_DEPTH and depth is None:
            raise ValueError("If color coding by depth, `depth` cannot be None!")

        if color_code == ColorCode.BY_TIME and time is None:
            raise ValueError("If color coding by time, `time` cannot be None!")

        if color_code == ColorCode.BY_FLUO and fid is None:
            raise ValueError("If color coding by fluorophore ID, `fid` cannot be None!")

        num_flags = sum([v is not None for v in [fid, depth, time]])
        if num_flags > 1:
            raise ValueError(
                "At most one of `fid`, `depth` and `time` can be not None."
            )

        # If we have an image, make sure to draw it first (but only if
        # x_param is "x" and y_param is "y"
        if self.state.show_confocal:
            if self.image_item is not None and x_param == "x" and y_param == "y":
                self.addItem(self.image_item)

        if self.state.show_localizations:

            new_x = x.to_numpy(copy=True)
            new_y = y.to_numpy(copy=True)
            if (
                self._plot_x_data is not None
                and self._plot_y_data is not None
                and (
                    len(new_x) != len(self._plot_x_data)
                    or len(new_y) != len(self._plot_y_data)
                    or not np.array_equal(new_x, self._plot_x_data)
                    or not np.array_equal(new_y, self._plot_y_data)
                )
            ):
                self._clear_measurements()

            self._plot_x_data = new_x
            self._plot_y_data = new_y

            # Do we need to recreate the colors?
            if self._need_to_recreate_colors(
                color_code, tid=tid, fid=fid, depth=depth, time=time
            ):
                # Recreate colors
                brushes = ColorsToBrushes().get_brushes(
                    color_code, tid=tid, fid=fid, depth=depth, time=time
                )
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

            # For a tracking dataset, we also add the connecting line_plot (for spatial parameters only)
            if self.state.is_tracking and (
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
        color_code,
        tid: pd.Series,
        fid: Optional[pd.Series] = None,
        depth: Optional[pd.Series] = None,
        time: Optional[pd.Series] = None,
    ):
        """Check if the colors need to be recreated (and store state)."""

        assert type(tid) == pd.Series, "`tid` must be a Pandas Series."
        if fid is not None:
            assert type(fid) == pd.Series, "`fid` must be a Pandas Series."
        if depth is not None:
            assert type(depth) == pd.Series, "`depth` must be a Pandas Series."
        if time is not None:
            assert type(time) == pd.Series, "`time` must be a Pandas Series."

        recreate_brushes = False
        if self.last_plot_parameters["color_code"] is None:

            # Fist time
            recreate_brushes = True
        else:

            # There were plots already
            if self.last_plot_parameters["color_code"] != color_code:

                # If the color code changed, be need to recreate the colors
                recreate_brushes = True

            else:

                # The color code is the same, we need to check if we can re-use the
                # same colors
                if color_code == ColorCode.NONE:

                    # We can count the number of tids
                    if (
                        self.last_plot_parameters["tid"] is None
                        or len(tid) != len(self.last_plot_parameters["tid"])
                        or np.any(tid.index != self.last_plot_parameters["tid"].index)
                        or np.any(tid.values != self.last_plot_parameters["tid"].values)
                    ):
                        recreate_brushes = True

                elif color_code == ColorCode.BY_TID:
                    if (
                        self.last_plot_parameters["tid"] is None
                        or len(tid) != len(self.last_plot_parameters["tid"])
                        or np.any(tid.index != self.last_plot_parameters["tid"].index)
                        or np.any(tid.values != self.last_plot_parameters["tid"].values)
                    ):
                        recreate_brushes = True

                elif color_code == ColorCode.BY_FLUO:
                    if (
                        self.last_plot_parameters["fid"] is None
                        or len(fid) != len(self.last_plot_parameters["fid"])
                        or np.any(fid.index != self.last_plot_parameters["fid"].index)
                        or np.any(fid.values != self.last_plot_parameters["fid"].values)
                    ):
                        recreate_brushes = True

                elif color_code == ColorCode.BY_DEPTH:
                    if (
                        self.last_plot_parameters["depth"] is None
                        or len(depth) != len(self.last_plot_parameters["depth"])
                        or np.any(
                            depth.index != self.last_plot_parameters["depth"].index
                        )
                        or np.any(
                            depth.values != self.last_plot_parameters["depth"].values
                        )
                    ):
                        recreate_brushes = True

                elif color_code == ColorCode.BY_TIME:
                    if (
                        self.last_plot_parameters["time"] is None
                        or len(time) != len(self.last_plot_parameters["time"])
                        or np.any(time.index != self.last_plot_parameters["time"].index)
                        or np.any(
                            time.values != self.last_plot_parameters["time"].values
                        )
                    ):
                        recreate_brushes = True
                else:
                    # Unsupported case!
                    raise ValueError("Unknown color code!")

        # Remember the new parameters
        self.last_plot_parameters["color_code"] = color_code
        self.last_plot_parameters["tid"] = tid
        self.last_plot_parameters["fid"] = fid
        self.last_plot_parameters["depth"] = depth
        self.last_plot_parameters["time"] = time

        # Return
        return recreate_brushes

    def crop_data_by_roi_selection(self, item):
        """Open dialog to manually set the filter ranges"""

        # Get the ROI bounds
        pos = self.ROI.pos()
        size = self.ROI.size()

        # Create the ranges
        x_range = (pos[0], pos[0] + size[0])
        y_range = (pos[1], pos[1] + size[1])

        # Get the parameter names
        x_param = self.state.x_param
        y_param = self.state.y_param

        self.crop_region_selected.emit(x_param, y_param, x_range, y_range)

        # Delete ROI after it has been used to crop
        self.removeItem(self.ROI)
        self.ROI.deleteLater()
        self.ROI = None

    def roi_moved(self):
        """Inform that the selection of localizations may have changed after the ROI was moved."""

        # If the ROI is being drawn now, do nothing
        if self._roi_is_being_drawn:
            return

        # Extract the ranges
        x_range, y_range = self._get_ranges_from_roi()

        # Get current parameters
        x_param = self.state.x_param
        y_param = self.state.y_param

        # Update the DataViewer with current selection
        if x_range is not None and y_range is not None:
            self.locations_selected_by_range.emit(x_param, y_param, x_range, y_range)

    def clicked(self, _, points):
        """Emit 'signal_selected_locations' when points are selected in the plot."""
        self.locations_selected.emit(points)

        # Remove ROI if it exists
        if self.ROI is not None:
            self.removeItem(self.ROI)
            self.ROI = None

    def keyPressEvent(self, ev):
        if ev.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            measurement = self._get_selected_measurement()
            if measurement is not None:
                self._delete_measurement(measurement["id"])
                ev.accept()
                return

        super().keyPressEvent(ev)

    def _get_ranges_from_roi(self):
        """Calculate x and y ranges from ROI."""

        return self._get_ranges_from_item(self.ROI)

    def _get_ranges_from_item(self, roi):
        """Calculate x and y ranges from a ROI-like item."""

        # Initialize x and y ranges to None
        x_range = None
        y_range = None

        # Extract x and y ranges
        if roi is not None:
            x_range = (roi.pos()[0], roi.pos()[0] + roi.size()[0])
            y_range = (roi.pos()[1], roi.pos()[1] + roi.size()[1])

        return x_range, y_range

    def _get_selected_measurement(self):
        for measurement in self._measurements:
            if measurement["id"] == self._selected_measurement_id:
                return measurement
        return None

    def _measurement_at_scene_pos(self, scene_pos):
        if not self._measurements:
            return None

        view_pos = self.getPlotItem().getViewBox().mapSceneToView(scene_pos)
        point = np.array([view_pos.x(), view_pos.y()], dtype=float)

        for measurement in reversed(self._measurements):
            geometry = measurement["geometry"]
            delta = point - geometry["center"]
            along = float(delta @ geometry["axis"])
            orth = float(delta @ geometry["perp"])
            margin = max(10.0, 0.1 * (geometry["along_max"] - geometry["along_min"]))
            if (
                geometry["along_min"] - margin
                <= along
                <= geometry["along_max"] + margin
                and geometry["orth_min"] - margin
                <= orth
                <= geometry["orth_max"] + margin
            ):
                return measurement

        return None

    def _format_measurement_text(self, measurement):
        geometry = measurement["geometry"]
        return (
            f"#{measurement['id'] + 1}: mean {geometry['mean_thickness']:.2f} nm\n"
            f"median {geometry['median_thickness']:.2f} nm, p95 {geometry['p95_thickness']:.2f} nm\n"
            f"side -{geometry['max_negative_offset']:.2f} / +{geometry['max_positive_offset']:.2f} nm"
        )

    def _create_measurement(self, geometry):
        measurement_id = self._measurement_counter
        self._measurement_counter += 1

        box_pen = mkPen(color=(0, 255, 255), width=2)
        line_pen = mkPen(color=(255, 255, 0), width=2)
        point_brush = pg.mkBrush(0, 255, 255, 70)

        box_item = PlotCurveItem(
            x=geometry["box_xy"][:, 0],
            y=geometry["box_xy"][:, 1],
            pen=box_pen,
        )
        line_item = PlotCurveItem(
            x=geometry["line_xy"][:, 0],
            y=geometry["line_xy"][:, 1],
            pen=line_pen,
        )
        points_item = pg.ScatterPlotItem(
            x=geometry["points"][:, 0],
            y=geometry["points"][:, 1],
            size=7,
            pen=None,
            brush=point_brush,
        )
        label_item = TextItem(
            text=self._format_measurement_text(
                {"id": measurement_id, "geometry": geometry}
            ),
            color=(255, 255, 255),
            anchor=(0, 1),
        )
        label_item.setPos(
            float(geometry["box_xy"][0, 0]), float(geometry["box_xy"][0, 1])
        )

        for item in (box_item, line_item, points_item, label_item):
            self.addItem(item)
            if hasattr(item, "setAcceptedMouseButtons"):
                item.setAcceptedMouseButtons(Qt.MouseButton.NoButton)

        measurement = {
            "id": measurement_id,
            "geometry": geometry,
            "box_item": box_item,
            "line_item": line_item,
            "points_item": points_item,
            "label_item": label_item,
        }
        self._measurements.append(measurement)
        self._select_measurement(measurement_id)

    def _select_measurement(self, measurement_id):
        self._selected_measurement_id = measurement_id

        for measurement in self._measurements:
            is_selected = measurement["id"] == measurement_id
            measurement["box_item"].setPen(
                mkPen(
                    color=(0, 255, 255) if is_selected else (0, 180, 180),
                    width=3 if is_selected else 1,
                )
            )
            measurement["line_item"].setPen(
                mkPen(
                    color=(255, 255, 0) if is_selected else (180, 180, 0),
                    width=3 if is_selected else 1,
                )
            )
            measurement["points_item"].setBrush(
                pg.mkBrush(0, 255, 255, 100 if is_selected else 50)
            )
            measurement["label_item"].setColor(
                (255, 255, 255) if is_selected else (190, 190, 190)
            )

    def _delete_measurement(self, measurement_id):
        remaining = []
        for measurement in self._measurements:
            if measurement["id"] == measurement_id:
                for item in (
                    measurement["box_item"],
                    measurement["line_item"],
                    measurement["points_item"],
                    measurement["label_item"],
                ):
                    self.removeItem(item)
                    item.deleteLater()
            else:
                remaining.append(measurement)

        self._measurements = remaining
        if self._selected_measurement_id == measurement_id:
            self._selected_measurement_id = None
            if self._measurements:
                self._select_measurement(self._measurements[-1]["id"])

    def _clear_measurements(self):
        for measurement in self._measurements:
            for item in (
                measurement["box_item"],
                measurement["line_item"],
                measurement["points_item"],
                measurement["label_item"],
            ):
                self.removeItem(item)
                item.deleteLater()

        self._measurements = []
        self._selected_measurement_id = None

    def _remove_measurement_roi(self):
        if self._measurement_roi is not None:
            self.removeItem(self._measurement_roi)
            self._measurement_roi.deleteLater()
            self._measurement_roi = None

    def _clear_drawn_roi(self):
        if self.ROI is not None:
            self.removeItem(self.ROI)
            self.ROI.deleteLater()
            self.ROI = None
        if self.line is not None:
            self.removeItem(self.line)
            self.line.deleteLater()
            self.line = None
        if self.line_text is not None:
            self.removeItem(self.line_text)
            self.line_text.deleteLater()
            self.line_text = None
        self._roi_start_point = None
        self._roi_is_being_drawn = False
        self._line_start_point = None
        self._line_is_being_drawn = False

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
            "All Supported Files (*.msr);;" "MSR file (*.pmx);;",
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
