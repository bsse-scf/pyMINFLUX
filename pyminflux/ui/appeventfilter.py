from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal


class AppEventFilter(QtCore.QObject):

    # Add a signal for changing current image index
    signal_zoom_in = Signal(int, name='signal_zoom_in')
    signal_zoom_out = Signal(int, name='signal_zoom_out')
    signal_delete_selection = Signal(name='signal_delete_selection')

    def eventFilter(self, receiver, event):

        if event.type() == QtCore.QEvent.Type.KeyPress:

            if event.key() == Qt.Key.Key_Minus:

                # Emit the zoom_out signal
                self.signal_zoom_out.emit(2)

                return True

            if event.key() == Qt.Key.Key_Plus:

                # Emit the zoom_in signal
                self.signal_zoom_in.emit(2)

                return True

            if event.key() == Qt.Key.Key_Delete:

                # Emit the delete_objects signal
                self.signal_delete_selection.emit()

                return True

            else:

                # Call Base Class Method to Continue Normal Event Processing
                return super(AppEventFilter, self).eventFilter(receiver, event)

        else:

            # Call Base Class Method to Continue Normal Event Processing
            return super(AppEventFilter, self).eventFilter(receiver, event)
