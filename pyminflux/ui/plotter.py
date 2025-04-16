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
        self.remove_points()
        self.hideAxis("bottom")
        self.hideAxis("left")
        self.show()

        # Disable default context menu
        self.setMenuEnabled(False)

        # Set aspect ratio to 1.0 locked
        self.getPlotItem().getViewBox().setAspectLocked(lock=True, ratio=1.0)

        # Keep a reference to the singleton State class
        self.state = State()

        # Keep track of whether the y axis is inverted
        self._y_axis_inverted = False

        # Keep track of the mapping between unique identifiers or fluorophore identifiers and cached QBrushes
        self._id_to_brush = None
        self._fid_to_brush = None

        # Keep a reference to the scatter plot/line plot and image item objects
        self.scatter_plot = None
        self.line_plot = None
        self.image_item = None

        # ROI for localizations selection
        self.ROI = None
        self.line = None
        self.line_text = None
        self._roi_start_point = None
        self._roi_is_being_drawn = False
        self._line_start_point = None
        self._line_is_being_drawn = False

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

        else:

            # Is the user trying to open a context menu?
            if (
                self.scatter_plot is not None
                and ev.button() == Qt.MouseButton.RightButton
            ):
                menu = QMenu()
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
                flip_y_axis_action = QAction("Flip y axis")
                flip_y_axis_action.triggered.connect(self.invert_y_axis)
                menu.addAction(flip_y_axis_action)
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

    def invert_y_axis(self):
        """Invert the Y axis of the plot."""
        if self._y_axis_inverted:
            self.getPlotItem().getViewBox().invertY(False)
        else:
            self.getPlotItem().getViewBox().invertY(True)
        self._y_axis_inverted = not self._y_axis_inverted

    def mouseMoveEvent(self, ev):
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

    def _get_ranges_from_roi(self):
        """Calculate x and y ranges from ROI."""

        # Initialize x and y ranges to None
        x_range = None
        y_range = None

        # Extract x and y ranges
        if self.ROI is not None:
            x_range = (self.ROI.pos()[0], self.ROI.pos()[0] + self.ROI.size()[0])
            y_range = (self.ROI.pos()[1], self.ROI.pos()[1] + self.ROI.size()[1])

        return x_range, y_range

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
