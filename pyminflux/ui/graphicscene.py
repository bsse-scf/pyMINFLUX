from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QGraphicsScene, QApplication
from PySide6.QtCore import Slot
from PySide6.QtCore import Signal

from .Point import Point


class GraphicScene(QGraphicsScene):
    """
    The GraphicsScene performs all the plotting and rendering of results
    and allows for interactive work with them.
    """

    # Add a signal for changing selection in the scene
    signal_selection_completed = \
        Signal(list, name='signal_selection_completed')

    signal_add_cell_at_position = \
        Signal(float, float, name='signal_add_cell_at_position')

    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, parent)

        self.image = None
        self.selectionChanged.connect(self.selection_changed)

    @Slot(int, name="zoom_in")
    def zoom_in(self, zoom_in_factor):
        """
        Zoom the scene in
        """

        f = float(zoom_in_factor)
        self.views()[0].scale(f, f)

    @Slot(int, name="zoom_out")
    def zoom_out(self, zoom_out_factor):
        """
        Zoom the scene out
        """

        f = 1.0 / float(zoom_out_factor)
        self.views()[0].scale(f, f)

    @Slot(list, name="handle_data_viewer_selection_completed")
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
        if event.buttons() == Qt.MouseButton.LeftButton:
            if QApplication.keyboardModifiers() == Qt.KeyboardModifier.ShiftModifier:
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

    @Slot(name="selection_changed")
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
