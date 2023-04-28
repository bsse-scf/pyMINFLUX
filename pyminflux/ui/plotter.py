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
import pyqtgraph as pg
from pyqtgraph import ROI, PlotCurveItem, PlotWidget, TextItem, ViewBox, mkPen
from PySide6 import QtCore
from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu

from ..state import ColorCode, State


class Plotter(PlotWidget):
    # Signals
    locations_selected = Signal(list, name="locations_selected")
    locations_selected_by_range = Signal(
        str, str, tuple, tuple, name="locations_selected_by_range"
    )
    crop_region_selected = Signal(str, str, tuple, tuple, name="crop_region_selected")

    def __init__(self):
        super().__init__()
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
        self.line = None
        self.line_text = None
        self.__roi_start_point = None
        self.__roi_is_being_drawn = False
        self.__line_start_point = None
        self.__line_is_being_drawn = False

        # Keep track of last plot
        self.__last_x_param = None
        self.__last_y_param = None

    def enableAutoRange(self, enable: bool):
        """Enable/disable axes autorange."""
        self.getViewBox().enableAutoRange(axis=ViewBox.XYAxes, enable=enable)

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
                self.ROI.deleteLater()
                self.ROI = None

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
            self.ROI.setAcceptedMouseButtons(Qt.MouseButton.RightButton)
            self.ROI.sigClicked.connect(self.roi_mouse_click_event)
            self.addItem(self.ROI)
            self.ROI.show()

            # Make sure to react to ROI shifts
            self.ROI.sigRegionChangeFinished.connect(self.roi_moved)

            # Accept the event
            ev.accept()

        elif (
            self.scatter is not None
            and ev.button() == Qt.MouseButton.LeftButton
            and ev.modifiers() == QtCore.Qt.ControlModifier
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
            self.__line_is_being_drawn = True
            self.__line_start_point = (
                self.getPlotItem().getViewBox().mapSceneToView(ev.position())
            )
            self.line = PlotCurveItem(
                x=[self.__line_start_point.x(), self.__line_start_point.x()],
                y=[self.__line_start_point.y(), self.__line_start_point.y()],
                pen=mkPen(color=(255, 0, 0), width=2),
            )
            self.addItem(self.line)
            self.line.show()

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
            and self.__roi_is_being_drawn
        ):
            # Resize the ROI
            current_point = (
                self.getPlotItem().getViewBox().mapSceneToView(ev.position())
            )
            self.ROI.setSize(current_point - self.__roi_start_point)

            # Accept the event
            ev.accept()

        elif (
            self.scatter is not None
            and ev.buttons() == Qt.MouseButton.LeftButton
            and self.__line_is_being_drawn
        ):
            # Is the user drawing a line?

            # Resize the ROI
            current_point = (
                self.getPlotItem().getViewBox().mapSceneToView(ev.position())
            )
            self.line.setData(
                x=[self.__line_start_point.x(), current_point.x()],
                y=[self.__line_start_point.y(), current_point.y()],
            )

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
            and self.__roi_is_being_drawn
        ):
            # Extract the ranges
            x_range, y_range = self._get_ranges_from_roi()

            # Get current parameters
            x_param = self.state.x_param
            y_param = self.state.y_param

            # Update the DataViewer with current selection
            if x_range is not None and y_range is not None:
                self.locations_selected_by_range.emit(
                    x_param, y_param, x_range, y_range
                )

            # Reset flags
            self.__roi_start_point = None
            self.__roi_is_being_drawn = False

            # Accept the event
            ev.accept()

        elif (
            self.scatter is not None
            and ev.button() == Qt.MouseButton.LeftButton
            and self.__line_is_being_drawn
        ):
            # Display the measurement
            x_data, y_data = self.line.getData()
            center = np.array(
                [0.5 * (x_data[0] + x_data[1]), 0.5 * (y_data[0] + y_data[1])]
            )
            delta_y = np.array(y_data[1] - y_data[0])
            delta_x = np.array(x_data[1] - x_data[0])
            v = np.array([-1.0 * delta_y, delta_x])
            norm = np.linalg.norm(v)
            if np.abs(norm) >= 1e-4:
                v_norm = v / norm
                length = np.sqrt(delta_x * delta_x + delta_y * delta_y)
                pos = center + 1.0 * v_norm
                self.line_text = TextItem(
                    text=f"{length:.2f} nm", color=(255, 255, 255)
                )
                self.line_text.setPos(pos[0], pos[1])
                self.addItem(self.line_text)
            else:
                if self.line is not None:
                    self.removeItem(self.line)
                    self.line.deleteLater()
                    self.line = None

            # Reset flags
            self.__line_start_point = None
            self.__line_is_being_drawn = False

            # Accept the event
            ev.accept()

        else:
            # Call the parent method
            ev.ignore()
            super().mouseReleaseEvent(ev)

    def remove_points(self):
        self.setBackground("w")
        self.clear()

    def plot_parameters(self, x, y, x_param, y_param, tid, fid):
        """Plot localizations in a 2D scatter plot."""

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
        if self.state.color_code == ColorCode.NONE:
            brushes = self.brush
        elif self.state.color_code == ColorCode.BY_TID:
            brushes = tid
        elif self.state.color_code == ColorCode.BY_FLUO:
            brushes = [6 if i == 1 else 9 for i in fid]
        else:
            raise ValueError("Unexpected request for color-coding the localizations!")

        self.scatter.addPoints(
            x=x,
            y=y,
            data=tid,
            brush=brushes,
        )
        self.addItem(self.scatter)
        self.setLabel("bottom", text=x_param)
        self.setLabel("left", text=y_param)
        self.showAxis("bottom")
        self.showAxis("left")
        self.setBackground("k")

        if (self.__last_x_param is None or self.__last_x_param != x_param) or (
            self.__last_y_param is None or self.__last_y_param != y_param
        ):
            # Update range
            self.getViewBox().enableAutoRange(axis=ViewBox.XYAxes, enable=True)

            # Fix aspect ratio
            x_scale = (x.max() - x.min()) / (len(x) - 1)
            y_scale = (y.max() - y.min()) / (len(y) - 1)
            aspect_ratio = y_scale / x_scale
            self.getPlotItem().getViewBox().setAspectLocked(
                lock=True, ratio=aspect_ratio
            )

        # Update last plotted parameters
        self.__last_x_param = x_param
        self.__last_y_param = y_param

    def customize_context_menu(self):
        """Remove some default context menu actions.

        See: https://stackoverflow.com/questions/44402399/how-to-disable-the-default-context-menu-of-pyqtgraph#44420152
        """

        # Hide the "Plot Options" menu
        self.getPlotItem().ctrlMenu.menuAction().setVisible(False)

    def roi_mouse_click_event(self, roi, ev):
        """Right-click event on the ROI."""
        if ev.button() == Qt.MouseButton.RightButton and self.ROI.isMoving:
            # Make sure the ROI is not moving
            self.ROI.isMoving = False
            self.ROI.movePoint(self.ROI.startPos, finish=True)
            ev.accept()
        elif self.ROI.acceptedMouseButtons() & ev.button():
            ev.accept()
            if ev.button() == Qt.MouseButton.RightButton:
                self.roi_raise_context_menu(ev)
        else:
            ev.ignore()

    def roi_raise_context_menu(self, ev):
        """Create a context menu on the ROI."""
        # Open context menu
        menu = QMenu()
        crop_data_action = QAction("Crop data")
        crop_data_action.triggered.connect(self.crop_data_by_roi_selection)
        menu.addAction(crop_data_action)
        pos = ev.screenPos()
        menu.exec(QPoint(int(pos.x()), int(pos.y())))

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

    def roi_moved(self):
        """Inform that the selection of localizations may have changed after the ROI was moved."""

        # If the ROI is being drawn now, do nothing
        if self.__roi_is_being_drawn:
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
