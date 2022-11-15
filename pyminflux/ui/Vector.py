from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QGraphicsLineItem


class Vector(QGraphicsLineItem):
    """
    Draws a vector.

    By default, the vector is drawn from (x, y) to (x+u, y+v), but it can optionally
    by drawn from (x-u, y-v) to (x, y).
    """
    def __init__(self, x, y, u, v, index, class_name='raw', to_xy=False, color=Qt.yellow, parent=None):
        """
        Draws a vector.
        :param x: origin, x coordinate.
        :param y: origin, y coordinate.
        :param u: vector x component.
        :param v: vector y component.
        :param index: vector index.
        :param class_name: vector type (default = 'raw')
        :param to_xy: (default = False). If False, the arrow is drawn from (x, y) to (x+u, y+v);
                                         if True, the arrow is drawn from (x-u, y-v) to (x, y).
        :param color: a valid Qt color (default = Qt.yellow)
        :param parent: parent widget (default = None).
        """

        # Call parent constructor
        if to_xy:
            QGraphicsLineItem.__init__(self, float(x - u), float(y - v), float(x), float(y), parent)
        else:
            QGraphicsLineItem.__init__(self, float(x), float(y), float(x + u), float(y + v), parent)

        # Store the index and the class name
        self._index = index
        self._class_name = class_name

        self.setFlag(QGraphicsLineItem.ItemIsSelectable, True)
        pen = QPen(color, 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        self.setPen(pen)

    @property
    def index(self):
        """Index"""
        return int(self._index)

    @property
    def class_name(self):
        """Index"""
        return self._class_name

    def __repr__(self):
        """
        Vector representation.
        :return: string 
        """
        return "Vector '%s' with index = %d" % (self._class_name, self._index)
