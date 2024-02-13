# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'histogram_plotter.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QGridLayout,
    QHBoxLayout, QLabel, QLayout, QPushButton,
    QSizePolicy, QSpacerItem, QWidget)

class Ui_HistogramPlotter(object):
    def setupUi(self, HistogramPlotter):
        if not HistogramPlotter.objectName():
            HistogramPlotter.setObjectName(u"HistogramPlotter")
        HistogramPlotter.resize(800, 600)
        HistogramPlotter.setMinimumSize(QSize(800, 600))
        self.gridLayout = QGridLayout(HistogramPlotter)
        self.gridLayout.setObjectName(u"gridLayout")
        self.hlParameters = QHBoxLayout()
        self.hlParameters.setObjectName(u"hlParameters")
        self.hlParameters.setSizeConstraint(QLayout.SetFixedSize)
        self.hsCFRFilterBefore = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hlParameters.addItem(self.hsCFRFilterBefore)

        self.lbParameter = QLabel(HistogramPlotter)
        self.lbParameter.setObjectName(u"lbParameter")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbParameter.sizePolicy().hasHeightForWidth())
        self.lbParameter.setSizePolicy(sizePolicy)

        self.hlParameters.addWidget(self.lbParameter)

        self.cbParam = QComboBox(HistogramPlotter)
        self.cbParam.setObjectName(u"cbParam")

        self.hlParameters.addWidget(self.cbParam)

        self.pbPlotHistogram = QPushButton(HistogramPlotter)
        self.pbPlotHistogram.setObjectName(u"pbPlotHistogram")
        sizePolicy.setHeightForWidth(self.pbPlotHistogram.sizePolicy().hasHeightForWidth())
        self.pbPlotHistogram.setSizePolicy(sizePolicy)

        self.hlParameters.addWidget(self.pbPlotHistogram)

        self.hsCFRFilterAfter = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hlParameters.addItem(self.hsCFRFilterAfter)


        self.gridLayout.addLayout(self.hlParameters, 0, 0, 1, 1)

        self.hlPlot = QHBoxLayout()
        self.hlPlot.setObjectName(u"hlPlot")

        self.gridLayout.addLayout(self.hlPlot, 1, 0, 1, 1)


        self.retranslateUi(HistogramPlotter)

        QMetaObject.connectSlotsByName(HistogramPlotter)
    # setupUi

    def retranslateUi(self, HistogramPlotter):
        HistogramPlotter.setWindowTitle(QCoreApplication.translate("HistogramPlotter", u"Histogram Plotter", None))
        self.lbParameter.setText(QCoreApplication.translate("HistogramPlotter", u"Parameter", None))
        self.pbPlotHistogram.setText(QCoreApplication.translate("HistogramPlotter", u"Plot", None))
    # retranslateUi

