import pyqtgraph as pg
from pyqtgraph import PlotWidget, ViewBox
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget

from ..processor import MinFluxProcessor
from ..reader import MinFluxReader
from ..state import State
from .ui_main_plotter import Ui_MainPlotter


class MainPlotter(QWidget, Ui_MainPlotter):
    def __init__(self, parent=None):
        """Constructor."""

        # Call the base class
        super().__init__(parent=parent)

        # Initialize the dialog
        self.ui = Ui_MainPlotter()
        self.ui.setupUi(self)

        # Initialize state
        self.state = State()

        # Constants
        self.brush = pg.mkBrush(255, 255, 255, 128)
        self.pen = pg.mkPen(None)

        # Keep a reference to the Processor
        self.__minfluxprocessor = None

        # Add the values to the combo boxes
        self.ui.cbFirstParam.addItems(MinFluxReader.processed_properties())
        self.ui.cbFirstParam.setCurrentIndex(
            MinFluxReader.processed_properties().index("x")
        )
        self.ui.cbSecondParam.addItems(MinFluxReader.processed_properties())
        self.ui.cbSecondParam.setCurrentIndex(
            MinFluxReader.processed_properties().index("y")
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
        self.plot_widget.setBackground("w")
        self.customize_context_menu()
        self.ui.main_layout.removeItem(self.ui.verticalSpacer)
        self.plot_widget.addItem(self.scatter)
        self.plot_widget.hideAxis("bottom")
        self.plot_widget.hideAxis("left")
        self.ui.main_layout.addWidget(self.plot_widget)

        # Plot the first data pair
        self.plot_selected_params()

        # Add connections
        self.ui.pbPlot.clicked.connect(self.plot_selected_params)

    def clear(self):
        """Clear the plots."""
        if self.scatter is None:
            return
        self.scatter.setData(
            x=[],
            y=[],
        )

    def enableAutoRange(self, enable: bool):
        """Toggle axis anable auto range."""
        # Make sure to autoupdate the axis (on load only)
        self.plot_widget.getViewBox().enableAutoRange(
            axis=ViewBox.XYAxes, enable=enable
        )

    def customize_context_menu(self):
        """Remove some default context menu actions.

        See: https://stackoverflow.com/questions/44402399/how-to-disable-the-default-context-menu-of-pyqtgraph#44420152
        """

        # Hide the "Plot Options" menu
        self.plot_widget.getPlotItem().ctrlMenu.menuAction().setVisible(False)

    def set_processor(self, processor: MinFluxProcessor):
        """Set a reference to the processor when there is data to plot."""
        self.__minfluxprocessor = processor

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

        # If an only if the requested parameters are "x" and "y" (in any order),
        # we consider the State.plot_average_localisations property.
        if (first == "x" and second == "y") or (first == "y" and second == "x"):
            if self.state.plot_average_localisations:
                # Get the (potentially filtered) averaged dataframe
                dataframe = self.__minfluxprocessor.weighted_localizations
            else:
                # Get the (potentially filtered) full dataframe
                dataframe = self.__minfluxprocessor.filtered_dataframe
        else:
            # Get the (potentially filtered) full dataframe
            dataframe = self.__minfluxprocessor.filtered_dataframe

        # Extract values
        x = dataframe[first].values
        y = dataframe[second].values

        # Add the data points to the scatter plot
        self.scatter.setData(
            x=x,
            y=y,
        )
        self.plot_widget.getViewBox().enableAutoRange(axis=ViewBox.XYAxes, enable=True)
        self.plot_widget.showAxis("bottom")
        self.plot_widget.showAxis("left")
        self.plot_widget.setLabel("bottom", text=first)
        self.plot_widget.setLabel("left", text=second)
        self.plot_widget.setBackground("k")

        # Fix aspect ratio
        x_scale = (x.max() - x.min()) / (len(x) - 1)
        y_scale = (y.max() - y.min()) / (len(y) - 1)
        aspect_ratio = y_scale / x_scale
        self.plot_widget.getPlotItem().getViewBox().setAspectLocked(
            lock=True, ratio=aspect_ratio
        )
