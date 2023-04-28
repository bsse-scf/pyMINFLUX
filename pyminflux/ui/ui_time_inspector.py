# -*- coding: utf-8 -*-

#  Copyright (c) 2022 - 2023 D-BSSE, ETH Zurich.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#   limitations under the License.
#

################################################################################
## Form generated from reading UI file 'time_inspector.ui'
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
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class Ui_TimeInspector(object):
    def setupUi(self, TimeInspector):
        if not TimeInspector.objectName():
            TimeInspector.setObjectName("TimeInspector")
        TimeInspector.resize(800, 600)
        self.verticalLayout_2 = QVBoxLayout(TimeInspector)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.main_layout = QVBoxLayout()
        self.main_layout.setObjectName("main_layout")
        self.commands_layout = QHBoxLayout()
        self.commands_layout.setObjectName("commands_layout")
        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.commands_layout.addItem(self.horizontalSpacer)

        self.cbAnalysisSelection = QComboBox(TimeInspector)
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

        self.pbPlot = QPushButton(TimeInspector)
        self.pbPlot.setObjectName("pbPlot")

        self.commands_layout.addWidget(self.pbPlot)

        self.horizontalSpacer_2 = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.commands_layout.addItem(self.horizontalSpacer_2)

        self.lbSelectionActions = QLabel(TimeInspector)
        self.lbSelectionActions.setObjectName("lbSelectionActions")

        self.commands_layout.addWidget(self.lbSelectionActions)

        self.pbAreaToggleVisibility = QPushButton(TimeInspector)
        self.pbAreaToggleVisibility.setObjectName("pbAreaToggleVisibility")

        self.commands_layout.addWidget(self.pbAreaToggleVisibility)

        self.pbSelectionKeepData = QPushButton(TimeInspector)
        self.pbSelectionKeepData.setObjectName("pbSelectionKeepData")

        self.commands_layout.addWidget(self.pbSelectionKeepData)

        self.pbSelectionCropData = QPushButton(TimeInspector)
        self.pbSelectionCropData.setObjectName("pbSelectionCropData")

        self.commands_layout.addWidget(self.pbSelectionCropData)

        self.main_layout.addLayout(self.commands_layout)

        self.verticalLayout_2.addLayout(self.main_layout)

        self.retranslateUi(TimeInspector)

        QMetaObject.connectSlotsByName(TimeInspector)

    # setupUi

    def retranslateUi(self, TimeInspector):
        TimeInspector.setWindowTitle(
            QCoreApplication.translate("TimeInspector", "Time Inspector", None)
        )
        self.cbAnalysisSelection.setItemText(
            0,
            QCoreApplication.translate(
                "TimeInspector", "Localization number per minute", None
            ),
        )
        self.cbAnalysisSelection.setItemText(
            1,
            QCoreApplication.translate(
                "TimeInspector", "Localization precision per minute", None
            ),
        )
        self.cbAnalysisSelection.setItemText(
            2,
            QCoreApplication.translate(
                "TimeInspector", "Localization precision per minute (std err)", None
            ),
        )

        self.pbPlot.setText(QCoreApplication.translate("TimeInspector", "Plot", None))
        self.lbSelectionActions.setText(
            QCoreApplication.translate("TimeInspector", "Selection", None)
        )
        self.pbAreaToggleVisibility.setText(
            QCoreApplication.translate("TimeInspector", "Hide", None)
        )
        self.pbSelectionKeepData.setText(
            QCoreApplication.translate("TimeInspector", "Keep data", None)
        )
        self.pbSelectionCropData.setText(
            QCoreApplication.translate("TimeInspector", "Drop data", None)
        )

    # retranslateUi
