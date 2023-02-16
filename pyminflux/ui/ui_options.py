# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'options.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog, QGridLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QWidget)

class Ui_Options(object):
    def setupUi(self, Options):
        if not Options.objectName():
            Options.setObjectName(u"Options")
        Options.resize(460, 167)
        self.gridLayout = QGridLayout(Options)
        self.gridLayout.setObjectName(u"gridLayout")
        self.hlMinNumTraces = QHBoxLayout()
        self.hlMinNumTraces.setObjectName(u"hlMinNumTraces")
        self.lbMinTIDNum = QLabel(Options)
        self.lbMinTIDNum.setObjectName(u"lbMinTIDNum")

        self.hlMinNumTraces.addWidget(self.lbMinTIDNum)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hlMinNumTraces.addItem(self.horizontalSpacer)

        self.leMinTIDNum = QLineEdit(Options)
        self.leMinTIDNum.setObjectName(u"leMinTIDNum")
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.leMinTIDNum.sizePolicy().hasHeightForWidth())
        self.leMinTIDNum.setSizePolicy(sizePolicy)

        self.hlMinNumTraces.addWidget(self.leMinTIDNum)


        self.gridLayout.addLayout(self.hlMinNumTraces, 0, 0, 1, 1)

        self.cbColorLocsByTID = QCheckBox(Options)
        self.cbColorLocsByTID.setObjectName(u"cbColorLocsByTID")

        self.gridLayout.addWidget(self.cbColorLocsByTID, 4, 0, 1, 1)

        self.pbSetDefault = QPushButton(Options)
        self.pbSetDefault.setObjectName(u"pbSetDefault")

        self.gridLayout.addWidget(self.pbSetDefault, 6, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 5, 0, 1, 1)

        self.lbInfo = QLabel(Options)
        self.lbInfo.setObjectName(u"lbInfo")
        font = QFont()
        font.setItalic(True)
        self.lbInfo.setFont(font)

        self.gridLayout.addWidget(self.lbInfo, 3, 0, 1, 1)

        self.hlEFOBinSize = QHBoxLayout()
        self.hlEFOBinSize.setObjectName(u"hlEFOBinSize")
        self.lbEFOBinSize = QLabel(Options)
        self.lbEFOBinSize.setObjectName(u"lbEFOBinSize")

        self.hlEFOBinSize.addWidget(self.lbEFOBinSize)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hlEFOBinSize.addItem(self.horizontalSpacer_2)

        self.leEFOBinSize = QLineEdit(Options)
        self.leEFOBinSize.setObjectName(u"leEFOBinSize")
        sizePolicy.setHeightForWidth(self.leEFOBinSize.sizePolicy().hasHeightForWidth())
        self.leEFOBinSize.setSizePolicy(sizePolicy)

        self.hlEFOBinSize.addWidget(self.leEFOBinSize)


        self.gridLayout.addLayout(self.hlEFOBinSize, 1, 0, 1, 1)


        self.retranslateUi(Options)

        QMetaObject.connectSlotsByName(Options)
    # setupUi

    def retranslateUi(self, Options):
        Options.setWindowTitle(QCoreApplication.translate("Options", u"Options", None))
        self.lbMinTIDNum.setText(QCoreApplication.translate("Options", u"Minimum number of trace localizations", None))
        self.cbColorLocsByTID.setText(QCoreApplication.translate("Options", u"Color-code localizations by TID in main plotter", None))
        self.pbSetDefault.setText(QCoreApplication.translate("Options", u"Set as new default", None))
        self.lbInfo.setText(QCoreApplication.translate("Options", u"Changes above will be applied to new data and when hitting Filter in the Analyzer.", None))
        self.lbEFOBinSize.setText(QCoreApplication.translate("Options", u"EFO bin size (kHz)", None))
    # retranslateUi

