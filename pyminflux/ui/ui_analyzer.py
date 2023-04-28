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
## Form generated from reading UI file 'analyzer.ui'
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
    QCheckBox,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTabWidget,
    QWidget,
)


class Ui_Analyzer(object):
    def setupUi(self, Analyzer):
        if not Analyzer.objectName():
            Analyzer.setObjectName("Analyzer")
        Analyzer.resize(1050, 800)
        Analyzer.setMinimumSize(QSize(800, 600))
        self.gridLayout = QGridLayout(Analyzer)
        self.gridLayout.setObjectName("gridLayout")
        self.tabFilterOptions = QTabWidget(Analyzer)
        self.tabFilterOptions.setObjectName("tabFilterOptions")
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.tabFilterOptions.sizePolicy().hasHeightForWidth()
        )
        self.tabFilterOptions.setSizePolicy(sizePolicy)
        self.tabFilterOptions.setMaximumSize(QSize(16777215, 16777215))
        self.tab_efo_thresholding = QWidget()
        self.tab_efo_thresholding.setObjectName("tab_efo_thresholding")
        sizePolicy1 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(
            self.tab_efo_thresholding.sizePolicy().hasHeightForWidth()
        )
        self.tab_efo_thresholding.setSizePolicy(sizePolicy1)
        self.horizontalLayout_3 = QHBoxLayout(self.tab_efo_thresholding)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.hsEFOPeakBefore = QSpacerItem(
            20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout_3.addItem(self.hsEFOPeakBefore)

        self.lbEFOExpectedCutoff = QLabel(self.tab_efo_thresholding)
        self.lbEFOExpectedCutoff.setObjectName("lbEFOExpectedCutoff")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(
            self.lbEFOExpectedCutoff.sizePolicy().hasHeightForWidth()
        )
        self.lbEFOExpectedCutoff.setSizePolicy(sizePolicy2)

        self.horizontalLayout_3.addWidget(self.lbEFOExpectedCutoff)

        self.leEFOExpectedCutoff = QLineEdit(self.tab_efo_thresholding)
        self.leEFOExpectedCutoff.setObjectName("leEFOExpectedCutoff")
        sizePolicy2.setHeightForWidth(
            self.leEFOExpectedCutoff.sizePolicy().hasHeightForWidth()
        )
        self.leEFOExpectedCutoff.setSizePolicy(sizePolicy2)

        self.horizontalLayout_3.addWidget(self.leEFOExpectedCutoff)

        self.pbDetectCutoffFrequency = QPushButton(self.tab_efo_thresholding)
        self.pbDetectCutoffFrequency.setObjectName("pbDetectCutoffFrequency")
        sizePolicy2.setHeightForWidth(
            self.pbDetectCutoffFrequency.sizePolicy().hasHeightForWidth()
        )
        self.pbDetectCutoffFrequency.setSizePolicy(sizePolicy2)

        self.horizontalLayout_3.addWidget(self.pbDetectCutoffFrequency)

        self.pbEFORunFilter = QPushButton(self.tab_efo_thresholding)
        self.pbEFORunFilter.setObjectName("pbEFORunFilter")
        self.pbEFORunFilter.setEnabled(True)
        sizePolicy2.setHeightForWidth(
            self.pbEFORunFilter.sizePolicy().hasHeightForWidth()
        )
        self.pbEFORunFilter.setSizePolicy(sizePolicy2)

        self.horizontalLayout_3.addWidget(self.pbEFORunFilter)

        self.hshsEFOPeakAfter = QSpacerItem(
            20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout_3.addItem(self.hshsEFOPeakAfter)

        self.tabFilterOptions.addTab(self.tab_efo_thresholding, "")
        self.tab_cfr_thresholding = QWidget()
        self.tab_cfr_thresholding.setObjectName("tab_cfr_thresholding")
        sizePolicy1.setHeightForWidth(
            self.tab_cfr_thresholding.sizePolicy().hasHeightForWidth()
        )
        self.tab_cfr_thresholding.setSizePolicy(sizePolicy1)
        self.horizontalLayout_4 = QHBoxLayout(self.tab_cfr_thresholding)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.hsCFRFilterBefore = QSpacerItem(
            20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout_4.addItem(self.hsCFRFilterBefore)

        self.checkCFRLowerThreshold = QCheckBox(self.tab_cfr_thresholding)
        self.checkCFRLowerThreshold.setObjectName("checkCFRLowerThreshold")
        sizePolicy3 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(
            self.checkCFRLowerThreshold.sizePolicy().hasHeightForWidth()
        )
        self.checkCFRLowerThreshold.setSizePolicy(sizePolicy3)

        self.horizontalLayout_4.addWidget(self.checkCFRLowerThreshold)

        self.checkCFRUpperThreshold = QCheckBox(self.tab_cfr_thresholding)
        self.checkCFRUpperThreshold.setObjectName("checkCFRUpperThreshold")
        sizePolicy3.setHeightForWidth(
            self.checkCFRUpperThreshold.sizePolicy().hasHeightForWidth()
        )
        self.checkCFRUpperThreshold.setSizePolicy(sizePolicy3)

        self.horizontalLayout_4.addWidget(self.checkCFRUpperThreshold)

        self.lbCFRFilterThreshFactor = QLabel(self.tab_cfr_thresholding)
        self.lbCFRFilterThreshFactor.setObjectName("lbCFRFilterThreshFactor")
        sizePolicy2.setHeightForWidth(
            self.lbCFRFilterThreshFactor.sizePolicy().hasHeightForWidth()
        )
        self.lbCFRFilterThreshFactor.setSizePolicy(sizePolicy2)

        self.horizontalLayout_4.addWidget(self.lbCFRFilterThreshFactor)

        self.leCFRFilterThreshFactor = QLineEdit(self.tab_cfr_thresholding)
        self.leCFRFilterThreshFactor.setObjectName("leCFRFilterThreshFactor")
        sizePolicy2.setHeightForWidth(
            self.leCFRFilterThreshFactor.sizePolicy().hasHeightForWidth()
        )
        self.leCFRFilterThreshFactor.setSizePolicy(sizePolicy2)

        self.horizontalLayout_4.addWidget(self.leCFRFilterThreshFactor)

        self.pbCFRRunAutoThreshold = QPushButton(self.tab_cfr_thresholding)
        self.pbCFRRunAutoThreshold.setObjectName("pbCFRRunAutoThreshold")
        sizePolicy2.setHeightForWidth(
            self.pbCFRRunAutoThreshold.sizePolicy().hasHeightForWidth()
        )
        self.pbCFRRunAutoThreshold.setSizePolicy(sizePolicy2)

        self.horizontalLayout_4.addWidget(self.pbCFRRunAutoThreshold)

        self.pbCFRRunFilter = QPushButton(self.tab_cfr_thresholding)
        self.pbCFRRunFilter.setObjectName("pbCFRRunFilter")
        sizePolicy2.setHeightForWidth(
            self.pbCFRRunFilter.sizePolicy().hasHeightForWidth()
        )
        self.pbCFRRunFilter.setSizePolicy(sizePolicy2)

        self.horizontalLayout_4.addWidget(self.pbCFRRunFilter)

        self.hsCFRFilterAfter = QSpacerItem(
            20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout_4.addItem(self.hsCFRFilterAfter)

        self.tabFilterOptions.addTab(self.tab_cfr_thresholding, "")

        self.gridLayout.addWidget(self.tabFilterOptions, 0, 0, 1, 1)

        self.localizations_layout = QHBoxLayout()
        self.localizations_layout.setObjectName("localizations_layout")

        self.gridLayout.addLayout(self.localizations_layout, 3, 0, 1, 1)

        self.actions_layout = QHBoxLayout()
        self.actions_layout.setObjectName("actions_layout")
        self.pbReset = QPushButton(Analyzer)
        self.pbReset.setObjectName("pbReset")

        self.actions_layout.addWidget(self.pbReset)

        self.gridLayout.addLayout(self.actions_layout, 6, 0, 1, 1)

        self.parameters_layout = QHBoxLayout()
        self.parameters_layout.setObjectName("parameters_layout")

        self.gridLayout.addLayout(self.parameters_layout, 2, 0, 1, 1)

        self.communication_layout = QHBoxLayout()
        self.communication_layout.setObjectName("communication_layout")

        self.gridLayout.addLayout(self.communication_layout, 1, 0, 1, 1)

        self.retranslateUi(Analyzer)

        self.tabFilterOptions.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(Analyzer)

    # setupUi

    def retranslateUi(self, Analyzer):
        Analyzer.setWindowTitle(
            QCoreApplication.translate("Analyzer", "Analyzer", None)
        )
        self.lbEFOExpectedCutoff.setText(
            QCoreApplication.translate(
                "Analyzer", "Expected frequency of single emitters (Hz)", None
            )
        )
        self.leEFOExpectedCutoff.setText("")
        self.pbDetectCutoffFrequency.setText(
            QCoreApplication.translate("Analyzer", "Detect", None)
        )
        self.pbEFORunFilter.setText(
            QCoreApplication.translate("Analyzer", "Filter", None)
        )
        self.tabFilterOptions.setTabText(
            self.tabFilterOptions.indexOf(self.tab_efo_thresholding),
            QCoreApplication.translate("Analyzer", "EFO thresholding", None),
        )
        self.checkCFRLowerThreshold.setText(
            QCoreApplication.translate("Analyzer", "Lower bound", None)
        )
        self.checkCFRUpperThreshold.setText(
            QCoreApplication.translate("Analyzer", "Upper bound", None)
        )
        self.lbCFRFilterThreshFactor.setText(
            QCoreApplication.translate("Analyzer", "Threshold factor", None)
        )
        self.pbCFRRunAutoThreshold.setText(
            QCoreApplication.translate("Analyzer", "Threshold", None)
        )
        self.pbCFRRunFilter.setText(
            QCoreApplication.translate("Analyzer", "Filter", None)
        )
        self.tabFilterOptions.setTabText(
            self.tabFilterOptions.indexOf(self.tab_cfr_thresholding),
            QCoreApplication.translate("Analyzer", "CFR thresholding", None),
        )
        self.pbReset.setText(QCoreApplication.translate("Analyzer", "Reset", None))

    # retranslateUi
