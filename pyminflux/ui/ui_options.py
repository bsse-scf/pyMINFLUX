# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'options.ui'
##
## Created by: Qt User Interface Compiler version 6.7.3
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
    QTextEdit,
    QWidget,
)


class Ui_Options(object):
    def setupUi(self, Options):
        if not Options.objectName():
            Options.setObjectName("Options")
        Options.resize(575, 583)
        self.gridLayout = QGridLayout(Options)
        self.gridLayout.setObjectName("gridLayout")
        self.hlLocPrecRange = QHBoxLayout()
        self.hlLocPrecRange.setObjectName("hlLocPrecRange")
        self.pbLocPrecRangeHelp = QPushButton(Options)
        self.pbLocPrecRangeHelp.setObjectName("pbLocPrecRangeHelp")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.pbLocPrecRangeHelp.sizePolicy().hasHeightForWidth()
        )
        self.pbLocPrecRangeHelp.setSizePolicy(sizePolicy)
        self.pbLocPrecRangeHelp.setMaximumSize(QSize(20, 16777215))
        self.pbLocPrecRangeHelp.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.hlLocPrecRange.addWidget(self.pbLocPrecRangeHelp)

        self.lbLocPrecRange = QLabel(Options)
        self.lbLocPrecRange.setObjectName("lbLocPrecRange")

        self.hlLocPrecRange.addWidget(self.lbLocPrecRange)

        self.hsLocPrecRange = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.hlLocPrecRange.addItem(self.hsLocPrecRange)

        self.leLocPrecRangeMin = QLineEdit(Options)
        self.leLocPrecRangeMin.setObjectName("leLocPrecRangeMin")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
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

        self.gridLayout.addLayout(self.hlLocPrecRange, 8, 0, 1, 1)

        self.hlEFORange = QHBoxLayout()
        self.hlEFORange.setObjectName("hlEFORange")
        self.pbEFORangeHelp = QPushButton(Options)
        self.pbEFORangeHelp.setObjectName("pbEFORangeHelp")
        sizePolicy.setHeightForWidth(
            self.pbEFORangeHelp.sizePolicy().hasHeightForWidth()
        )
        self.pbEFORangeHelp.setSizePolicy(sizePolicy)
        self.pbEFORangeHelp.setMaximumSize(QSize(20, 16777215))
        self.pbEFORangeHelp.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.hlEFORange.addWidget(self.pbEFORangeHelp)

        self.lbEFORange = QLabel(Options)
        self.lbEFORange.setObjectName("lbEFORange")

        self.hlEFORange.addWidget(self.lbEFORange)

        self.hsEFORange = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
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

        self.gridLayout.addLayout(self.hlEFORange, 6, 0, 1, 1)

        self.lbQuickHelp = QLabel(Options)
        self.lbQuickHelp.setObjectName("lbQuickHelp")
        font = QFont()
        font.setBold(True)
        self.lbQuickHelp.setFont(font)

        self.gridLayout.addWidget(self.lbQuickHelp, 23, 0, 1, 1)

        self.lbInfoAtStart = QLabel(Options)
        self.lbInfoAtStart.setObjectName("lbInfoAtStart")
        font1 = QFont()
        font1.setItalic(True)
        self.lbInfoAtStart.setFont(font1)

        self.gridLayout.addWidget(self.lbInfoAtStart, 20, 0, 1, 1)

        self.pbSetDefault = QPushButton(Options)
        self.pbSetDefault.setObjectName("pbSetDefault")

        self.gridLayout.addWidget(self.pbSetDefault, 26, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(
            20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.gridLayout.addItem(self.verticalSpacer, 22, 0, 1, 1)

        self.lbInfo = QLabel(Options)
        self.lbInfo.setObjectName("lbInfo")
        self.lbInfo.setFont(font1)

        self.gridLayout.addWidget(self.lbInfo, 0, 0, 1, 1)

        self.hl_immediate = QFrame(Options)
        self.hl_immediate.setObjectName("hl_immediate")
        self.hl_immediate.setFrameShape(QFrame.Shape.HLine)
        self.hl_immediate.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.hl_immediate, 11, 0, 1, 1)

        self.hlCFRRange = QHBoxLayout()
        self.hlCFRRange.setObjectName("hlCFRRange")
        self.pbCFRRangeHelp = QPushButton(Options)
        self.pbCFRRangeHelp.setObjectName("pbCFRRangeHelp")
        sizePolicy.setHeightForWidth(
            self.pbCFRRangeHelp.sizePolicy().hasHeightForWidth()
        )
        self.pbCFRRangeHelp.setSizePolicy(sizePolicy)
        self.pbCFRRangeHelp.setMaximumSize(QSize(20, 16777215))
        self.pbCFRRangeHelp.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.hlCFRRange.addWidget(self.pbCFRRangeHelp)

        self.lbCFRRange = QLabel(Options)
        self.lbCFRRange.setObjectName("lbCFRRange")

        self.hlCFRRange.addWidget(self.lbCFRRange)

        self.hsCFRRange = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
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

        self.gridLayout.addLayout(self.hlCFRRange, 7, 0, 1, 1)

        self.hl_at_start = QFrame(Options)
        self.hl_at_start.setObjectName("hl_at_start")
        self.hl_at_start.setFrameShape(QFrame.Shape.HLine)
        self.hl_at_start.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.hl_at_start, 19, 0, 1, 1)

        self.hlZScalingFactor = QHBoxLayout()
        self.hlZScalingFactor.setObjectName("hlZScalingFactor")
        self.pbZScalingFactorHelp = QPushButton(Options)
        self.pbZScalingFactorHelp.setObjectName("pbZScalingFactorHelp")
        sizePolicy.setHeightForWidth(
            self.pbZScalingFactorHelp.sizePolicy().hasHeightForWidth()
        )
        self.pbZScalingFactorHelp.setSizePolicy(sizePolicy)
        self.pbZScalingFactorHelp.setMaximumSize(QSize(20, 16777215))
        self.pbZScalingFactorHelp.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.hlZScalingFactor.addWidget(self.pbZScalingFactorHelp)

        self.lbZScalingFactor = QLabel(Options)
        self.lbZScalingFactor.setObjectName("lbZScalingFactor")

        self.hlZScalingFactor.addWidget(self.lbZScalingFactor)

        self.hsZScalingFactor = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.hlZScalingFactor.addItem(self.hsZScalingFactor)

        self.leZScalingFactor = QLineEdit(Options)
        self.leZScalingFactor.setObjectName("leZScalingFactor")
        sizePolicy1.setHeightForWidth(
            self.leZScalingFactor.sizePolicy().hasHeightForWidth()
        )
        self.leZScalingFactor.setSizePolicy(sizePolicy1)

        self.hlZScalingFactor.addWidget(self.leZScalingFactor)

        self.gridLayout.addLayout(self.hlZScalingFactor, 3, 0, 1, 1)

        self.hlWeightAvgLocByECO = QHBoxLayout()
        self.hlWeightAvgLocByECO.setObjectName("hlWeightAvgLocByECO")
        self.pbWeightAvgLocByECOHelp = QPushButton(Options)
        self.pbWeightAvgLocByECOHelp.setObjectName("pbWeightAvgLocByECOHelp")
        sizePolicy.setHeightForWidth(
            self.pbWeightAvgLocByECOHelp.sizePolicy().hasHeightForWidth()
        )
        self.pbWeightAvgLocByECOHelp.setSizePolicy(sizePolicy)
        self.pbWeightAvgLocByECOHelp.setMaximumSize(QSize(20, 16777215))
        self.pbWeightAvgLocByECOHelp.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.hlWeightAvgLocByECO.addWidget(self.pbWeightAvgLocByECOHelp)

        self.cbWeightAvgLocByECO = QCheckBox(Options)
        self.cbWeightAvgLocByECO.setObjectName("cbWeightAvgLocByECO")

        self.hlWeightAvgLocByECO.addWidget(self.cbWeightAvgLocByECO)

        self.gridLayout.addLayout(self.hlWeightAvgLocByECO, 14, 0, 1, 1)

        self.hlPlotExportDPI = QHBoxLayout()
        self.hlPlotExportDPI.setObjectName("hlPlotExportDPI")
        self.pbPlotExportDPIHelp = QPushButton(Options)
        self.pbPlotExportDPIHelp.setObjectName("pbPlotExportDPIHelp")
        sizePolicy.setHeightForWidth(
            self.pbPlotExportDPIHelp.sizePolicy().hasHeightForWidth()
        )
        self.pbPlotExportDPIHelp.setSizePolicy(sizePolicy)
        self.pbPlotExportDPIHelp.setMaximumSize(QSize(20, 16777215))
        self.pbPlotExportDPIHelp.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.hlPlotExportDPI.addWidget(self.pbPlotExportDPIHelp)

        self.lbPlotExportDPI = QLabel(Options)
        self.lbPlotExportDPI.setObjectName("lbPlotExportDPI")

        self.hlPlotExportDPI.addWidget(self.lbPlotExportDPI)

        self.hsPlotExportDPI = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.hlPlotExportDPI.addItem(self.hsPlotExportDPI)

        self.lePlotExportDPI = QLineEdit(Options)
        self.lePlotExportDPI.setObjectName("lePlotExportDPI")
        sizePolicy1.setHeightForWidth(
            self.lePlotExportDPI.sizePolicy().hasHeightForWidth()
        )
        self.lePlotExportDPI.setSizePolicy(sizePolicy1)

        self.hlPlotExportDPI.addWidget(self.lePlotExportDPI)

        self.gridLayout.addLayout(self.hlPlotExportDPI, 17, 0, 1, 1)

        self.hlEFOBinSize = QHBoxLayout()
        self.hlEFOBinSize.setObjectName("hlEFOBinSize")
        self.pbEFOBinSizeHelp = QPushButton(Options)
        self.pbEFOBinSizeHelp.setObjectName("pbEFOBinSizeHelp")
        sizePolicy.setHeightForWidth(
            self.pbEFOBinSizeHelp.sizePolicy().hasHeightForWidth()
        )
        self.pbEFOBinSizeHelp.setSizePolicy(sizePolicy)
        self.pbEFOBinSizeHelp.setMaximumSize(QSize(20, 16777215))
        self.pbEFOBinSizeHelp.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.hlEFOBinSize.addWidget(self.pbEFOBinSizeHelp)

        self.lbEFOBinSize = QLabel(Options)
        self.lbEFOBinSize.setObjectName("lbEFOBinSize")

        self.hlEFOBinSize.addWidget(self.lbEFOBinSize)

        self.hsEFOBinSize = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.hlEFOBinSize.addItem(self.hsEFOBinSize)

        self.leEFOBinSize = QLineEdit(Options)
        self.leEFOBinSize.setObjectName("leEFOBinSize")
        sizePolicy1.setHeightForWidth(
            self.leEFOBinSize.sizePolicy().hasHeightForWidth()
        )
        self.leEFOBinSize.setSizePolicy(sizePolicy1)

        self.hlEFOBinSize.addWidget(self.leEFOBinSize)

        self.gridLayout.addLayout(self.hlEFOBinSize, 4, 0, 1, 1)

        self.hlExpectedEFOFrequency = QHBoxLayout()
        self.hlExpectedEFOFrequency.setObjectName("hlExpectedEFOFrequency")
        self.pbEFOSingleEmitterFrequencyHelp = QPushButton(Options)
        self.pbEFOSingleEmitterFrequencyHelp.setObjectName(
            "pbEFOSingleEmitterFrequencyHelp"
        )
        sizePolicy.setHeightForWidth(
            self.pbEFOSingleEmitterFrequencyHelp.sizePolicy().hasHeightForWidth()
        )
        self.pbEFOSingleEmitterFrequencyHelp.setSizePolicy(sizePolicy)
        self.pbEFOSingleEmitterFrequencyHelp.setMaximumSize(QSize(20, 16777215))
        self.pbEFOSingleEmitterFrequencyHelp.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.hlExpectedEFOFrequency.addWidget(self.pbEFOSingleEmitterFrequencyHelp)

        self.lbEFOSingleEmitterFrequency = QLabel(Options)
        self.lbEFOSingleEmitterFrequency.setObjectName("lbEFOSingleEmitterFrequency")

        self.hlExpectedEFOFrequency.addWidget(self.lbEFOSingleEmitterFrequency)

        self.hsEFOSingleEmitterFrequency = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.hlExpectedEFOFrequency.addItem(self.hsEFOSingleEmitterFrequency)

        self.leEFOSingleEmitterFrequency = QLineEdit(Options)
        self.leEFOSingleEmitterFrequency.setObjectName("leEFOSingleEmitterFrequency")
        sizePolicy2 = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(
            self.leEFOSingleEmitterFrequency.sizePolicy().hasHeightForWidth()
        )
        self.leEFOSingleEmitterFrequency.setSizePolicy(sizePolicy2)

        self.hlExpectedEFOFrequency.addWidget(self.leEFOSingleEmitterFrequency)

        self.gridLayout.addLayout(self.hlExpectedEFOFrequency, 5, 0, 1, 1)

        self.hlShowConsoleAtStart = QHBoxLayout()
        self.hlShowConsoleAtStart.setObjectName("hlShowConsoleAtStart")
        self.pbOpenConsoleAtStartHelp = QPushButton(Options)
        self.pbOpenConsoleAtStartHelp.setObjectName("pbOpenConsoleAtStartHelp")
        sizePolicy.setHeightForWidth(
            self.pbOpenConsoleAtStartHelp.sizePolicy().hasHeightForWidth()
        )
        self.pbOpenConsoleAtStartHelp.setSizePolicy(sizePolicy)
        self.pbOpenConsoleAtStartHelp.setMaximumSize(QSize(20, 16777215))
        self.pbOpenConsoleAtStartHelp.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.hlShowConsoleAtStart.addWidget(self.pbOpenConsoleAtStartHelp)

        self.cbOpenConsoleAtStart = QCheckBox(Options)
        self.cbOpenConsoleAtStart.setObjectName("cbOpenConsoleAtStart")

        self.hlShowConsoleAtStart.addWidget(self.cbOpenConsoleAtStart)

        self.gridLayout.addLayout(self.hlShowConsoleAtStart, 21, 0, 1, 1)

        self.lbInfoImmediate = QLabel(Options)
        self.lbInfoImmediate.setObjectName("lbInfoImmediate")
        self.lbInfoImmediate.setFont(font1)

        self.gridLayout.addWidget(self.lbInfoImmediate, 12, 0, 1, 1)

        self.teHelp = QTextEdit(Options)
        self.teHelp.setObjectName("teHelp")
        self.teHelp.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.gridLayout.addWidget(self.teHelp, 25, 0, 1, 1)

        self.hlMinNumTraces = QHBoxLayout()
        self.hlMinNumTraces.setObjectName("hlMinNumTraces")
        self.pbMinTIDNumHelp = QPushButton(Options)
        self.pbMinTIDNumHelp.setObjectName("pbMinTIDNumHelp")
        sizePolicy.setHeightForWidth(
            self.pbMinTIDNumHelp.sizePolicy().hasHeightForWidth()
        )
        self.pbMinTIDNumHelp.setSizePolicy(sizePolicy)
        self.pbMinTIDNumHelp.setMaximumSize(QSize(20, 16777215))
        self.pbMinTIDNumHelp.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.hlMinNumTraces.addWidget(self.pbMinTIDNumHelp)

        self.lbMinTIDNum = QLabel(Options)
        self.lbMinTIDNum.setObjectName("lbMinTIDNum")

        self.hlMinNumTraces.addWidget(self.lbMinTIDNum)

        self.hsMinTIDNum = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.hlMinNumTraces.addItem(self.hsMinTIDNum)

        self.leMinTIDNum = QLineEdit(Options)
        self.leMinTIDNum.setObjectName("leMinTIDNum")
        sizePolicy1.setHeightForWidth(self.leMinTIDNum.sizePolicy().hasHeightForWidth())
        self.leMinTIDNum.setSizePolicy(sizePolicy1)

        self.hlMinNumTraces.addWidget(self.leMinTIDNum)

        self.gridLayout.addLayout(self.hlMinNumTraces, 1, 0, 1, 1)

        self.hlNumLocsToDrop = QHBoxLayout()
        self.hlNumLocsToDrop.setObjectName("hlNumLocsToDrop")
        self.pbNumLocsToDropHelp = QPushButton(Options)
        self.pbNumLocsToDropHelp.setObjectName("pbNumLocsToDropHelp")
        sizePolicy.setHeightForWidth(
            self.pbNumLocsToDropHelp.sizePolicy().hasHeightForWidth()
        )
        self.pbNumLocsToDropHelp.setSizePolicy(sizePolicy)
        self.pbNumLocsToDropHelp.setMaximumSize(QSize(20, 16777215))
        self.pbNumLocsToDropHelp.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.hlNumLocsToDrop.addWidget(self.pbNumLocsToDropHelp)

        self.lbNumLocsToDrop = QLabel(Options)
        self.lbNumLocsToDrop.setObjectName("lbNumLocsToDrop")

        self.hlNumLocsToDrop.addWidget(self.lbNumLocsToDrop)

        self.hsNumLocsToDrop = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.hlNumLocsToDrop.addItem(self.hsNumLocsToDrop)

        self.leNumLocsToDrop = QLineEdit(Options)
        self.leNumLocsToDrop.setObjectName("leNumLocsToDrop")
        sizePolicy1.setHeightForWidth(
            self.leNumLocsToDrop.sizePolicy().hasHeightForWidth()
        )
        self.leNumLocsToDrop.setSizePolicy(sizePolicy1)

        self.hlNumLocsToDrop.addWidget(self.leNumLocsToDrop)

        self.gridLayout.addLayout(self.hlNumLocsToDrop, 2, 0, 1, 1)

        QWidget.setTabOrder(self.leMinTIDNum, self.leNumLocsToDrop)
        QWidget.setTabOrder(self.leNumLocsToDrop, self.leZScalingFactor)
        QWidget.setTabOrder(self.leZScalingFactor, self.leEFOBinSize)
        QWidget.setTabOrder(self.leEFOBinSize, self.leEFOSingleEmitterFrequency)
        QWidget.setTabOrder(self.leEFOSingleEmitterFrequency, self.leEFORangeMin)
        QWidget.setTabOrder(self.leEFORangeMin, self.leEFORangeMax)
        QWidget.setTabOrder(self.leEFORangeMax, self.leCFRRangeMin)
        QWidget.setTabOrder(self.leCFRRangeMin, self.leCFRRangeMax)
        QWidget.setTabOrder(self.leCFRRangeMax, self.leLocPrecRangeMin)
        QWidget.setTabOrder(self.leLocPrecRangeMin, self.leLocPrecRangeMax)
        QWidget.setTabOrder(self.leLocPrecRangeMax, self.cbWeightAvgLocByECO)
        QWidget.setTabOrder(self.cbWeightAvgLocByECO, self.lePlotExportDPI)
        QWidget.setTabOrder(self.lePlotExportDPI, self.cbOpenConsoleAtStart)
        QWidget.setTabOrder(self.cbOpenConsoleAtStart, self.pbSetDefault)

        self.retranslateUi(Options)

        QMetaObject.connectSlotsByName(Options)

    # setupUi

    def retranslateUi(self, Options):
        Options.setWindowTitle(QCoreApplication.translate("Options", "Options", None))
        self.pbLocPrecRangeHelp.setText(
            QCoreApplication.translate("Options", "?", None)
        )
        # if QT_CONFIG(tooltip)
        self.lbLocPrecRange.setToolTip("")
        # endif // QT_CONFIG(tooltip)
        self.lbLocPrecRange.setText(
            QCoreApplication.translate(
                "Options", "Localization precision default plot range", None
            )
        )
        # if QT_CONFIG(tooltip)
        self.leLocPrecRangeMin.setToolTip("")
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(tooltip)
        self.leLocPrecRangeMax.setToolTip("")
        # endif // QT_CONFIG(tooltip)
        self.pbEFORangeHelp.setText(QCoreApplication.translate("Options", "?", None))
        # if QT_CONFIG(tooltip)
        self.lbEFORange.setToolTip("")
        # endif // QT_CONFIG(tooltip)
        self.lbEFORange.setText(
            QCoreApplication.translate("Options", "EFO default plot range", None)
        )
        # if QT_CONFIG(tooltip)
        self.leEFORangeMin.setToolTip("")
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(tooltip)
        self.leEFORangeMax.setToolTip("")
        # endif // QT_CONFIG(tooltip)
        self.lbQuickHelp.setText(
            QCoreApplication.translate("Options", "Quick help", None)
        )
        self.lbInfoAtStart.setText(
            QCoreApplication.translate(
                "Options", "Changes below will be applied at application start.", None
            )
        )
        self.pbSetDefault.setText(
            QCoreApplication.translate("Options", "Set as new default", None)
        )
        self.lbInfo.setText(
            QCoreApplication.translate(
                "Options",
                "Changes below will be applied when loading new data or when applying filters.",
                None,
            )
        )
        self.pbCFRRangeHelp.setText(QCoreApplication.translate("Options", "?", None))
        # if QT_CONFIG(tooltip)
        self.lbCFRRange.setToolTip("")
        # endif // QT_CONFIG(tooltip)
        self.lbCFRRange.setText(
            QCoreApplication.translate("Options", "CFR default plot range", None)
        )
        # if QT_CONFIG(tooltip)
        self.leCFRRangeMin.setToolTip("")
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(tooltip)
        self.leCFRRangeMax.setToolTip("")
        # endif // QT_CONFIG(tooltip)
        self.pbZScalingFactorHelp.setText(
            QCoreApplication.translate("Options", "?", None)
        )
        # if QT_CONFIG(tooltip)
        self.lbZScalingFactor.setToolTip("")
        # endif // QT_CONFIG(tooltip)
        self.lbZScalingFactor.setText(
            QCoreApplication.translate("Options", "Z scaling factor", None)
        )
        # if QT_CONFIG(tooltip)
        self.leZScalingFactor.setToolTip("")
        # endif // QT_CONFIG(tooltip)
        self.pbWeightAvgLocByECOHelp.setText(
            QCoreApplication.translate("Options", "?", None)
        )
        # if QT_CONFIG(tooltip)
        self.cbWeightAvgLocByECO.setToolTip("")
        # endif // QT_CONFIG(tooltip)
        self.cbWeightAvgLocByECO.setText(
            QCoreApplication.translate(
                "Options",
                "Use relative ECO count for weighted average localization calculation",
                None,
            )
        )
        self.pbPlotExportDPIHelp.setText(
            QCoreApplication.translate("Options", "?", None)
        )
        self.lbPlotExportDPI.setText(
            QCoreApplication.translate(
                "Options", "Resolution (DPI) for exporting plots", None
            )
        )
        self.pbEFOBinSizeHelp.setText(QCoreApplication.translate("Options", "?", None))
        # if QT_CONFIG(tooltip)
        self.lbEFOBinSize.setToolTip("")
        # endif // QT_CONFIG(tooltip)
        self.lbEFOBinSize.setText(
            QCoreApplication.translate("Options", "EFO bin size (Hz)", None)
        )
        # if QT_CONFIG(tooltip)
        self.leEFOBinSize.setToolTip("")
        # endif // QT_CONFIG(tooltip)
        self.pbEFOSingleEmitterFrequencyHelp.setText(
            QCoreApplication.translate("Options", "?", None)
        )
        # if QT_CONFIG(tooltip)
        self.lbEFOSingleEmitterFrequency.setToolTip("")
        # endif // QT_CONFIG(tooltip)
        self.lbEFOSingleEmitterFrequency.setText(
            QCoreApplication.translate(
                "Options", "EFO expected frequency for single emitters (Hz)", None
            )
        )
        # if QT_CONFIG(tooltip)
        self.leEFOSingleEmitterFrequency.setToolTip("")
        # endif // QT_CONFIG(tooltip)
        self.pbOpenConsoleAtStartHelp.setText(
            QCoreApplication.translate("Options", "?", None)
        )
        self.cbOpenConsoleAtStart.setText(
            QCoreApplication.translate("Options", "Show console at start", None)
        )
        self.lbInfoImmediate.setText(
            QCoreApplication.translate(
                "Options",
                "Changes below will be applied immediately to all open views.",
                None,
            )
        )
        self.pbMinTIDNumHelp.setText(QCoreApplication.translate("Options", "?", None))
        # if QT_CONFIG(tooltip)
        self.lbMinTIDNum.setToolTip("")
        # endif // QT_CONFIG(tooltip)
        self.lbMinTIDNum.setText(
            QCoreApplication.translate(
                "Options", "Minimum number of trace localizations", None
            )
        )
        # if QT_CONFIG(tooltip)
        self.leMinTIDNum.setToolTip("")
        # endif // QT_CONFIG(tooltip)
        self.pbNumLocsToDropHelp.setText(
            QCoreApplication.translate("Options", "?", None)
        )
        self.lbNumLocsToDrop.setText(
            QCoreApplication.translate(
                "Options",
                "Number of localizations to drop at the beginning of each trace",
                None,
            )
        )

    # retranslateUi
