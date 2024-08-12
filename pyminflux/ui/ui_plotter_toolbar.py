# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'plotter_toolbar.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    Qt,
    QTime,
    QUrl,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QWidget,
)


class Ui_PlotterToolbar(object):
    def setupUi(self, PlotterToolbar):
        if not PlotterToolbar.objectName():
            PlotterToolbar.setObjectName("PlotterToolbar")
        PlotterToolbar.resize(1077, 34)
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(PlotterToolbar.sizePolicy().hasHeightForWidth())
        PlotterToolbar.setSizePolicy(sizePolicy)
        self.horizontalLayout = QHBoxLayout(PlotterToolbar)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, 3, -1, 3)
        self.horizontalSpacer_2 = QSpacerItem(
            10, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.cbPlot3D = QCheckBox(PlotterToolbar)
        self.cbPlot3D.setObjectName("cbPlot3D")

        self.horizontalLayout.addWidget(self.cbPlot3D)

        self.cbProjection = QComboBox(PlotterToolbar)
        self.cbProjection.addItem("")
        self.cbProjection.addItem("")
        self.cbProjection.setObjectName("cbProjection")
        sizePolicy1 = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(
            self.cbProjection.sizePolicy().hasHeightForWidth()
        )
        self.cbProjection.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.cbProjection)

        self.lbOptions = QLabel(PlotterToolbar)
        self.lbOptions.setObjectName("lbOptions")

        self.horizontalLayout.addWidget(self.lbOptions)

        self.cbColorCodeSelector = QComboBox(PlotterToolbar)
        self.cbColorCodeSelector.addItem("")
        self.cbColorCodeSelector.addItem("")
        self.cbColorCodeSelector.addItem("")
        self.cbColorCodeSelector.addItem("")
        self.cbColorCodeSelector.addItem("")
        self.cbColorCodeSelector.setObjectName("cbColorCodeSelector")

        self.horizontalLayout.addWidget(self.cbColorCodeSelector)

        self.cbPlotAveragePos = QCheckBox(PlotterToolbar)
        self.cbPlotAveragePos.setObjectName("cbPlotAveragePos")

        self.horizontalLayout.addWidget(self.cbPlotAveragePos)

        self.line = QFrame(PlotterToolbar)
        self.line.setObjectName("line")
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout.addWidget(self.line)

        self.cbFirstParam = QComboBox(PlotterToolbar)
        self.cbFirstParam.setObjectName("cbFirstParam")
        sizePolicy.setHeightForWidth(self.cbFirstParam.sizePolicy().hasHeightForWidth())
        self.cbFirstParam.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.cbFirstParam)

        self.cbSecondParam = QComboBox(PlotterToolbar)
        self.cbSecondParam.setObjectName("cbSecondParam")
        sizePolicy.setHeightForWidth(
            self.cbSecondParam.sizePolicy().hasHeightForWidth()
        )
        self.cbSecondParam.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.cbSecondParam)

        self.pbPlot = QPushButton(PlotterToolbar)
        self.pbPlot.setObjectName("pbPlot")
        sizePolicy.setHeightForWidth(self.pbPlot.sizePolicy().hasHeightForWidth())
        self.pbPlot.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.pbPlot)

        self.horizontalSpacer_4 = QSpacerItem(
            10, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout.addItem(self.horizontalSpacer_4)

        self.retranslateUi(PlotterToolbar)

        QMetaObject.connectSlotsByName(PlotterToolbar)

    # setupUi

    def retranslateUi(self, PlotterToolbar):
        PlotterToolbar.setWindowTitle(
            QCoreApplication.translate("PlotterToolbar", "Form", None)
        )
        self.cbPlot3D.setText(QCoreApplication.translate("PlotterToolbar", "3D", None))
        self.cbProjection.setItemText(
            0, QCoreApplication.translate("PlotterToolbar", "Orthogonal", None)
        )
        self.cbProjection.setItemText(
            1,
            QCoreApplication.translate(
                "PlotterToolbar", "Perspective (45\u00b0)", None
            ),
        )

        self.lbOptions.setText(
            QCoreApplication.translate("PlotterToolbar", "Color-code by:", None)
        )
        self.cbColorCodeSelector.setItemText(
            0, QCoreApplication.translate("PlotterToolbar", "nothing", None)
        )
        self.cbColorCodeSelector.setItemText(
            1, QCoreApplication.translate("PlotterToolbar", "tid", None)
        )
        self.cbColorCodeSelector.setItemText(
            2, QCoreApplication.translate("PlotterToolbar", "fluorophore", None)
        )
        self.cbColorCodeSelector.setItemText(
            3, QCoreApplication.translate("PlotterToolbar", "depth", None)
        )
        self.cbColorCodeSelector.setItemText(
            4, QCoreApplication.translate("PlotterToolbar", "time", None)
        )

        self.cbPlotAveragePos.setText(
            QCoreApplication.translate("PlotterToolbar", "Avg Loc (TID)", None)
        )
        self.pbPlot.setText(QCoreApplication.translate("PlotterToolbar", "Plot", None))

    # retranslateUi
