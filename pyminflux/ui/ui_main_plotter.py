# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_plotter.ui'
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
    QLayout,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class Ui_MainPlotter(object):
    def setupUi(self, MainPlotter):
        if not MainPlotter.objectName():
            MainPlotter.setObjectName("MainPlotter")
        MainPlotter.resize(1127, 575)
        self.horizontalLayout = QHBoxLayout(MainPlotter)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.main_layout = QVBoxLayout()
        self.main_layout.setObjectName("main_layout")
        self.commands_layout = QHBoxLayout()
        self.commands_layout.setObjectName("commands_layout")
        self.commands_layout.setSizeConstraint(QLayout.SetMinimumSize)
        self.cbFluorophoreIndex = QComboBox(MainPlotter)
        self.cbFluorophoreIndex.addItem("")
        self.cbFluorophoreIndex.addItem("")
        self.cbFluorophoreIndex.setObjectName("cbFluorophoreIndex")

        self.commands_layout.addWidget(self.cbFluorophoreIndex)

        self.cbFirstParam = QComboBox(MainPlotter)
        self.cbFirstParam.setObjectName("cbFirstParam")

        self.commands_layout.addWidget(self.cbFirstParam)

        self.cbSecondParam = QComboBox(MainPlotter)
        self.cbSecondParam.setObjectName("cbSecondParam")

        self.commands_layout.addWidget(self.cbSecondParam)

        self.pbPlot = QPushButton(MainPlotter)
        self.pbPlot.setObjectName("pbPlot")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pbPlot.sizePolicy().hasHeightForWidth())
        self.pbPlot.setSizePolicy(sizePolicy)

        self.commands_layout.addWidget(self.pbPlot)

        self.main_layout.addLayout(self.commands_layout)

        self.verticalSpacer = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding
        )

        self.main_layout.addItem(self.verticalSpacer)

        self.horizontalLayout.addLayout(self.main_layout)

        self.retranslateUi(MainPlotter)

        QMetaObject.connectSlotsByName(MainPlotter)

    # setupUi

    def retranslateUi(self, MainPlotter):
        MainPlotter.setWindowTitle(
            QCoreApplication.translate("MainPlotter", "Form", None)
        )
        self.cbFluorophoreIndex.setItemText(
            0, QCoreApplication.translate("MainPlotter", "Fluorophore", None)
        )
        self.cbFluorophoreIndex.setItemText(
            1, QCoreApplication.translate("MainPlotter", "1", None)
        )

        self.pbPlot.setText(QCoreApplication.translate("MainPlotter", "Plot", None))

    # retranslateUi
