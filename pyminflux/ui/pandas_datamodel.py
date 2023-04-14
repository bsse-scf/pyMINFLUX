from PySide6 import QtCore
from PySide6.QtCore import Qt


class PandasDataModel(QtCore.QAbstractTableModel):
    """
    Class to populate a table view with a pandas dataframe
    """

    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                value = self._data.iloc[index.row(), index.column()]
                if self._data.columns[index.column()] in ["efo", "dwell"]:
                    return f"{int(value)}"
                if self._data.columns[index.column()] in ["x", "y", "z"]:
                    return f"{value:.1f}"
                if self._data.columns[index.column()] in ["cfr", "dcr"]:
                    return f"{value:.3f}"
                if isinstance(value, float):  # Check if the value is a float
                    return (
                        f"{value:.2f}"  # Format the float value with 2 decimal places
                    )
                return str(value)
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None
