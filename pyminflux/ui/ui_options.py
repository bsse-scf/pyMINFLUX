# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'options.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog, QFrame,
    QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QSpacerItem, QWidget)

class Ui_Options(object):
    def setupUi(self, Options):
        if not Options.objectName():
            Options.setObjectName(u"Options")
        Options.resize(489, 261)
        self.gridLayout = QGridLayout(Options)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lbEFOExpectedCutoffFrequency = QLabel(Options)
        self.lbEFOExpectedCutoffFrequency.setObjectName(u"lbEFOExpectedCutoffFrequency")

        self.horizontalLayout.addWidget(self.lbEFOExpectedCutoffFrequency)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_3)

        self.leEFOExpectedCutoffFrequency = QLineEdit(Options)
        self.leEFOExpectedCutoffFrequency.setObjectName(u"leEFOExpectedCutoffFrequency")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.leEFOExpectedCutoffFrequency.sizePolicy().hasHeightForWidth())
        self.leEFOExpectedCutoffFrequency.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.leEFOExpectedCutoffFrequency)


        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 1)

        self.cbWeightAvgLocByECO = QCheckBox(Options)
        self.cbWeightAvgLocByECO.setObjectName(u"cbWeightAvgLocByECO")

        self.gridLayout.addWidget(self.cbWeightAvgLocByECO, 6, 0, 1, 1)

        self.line = QFrame(Options)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.gridLayout.addWidget(self.line, 4, 0, 1, 1)

        self.lbInfoImmediate = QLabel(Options)
        self.lbInfoImmediate.setObjectName(u"lbInfoImmediate")
        font = QFont()
        font.setItalic(True)
        self.lbInfoImmediate.setFont(font)

        self.gridLayout.addWidget(self.lbInfoImmediate, 5, 0, 1, 1)

        self.lbInfo = QLabel(Options)
        self.lbInfo.setObjectName(u"lbInfo")
        self.lbInfo.setFont(font)

        self.gridLayout.addWidget(self.lbInfo, 3, 0, 1, 1)

        self.hlMinNumTraces = QHBoxLayout()
        self.hlMinNumTraces.setObjectName(u"hlMinNumTraces")
        self.lbMinTIDNum = QLabel(Options)
        self.lbMinTIDNum.setObjectName(u"lbMinTIDNum")

        self.hlMinNumTraces.addWidget(self.lbMinTIDNum)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hlMinNumTraces.addItem(self.horizontalSpacer)

        self.leMinTIDNum = QLineEdit(Options)
        self.leMinTIDNum.setObjectName(u"leMinTIDNum")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.leMinTIDNum.sizePolicy().hasHeightForWidth())
        self.leMinTIDNum.setSizePolicy(sizePolicy1)

        self.hlMinNumTraces.addWidget(self.leMinTIDNum)


        self.gridLayout.addLayout(self.hlMinNumTraces, 0, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 7, 0, 1, 1)

        self.hlEFOBinSize = QHBoxLayout()
        self.hlEFOBinSize.setObjectName(u"hlEFOBinSize")
        self.lbEFOBinSize = QLabel(Options)
        self.lbEFOBinSize.setObjectName(u"lbEFOBinSize")

        self.hlEFOBinSize.addWidget(self.lbEFOBinSize)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hlEFOBinSize.addItem(self.horizontalSpacer_2)

        self.leEFOBinSize = QLineEdit(Options)
        self.leEFOBinSize.setObjectName(u"leEFOBinSize")
        sizePolicy1.setHeightForWidth(self.leEFOBinSize.sizePolicy().hasHeightForWidth())
        self.leEFOBinSize.setSizePolicy(sizePolicy1)

        self.hlEFOBinSize.addWidget(self.leEFOBinSize)


        self.gridLayout.addLayout(self.hlEFOBinSize, 1, 0, 1, 1)

        self.pbSetDefault = QPushButton(Options)
        self.pbSetDefault.setObjectName(u"pbSetDefault")

        self.gridLayout.addWidget(self.pbSetDefault, 8, 0, 1, 1)


        self.retranslateUi(Options)

        QMetaObject.connectSlotsByName(Options)
    # setupUi

    def retranslateUi(self, Options):
        Options.setWindowTitle(QCoreApplication.translate("Options", u"Options", None))
        self.lbEFOExpectedCutoffFrequency.setText(QCoreApplication.translate("Options", u"EFO expected cutoff frequency (Hz)", None))
        self.cbWeightAvgLocByECO.setText(QCoreApplication.translate("Options", u"Use relative ECO count for weighted average localization calculation", None))
        self.lbInfoImmediate.setText(QCoreApplication.translate("Options", u"Changes below will be applied immediately to all open views.", None))
        self.lbInfo.setText(QCoreApplication.translate("Options", u"Changes above will be applied when loading new data or when filtering in the Analyzer.", None))
        self.lbMinTIDNum.setText(QCoreApplication.translate("Options", u"Minimum number of trace localizations", None))
        self.lbEFOBinSize.setText(QCoreApplication.translate("Options", u"EFO bin size (Hz): set to 0 for automatic estimation", None))
        self.pbSetDefault.setText(QCoreApplication.translate("Options", u"Set as new default", None))
    # retranslateUi

