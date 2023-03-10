import pyqtgraph as pg
from pyqtgraph import PlotWidget, ViewBox
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QComboBox, QDialog

from pyminflux.reader import MinFluxReader
from pyminflux.state import State
from pyminflux.ui.ui_data_inspector import Ui_DataInspector


class DataInspector(QDialog, Ui_DataInspector):
    """
    A QDialog to display scatter plot of all possible pairs of measurements.
    """

    def __init__(self, processor, parent):

        # Call the base class
        super().__init__(parent=parent)

        # Initialize the dialog
        self.ui = Ui_DataInspector()
        self.ui.setupUi(self)

        # Constants
        self.brush = pg.mkBrush(255, 255, 255, 128)
        self.pen = pg.mkPen(None)

        # Keep a reference to the Processor
        self.__minfluxprocessor = processor

        # Add the values to the combo boxes
        self.ui.cbFirstParam.addItems(MinFluxReader.processed_properties())
        self.ui.cbFirstParam.setCurrentIndex(
            MinFluxReader.processed_properties().index("efo")
        )
        self.ui.cbSecondParam.addItems(MinFluxReader.processed_properties())
        self.ui.cbSecondParam.setCurrentIndex(
            MinFluxReader.processed_properties().index("cfr")
        )

        # Add the plot widget
        self.plot_widget = PlotWidget()
        self.scatter = pg.ScatterPlotItem(
            size=5,
            pen=self.pen,
            brush=self.brush,
            hoverable=True,
            hoverSymbol="s",
            hoverSize=5,
            hoverPen=pg.mkPen("w", width=2),
            hoverBrush=None,
            enableAutoRange=True,
        )
        self.customize_context_menu()
        self.plot_widget.addItem(self.scatter)
        self.plot_widget.showAxis("bottom")
        self.plot_widget.showAxis("left")
        self.ui.main_layout.addWidget(self.plot_widget)

        # Plot the first data pair
        self.plot_selected_params()

        # Add connections
        self.ui.pbPlot.clicked.connect(self.plot_selected_params)

    def customize_context_menu(self):
        """Remove some default context menu actions.

        See: https://stackoverflow.com/questions/44402399/how-to-disable-the-default-context-menu-of-pyqtgraph#44420152
        """

        # Hide the "Plot Options" menu
        self.plot_widget.getPlotItem().ctrlMenu.menuAction().setVisible(False)

    @Slot(None, name="plot_selected_params")
    def plot_selected_params(self):
        """Plot the requested parameters."""

        # Do we have something to plot?
        if self.__minfluxprocessor is None or self.__minfluxprocessor.num_values == 0:
            return

        # Update the scatter plot
        first = MinFluxReader.processed_properties()[
            self.ui.cbFirstParam.currentIndex()
        ]
        second = MinFluxReader.processed_properties()[
            self.ui.cbSecondParam.currentIndex()
        ]
        self.scatter.setData(
            x=self.__minfluxprocessor.filtered_dataframe[first],
            y=self.__minfluxprocessor.filtered_dataframe[second],
        )
        self.scatter.getViewBox().enableAutoRange(axis=ViewBox.XYAxes, enable=True)
        self.plot_widget.setLabel("bottom", text=first)
        self.plot_widget.setLabel("left", text=second)
