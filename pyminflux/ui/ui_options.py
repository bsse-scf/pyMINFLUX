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
from PySide6.QtWidgets import (QApplication, QDialog, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QWidget)

class Ui_Options(object):
    def setupUi(self, Options):
        if not Options.objectName():
            Options.setObjectName(u"Options")
        Options.resize(419, 136)
        self.gridLayout = QGridLayout(Options)
        self.gridLayout.setObjectName(u"gridLayout")
        self.pbSetDefault = QPushButton(Options)
        self.pbSetDefault.setObjectName(u"pbSetDefault")

        self.gridLayout.addWidget(self.pbSetDefault, 3, 0, 1, 1)

        self.lbInfo = QLabel(Options)
        self.lbInfo.setObjectName(u"lbInfo")
        font = QFont()
        font.setItalic(True)
        self.lbInfo.setFont(font)

        self.gridLayout.addWidget(self.lbInfo, 1, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 2, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lbMinTIDNum = QLabel(Options)
        self.lbMinTIDNum.setObjectName(u"lbMinTIDNum")

        self.horizontalLayout.addWidget(self.lbMinTIDNum)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.leMinTIDNum = QLineEdit(Options)
        self.leMinTIDNum.setObjectName(u"leMinTIDNum")

        self.horizontalLayout.addWidget(self.leMinTIDNum)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)


        self.retranslateUi(Options)

        QMetaObject.connectSlotsByName(Options)
    # setupUi

    def retranslateUi(self, Options):
        Options.setWindowTitle(QCoreApplication.translate("Options", u"Options", None))
        self.pbSetDefault.setText(QCoreApplication.translate("Options", u"Set as new default", None))
        self.lbInfo.setText(QCoreApplication.translate("Options", u"Changes will be applied to new data and when hitting Filter in the Analyzer.", None))
        self.lbMinTIDNum.setText(QCoreApplication.translate("Options", u"Minimum number of trace localizations", None))
    # retranslateUi

