# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'histogram_viewer.ui'
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
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QSizePolicy,
    QWidget,
)


class Ui_HistogramViewer(object):
    def setupUi(self, HistogramViewer):
        if not HistogramViewer.objectName():
            HistogramViewer.setObjectName("HistogramViewer")
        HistogramViewer.resize(1191, 1087)
        self.gridLayout = QGridLayout(HistogramViewer)
        self.gridLayout.setObjectName("gridLayout")
        self.parameters_layout = QHBoxLayout()
        self.parameters_layout.setObjectName("parameters_layout")

        self.gridLayout.addLayout(self.parameters_layout, 0, 0, 1, 1)

        self.localizations_layout = QHBoxLayout()
        self.localizations_layout.setObjectName("localizations_layout")

        self.gridLayout.addLayout(self.localizations_layout, 1, 0, 1, 1)

        self.controls_layouts = QHBoxLayout()
        self.controls_layouts.setObjectName("controls_layouts")

        self.gridLayout.addLayout(self.controls_layouts, 2, 0, 1, 1)

        self.retranslateUi(HistogramViewer)

        QMetaObject.connectSlotsByName(HistogramViewer)

    # setupUi

    def retranslateUi(self, HistogramViewer):
        HistogramViewer.setWindowTitle(
            QCoreApplication.translate("HistogramViewer", "Histogram Viewer", None)
        )

    # retranslateUi