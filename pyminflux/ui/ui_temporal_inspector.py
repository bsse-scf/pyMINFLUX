# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'temporal_inspector.ui'
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
    QComboBox,
    QDialog,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class Ui_TemporalInspector(object):
    def setupUi(self, TemporalInspector):
        if not TemporalInspector.objectName():
            TemporalInspector.setObjectName("TemporalInspector")
        TemporalInspector.resize(800, 600)
        self.verticalLayout_2 = QVBoxLayout(TemporalInspector)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.main_layout = QVBoxLayout()
        self.main_layout.setObjectName("main_layout")
        self.commands_layout = QHBoxLayout()
        self.commands_layout.setObjectName("commands_layout")
        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.commands_layout.addItem(self.horizontalSpacer)

        self.cbAnalysisSelection = QComboBox(TemporalInspector)
        self.cbAnalysisSelection.addItem("")
        self.cbAnalysisSelection.addItem("")
        self.cbAnalysisSelection.addItem("")
        self.cbAnalysisSelection.setObjectName("cbAnalysisSelection")
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.cbAnalysisSelection.sizePolicy().hasHeightForWidth()
        )
        self.cbAnalysisSelection.setSizePolicy(sizePolicy)

        self.commands_layout.addWidget(self.cbAnalysisSelection)

        self.pbPlot = QPushButton(TemporalInspector)
        self.pbPlot.setObjectName("pbPlot")

        self.commands_layout.addWidget(self.pbPlot)

        self.horizontalSpacer_2 = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.commands_layout.addItem(self.horizontalSpacer_2)

        self.main_layout.addLayout(self.commands_layout)

        self.verticalLayout_2.addLayout(self.main_layout)

        self.retranslateUi(TemporalInspector)

        QMetaObject.connectSlotsByName(TemporalInspector)

    # setupUi

    def retranslateUi(self, TemporalInspector):
        TemporalInspector.setWindowTitle(
            QCoreApplication.translate("TemporalInspector", "Temporal Inspector", None)
        )
        self.cbAnalysisSelection.setItemText(
            0,
            QCoreApplication.translate(
                "TemporalInspector", "Localization number per minute", None
            ),
        )
        self.cbAnalysisSelection.setItemText(
            1,
            QCoreApplication.translate(
                "TemporalInspector", "Localization precision per minute", None
            ),
        )
        self.cbAnalysisSelection.setItemText(
            2,
            QCoreApplication.translate(
                "TemporalInspector", "Localization precision per minute (std err)", None
            ),
        )

        self.pbPlot.setText(
            QCoreApplication.translate("TemporalInspector", "Plot", None)
        )

    # retranslateUi
