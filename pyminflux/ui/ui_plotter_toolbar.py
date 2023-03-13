# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'plotter_toolbar.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
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
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QSpacerItem, QWidget)

class Ui_PlotterToolbar(object):
    def setupUi(self, PlotterToolbar):
        if not PlotterToolbar.objectName():
            PlotterToolbar.setObjectName(u"PlotterToolbar")
        PlotterToolbar.resize(791, 31)
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(PlotterToolbar.sizePolicy().hasHeightForWidth())
        PlotterToolbar.setSizePolicy(sizePolicy)
        self.horizontalLayout = QHBoxLayout(PlotterToolbar)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, 3, -1, 3)
        self.horizontalSpacer = QSpacerItem(106, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.lbFluorophoreIndex = QLabel(PlotterToolbar)
        self.lbFluorophoreIndex.setObjectName(u"lbFluorophoreIndex")
        self.lbFluorophoreIndex.setEnabled(True)
        self.lbFluorophoreIndex.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout.addWidget(self.lbFluorophoreIndex)

        self.cbFluorophoreIndex = QComboBox(PlotterToolbar)
        self.cbFluorophoreIndex.addItem("")
        self.cbFluorophoreIndex.setObjectName(u"cbFluorophoreIndex")

        self.horizontalLayout.addWidget(self.cbFluorophoreIndex)

        self.pbAssignFluorophores = QPushButton(PlotterToolbar)
        self.pbAssignFluorophores.setObjectName(u"pbAssignFluorophores")
        self.pbAssignFluorophores.setEnabled(False)

        self.horizontalLayout.addWidget(self.pbAssignFluorophores)

        self.horizontalSpacer_3 = QSpacerItem(105, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_3)

        self.cbFirstParam = QComboBox(PlotterToolbar)
        self.cbFirstParam.setObjectName(u"cbFirstParam")

        self.horizontalLayout.addWidget(self.cbFirstParam)

        self.cbSecondParam = QComboBox(PlotterToolbar)
        self.cbSecondParam.setObjectName(u"cbSecondParam")

        self.horizontalLayout.addWidget(self.cbSecondParam)

        self.pbPlot = QPushButton(PlotterToolbar)
        self.pbPlot.setObjectName(u"pbPlot")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.pbPlot.sizePolicy().hasHeightForWidth())
        self.pbPlot.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.pbPlot)

        self.horizontalSpacer_2 = QSpacerItem(106, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)


        self.retranslateUi(PlotterToolbar)

        QMetaObject.connectSlotsByName(PlotterToolbar)
    # setupUi

    def retranslateUi(self, PlotterToolbar):
        PlotterToolbar.setWindowTitle(QCoreApplication.translate("PlotterToolbar", u"Form", None))
        self.lbFluorophoreIndex.setText(QCoreApplication.translate("PlotterToolbar", u"Fluorophore", None))
        self.cbFluorophoreIndex.setItemText(0, QCoreApplication.translate("PlotterToolbar", u"1", None))

        self.pbAssignFluorophores.setText(QCoreApplication.translate("PlotterToolbar", u"Assign", None))
        self.pbPlot.setText(QCoreApplication.translate("PlotterToolbar", u"Plot", None))
    # retranslateUi

