# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'analyzer.ui'
##
## Created by: Qt User Interface Compiler version 6.4.0
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

class Ui_Analyzer(object):
    def setupUi(self, Analyzer):
        if not Analyzer.objectName():
            Analyzer.setObjectName(u"Analyzer")
        Analyzer.resize(1191, 1087)
        self.gridLayout = QGridLayout(Analyzer)
        self.gridLayout.setObjectName(u"gridLayout")
        self.localizations_layout = QHBoxLayout()
        self.localizations_layout.setObjectName(u"localizations_layout")

        self.gridLayout.addLayout(self.localizations_layout, 3, 0, 1, 1)

        self.pbUpdateViewers = QPushButton(Analyzer)
        self.pbUpdateViewers.setObjectName(u"pbUpdateViewers")
        self.pbUpdateViewers.setEnabled(True)

        self.gridLayout.addWidget(self.pbUpdateViewers, 5, 0, 1, 1)

        self.parameters_layout = QHBoxLayout()
        self.parameters_layout.setObjectName(u"parameters_layout")

        self.gridLayout.addLayout(self.parameters_layout, 2, 0, 1, 1)

        self.pbAutoThreshold = QPushButton(Analyzer)
        self.pbAutoThreshold.setObjectName(u"pbAutoThreshold")

        self.gridLayout.addWidget(self.pbAutoThreshold, 1, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.checkLowerThreshold = QCheckBox(Analyzer)
        self.checkLowerThreshold.setObjectName(u"checkLowerThreshold")

        self.horizontalLayout.addWidget(self.checkLowerThreshold)

        self.checkUpperThreshold = QCheckBox(Analyzer)
        self.checkUpperThreshold.setObjectName(u"checkUpperThreshold")

        self.horizontalLayout.addWidget(self.checkUpperThreshold)

        self.lbThreshMultFactor = QLabel(Analyzer)
        self.lbThreshMultFactor.setObjectName(u"lbThreshMultFactor")

        self.horizontalLayout.addWidget(self.lbThreshMultFactor)

        self.leThreshFactor = QLineEdit(Analyzer)
        self.leThreshFactor.setObjectName(u"leThreshFactor")
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.leThreshFactor.sizePolicy().hasHeightForWidth())
        self.leThreshFactor.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.leThreshFactor)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.cbEnableEFOFiltering = QCheckBox(Analyzer)
        self.cbEnableEFOFiltering.setObjectName(u"cbEnableEFOFiltering")
        self.cbEnableEFOFiltering.setEnabled(True)

        self.gridLayout_2.addWidget(self.cbEnableEFOFiltering, 0, 1, 1, 1)

        self.cbEnableCFRFiltering = QCheckBox(Analyzer)
        self.cbEnableCFRFiltering.setObjectName(u"cbEnableCFRFiltering")
        self.cbEnableCFRFiltering.setEnabled(True)

        self.gridLayout_2.addWidget(self.cbEnableCFRFiltering, 0, 2, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_3, 0, 0, 1, 1)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_4, 0, 3, 1, 1)


        self.gridLayout.addLayout(self.gridLayout_2, 4, 0, 1, 1)

        self.pbReset = QPushButton(Analyzer)
        self.pbReset.setObjectName(u"pbReset")

        self.gridLayout.addWidget(self.pbReset, 6, 0, 1, 1)


        self.retranslateUi(Analyzer)

        QMetaObject.connectSlotsByName(Analyzer)
    # setupUi

    def retranslateUi(self, Analyzer):
        Analyzer.setWindowTitle(QCoreApplication.translate("Analyzer", u"Analyzer", None))
        self.pbUpdateViewers.setText(QCoreApplication.translate("Analyzer", u"Filter", None))
        self.pbAutoThreshold.setText(QCoreApplication.translate("Analyzer", u"Auto-threshold", None))
        self.checkLowerThreshold.setText(QCoreApplication.translate("Analyzer", u"Lower bound", None))
        self.checkUpperThreshold.setText(QCoreApplication.translate("Analyzer", u"Upper bound", None))
        self.lbThreshMultFactor.setText(QCoreApplication.translate("Analyzer", u"Robust threshold multiplicative factor", None))
        self.leThreshFactor.setText(QCoreApplication.translate("Analyzer", u"2.0", None))
        self.cbEnableEFOFiltering.setText(QCoreApplication.translate("Analyzer", u"Filter on EFO values", None))
        self.cbEnableCFRFiltering.setText(QCoreApplication.translate("Analyzer", u"Filter on CFR values", None))
        self.pbReset.setText(QCoreApplication.translate("Analyzer", u"Reset", None))
    # retranslateUi

