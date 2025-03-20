# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'wizard.ui'
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
    QComboBox,
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
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.MinimumExpanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(WizardDialog.sizePolicy().hasHeightForWidth())
        WizardDialog.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(WizardDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalSpacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.gridLayout.addItem(self.verticalSpacer, 17, 0, 1, 1)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.setObjectName("mainLayout")
        self.pbLoadData = QPushButton(WizardDialog)
        self.pbLoadData.setObjectName("pbLoadData")
        self.pbLoadData.setMinimumSize(QSize(320, 0))

        self.mainLayout.addWidget(self.pbLoadData)

        self.pbReset = QPushButton(WizardDialog)
        self.pbReset.setObjectName("pbReset")

        self.mainLayout.addWidget(self.pbReset)

        self.verticalSpacer_2 = QSpacerItem(
            20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )

        self.mainLayout.addItem(self.verticalSpacer_2)

        self.lbMultiplexing = QLabel(WizardDialog)
        self.lbMultiplexing.setObjectName("lbMultiplexing")
        font = QFont()
        font.setBold(True)
        self.lbMultiplexing.setFont(font)

        self.mainLayout.addWidget(self.lbMultiplexing)

        self.color_layout = QHBoxLayout()
        self.color_layout.setObjectName("color_layout")
        self.pbSingleColor = QPushButton(WizardDialog)
        self.pbSingleColor.setObjectName("pbSingleColor")

        self.color_layout.addWidget(self.pbSingleColor)

        self.pbColorUnmixer = QPushButton(WizardDialog)
        self.pbColorUnmixer.setObjectName("pbColorUnmixer")

        self.color_layout.addWidget(self.pbColorUnmixer)

        self.mainLayout.addLayout(self.color_layout)

        self.fluorophores_layout = QHBoxLayout()
        self.fluorophores_layout.setObjectName("fluorophores_layout")
        self.lbActiveColor = QLabel(WizardDialog)
        self.lbActiveColor.setObjectName("lbActiveColor")
        sizePolicy1 = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(
            self.lbActiveColor.sizePolicy().hasHeightForWidth()
        )
        self.lbActiveColor.setSizePolicy(sizePolicy1)

        self.fluorophores_layout.addWidget(self.lbActiveColor)

        self.cmActiveColor = QComboBox(WizardDialog)
        self.cmActiveColor.addItem("")
        self.cmActiveColor.setObjectName("cmActiveColor")
        sizePolicy2 = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(
            self.cmActiveColor.sizePolicy().hasHeightForWidth()
        )
        self.cmActiveColor.setSizePolicy(sizePolicy2)

        self.fluorophores_layout.addWidget(self.cmActiveColor)

        self.mainLayout.addLayout(self.fluorophores_layout)

        self.verticalSpacer_4 = QSpacerItem(
            20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )

        self.mainLayout.addItem(self.verticalSpacer_4)

        self.lbFilters = QLabel(WizardDialog)
        self.lbFilters.setObjectName("lbFilters")
        self.lbFilters.setFont(font)

        self.mainLayout.addWidget(self.lbFilters)

        self.pbTimeInspector = QPushButton(WizardDialog)
        self.pbTimeInspector.setObjectName("pbTimeInspector")

        self.mainLayout.addWidget(self.pbTimeInspector)

        self.verticalSpacer_3 = QSpacerItem(
            20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )

        self.mainLayout.addItem(self.verticalSpacer_3)

        self.pbAnalyzer = QPushButton(WizardDialog)
        self.pbAnalyzer.setObjectName("pbAnalyzer")

        self.mainLayout.addWidget(self.pbAnalyzer)

        self.lbEFOFiltering = QLabel(WizardDialog)
        self.lbEFOFiltering.setObjectName("lbEFOFiltering")
        self.lbEFOFiltering.setFont(font)

        self.mainLayout.addWidget(self.lbEFOFiltering)

        self.efo_lower_bound_layout = QHBoxLayout()
        self.efo_lower_bound_layout.setObjectName("efo_lower_bound_layout")
        self.lbEFOLowerBound = QLabel(WizardDialog)
        self.lbEFOLowerBound.setObjectName("lbEFOLowerBound")

        self.efo_lower_bound_layout.addWidget(self.lbEFOLowerBound)

        self.leEFOLowerBound = QLineEdit(WizardDialog)
        self.leEFOLowerBound.setObjectName("leEFOLowerBound")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(
            self.leEFOLowerBound.sizePolicy().hasHeightForWidth()
        )
        self.leEFOLowerBound.setSizePolicy(sizePolicy3)

        self.efo_lower_bound_layout.addWidget(self.leEFOLowerBound)

        self.mainLayout.addLayout(self.efo_lower_bound_layout)

        self.efo_upper_bound_layout = QHBoxLayout()
        self.efo_upper_bound_layout.setObjectName("efo_upper_bound_layout")
        self.lbEFOUpperBound = QLabel(WizardDialog)
        self.lbEFOUpperBound.setObjectName("lbEFOUpperBound")

        self.efo_upper_bound_layout.addWidget(self.lbEFOUpperBound)

        self.leEFOUpperBound = QLineEdit(WizardDialog)
        self.leEFOUpperBound.setObjectName("leEFOUpperBound")
        sizePolicy3.setHeightForWidth(
            self.leEFOUpperBound.sizePolicy().hasHeightForWidth()
        )
        self.leEFOUpperBound.setSizePolicy(sizePolicy3)

        self.efo_upper_bound_layout.addWidget(self.leEFOUpperBound)

        self.mainLayout.addLayout(self.efo_upper_bound_layout)

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
        sizePolicy3.setHeightForWidth(
            self.leCFRLowerBound.sizePolicy().hasHeightForWidth()
        )
        self.leCFRLowerBound.setSizePolicy(sizePolicy3)

        self.cfr_lower_bound_layout.addWidget(self.leCFRLowerBound)

        self.mainLayout.addLayout(self.cfr_lower_bound_layout)

        self.cfr_upper_bound_layout = QHBoxLayout()
        self.cfr_upper_bound_layout.setObjectName("cfr_upper_bound_layout")
        self.lbCFRUpperBound = QLabel(WizardDialog)
        self.lbCFRUpperBound.setObjectName("lbCFRUpperBound")

        self.cfr_upper_bound_layout.addWidget(self.lbCFRUpperBound)

        self.leCFRUpperBound = QLineEdit(WizardDialog)
        self.leCFRUpperBound.setObjectName("leCFRUpperBound")
        sizePolicy3.setHeightForWidth(
            self.leCFRUpperBound.sizePolicy().hasHeightForWidth()
        )
        self.leCFRUpperBound.setSizePolicy(sizePolicy3)

        self.cfr_upper_bound_layout.addWidget(self.leCFRUpperBound)

        self.mainLayout.addLayout(self.cfr_upper_bound_layout)

        self.pbCFRFilter = QPushButton(WizardDialog)
        self.pbCFRFilter.setObjectName("pbCFRFilter")

        self.mainLayout.addWidget(self.pbCFRFilter)

        self.verticalSpacer_5 = QSpacerItem(
            20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )

        self.mainLayout.addItem(self.verticalSpacer_5)

        self.pbSaveData = QPushButton(WizardDialog)
        self.pbSaveData.setObjectName("pbSaveData")

        self.mainLayout.addWidget(self.pbSaveData)

        self.pbExportData = QPushButton(WizardDialog)
        self.pbExportData.setObjectName("pbExportData")

        self.mainLayout.addWidget(self.pbExportData)

        self.gridLayout.addLayout(self.mainLayout, 0, 0, 1, 1)

        QWidget.setTabOrder(self.pbLoadData, self.pbReset)
        QWidget.setTabOrder(self.pbReset, self.pbSingleColor)
        QWidget.setTabOrder(self.pbSingleColor, self.pbColorUnmixer)
        QWidget.setTabOrder(self.pbColorUnmixer, self.cmActiveColor)
        QWidget.setTabOrder(self.cmActiveColor, self.pbTimeInspector)
        QWidget.setTabOrder(self.pbTimeInspector, self.pbAnalyzer)
        QWidget.setTabOrder(self.pbAnalyzer, self.leEFOLowerBound)
        QWidget.setTabOrder(self.leEFOLowerBound, self.leEFOUpperBound)
        QWidget.setTabOrder(self.leEFOUpperBound, self.pbEFOFilter)
        QWidget.setTabOrder(self.pbEFOFilter, self.leCFRLowerBound)
        QWidget.setTabOrder(self.leCFRLowerBound, self.leCFRUpperBound)
        QWidget.setTabOrder(self.leCFRUpperBound, self.pbCFRFilter)
        QWidget.setTabOrder(self.pbCFRFilter, self.pbSaveData)
        QWidget.setTabOrder(self.pbSaveData, self.pbExportData)

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
        self.pbReset.setText(QCoreApplication.translate("WizardDialog", "Reset", None))
        self.lbMultiplexing.setText(
            QCoreApplication.translate("WizardDialog", "Multiplexing", None)
        )
        self.pbSingleColor.setText(
            QCoreApplication.translate("WizardDialog", "Single fluorophore", None)
        )
        self.pbColorUnmixer.setText(
            QCoreApplication.translate("WizardDialog", "Unmixer", None)
        )
        self.lbActiveColor.setText(
            QCoreApplication.translate("WizardDialog", "Active fluorophore", None)
        )
        self.cmActiveColor.setItemText(
            0, QCoreApplication.translate("WizardDialog", "All", None)
        )

        self.lbFilters.setText(
            QCoreApplication.translate("WizardDialog", "Filters", None)
        )
        self.pbTimeInspector.setText(
            QCoreApplication.translate("WizardDialog", "Time Inspector", None)
        )
        self.pbAnalyzer.setText(
            QCoreApplication.translate("WizardDialog", "Analyzer", None)
        )
        self.lbEFOFiltering.setText(
            QCoreApplication.translate("WizardDialog", "EFO filtering", None)
        )
        self.lbEFOLowerBound.setText(
            QCoreApplication.translate("WizardDialog", "Lower bound (Hz)", None)
        )
        self.lbEFOUpperBound.setText(
            QCoreApplication.translate("WizardDialog", "Upper bound (Hz)", None)
        )
        self.pbEFOFilter.setText(
            QCoreApplication.translate("WizardDialog", "FIlter EFO", None)
        )
        self.lbCFRFiltering.setText(
            QCoreApplication.translate("WizardDialog", "CFR filtering", None)
        )
        self.lbCFRLowerBound.setText(
            QCoreApplication.translate("WizardDialog", "Lower bound", None)
        )
        self.lbCFRUpperBound.setText(
            QCoreApplication.translate("WizardDialog", "Upper bound", None)
        )
        self.pbCFRFilter.setText(
            QCoreApplication.translate("WizardDialog", "FIlter CFR", None)
        )
        self.pbSaveData.setText(
            QCoreApplication.translate("WizardDialog", "Save", None)
        )
        self.pbExportData.setText(
            QCoreApplication.translate("WizardDialog", "Export", None)
        )

    # retranslateUi
