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

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import QMargins, QRectF, QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QSizePolicy, QVBoxLayout, QWidget

from pyminflux.ui.colors import ColorMap
from pyminflux.ui.helpers import export_colorbar


class ColorBarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create a vertical layout for this widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create a pyqtgraph GraphicsLayoutWidget
        self.graphWidget = pg.GraphicsLayoutWidget()
        layout.addWidget(self.graphWidget)

        # Create a ColorBarItem
        self.colorbar = pg.ColorBarItem(
            values=(0, 1),
            colorMap="viridis",
            label="",
            interactive=False,
            colorMapMenu=False,
            orientation="vertical",
        )

        # Add the ColorBarItem to the GraphicsLayoutWidget
        self.graphWidget.addItem(self.colorbar)

        # Set margins for the ColorBarItem
        self.margins = QMargins(10, 10, 10, 10)

        # Set the size policy
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        # Use a timer to query the size after the widget has been shown
        QTimer.singleShot(0, self.initializeSize)

        # Now hide it
        self.hide()

    def reset(self, colormap: str, data_range: tuple[float, float], label: str = ""):
        """Update the color bar."""

        if colormap is None:
            return

        if colormap not in ["jet", "plasma"]:
            raise ValueError(f"Unsupported colormap `{colormap}`.")

        # Remove the previous colorbar item
        if self.colorbar is not None:
            self.graphWidget.removeItem(self.colorbar)

        # Create the colormap
        if colormap == "jet":
            _, colors = ColorMap().generate_jet_colormap(n_colors=256)
        elif colormap == "plasma":
            _, colors = ColorMap().generate_plasma_colormap(n_colors=256)
        else:
            raise ValueError(f"Unsupported colormap `{colormap}`.")
        pg_colormap = pg.ColorMap(np.linspace(0.0, 1.0, colors.shape[0]), colors)

        # Create a ColorBarItem
        self.colorbar = pg.ColorBarItem(
            values=data_range,
            colorMap=pg_colormap,
            label=label,
            interactive=False,
            colorMapMenu=False,
            orientation="vertical",
        )

        # Add the new ColorBarItem to the GraphicsLayoutWidget
        self.graphWidget.addItem(self.colorbar)

        # Add the geometry
        QTimer.singleShot(0, self.initializeSize)

    def initializeSize(self):
        # Query the actual size of the ColorBarItem
        self.colorbar_width = self.colorbar.boundingRect().width()

        # Calculate and set the fixed width of the widget
        total_width = self.colorbar_width + self.margins.left() + self.margins.right()
        self.setFixedWidth(int(total_width))

        # Update the ColorBarItem geometry
        self.updateColorBarGeometry()

    def sizeHint(self):
        # Provide a default size hint
        return self.graphWidget.sizeHint()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateColorBarGeometry()

    def updateColorBarGeometry(self):
        if hasattr(self, "colorbar_width"):
            # Calculate the centered position for the ColorBarItem
            available_width = self.width() - self.margins.left() - self.margins.right()
            x_offset = (available_width - self.colorbar_width) / 2 + self.margins.left()

            # Set the geometry of the ColorBarItem
            rect = QRectF(
                x_offset,
                self.margins.top(),
                self.colorbar_width,
                self.height() - self.margins.top() - self.margins.bottom(),
            )
            self.colorbar.setGeometry(rect)

    def contextMenuEvent(self, ev):
        """Create a context menu on the plot."""
        menu = QMenu()
        export_action = QAction("Save as image")
        export_action.triggered.connect(lambda checked: export_colorbar(self))
        menu.addAction(export_action)
        menu.exec(ev.globalPos())
