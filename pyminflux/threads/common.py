from PySide6.QtCore import QMutex, QMutexLocker


class CancelFlag:
    """Encapulates a Mutex to communicate state change to the Workers."""

    def __init__(self):
        self._cancelled = False
        self._mutex = QMutex()

    def is_cancelled(self):
        with QMutexLocker(self._mutex):
            return self._cancelled

    def cancel(self):
        with QMutexLocker(self._mutex):
            self._cancelled = True
