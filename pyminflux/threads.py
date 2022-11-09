from PyQt5 import QtCore


class TrackerThread(QtCore.QThread):
    """
    Thread that runs the tracker without blocking the UI.
    """
    def __init__(self, tracker):
        super(TrackerThread, self).__init__()

        self.__tracker = tracker

    def run(self):

        # Run tracker
        self.__tracker.track()

        # Save the results
        print("Saving results...")
        self.__tracker.save()
        print("Done.")
