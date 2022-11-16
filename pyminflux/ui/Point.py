from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QPen
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsItem


class Point(QGraphicsEllipseItem):
    def __init__(
        self,
        x,
        y,
        z,
        tid,
        diameter=3,
        color=Qt.GlobalColor.red,
        selected_color=Qt.GlobalColor.yellow,
        parent=None,
    ):

        self._x = x
        self._y = y
        self._z = z
        self._tid = tid
        self._color = QColor(color)
        self._selected_color = QColor(selected_color)

        self.radius = diameter // 2
        QGraphicsEllipseItem.__init__(
            self, x - self.radius, y - self.radius, diameter, diameter, parent
        )

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setPen(self._color)
        self.setBrush(self._color)

    def __repr__(self):
        """
        Point representation
        :return: string
        """
        return f"Point at position ({self._x}, {self._y}, {self._z}) and tid = {self._tid}."

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

        painter.drawText(
            self._x - self.radius - 1, self._y - self.radius - 1, str(self._tid)
        )
