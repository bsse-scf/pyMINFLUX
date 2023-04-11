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
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class Ui_WizardDialog(object):
    def setupUi(self, WizardDialog):
        if not WizardDialog.objectName():
            WizardDialog.setObjectName("WizardDialog")
        WizardDialog.resize(357, 939)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(WizardDialog.sizePolicy().hasHeightForWidth())
        WizardDialog.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(WizardDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalSpacer = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding
        )

        self.gridLayout.addItem(self.verticalSpacer, 17, 0, 1, 1)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.setObjectName("mainLayout")
        self.pbLoadData = QPushButton(WizardDialog)
        self.pbLoadData.setObjectName("pbLoadData")

        self.mainLayout.addWidget(self.pbLoadData)

        self.color_layout = QHBoxLayout()
        self.color_layout.setObjectName("color_layout")
        self.pbSingleColor = QPushButton(WizardDialog)
        self.pbSingleColor.setObjectName("pbSingleColor")

        self.color_layout.addWidget(self.pbSingleColor)

        self.pbColorUnmixer = QPushButton(WizardDialog)
        self.pbColorUnmixer.setObjectName("pbColorUnmixer")

        self.color_layout.addWidget(self.pbColorUnmixer)

        self.mainLayout.addLayout(self.color_layout)

        self.pbTimeInspector = QPushButton(WizardDialog)
        self.pbTimeInspector.setObjectName("pbTimeInspector")

        self.mainLayout.addWidget(self.pbTimeInspector)

        self.pbAnalyzer = QPushButton(WizardDialog)
        self.pbAnalyzer.setObjectName("pbAnalyzer")

        self.mainLayout.addWidget(self.pbAnalyzer)

        self.lbEFOFiltering = QLabel(WizardDialog)
        self.lbEFOFiltering.setObjectName("lbEFOFiltering")
        font = QFont()
        font.setBold(True)
        self.lbEFOFiltering.setFont(font)

        self.mainLayout.addWidget(self.lbEFOFiltering)

        self.efo_lower_bound_layout = QHBoxLayout()
        self.efo_lower_bound_layout.setObjectName("efo_lower_bound_layout")
        self.lbEFOLowerBound = QLabel(WizardDialog)
        self.lbEFOLowerBound.setObjectName("lbEFOLowerBound")

        self.efo_lower_bound_layout.addWidget(self.lbEFOLowerBound)

        self.leEFOLowerBound = QLineEdit(WizardDialog)
        self.leEFOLowerBound.setObjectName("leEFOLowerBound")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(
            self.leEFOLowerBound.sizePolicy().hasHeightForWidth()
        )
        self.leEFOLowerBound.setSizePolicy(sizePolicy1)

        self.efo_lower_bound_layout.addWidget(self.leEFOLowerBound)

        self.mainLayout.addLayout(self.efo_lower_bound_layout)

        self.efo_upper_bound_layout = QHBoxLayout()
        self.efo_upper_bound_layout.setObjectName("efo_upper_bound_layout")
        self.lbEFOUpperBound = QLabel(WizardDialog)
        self.lbEFOUpperBound.setObjectName("lbEFOUpperBound")

        self.efo_upper_bound_layout.addWidget(self.lbEFOUpperBound)

        self.leEFOUpperBound = QLineEdit(WizardDialog)
        self.leEFOUpperBound.setObjectName("leEFOUpperBound")
        sizePolicy1.setHeightForWidth(
            self.leEFOUpperBound.sizePolicy().hasHeightForWidth()
        )
        self.leEFOUpperBound.setSizePolicy(sizePolicy1)

        self.efo_upper_bound_layout.addWidget(self.leEFOUpperBound)

        self.mainLayout.addLayout(self.efo_upper_bound_layout)

        self.efo_emitters_layout = QHBoxLayout()
        self.efo_emitters_layout.setObjectName("efo_emitters_layout")
        self.lbFrequencySingleEmitters = QLabel(WizardDialog)
        self.lbFrequencySingleEmitters.setObjectName("lbFrequencySingleEmitters")

        self.efo_emitters_layout.addWidget(self.lbFrequencySingleEmitters)

        self.leFrequencySingleEmitters = QLineEdit(WizardDialog)
        self.leFrequencySingleEmitters.setObjectName("leFrequencySingleEmitters")
        sizePolicy1.setHeightForWidth(
            self.leFrequencySingleEmitters.sizePolicy().hasHeightForWidth()
        )
        self.leFrequencySingleEmitters.setSizePolicy(sizePolicy1)

        self.efo_emitters_layout.addWidget(self.leFrequencySingleEmitters)

        self.mainLayout.addLayout(self.efo_emitters_layout)

        self.pbEFOFilter = QPushButton(WizardDialog)
        self.pbEFOFilter.setObjectName("pbEFOFilter")

        self.mainLayout.addWidget(self.pbEFOFilter)

        self.lbCFRFiltering = QLabel(WizardDialog)
        self.lbCFRFiltering.setObjectName("lbCFRFiltering")
        self.lbCFRFiltering.setFont(font)

        self.mainLayout.addWidget(self.lbCFRFiltering)

        self.cfr_lower_bound_layout = QHBoxLayout()
        self.cfr_lower_bound_layout.setObjectName("cfr_lower_bound_layout")
        self.lbCFRLowerBound = QLabel(WizardDialog)
        self.lbCFRLowerBound.setObjectName("lbCFRLowerBound")

        self.cfr_lower_bound_layout.addWidget(self.lbCFRLowerBound)

        self.leCFRLowerBound = QLineEdit(WizardDialog)
        self.leCFRLowerBound.setObjectName("leCFRLowerBound")
        sizePolicy1.setHeightForWidth(
            self.leCFRLowerBound.sizePolicy().hasHeightForWidth()
        )
        self.leCFRLowerBound.setSizePolicy(sizePolicy1)

        self.cfr_lower_bound_layout.addWidget(self.leCFRLowerBound)

        self.mainLayout.addLayout(self.cfr_lower_bound_layout)

        self.cfr_upper_bound_layout = QHBoxLayout()
        self.cfr_upper_bound_layout.setObjectName("cfr_upper_bound_layout")
        self.lbCFRUpperBound = QLabel(WizardDialog)
        self.lbCFRUpperBound.setObjectName("lbCFRUpperBound")

        self.cfr_upper_bound_layout.addWidget(self.lbCFRUpperBound)

        self.leCFRUpperBound = QLineEdit(WizardDialog)
        self.leCFRUpperBound.setObjectName("leCFRUpperBound")
        sizePolicy1.setHeightForWidth(
            self.leCFRUpperBound.sizePolicy().hasHeightForWidth()
        )
        self.leCFRUpperBound.setSizePolicy(sizePolicy1)

        self.cfr_upper_bound_layout.addWidget(self.leCFRUpperBound)

        self.mainLayout.addLayout(self.cfr_upper_bound_layout)

        self.robust_threshold_layout = QHBoxLayout()
        self.robust_threshold_layout.setObjectName("robust_threshold_layout")
        self.lbCFRSigma = QLabel(WizardDialog)
        self.lbCFRSigma.setObjectName("lbCFRSigma")

        self.robust_threshold_layout.addWidget(self.lbCFRSigma)

        self.leCFRSigma = QLineEdit(WizardDialog)
        self.leCFRSigma.setObjectName("leCFRSigma")
        sizePolicy1.setHeightForWidth(self.leCFRSigma.sizePolicy().hasHeightForWidth())
        self.leCFRSigma.setSizePolicy(sizePolicy1)

        self.robust_threshold_layout.addWidget(self.leCFRSigma)

        self.mainLayout.addLayout(self.robust_threshold_layout)

        self.cfr_bounds_layout = QHBoxLayout()
        self.cfr_bounds_layout.setObjectName("cfr_bounds_layout")
        self.cbCFRLowerBound = QCheckBox(WizardDialog)
        self.cbCFRLowerBound.setObjectName("cbCFRLowerBound")
        self.cbCFRLowerBound.setContextMenuPolicy(Qt.DefaultContextMenu)

        self.cfr_bounds_layout.addWidget(self.cbCFRLowerBound)

        self.cbCFRUpperBound = QCheckBox(WizardDialog)
        self.cbCFRUpperBound.setObjectName("cbCFRUpperBound")
        self.cbCFRUpperBound.setContextMenuPolicy(Qt.DefaultContextMenu)

        self.cfr_bounds_layout.addWidget(self.cbCFRUpperBound)

        self.mainLayout.addLayout(self.cfr_bounds_layout)

        self.pbCFRFilter = QPushButton(WizardDialog)
        self.pbCFRFilter.setObjectName("pbCFRFilter")

        self.mainLayout.addWidget(self.pbCFRFilter)

        self.gridLayout.addLayout(self.mainLayout, 0, 0, 1, 1)

        self.retranslateUi(WizardDialog)

        QMetaObject.connectSlotsByName(WizardDialog)

    # setupUi

    def retranslateUi(self, WizardDialog):
        WizardDialog.setWindowTitle(
            QCoreApplication.translate("WizardDialog", "Dialog", None)
        )
        self.pbLoadData.setText(
            QCoreApplication.translate("WizardDialog", "Load", None)
        )
        self.pbSingleColor.setText(
            QCoreApplication.translate("WizardDialog", "Single Color", None)
        )
        self.pbColorUnmixer.setText(
            QCoreApplication.translate("WizardDialog", "Color Unmizer", None)
        )
        self.pbTimeInspector.setText(
            QCoreApplication.translate("WizardDialog", "Time Inspector", None)
        )
        self.pbAnalyzer.setText(
            QCoreApplication.translate("WizardDialog", "Analyzer", None)
        )
        self.lbEFOFiltering.setText(
            QCoreApplication.translate("WizardDialog", "EFO Filtering", None)
        )
        self.lbEFOLowerBound.setText(
            QCoreApplication.translate("WizardDialog", "Lower bound (Hz)", None)
        )
        self.lbEFOUpperBound.setText(
            QCoreApplication.translate("WizardDialog", "Upper Bound (Hz)", None)
        )
        self.lbFrequencySingleEmitters.setText(
            QCoreApplication.translate(
                "WizardDialog", "Frequency single emitters (Hz)", None
            )
        )
        self.pbEFOFilter.setText(
            QCoreApplication.translate("WizardDialog", "FIlter EFO", None)
        )
        self.lbCFRFiltering.setText(
            QCoreApplication.translate("WizardDialog", "CFR Filtering", None)
        )
        self.lbCFRLowerBound.setText(
            QCoreApplication.translate("WizardDialog", "Lower bound", None)
        )
        self.lbCFRUpperBound.setText(
            QCoreApplication.translate("WizardDialog", "Upper bound", None)
        )
        self.lbCFRSigma.setText(
            QCoreApplication.translate("WizardDialog", "Robust threshold", None)
        )
        self.cbCFRLowerBound.setText(
            QCoreApplication.translate("WizardDialog", "Lower bound", None)
        )
        self.cbCFRUpperBound.setText(
            QCoreApplication.translate("WizardDialog", "Upper bound", None)
        )
        self.pbCFRFilter.setText(
            QCoreApplication.translate("WizardDialog", "FIlter CFR", None)
        )

    # retranslateUi
