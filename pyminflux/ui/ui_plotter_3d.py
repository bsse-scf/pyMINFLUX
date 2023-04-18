# -*- coding: utf-8 -*-

#  Copyright (c) 2022 - 2023 D-BSSE, ETH Zurich. All rights reserved.

################################################################################
## Form generated from reading UI file 'plotter_3d.ui'
##
## Created by: Qt User Interface Compiler version 6.4.0
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
from PySide6.QtWidgets import QApplication, QDialog, QGridLayout, QSizePolicy, QWidget


class Ui_Plotter3D(object):
    def setupUi(self, Plotter3D):
        if not Plotter3D.objectName():
            Plotter3D.setObjectName("Plotter3D")
        Plotter3D.resize(800, 600)
        self.gridLayout_2 = QGridLayout(Plotter3D)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.mainLayout = QGridLayout()
        self.mainLayout.setObjectName("mainLayout")

        self.gridLayout_2.addLayout(self.mainLayout, 0, 0, 1, 1)

        self.retranslateUi(Plotter3D)

        QMetaObject.connectSlotsByName(Plotter3D)

    # setupUi

    def retranslateUi(self, Plotter3D):
        Plotter3D.setWindowTitle(
            QCoreApplication.translate("Plotter3D", "Plotter 3D", None)
        )

    # retranslateUi
