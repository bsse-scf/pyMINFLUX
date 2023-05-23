# -*- coding: utf-8 -*-

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
        Options.resize(575, 396)
        self.gridLayout = QGridLayout(Options)
        self.gridLayout.setObjectName("gridLayout")
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
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.leEFOSingleEmitterFrequency.sizePolicy().hasHeightForWidth()
        )
        self.leEFOSingleEmitterFrequency.setSizePolicy(sizePolicy)

        self.hlExpectedEFOFrequency.addWidget(self.leEFOSingleEmitterFrequency)

        self.gridLayout.addLayout(self.hlExpectedEFOFrequency, 4, 0, 1, 1)

        self.lbInfoImmediate = QLabel(Options)
        self.lbInfoImmediate.setObjectName("lbInfoImmediate")
        font = QFont()
        font.setItalic(True)
        self.lbInfoImmediate.setFont(font)

        self.gridLayout.addWidget(self.lbInfoImmediate, 10, 0, 1, 1)

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
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(
            self.leEFOBinSize.sizePolicy().hasHeightForWidth()
        )
        self.leEFOBinSize.setSizePolicy(sizePolicy1)

        self.hlEFOBinSize.addWidget(self.leEFOBinSize)

        self.gridLayout.addLayout(self.hlEFOBinSize, 3, 0, 1, 1)

        self.line = QFrame(Options)
        self.line.setObjectName("line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.gridLayout.addWidget(self.line, 9, 0, 1, 1)

        self.cbWeightAvgLocByECO = QCheckBox(Options)
        self.cbWeightAvgLocByECO.setObjectName("cbWeightAvgLocByECO")

        self.gridLayout.addWidget(self.cbWeightAvgLocByECO, 11, 0, 1, 1)

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
        sizePolicy1.setHeightForWidth(
            self.leCFRRangeMin.sizePolicy().hasHeightForWidth()
        )
        self.leCFRRangeMin.setSizePolicy(sizePolicy1)

        self.hlCFRRange.addWidget(self.leCFRRangeMin)

        self.leCFRRangeMax = QLineEdit(Options)
        self.leCFRRangeMax.setObjectName("leCFRRangeMax")
        sizePolicy1.setHeightForWidth(
            self.leCFRRangeMax.sizePolicy().hasHeightForWidth()
        )
        self.leCFRRangeMax.setSizePolicy(sizePolicy1)

        self.hlCFRRange.addWidget(self.leCFRRangeMax)

        self.gridLayout.addLayout(self.hlCFRRange, 6, 0, 1, 1)

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
        sizePolicy1.setHeightForWidth(
            self.leEFORangeMin.sizePolicy().hasHeightForWidth()
        )
        self.leEFORangeMin.setSizePolicy(sizePolicy1)

        self.hlEFORange.addWidget(self.leEFORangeMin)

        self.leEFORangeMax = QLineEdit(Options)
        self.leEFORangeMax.setObjectName("leEFORangeMax")
        sizePolicy1.setHeightForWidth(
            self.leEFORangeMax.sizePolicy().hasHeightForWidth()
        )
        self.leEFORangeMax.setSizePolicy(sizePolicy1)

        self.hlEFORange.addWidget(self.leEFORangeMax)

        self.gridLayout.addLayout(self.hlEFORange, 5, 0, 1, 1)

        self.lbInfo = QLabel(Options)
        self.lbInfo.setObjectName("lbInfo")
        self.lbInfo.setFont(font)

        self.gridLayout.addWidget(self.lbInfo, 8, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding
        )

        self.gridLayout.addItem(self.verticalSpacer, 12, 0, 1, 1)

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
        sizePolicy1.setHeightForWidth(self.leMinTIDNum.sizePolicy().hasHeightForWidth())
        self.leMinTIDNum.setSizePolicy(sizePolicy1)

        self.hlMinNumTraces.addWidget(self.leMinTIDNum)

        self.gridLayout.addLayout(self.hlMinNumTraces, 0, 0, 1, 1)

        self.pbSetDefault = QPushButton(Options)
        self.pbSetDefault.setObjectName("pbSetDefault")

        self.gridLayout.addWidget(self.pbSetDefault, 13, 0, 1, 1)

        self.hlZScalingFactor = QHBoxLayout()
        self.hlZScalingFactor.setObjectName("hlZScalingFactor")
        self.lbZScalingFactor = QLabel(Options)
        self.lbZScalingFactor.setObjectName("lbZScalingFactor")

        self.hlZScalingFactor.addWidget(self.lbZScalingFactor)

        self.hsZScalingFactor = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.hlZScalingFactor.addItem(self.hsZScalingFactor)

        self.leZScalingFactor = QLineEdit(Options)
        self.leZScalingFactor.setObjectName("leZScalingFactor")
        sizePolicy1.setHeightForWidth(
            self.leZScalingFactor.sizePolicy().hasHeightForWidth()
        )
        self.leZScalingFactor.setSizePolicy(sizePolicy1)

        self.hlZScalingFactor.addWidget(self.leZScalingFactor)

        self.gridLayout.addLayout(self.hlZScalingFactor, 1, 0, 1, 1)

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
        sizePolicy1.setHeightForWidth(
            self.leLocPrecRangeMin.sizePolicy().hasHeightForWidth()
        )
        self.leLocPrecRangeMin.setSizePolicy(sizePolicy1)

        self.hlLocPrecRange.addWidget(self.leLocPrecRangeMin)

        self.leLocPrecRangeMax = QLineEdit(Options)
        self.leLocPrecRangeMax.setObjectName("leLocPrecRangeMax")
        sizePolicy1.setHeightForWidth(
            self.leLocPrecRangeMax.sizePolicy().hasHeightForWidth()
        )
        self.leLocPrecRangeMax.setSizePolicy(sizePolicy1)

        self.hlLocPrecRange.addWidget(self.leLocPrecRangeMax)

        self.gridLayout.addLayout(self.hlLocPrecRange, 7, 0, 1, 1)

        self.lbInfoZScalingFactor = QLabel(Options)
        self.lbInfoZScalingFactor.setObjectName("lbInfoZScalingFactor")
        font1 = QFont()
        font1.setPointSize(8)
        font1.setItalic(True)
        self.lbInfoZScalingFactor.setFont(font1)
        self.lbInfoZScalingFactor.setAlignment(
            Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter
        )

        self.gridLayout.addWidget(self.lbInfoZScalingFactor, 2, 0, 1, 1)

        QWidget.setTabOrder(self.leMinTIDNum, self.leZScalingFactor)
        QWidget.setTabOrder(self.leZScalingFactor, self.leEFOBinSize)
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
        self.lbEFOSingleEmitterFrequency.setText(
            QCoreApplication.translate(
                "Options", "EFO expected frequency for single emitters (Hz)", None
            )
        )
        self.lbInfoImmediate.setText(
            QCoreApplication.translate(
                "Options",
                "Changes below will be applied immediately to all open views.",
                None,
            )
        )
        self.lbEFOBinSize.setText(
            QCoreApplication.translate(
                "Options", "EFO bin size (Hz): set to 0 for automatic estimation", None
            )
        )
        self.cbWeightAvgLocByECO.setText(
            QCoreApplication.translate(
                "Options",
                "Use relative ECO count for weighted average localization calculation",
                None,
            )
        )
        self.lbCFRRange.setText(
            QCoreApplication.translate("Options", "CFR default plot range", None)
        )
        self.lbEFORange.setText(
            QCoreApplication.translate("Options", "EFO default plot range", None)
        )
        self.lbInfo.setText(
            QCoreApplication.translate(
                "Options",
                "Changes above will be applied when loading new data or when applying filters.",
                None,
            )
        )
        self.lbMinTIDNum.setText(
            QCoreApplication.translate(
                "Options", "Minimum number of trace localizations", None
            )
        )
        self.pbSetDefault.setText(
            QCoreApplication.translate("Options", "Set as new default", None)
        )
        self.lbZScalingFactor.setText(
            QCoreApplication.translate("Options", "Z scaling factor", None)
        )
        self.lbLocPrecRange.setText(
            QCoreApplication.translate(
                "Options", "Localization precision default plot range", None
            )
        )
        self.lbInfoZScalingFactor.setText(
            QCoreApplication.translate(
                "Options",
                "Scales the z positions to compensate for the refractive index mismatch between the coverglass and the sample.",
                None,
            )
        )

    # retranslateUi
