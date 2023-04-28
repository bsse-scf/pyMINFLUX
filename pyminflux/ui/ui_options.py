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
## Form generated from reading UI file 'options.ui'
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
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QWidget,
)


class Ui_Options(object):
    def setupUi(self, Options):
        if not Options.objectName():
            Options.setObjectName("Options")
        Options.resize(575, 331)
        self.gridLayout = QGridLayout(Options)
        self.gridLayout.setObjectName("gridLayout")
        self.lbInfo = QLabel(Options)
        self.lbInfo.setObjectName("lbInfo")
        font = QFont()
        font.setItalic(True)
        self.lbInfo.setFont(font)

        self.gridLayout.addWidget(self.lbInfo, 6, 0, 1, 1)

        self.hlEFORange = QHBoxLayout()
        self.hlEFORange.setObjectName("hlEFORange")
        self.lbEFORange = QLabel(Options)
        self.lbEFORange.setObjectName("lbEFORange")

        self.hlEFORange.addWidget(self.lbEFORange)

        self.hsEFORange = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.hlEFORange.addItem(self.hsEFORange)

        self.leEFORangeMin = QLineEdit(Options)
        self.leEFORangeMin.setObjectName("leEFORangeMin")
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.leEFORangeMin.sizePolicy().hasHeightForWidth()
        )
        self.leEFORangeMin.setSizePolicy(sizePolicy)

        self.hlEFORange.addWidget(self.leEFORangeMin)

        self.leEFORangeMax = QLineEdit(Options)
        self.leEFORangeMax.setObjectName("leEFORangeMax")
        sizePolicy.setHeightForWidth(
            self.leEFORangeMax.sizePolicy().hasHeightForWidth()
        )
        self.leEFORangeMax.setSizePolicy(sizePolicy)

        self.hlEFORange.addWidget(self.leEFORangeMax)

        self.gridLayout.addLayout(self.hlEFORange, 3, 0, 1, 1)

        self.hlCFRRange = QHBoxLayout()
        self.hlCFRRange.setObjectName("hlCFRRange")
        self.lbCFRRange = QLabel(Options)
        self.lbCFRRange.setObjectName("lbCFRRange")

        self.hlCFRRange.addWidget(self.lbCFRRange)

        self.hsCFRRange = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.hlCFRRange.addItem(self.hsCFRRange)

        self.leCFRRangeMin = QLineEdit(Options)
        self.leCFRRangeMin.setObjectName("leCFRRangeMin")
        sizePolicy.setHeightForWidth(
            self.leCFRRangeMin.sizePolicy().hasHeightForWidth()
        )
        self.leCFRRangeMin.setSizePolicy(sizePolicy)

        self.hlCFRRange.addWidget(self.leCFRRangeMin)

        self.leCFRRangeMax = QLineEdit(Options)
        self.leCFRRangeMax.setObjectName("leCFRRangeMax")
        sizePolicy.setHeightForWidth(
            self.leCFRRangeMax.sizePolicy().hasHeightForWidth()
        )
        self.leCFRRangeMax.setSizePolicy(sizePolicy)

        self.hlCFRRange.addWidget(self.leCFRRangeMax)

        self.gridLayout.addLayout(self.hlCFRRange, 4, 0, 1, 1)

        self.lbInfoImmediate = QLabel(Options)
        self.lbInfoImmediate.setObjectName("lbInfoImmediate")
        self.lbInfoImmediate.setFont(font)

        self.gridLayout.addWidget(self.lbInfoImmediate, 8, 0, 1, 1)

        self.cbWeightAvgLocByECO = QCheckBox(Options)
        self.cbWeightAvgLocByECO.setObjectName("cbWeightAvgLocByECO")

        self.gridLayout.addWidget(self.cbWeightAvgLocByECO, 9, 0, 1, 1)

        self.pbSetDefault = QPushButton(Options)
        self.pbSetDefault.setObjectName("pbSetDefault")

        self.gridLayout.addWidget(self.pbSetDefault, 11, 0, 1, 1)

        self.hlEFOBinSize = QHBoxLayout()
        self.hlEFOBinSize.setObjectName("hlEFOBinSize")
        self.lbEFOBinSize = QLabel(Options)
        self.lbEFOBinSize.setObjectName("lbEFOBinSize")

        self.hlEFOBinSize.addWidget(self.lbEFOBinSize)

        self.hsEFOBinSize = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.hlEFOBinSize.addItem(self.hsEFOBinSize)

        self.leEFOBinSize = QLineEdit(Options)
        self.leEFOBinSize.setObjectName("leEFOBinSize")
        sizePolicy.setHeightForWidth(self.leEFOBinSize.sizePolicy().hasHeightForWidth())
        self.leEFOBinSize.setSizePolicy(sizePolicy)

        self.hlEFOBinSize.addWidget(self.leEFOBinSize)

        self.gridLayout.addLayout(self.hlEFOBinSize, 1, 0, 1, 1)

        self.hlExpectedEFOFrequency = QHBoxLayout()
        self.hlExpectedEFOFrequency.setObjectName("hlExpectedEFOFrequency")
        self.lbEFOSingleEmitterFrequency = QLabel(Options)
        self.lbEFOSingleEmitterFrequency.setObjectName("lbEFOSingleEmitterFrequency")

        self.hlExpectedEFOFrequency.addWidget(self.lbEFOSingleEmitterFrequency)

        self.hsEFOSingleEmitterFrequency = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.hlExpectedEFOFrequency.addItem(self.hsEFOSingleEmitterFrequency)

        self.leEFOSingleEmitterFrequency = QLineEdit(Options)
        self.leEFOSingleEmitterFrequency.setObjectName("leEFOSingleEmitterFrequency")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(
            self.leEFOSingleEmitterFrequency.sizePolicy().hasHeightForWidth()
        )
        self.leEFOSingleEmitterFrequency.setSizePolicy(sizePolicy1)

        self.hlExpectedEFOFrequency.addWidget(self.leEFOSingleEmitterFrequency)

        self.gridLayout.addLayout(self.hlExpectedEFOFrequency, 2, 0, 1, 1)

        self.line = QFrame(Options)
        self.line.setObjectName("line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.gridLayout.addWidget(self.line, 7, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding
        )

        self.gridLayout.addItem(self.verticalSpacer, 10, 0, 1, 1)

        self.hlMinNumTraces = QHBoxLayout()
        self.hlMinNumTraces.setObjectName("hlMinNumTraces")
        self.lbMinTIDNum = QLabel(Options)
        self.lbMinTIDNum.setObjectName("lbMinTIDNum")

        self.hlMinNumTraces.addWidget(self.lbMinTIDNum)

        self.hsMinTIDNum = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.hlMinNumTraces.addItem(self.hsMinTIDNum)

        self.leMinTIDNum = QLineEdit(Options)
        self.leMinTIDNum.setObjectName("leMinTIDNum")
        sizePolicy.setHeightForWidth(self.leMinTIDNum.sizePolicy().hasHeightForWidth())
        self.leMinTIDNum.setSizePolicy(sizePolicy)

        self.hlMinNumTraces.addWidget(self.leMinTIDNum)

        self.gridLayout.addLayout(self.hlMinNumTraces, 0, 0, 1, 1)

        self.hlLocPrecRange = QHBoxLayout()
        self.hlLocPrecRange.setObjectName("hlLocPrecRange")
        self.lbLocPrecRange = QLabel(Options)
        self.lbLocPrecRange.setObjectName("lbLocPrecRange")

        self.hlLocPrecRange.addWidget(self.lbLocPrecRange)

        self.hsLocPrecRange = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.hlLocPrecRange.addItem(self.hsLocPrecRange)

        self.leLocPrecRangeMin = QLineEdit(Options)
        self.leLocPrecRangeMin.setObjectName("leLocPrecRangeMin")
        sizePolicy.setHeightForWidth(
            self.leLocPrecRangeMin.sizePolicy().hasHeightForWidth()
        )
        self.leLocPrecRangeMin.setSizePolicy(sizePolicy)

        self.hlLocPrecRange.addWidget(self.leLocPrecRangeMin)

        self.leLocPrecRangeMax = QLineEdit(Options)
        self.leLocPrecRangeMax.setObjectName("leLocPrecRangeMax")
        sizePolicy.setHeightForWidth(
            self.leLocPrecRangeMax.sizePolicy().hasHeightForWidth()
        )
        self.leLocPrecRangeMax.setSizePolicy(sizePolicy)

        self.hlLocPrecRange.addWidget(self.leLocPrecRangeMax)

        self.gridLayout.addLayout(self.hlLocPrecRange, 5, 0, 1, 1)

        QWidget.setTabOrder(self.leMinTIDNum, self.leEFOBinSize)
        QWidget.setTabOrder(self.leEFOBinSize, self.leEFOSingleEmitterFrequency)
        QWidget.setTabOrder(self.leEFOSingleEmitterFrequency, self.leEFORangeMin)
        QWidget.setTabOrder(self.leEFORangeMin, self.leEFORangeMax)
        QWidget.setTabOrder(self.leEFORangeMax, self.leCFRRangeMin)
        QWidget.setTabOrder(self.leCFRRangeMin, self.leCFRRangeMax)
        QWidget.setTabOrder(self.leCFRRangeMax, self.leLocPrecRangeMin)
        QWidget.setTabOrder(self.leLocPrecRangeMin, self.leLocPrecRangeMax)
        QWidget.setTabOrder(self.leLocPrecRangeMax, self.cbWeightAvgLocByECO)
        QWidget.setTabOrder(self.cbWeightAvgLocByECO, self.pbSetDefault)

        self.retranslateUi(Options)

        QMetaObject.connectSlotsByName(Options)

    # setupUi

    def retranslateUi(self, Options):
        Options.setWindowTitle(QCoreApplication.translate("Options", "Options", None))
        self.lbInfo.setText(
            QCoreApplication.translate(
                "Options",
                "Changes above will be applied when loading new data or when filtering in the Analyzer.",
                None,
            )
        )
        self.lbEFORange.setText(
            QCoreApplication.translate("Options", "EFO default plot range", None)
        )
        self.lbCFRRange.setText(
            QCoreApplication.translate("Options", "CFR default plot range", None)
        )
        self.lbInfoImmediate.setText(
            QCoreApplication.translate(
                "Options",
                "Changes below will be applied immediately to all open views.",
                None,
            )
        )
        self.cbWeightAvgLocByECO.setText(
            QCoreApplication.translate(
                "Options",
                "Use relative ECO count for weighted average localization calculation",
                None,
            )
        )
        self.pbSetDefault.setText(
            QCoreApplication.translate("Options", "Set as new default", None)
        )
        self.lbEFOBinSize.setText(
            QCoreApplication.translate(
                "Options", "EFO bin size (Hz): set to 0 for automatic estimation", None
            )
        )
        self.lbEFOSingleEmitterFrequency.setText(
            QCoreApplication.translate(
                "Options", "EFO expected frequency for single emitters (Hz)", None
            )
        )
        self.lbMinTIDNum.setText(
            QCoreApplication.translate(
                "Options", "Minimum number of trace localizations", None
            )
        )
        self.lbLocPrecRange.setText(
            QCoreApplication.translate(
                "Options", "Localization precision default plot range", None
            )
        )

    # retranslateUi
