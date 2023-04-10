# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'wizard.ui'
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
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QWidget,
)


class Ui_WizardDialog(object):
    def setupUi(self, WizardDialog):
        if not WizardDialog.objectName():
            WizardDialog.setObjectName("WizardDialog")
        WizardDialog.resize(336, 939)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(WizardDialog.sizePolicy().hasHeightForWidth())
        WizardDialog.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(WizardDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.leFrequencySingleEmitters = QLineEdit(WizardDialog)
        self.leFrequencySingleEmitters.setObjectName("leFrequencySingleEmitters")

        self.gridLayout.addWidget(self.leFrequencySingleEmitters, 8, 2, 1, 2)

        self.lbEFOFiltering = QLabel(WizardDialog)
        self.lbEFOFiltering.setObjectName("lbEFOFiltering")
        font = QFont()
        font.setBold(True)
        self.lbEFOFiltering.setFont(font)

        self.gridLayout.addWidget(self.lbEFOFiltering, 5, 0, 1, 1)

        self.lbFrequencySingleEmitters = QLabel(WizardDialog)
        self.lbFrequencySingleEmitters.setObjectName("lbFrequencySingleEmitters")

        self.gridLayout.addWidget(self.lbFrequencySingleEmitters, 8, 0, 1, 2)

        self.cbCFRUpperBound = QCheckBox(WizardDialog)
        self.cbCFRUpperBound.setObjectName("cbCFRUpperBound")
        self.cbCFRUpperBound.setContextMenuPolicy(Qt.DefaultContextMenu)

        self.gridLayout.addWidget(self.cbCFRUpperBound, 14, 2, 1, 2)

        self.lbEFOUpperBound = QLabel(WizardDialog)
        self.lbEFOUpperBound.setObjectName("lbEFOUpperBound")

        self.gridLayout.addWidget(self.lbEFOUpperBound, 7, 0, 1, 1)

        self.pbAnalyzer = QPushButton(WizardDialog)
        self.pbAnalyzer.setObjectName("pbAnalyzer")

        self.gridLayout.addWidget(self.pbAnalyzer, 3, 0, 1, 4)

        self.lbCFRUpperBound = QLabel(WizardDialog)
        self.lbCFRUpperBound.setObjectName("lbCFRUpperBound")

        self.gridLayout.addWidget(self.lbCFRUpperBound, 12, 0, 1, 1)

        self.pbColorUnmixer = QPushButton(WizardDialog)
        self.pbColorUnmixer.setObjectName("pbColorUnmixer")

        self.gridLayout.addWidget(self.pbColorUnmixer, 1, 1, 1, 3)

        self.leEFOUpperBound = QLineEdit(WizardDialog)
        self.leEFOUpperBound.setObjectName("leEFOUpperBound")

        self.gridLayout.addWidget(self.leEFOUpperBound, 7, 2, 1, 2)

        self.lbCFRSigmaPre = QLabel(WizardDialog)
        self.lbCFRSigmaPre.setObjectName("lbCFRSigmaPre")

        self.gridLayout.addWidget(self.lbCFRSigmaPre, 13, 0, 1, 1)

        self.leCFRSigma = QLineEdit(WizardDialog)
        self.leCFRSigma.setObjectName("leCFRSigma")

        self.gridLayout.addWidget(self.leCFRSigma, 13, 2, 1, 2)

        self.leCFRLowerBound = QLineEdit(WizardDialog)
        self.leCFRLowerBound.setObjectName("leCFRLowerBound")

        self.gridLayout.addWidget(self.leCFRLowerBound, 11, 2, 1, 2)

        self.cbCFRLowerBound = QCheckBox(WizardDialog)
        self.cbCFRLowerBound.setObjectName("cbCFRLowerBound")
        self.cbCFRLowerBound.setContextMenuPolicy(Qt.DefaultContextMenu)

        self.gridLayout.addWidget(self.cbCFRLowerBound, 14, 0, 1, 1)

        self.pbSingleColor = QPushButton(WizardDialog)
        self.pbSingleColor.setObjectName("pbSingleColor")

        self.gridLayout.addWidget(self.pbSingleColor, 1, 0, 1, 1)

        self.leEFOLowerBound = QLineEdit(WizardDialog)
        self.leEFOLowerBound.setObjectName("leEFOLowerBound")

        self.gridLayout.addWidget(self.leEFOLowerBound, 5, 2, 2, 2)

        self.lbCFRLowerBound = QLabel(WizardDialog)
        self.lbCFRLowerBound.setObjectName("lbCFRLowerBound")

        self.gridLayout.addWidget(self.lbCFRLowerBound, 11, 0, 1, 1)

        self.pbEFOFilter = QPushButton(WizardDialog)
        self.pbEFOFilter.setObjectName("pbEFOFilter")

        self.gridLayout.addWidget(self.pbEFOFilter, 9, 0, 1, 4)

        self.leCFRUpperBound = QLineEdit(WizardDialog)
        self.leCFRUpperBound.setObjectName("leCFRUpperBound")

        self.gridLayout.addWidget(self.leCFRUpperBound, 12, 2, 1, 2)

        self.verticalSpacer = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding
        )

        self.gridLayout.addItem(self.verticalSpacer, 16, 0, 1, 1)

        self.pbCFRFilter = QPushButton(WizardDialog)
        self.pbCFRFilter.setObjectName("pbCFRFilter")

        self.gridLayout.addWidget(self.pbCFRFilter, 15, 0, 1, 4)

        self.lnCFRFiltering = QLabel(WizardDialog)
        self.lnCFRFiltering.setObjectName("lnCFRFiltering")
        self.lnCFRFiltering.setFont(font)

        self.gridLayout.addWidget(self.lnCFRFiltering, 10, 0, 1, 1)

        self.pbTimeInspector = QPushButton(WizardDialog)
        self.pbTimeInspector.setObjectName("pbTimeInspector")

        self.gridLayout.addWidget(self.pbTimeInspector, 2, 0, 1, 4)

        self.lbEFOLowerBound = QLabel(WizardDialog)
        self.lbEFOLowerBound.setObjectName("lbEFOLowerBound")

        self.gridLayout.addWidget(self.lbEFOLowerBound, 6, 0, 1, 1)

        self.pbLoadData = QPushButton(WizardDialog)
        self.pbLoadData.setObjectName("pbLoadData")

        self.gridLayout.addWidget(self.pbLoadData, 0, 0, 1, 4)

        QWidget.setTabOrder(self.pbLoadData, self.pbSingleColor)
        QWidget.setTabOrder(self.pbSingleColor, self.pbColorUnmixer)
        QWidget.setTabOrder(self.pbColorUnmixer, self.pbTimeInspector)
        QWidget.setTabOrder(self.pbTimeInspector, self.pbAnalyzer)
        QWidget.setTabOrder(self.pbAnalyzer, self.leEFOLowerBound)
        QWidget.setTabOrder(self.leEFOLowerBound, self.leEFOUpperBound)
        QWidget.setTabOrder(self.leEFOUpperBound, self.leFrequencySingleEmitters)
        QWidget.setTabOrder(self.leFrequencySingleEmitters, self.pbEFOFilter)
        QWidget.setTabOrder(self.pbEFOFilter, self.leCFRLowerBound)
        QWidget.setTabOrder(self.leCFRLowerBound, self.leCFRUpperBound)
        QWidget.setTabOrder(self.leCFRUpperBound, self.leCFRSigma)
        QWidget.setTabOrder(self.leCFRSigma, self.cbCFRLowerBound)
        QWidget.setTabOrder(self.cbCFRLowerBound, self.cbCFRUpperBound)
        QWidget.setTabOrder(self.cbCFRUpperBound, self.pbCFRFilter)

        self.retranslateUi(WizardDialog)

        QMetaObject.connectSlotsByName(WizardDialog)

    # setupUi

    def retranslateUi(self, WizardDialog):
        WizardDialog.setWindowTitle(
            QCoreApplication.translate("WizardDialog", "Dialog", None)
        )
        self.lbEFOFiltering.setText(
            QCoreApplication.translate("WizardDialog", "EFO Filtering", None)
        )
        self.lbFrequencySingleEmitters.setText(
            QCoreApplication.translate(
                "WizardDialog", "Frequency single emitters (Hz)", None
            )
        )
        self.cbCFRUpperBound.setText(
            QCoreApplication.translate("WizardDialog", "Upper bound", None)
        )
        self.lbEFOUpperBound.setText(
            QCoreApplication.translate("WizardDialog", "Upper Bound (Hz)", None)
        )
        self.pbAnalyzer.setText(
            QCoreApplication.translate("WizardDialog", "Analyzer", None)
        )
        self.lbCFRUpperBound.setText(
            QCoreApplication.translate("WizardDialog", "Upper bound", None)
        )
        self.pbColorUnmixer.setText(
            QCoreApplication.translate("WizardDialog", "Color Unmizer", None)
        )
        self.lbCFRSigmaPre.setText(
            QCoreApplication.translate("WizardDialog", "Robust threshold", None)
        )
        self.cbCFRLowerBound.setText(
            QCoreApplication.translate("WizardDialog", "Lower bound", None)
        )
        self.pbSingleColor.setText(
            QCoreApplication.translate("WizardDialog", "Single Color", None)
        )
        self.lbCFRLowerBound.setText(
            QCoreApplication.translate("WizardDialog", "Lower bound", None)
        )
        self.pbEFOFilter.setText(
            QCoreApplication.translate("WizardDialog", "FIlter EFO", None)
        )
        self.pbCFRFilter.setText(
            QCoreApplication.translate("WizardDialog", "FIlter CFR", None)
        )
        self.lnCFRFiltering.setText(
            QCoreApplication.translate("WizardDialog", "CFR Filtering", None)
        )
        self.pbTimeInspector.setText(
            QCoreApplication.translate("WizardDialog", "Time Inspector", None)
        )
        self.lbEFOLowerBound.setText(
            QCoreApplication.translate("WizardDialog", "Lower bound (Hz)", None)
        )
        self.pbLoadData.setText(
            QCoreApplication.translate("WizardDialog", "Load", None)
        )

    # retranslateUi
