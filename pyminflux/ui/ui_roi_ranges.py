# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'roi_ranges.ui'
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
    QAbstractButton,
    QApplication,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QSpacerItem,
    QWidget,
)


class Ui_ROIRanges(object):
    def setupUi(self, ROIRanges):
        if not ROIRanges.objectName():
            ROIRanges.setObjectName("ROIRanges")
        ROIRanges.resize(390, 140)
        self.gridLayout = QGridLayout(ROIRanges)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lbCFR = QLabel(ROIRanges)
        self.lbCFR.setObjectName("lbCFR")

        self.horizontalLayout.addWidget(self.lbCFR)

        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.lbMinCFR = QLabel(ROIRanges)
        self.lbMinCFR.setObjectName("lbMinCFR")

        self.horizontalLayout.addWidget(self.lbMinCFR)

        self.leCFRMin = QLineEdit(ROIRanges)
        self.leCFRMin.setObjectName("leCFRMin")

        self.horizontalLayout.addWidget(self.leCFRMin)

        self.lbCFRMax = QLabel(ROIRanges)
        self.lbCFRMax.setObjectName("lbCFRMax")

        self.horizontalLayout.addWidget(self.lbCFRMax)

        self.leCFRMax = QLineEdit(ROIRanges)
        self.leCFRMax.setObjectName("leCFRMax")

        self.horizontalLayout.addWidget(self.leCFRMax)

        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lbEFO = QLabel(ROIRanges)
        self.lbEFO.setObjectName("lbEFO")

        self.horizontalLayout_2.addWidget(self.lbEFO)

        self.horizontalSpacer_2 = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.lbEFOMin = QLabel(ROIRanges)
        self.lbEFOMin.setObjectName("lbEFOMin")

        self.horizontalLayout_2.addWidget(self.lbEFOMin)

        self.leEFOMin = QLineEdit(ROIRanges)
        self.leEFOMin.setObjectName("leEFOMin")

        self.horizontalLayout_2.addWidget(self.leEFOMin)

        self.lbEFOMax = QLabel(ROIRanges)
        self.lbEFOMax.setObjectName("lbEFOMax")

        self.horizontalLayout_2.addWidget(self.lbEFOMax)

        self.leEFOMax = QLineEdit(ROIRanges)
        self.leEFOMax.setObjectName("leEFOMax")

        self.horizontalLayout_2.addWidget(self.leEFOMax)

        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(ROIRanges)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)

        self.retranslateUi(ROIRanges)
        self.buttonBox.accepted.connect(ROIRanges.accept)
        self.buttonBox.rejected.connect(ROIRanges.reject)

        QMetaObject.connectSlotsByName(ROIRanges)

    # setupUi

    def retranslateUi(self, ROIRanges):
        self.lbCFR.setText(QCoreApplication.translate("ROIRanges", "CFR", None))
        self.lbMinCFR.setText(QCoreApplication.translate("ROIRanges", "min", None))
        self.lbCFRMax.setText(QCoreApplication.translate("ROIRanges", "max", None))
        self.lbEFO.setText(QCoreApplication.translate("ROIRanges", "EFO", None))
        self.lbEFOMin.setText(QCoreApplication.translate("ROIRanges", "min", None))
        self.lbEFOMax.setText(QCoreApplication.translate("ROIRanges", "max", None))
        pass

    # retranslateUi
