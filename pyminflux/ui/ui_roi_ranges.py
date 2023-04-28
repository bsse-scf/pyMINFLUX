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
## Form generated from reading UI file 'roi_ranges.ui'
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
    QAbstractButton,
    QApplication,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QSpacerItem,
    QWidget,
)


class Ui_ROIRanges(object):
    def setupUi(self, ROIRanges):
        if not ROIRanges.objectName():
            ROIRanges.setObjectName("ROIRanges")
        ROIRanges.resize(390, 140)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ROIRanges.sizePolicy().hasHeightForWidth())
        ROIRanges.setSizePolicy(sizePolicy)
        ROIRanges.setMaximumSize(QSize(16777215, 16777215))
        self.gridLayout = QGridLayout(ROIRanges)
        self.gridLayout.setObjectName("gridLayout")
        self.buttonBox = QDialogButtonBox(ROIRanges)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(
            20, 5, QSizePolicy.Minimum, QSizePolicy.Expanding
        )

        self.gridLayout.addItem(self.verticalSpacer, 3, 0, 1, 1)

        self.efo_layout = QHBoxLayout()
        self.efo_layout.setObjectName("efo_layout")
        self.lbEFO = QLabel(ROIRanges)
        self.lbEFO.setObjectName("lbEFO")

        self.efo_layout.addWidget(self.lbEFO)

        self.efo_spacer = QSpacerItem(40, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.efo_layout.addItem(self.efo_spacer)

        self.lbEFOMin = QLabel(ROIRanges)
        self.lbEFOMin.setObjectName("lbEFOMin")

        self.efo_layout.addWidget(self.lbEFOMin)

        self.leEFOMin = QLineEdit(ROIRanges)
        self.leEFOMin.setObjectName("leEFOMin")

        self.efo_layout.addWidget(self.leEFOMin)

        self.lbEFOMax = QLabel(ROIRanges)
        self.lbEFOMax.setObjectName("lbEFOMax")

        self.efo_layout.addWidget(self.lbEFOMax)

        self.leEFOMax = QLineEdit(ROIRanges)
        self.leEFOMax.setObjectName("leEFOMax")

        self.efo_layout.addWidget(self.leEFOMax)

        self.gridLayout.addLayout(self.efo_layout, 2, 0, 1, 1)

        self.cfr_layout = QHBoxLayout()
        self.cfr_layout.setObjectName("cfr_layout")
        self.lbCFR = QLabel(ROIRanges)
        self.lbCFR.setObjectName("lbCFR")

        self.cfr_layout.addWidget(self.lbCFR)

        self.cfr_spacer = QSpacerItem(40, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.cfr_layout.addItem(self.cfr_spacer)

        self.lbMinCFR = QLabel(ROIRanges)
        self.lbMinCFR.setObjectName("lbMinCFR")

        self.cfr_layout.addWidget(self.lbMinCFR)

        self.leCFRMin = QLineEdit(ROIRanges)
        self.leCFRMin.setObjectName("leCFRMin")

        self.cfr_layout.addWidget(self.leCFRMin)

        self.lbCFRMax = QLabel(ROIRanges)
        self.lbCFRMax.setObjectName("lbCFRMax")

        self.cfr_layout.addWidget(self.lbCFRMax)

        self.leCFRMax = QLineEdit(ROIRanges)
        self.leCFRMax.setObjectName("leCFRMax")

        self.cfr_layout.addWidget(self.leCFRMax)

        self.gridLayout.addLayout(self.cfr_layout, 1, 0, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(
            20, 5, QSizePolicy.Minimum, QSizePolicy.Expanding
        )

        self.gridLayout.addItem(self.verticalSpacer_2, 0, 0, 1, 1)

        self.retranslateUi(ROIRanges)
        self.buttonBox.accepted.connect(ROIRanges.accept)
        self.buttonBox.rejected.connect(ROIRanges.reject)

        QMetaObject.connectSlotsByName(ROIRanges)

    # setupUi

    def retranslateUi(self, ROIRanges):
        self.lbEFO.setText(QCoreApplication.translate("ROIRanges", "EFO", None))
        self.lbEFOMin.setText(QCoreApplication.translate("ROIRanges", "min", None))
        self.lbEFOMax.setText(QCoreApplication.translate("ROIRanges", "max", None))
        self.lbCFR.setText(QCoreApplication.translate("ROIRanges", "CFR", None))
        self.lbMinCFR.setText(QCoreApplication.translate("ROIRanges", "min", None))
        self.lbCFRMax.setText(QCoreApplication.translate("ROIRanges", "max", None))
        pass

    # retranslateUi
