# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'plotter_toolbar.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
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
    QComboBox,
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
        PlotterToolbar.resize(791, 31)
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(PlotterToolbar.sizePolicy().hasHeightForWidth())
        PlotterToolbar.setSizePolicy(sizePolicy)
        self.horizontalLayout = QHBoxLayout(PlotterToolbar)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, 3, -1, 3)
        self.lbFluorophoreIndex = QLabel(PlotterToolbar)
        self.lbFluorophoreIndex.setObjectName("lbFluorophoreIndex")
        self.lbFluorophoreIndex.setEnabled(True)
        self.lbFluorophoreIndex.setAlignment(
            Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter
        )

        self.horizontalLayout.addWidget(self.lbFluorophoreIndex)

        self.cbFluorophoreIndex = QComboBox(PlotterToolbar)
        self.cbFluorophoreIndex.addItem("")
        self.cbFluorophoreIndex.setObjectName("cbFluorophoreIndex")
        sizePolicy1 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(
            self.cbFluorophoreIndex.sizePolicy().hasHeightForWidth()
        )
        self.cbFluorophoreIndex.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.cbFluorophoreIndex)

        self.pbDetectFluorophores = QPushButton(PlotterToolbar)
        self.pbDetectFluorophores.setObjectName("pbDetectFluorophores")
        self.pbDetectFluorophores.setEnabled(True)
        sizePolicy1.setHeightForWidth(
            self.pbDetectFluorophores.sizePolicy().hasHeightForWidth()
        )
        self.pbDetectFluorophores.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.pbDetectFluorophores)

        self.horizontalSpacer_3 = QSpacerItem(
            60, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout.addItem(self.horizontalSpacer_3)

        self.cbFirstParam = QComboBox(PlotterToolbar)
        self.cbFirstParam.setObjectName("cbFirstParam")
        sizePolicy1.setHeightForWidth(
            self.cbFirstParam.sizePolicy().hasHeightForWidth()
        )
        self.cbFirstParam.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.cbFirstParam)

        self.cbSecondParam = QComboBox(PlotterToolbar)
        self.cbSecondParam.setObjectName("cbSecondParam")
        sizePolicy1.setHeightForWidth(
            self.cbSecondParam.sizePolicy().hasHeightForWidth()
        )
        self.cbSecondParam.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.cbSecondParam)

        self.pbPlot = QPushButton(PlotterToolbar)
        self.pbPlot.setObjectName("pbPlot")
        sizePolicy1.setHeightForWidth(self.pbPlot.sizePolicy().hasHeightForWidth())
        self.pbPlot.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.pbPlot)

        self.retranslateUi(PlotterToolbar)

        QMetaObject.connectSlotsByName(PlotterToolbar)

    # setupUi

    def retranslateUi(self, PlotterToolbar):
        PlotterToolbar.setWindowTitle(
            QCoreApplication.translate("PlotterToolbar", "Form", None)
        )
        self.lbFluorophoreIndex.setText(
            QCoreApplication.translate("PlotterToolbar", "Fluorophore", None)
        )
        self.cbFluorophoreIndex.setItemText(
            0, QCoreApplication.translate("PlotterToolbar", "All", None)
        )

        self.pbDetectFluorophores.setText(
            QCoreApplication.translate("PlotterToolbar", "Detect", None)
        )
        self.pbPlot.setText(QCoreApplication.translate("PlotterToolbar", "Plot", None))

    # retranslateUi
