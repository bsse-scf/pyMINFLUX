from PySide6.QtGui import QBrush, QPen
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsEllipseItem
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtCore import Qt
import numpy as np


class Point(QGraphicsEllipseItem):

    def __init__(self, x, y, diameter=3, cell_index=None, track_index=None,
                 color=Qt.GlobalColor.red, selected_color=Qt.GlobalColor.yellow,
                 plot_track_index=False, parent=None):

        self._x = x
        self._y = y
        self._cell_index = cell_index
        self._track_index = track_index
        self._plot_track_index = plot_track_index
        self._color = QColor(color)
        self._selected_color = QColor(selected_color)

        self.radius = diameter // 2
        QGraphicsEllipseItem.__init__(self, x - self.radius, y - self.radius,
                                      diameter, diameter, parent)

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setPen(self._color)
        self.setBrush(self._color)

    @property
    def cell_index(self):
        """Cell index.

        @return cell index
        @:rtype string
        """
        return str(self._cell_index)

    @property
    def track_index(self):
        """Track index.

        @return track index. If the cell does not have a track, return "".
        @:rtype string
        """
        if np.isnan(self._track_index):
            raise Exception("The track index should not be NAN!")
        else:
            return str(int(self._track_index))

    @property
    def plot_index(self):
        """Index to plot.

        @return index to plot. It can be either the cell index or the track
        index, depending on the value of plot_track_index that was passed to
        the constructor.
        @:rtype string

        """
        if self._plot_track_index:
            return self.track_index
        else:
            return self.cell_index

    @property
    def is_track_index(self):
        """Is track index"""
        return self._plot_track_index

    def __repr__(self):
        """
        Point representation
        :return: string 
        """
        return "Point at position (%d, %d) with cell" \
               " index = %s and track index %s" %\
               (self._x, self._y, self.cell_index, self.track_index)

    def paint(self, painter, option, widget=None):
        """
        Paint the Point.
        :param painter: 
        :param option: 
        :param widget: 
        :return: 
        """

        if self.isSelected():
            painter.setBrush(self._selected_color)
        else:
            painter.setBrush(self._color)

        QGraphicsEllipseItem.paint(self, painter, option, widget)

        if self.isSelected():
            painter.setPen(self._selected_color)
        else:
            painter.setPen(self._color)

        painter.drawText(self._x - self.radius - 1,
                         self._y - self.radius - 1,
                         self.plot_index)
