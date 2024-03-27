# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'trace_stats_viewer.ui'
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
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class Ui_TraceStatsViewer(object):
    def setupUi(self, TraceStatsViewer):
        if not TraceStatsViewer.objectName():
            TraceStatsViewer.setObjectName("TraceStatsViewer")
        TraceStatsViewer.resize(1100, 600)
        self.verticalLayout_2 = QVBoxLayout(TraceStatsViewer)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.main_layout = QVBoxLayout()
        self.main_layout.setObjectName("main_layout")
        self.commands_layout = QHBoxLayout()
        self.commands_layout.setObjectName("commands_layout")
        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.commands_layout.addItem(self.horizontalSpacer)

        self.pbExport = QPushButton(TraceStatsViewer)
        self.pbExport.setObjectName("pbExport")

        self.commands_layout.addWidget(self.pbExport)

        self.horizontalSpacer_2 = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.commands_layout.addItem(self.horizontalSpacer_2)

        self.main_layout.addLayout(self.commands_layout)

        self.verticalLayout_2.addLayout(self.main_layout)

        self.retranslateUi(TraceStatsViewer)

        QMetaObject.connectSlotsByName(TraceStatsViewer)

    # setupUi

    def retranslateUi(self, TraceStatsViewer):
        TraceStatsViewer.setWindowTitle(
            QCoreApplication.translate("TraceStatsViewer", "Trace Stats Viewer", None)
        )
        self.pbExport.setText(
            QCoreApplication.translate("TraceStatsViewer", "Export", None)
        )

    # retranslateUi
