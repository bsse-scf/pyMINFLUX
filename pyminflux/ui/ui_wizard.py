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
        self.lnCFRFiltering = QLabel(WizardDialog)
        self.lnCFRFiltering.setObjectName("lnCFRFiltering")
        font = QFont()
        font.setBold(True)
        self.lnCFRFiltering.setFont(font)

        self.gridLayout.addWidget(self.lnCFRFiltering, 8, 0, 1, 1)

        self.lbCFRUpperBound = QLabel(WizardDialog)
        self.lbCFRUpperBound.setObjectName("lbCFRUpperBound")

        self.gridLayout.addWidget(self.lbCFRUpperBound, 10, 0, 1, 1)

        self.lbEFOUpperBound = QLabel(WizardDialog)
        self.lbEFOUpperBound.setObjectName("lbEFOUpperBound")

        self.gridLayout.addWidget(self.lbEFOUpperBound, 5, 0, 1, 1)

        self.leCFRSigma = QLineEdit(WizardDialog)
        self.leCFRSigma.setObjectName("leCFRSigma")

        self.gridLayout.addWidget(self.leCFRSigma, 11, 2, 1, 2)

        self.leEFOUpperBound = QLineEdit(WizardDialog)
        self.leEFOUpperBound.setObjectName("leEFOUpperBound")

        self.gridLayout.addWidget(self.leEFOUpperBound, 5, 2, 1, 2)

        self.leFrequencySingleEmitters = QLineEdit(WizardDialog)
        self.leFrequencySingleEmitters.setObjectName("leFrequencySingleEmitters")

        self.gridLayout.addWidget(self.leFrequencySingleEmitters, 6, 2, 1, 2)

        self.verticalSpacer = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding
        )

        self.gridLayout.addItem(self.verticalSpacer, 14, 0, 1, 1)

        self.cbCFRLowerBound = QCheckBox(WizardDialog)
        self.cbCFRLowerBound.setObjectName("cbCFRLowerBound")
        self.cbCFRLowerBound.setContextMenuPolicy(Qt.DefaultContextMenu)

        self.gridLayout.addWidget(self.cbCFRLowerBound, 12, 0, 1, 1)

        self.cbCFRUpperBound = QCheckBox(WizardDialog)
        self.cbCFRUpperBound.setObjectName("cbCFRUpperBound")
        self.cbCFRUpperBound.setContextMenuPolicy(Qt.DefaultContextMenu)

        self.gridLayout.addWidget(self.cbCFRUpperBound, 12, 2, 1, 2)

        self.leEFOLowerBound = QLineEdit(WizardDialog)
        self.leEFOLowerBound.setObjectName("leEFOLowerBound")

        self.gridLayout.addWidget(self.leEFOLowerBound, 3, 2, 2, 2)

        self.lbFrequencySingleEmitters = QLabel(WizardDialog)
        self.lbFrequencySingleEmitters.setObjectName("lbFrequencySingleEmitters")

        self.gridLayout.addWidget(self.lbFrequencySingleEmitters, 6, 0, 1, 2)

        self.pbAnalyzer = QPushButton(WizardDialog)
        self.pbAnalyzer.setObjectName("pbAnalyzer")

        self.gridLayout.addWidget(self.pbAnalyzer, 1, 0, 1, 4)

        self.lbEFOFiltering = QLabel(WizardDialog)
        self.lbEFOFiltering.setObjectName("lbEFOFiltering")
        self.lbEFOFiltering.setFont(font)

        self.gridLayout.addWidget(self.lbEFOFiltering, 3, 0, 1, 1)

        self.pbTimeInspector = QPushButton(WizardDialog)
        self.pbTimeInspector.setObjectName("pbTimeInspector")

        self.gridLayout.addWidget(self.pbTimeInspector, 2, 0, 1, 4)

        self.lbEFOLowerBound = QLabel(WizardDialog)
        self.lbEFOLowerBound.setObjectName("lbEFOLowerBound")

        self.gridLayout.addWidget(self.lbEFOLowerBound, 4, 0, 1, 1)

        self.leCFRUpperBound = QLineEdit(WizardDialog)
        self.leCFRUpperBound.setObjectName("leCFRUpperBound")

        self.gridLayout.addWidget(self.leCFRUpperBound, 10, 2, 1, 2)

        self.lbCFRSigmaPre = QLabel(WizardDialog)
        self.lbCFRSigmaPre.setObjectName("lbCFRSigmaPre")

        self.gridLayout.addWidget(self.lbCFRSigmaPre, 11, 0, 1, 1)

        self.lbCFRLowerBound = QLabel(WizardDialog)
        self.lbCFRLowerBound.setObjectName("lbCFRLowerBound")

        self.gridLayout.addWidget(self.lbCFRLowerBound, 9, 0, 1, 1)

        self.leCFRLowerBound = QLineEdit(WizardDialog)
        self.leCFRLowerBound.setObjectName("leCFRLowerBound")

        self.gridLayout.addWidget(self.leCFRLowerBound, 9, 2, 1, 2)

        self.pbEFOFilter = QPushButton(WizardDialog)
        self.pbEFOFilter.setObjectName("pbEFOFilter")

        self.gridLayout.addWidget(self.pbEFOFilter, 7, 0, 1, 4)

        self.pbCFRFilter = QPushButton(WizardDialog)
        self.pbCFRFilter.setObjectName("pbCFRFilter")

        self.gridLayout.addWidget(self.pbCFRFilter, 13, 0, 1, 4)

        self.pbSingleColor = QPushButton(WizardDialog)
        self.pbSingleColor.setObjectName("pbSingleColor")

        self.gridLayout.addWidget(self.pbSingleColor, 0, 0, 1, 1)

        self.pbColorUnmixer = QPushButton(WizardDialog)
        self.pbColorUnmixer.setObjectName("pbColorUnmixer")

        self.gridLayout.addWidget(self.pbColorUnmixer, 0, 1, 1, 3)

        self.retranslateUi(WizardDialog)

        QMetaObject.connectSlotsByName(WizardDialog)

    # setupUi

    def retranslateUi(self, WizardDialog):
        WizardDialog.setWindowTitle(
            QCoreApplication.translate("WizardDialog", "Dialog", None)
        )
        self.lnCFRFiltering.setText(
            QCoreApplication.translate("WizardDialog", "CFR Filtering", None)
        )
        self.lbCFRUpperBound.setText(
            QCoreApplication.translate("WizardDialog", "Upper bound", None)
        )
        self.lbEFOUpperBound.setText(
            QCoreApplication.translate("WizardDialog", "Upper Bound (Hz)", None)
        )
        self.cbCFRLowerBound.setText(
            QCoreApplication.translate("WizardDialog", "Lower bound", None)
        )
        self.cbCFRUpperBound.setText(
            QCoreApplication.translate("WizardDialog", "Upper bound", None)
        )
        self.lbFrequencySingleEmitters.setText(
            QCoreApplication.translate(
                "WizardDialog", "Frequency single emitters (Hz)", None
            )
        )
        self.pbAnalyzer.setText(
            QCoreApplication.translate("WizardDialog", "Analyzer", None)
        )
        self.lbEFOFiltering.setText(
            QCoreApplication.translate("WizardDialog", "EFO Filtering", None)
        )
        self.pbTimeInspector.setText(
            QCoreApplication.translate("WizardDialog", "Time Inspector", None)
        )
        self.lbEFOLowerBound.setText(
            QCoreApplication.translate("WizardDialog", "Lower bound (Hz)", None)
        )
        self.lbCFRSigmaPre.setText(
            QCoreApplication.translate("WizardDialog", "Robust threshold", None)
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
        self.pbSingleColor.setText(
            QCoreApplication.translate("WizardDialog", "Single Color", None)
        )
        self.pbColorUnmixer.setText(
            QCoreApplication.translate("WizardDialog", "Color Unmizer", None)
        )

    # retranslateUi
