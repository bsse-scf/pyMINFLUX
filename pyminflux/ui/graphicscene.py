from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtWidgets import QGraphicsScene, QApplication
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import pyqtSignal

from .Vector import Vector
from .Point import Point


class GraphicScene(QGraphicsScene):
    """
    The GraphicsScene performs all the plotting and rendering of results
    and allows for interactive work with them.
    """

    # Add a signal for changing selection in the scene
    signal_selection_completed = \
        pyqtSignal(list, name='signal_selection_completed')

    signal_add_cell_at_position = \
        pyqtSignal(float, float, name='signal_add_cell_at_position')

    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, parent)

        self.image = None
        self.selectionChanged.connect(self.selection_changed)

    @pyqtSlot(int, name="zoom_in")
    def zoom_in(self, zoom_in_factor):
        """
        Zoom the scene in
        """

        f = float(zoom_in_factor)
        self.views()[0].scale(f, f)

    @pyqtSlot(int, name="zoom_out")
    def zoom_out(self, zoom_out_factor):
        """
        Zoom the scene out
        """

        f = 1.0 / float(zoom_out_factor)
        self.views()[0].scale(f, f)

    @pyqtSlot(list, name="handle_data_viewer_selection_completed")
    def handle_data_viewer_selection_completed(self, cell_indices):

        for item in self.items():
            if isinstance(item, Point):
                if item.cell_index in cell_indices:
                    item.setSelected(True)
                else:
                    item.setSelected(False)

    def mousePressEvent(self, event):
        """
        Process a mouse press event on the scene.
        :param event: A mouse press event.
        :return: 
        """
        if event.buttons() == Qt.LeftButton:
            if QApplication.keyboardModifiers() == Qt.ShiftModifier:
                x = event.scenePos().x()
                y = event.scenePos().y()
                self.signal_add_cell_at_position.emit(x, y)

    def display_image(self, image):
        """
        Stores and displays an image
        :param image: a QImage
        :return: void
        """

        # Show the image (and store it)
        self.image = QPixmap.fromImage(image)
        self.addPixmap(self.image)

        # Reset the scene size
        self.setSceneRect(0, 0, image.width(), image.height())

    def display_points(self, points):
        """
        This function adds all points from a list to the scene and redraws.
        :param points: a list of Points.
        :return:
        """

        for point in points:
            self.addItem(point)

    def remove_points(self):
        """
        Remove points
        :return: 
        """
        for item in self.items():
            if isinstance(item, Point):
                self.removeItem(item)

    def display_vectors(self, vectors):
        """
        This function adds all vectors from a list to the scene and redraws.
        :param vectors: a list of Vectors.
        :return:
        """

        for vector in vectors:
            self.addItem(vector)

    def remove_vectors(self, class_name=None):
        """
        This function removes all vectors of a given class (all, if no class name is given)
        :param class_name: (default = None). Name of the Vectors to remove. If None. all Vectors are removed.  
        :param vectors: a list of Vectors.
        :return:
        """

        for item in self.items():
            if isinstance(item, Vector):
                if class_name is None:
                    self.removeItem(item)
                elif item.class_name == class_name:
                    self.removeItem(item)
                else:
                    pass

    @pyqtSlot(name="selection_changed")
    def selection_changed(self):
        """
        Called on selection change.
        """
        pass

    def mouseReleaseEvent(self, event):

        # Emit selection_completed signal
        self.signal_selection_completed.emit(self.selectedItems())

    def redraw(self):
        """
        Redraws the scene.
        :return: void
        """
        self.views()[0].viewport().update()
