# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'analyzer.ui'
##
## Created by: Qt User Interface Compiler version 6.4.0
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
    QWidget,
)


class Ui_Analyzer(object):
    def setupUi(self, Analyzer):
        if not Analyzer.objectName():
            Analyzer.setObjectName("Analyzer")
        Analyzer.resize(1191, 1087)
        self.gridLayout = QGridLayout(Analyzer)
        self.gridLayout.setObjectName("gridLayout")
        self.parameters_layout = QHBoxLayout()
        self.parameters_layout.setObjectName("parameters_layout")

        self.gridLayout.addLayout(self.parameters_layout, 2, 0, 1, 1)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.cbEnableEFOFiltering = QCheckBox(Analyzer)
        self.cbEnableEFOFiltering.setObjectName("cbEnableEFOFiltering")
        self.cbEnableEFOFiltering.setEnabled(True)

        self.gridLayout_2.addWidget(self.cbEnableEFOFiltering, 0, 1, 1, 1)

        self.cbEnableCFRFiltering = QCheckBox(Analyzer)
        self.cbEnableCFRFiltering.setObjectName("cbEnableCFRFiltering")
        self.cbEnableCFRFiltering.setEnabled(True)

        self.gridLayout_2.addWidget(self.cbEnableCFRFiltering, 0, 2, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.gridLayout_2.addItem(self.horizontalSpacer_3, 0, 0, 1, 1)

        self.horizontalSpacer_4 = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.gridLayout_2.addItem(self.horizontalSpacer_4, 0, 3, 1, 1)

        self.gridLayout.addLayout(self.gridLayout_2, 4, 0, 1, 1)

        self.pbUpdateViewers = QPushButton(Analyzer)
        self.pbUpdateViewers.setObjectName("pbUpdateViewers")
        self.pbUpdateViewers.setEnabled(True)

        self.gridLayout.addWidget(self.pbUpdateViewers, 5, 0, 1, 1)

        self.localizations_layout = QHBoxLayout()
        self.localizations_layout.setObjectName("localizations_layout")

        self.gridLayout.addLayout(self.localizations_layout, 3, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalSpacer_2 = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.checkLowerThreshold = QCheckBox(Analyzer)
        self.checkLowerThreshold.setObjectName("checkLowerThreshold")

        self.horizontalLayout.addWidget(self.checkLowerThreshold)

        self.checkUpperThreshold = QCheckBox(Analyzer)
        self.checkUpperThreshold.setObjectName("checkUpperThreshold")

        self.horizontalLayout.addWidget(self.checkUpperThreshold)

        self.lbThreshMultFactor = QLabel(Analyzer)
        self.lbThreshMultFactor.setObjectName("lbThreshMultFactor")

        self.horizontalLayout.addWidget(self.lbThreshMultFactor)

        self.leThreshFactor = QLineEdit(Analyzer)
        self.leThreshFactor.setObjectName("leThreshFactor")
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.leThreshFactor.sizePolicy().hasHeightForWidth()
        )
        self.leThreshFactor.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.leThreshFactor)

        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.pbAutoThreshold = QPushButton(Analyzer)
        self.pbAutoThreshold.setObjectName("pbAutoThreshold")

        self.gridLayout.addWidget(self.pbAutoThreshold, 1, 0, 1, 1)

        self.retranslateUi(Analyzer)

        QMetaObject.connectSlotsByName(Analyzer)

    # setupUi

    def retranslateUi(self, Analyzer):
        Analyzer.setWindowTitle(
            QCoreApplication.translate("Analyzer", "Analyzer", None)
        )
        self.cbEnableEFOFiltering.setText(
            QCoreApplication.translate("Analyzer", "Filter on EFO values", None)
        )
        self.cbEnableCFRFiltering.setText(
            QCoreApplication.translate("Analyzer", "Filter on CFR values", None)
        )
        self.pbUpdateViewers.setText(
            QCoreApplication.translate("Analyzer", "Filter", None)
        )
        self.checkLowerThreshold.setText(
            QCoreApplication.translate("Analyzer", "Lower bound", None)
        )
        self.checkUpperThreshold.setText(
            QCoreApplication.translate("Analyzer", "Upper bound", None)
        )
        self.lbThreshMultFactor.setText(
            QCoreApplication.translate(
                "Analyzer", "Robust threshold multiplicative factor", None
            )
        )
        self.leThreshFactor.setText(QCoreApplication.translate("Analyzer", "2.0", None))
        self.pbAutoThreshold.setText(
            QCoreApplication.translate("Analyzer", "Auto-threshold", None)
        )

    # retranslateUi
