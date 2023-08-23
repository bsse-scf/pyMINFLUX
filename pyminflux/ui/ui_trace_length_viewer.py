# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'trace_length_viewer.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
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
from PySide6.QtWidgets import QApplication, QDialog, QSizePolicy, QVBoxLayout, QWidget


class Ui_TraceLengthViewer(object):
    def setupUi(self, TraceLengthViewer):
        if not TraceLengthViewer.objectName():
            TraceLengthViewer.setObjectName("TraceLengthViewer")
        TraceLengthViewer.resize(800, 600)
        self.verticalLayout_2 = QVBoxLayout(TraceLengthViewer)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.main_layout = QVBoxLayout()
        self.main_layout.setObjectName("main_layout")

        self.verticalLayout_2.addLayout(self.main_layout)

        self.retranslateUi(TraceLengthViewer)

        QMetaObject.connectSlotsByName(TraceLengthViewer)

    # setupUi

    def retranslateUi(self, TraceLengthViewer):
        TraceLengthViewer.setWindowTitle(
            QCoreApplication.translate("TraceLengthViewer", "Trace Length Viewer", None)
        )

    # retranslateUi
