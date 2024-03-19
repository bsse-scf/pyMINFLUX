# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'roi_ranges.ui'
##
## Created by: Qt User Interface Compiler version 6.6.2
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
        ROIRanges.resize(479, 168)
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ROIRanges.sizePolicy().hasHeightForWidth())
        ROIRanges.setSizePolicy(sizePolicy)
        ROIRanges.setMaximumSize(QSize(16777215, 16777215))
        self.gridLayout_2 = QGridLayout(ROIRanges)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setVerticalSpacing(0)
        self.leTrLenMin = QLineEdit(ROIRanges)
        self.leTrLenMin.setObjectName("leTrLenMin")

        self.gridLayout.addWidget(self.leTrLenMin, 2, 2, 1, 1)

        self.lbTrLenMax = QLabel(ROIRanges)
        self.lbTrLenMax.setObjectName("lbTrLenMax")

        self.gridLayout.addWidget(self.lbTrLenMax, 2, 3, 1, 1)

        self.lbEFOMax = QLabel(ROIRanges)
        self.lbEFOMax.setObjectName("lbEFOMax")

        self.gridLayout.addWidget(self.lbEFOMax, 1, 3, 1, 1)

        self.leEFOMin = QLineEdit(ROIRanges)
        self.leEFOMin.setObjectName("leEFOMin")

        self.gridLayout.addWidget(self.leEFOMin, 1, 2, 1, 1)

        self.lbTrLenMin = QLabel(ROIRanges)
        self.lbTrLenMin.setObjectName("lbTrLenMin")

        self.gridLayout.addWidget(self.lbTrLenMin, 2, 1, 1, 1)

        self.leCFRMax = QLineEdit(ROIRanges)
        self.leCFRMax.setObjectName("leCFRMax")

        self.gridLayout.addWidget(self.leCFRMax, 0, 4, 1, 1)

        self.lbMinCFR = QLabel(ROIRanges)
        self.lbMinCFR.setObjectName("lbMinCFR")

        self.gridLayout.addWidget(self.lbMinCFR, 0, 1, 1, 1)

        self.lbEFOMin = QLabel(ROIRanges)
        self.lbEFOMin.setObjectName("lbEFOMin")

        self.gridLayout.addWidget(self.lbEFOMin, 1, 1, 1, 1)

        self.lbEFO = QLabel(ROIRanges)
        self.lbEFO.setObjectName("lbEFO")

        self.gridLayout.addWidget(self.lbEFO, 1, 0, 1, 1)

        self.lbCFRMax = QLabel(ROIRanges)
        self.lbCFRMax.setObjectName("lbCFRMax")

        self.gridLayout.addWidget(self.lbCFRMax, 0, 3, 1, 1)

        self.leEFOMax = QLineEdit(ROIRanges)
        self.leEFOMax.setObjectName("leEFOMax")

        self.gridLayout.addWidget(self.leEFOMax, 1, 4, 1, 1)

        self.leCFRMin = QLineEdit(ROIRanges)
        self.leCFRMin.setObjectName("leCFRMin")

        self.gridLayout.addWidget(self.leCFRMin, 0, 2, 1, 1)

        self.leTrLenMax = QLineEdit(ROIRanges)
        self.leTrLenMax.setObjectName("leTrLenMax")

        self.gridLayout.addWidget(self.leTrLenMax, 2, 4, 1, 1)

        self.lbCFR = QLabel(ROIRanges)
        self.lbCFR.setObjectName("lbCFR")

        self.gridLayout.addWidget(self.lbCFR, 0, 0, 1, 1)

        self.lbTrLen = QLabel(ROIRanges)
        self.lbTrLen.setObjectName("lbTrLen")

        self.gridLayout.addWidget(self.lbTrLen, 2, 0, 1, 1)

        self.lbTime = QLabel(ROIRanges)
        self.lbTime.setObjectName("lbTime")

        self.gridLayout.addWidget(self.lbTime, 3, 0, 1, 1)

        self.lbTimeMin = QLabel(ROIRanges)
        self.lbTimeMin.setObjectName("lbTimeMin")

        self.gridLayout.addWidget(self.lbTimeMin, 3, 1, 1, 1)

        self.lbTimeMax = QLabel(ROIRanges)
        self.lbTimeMax.setObjectName("lbTimeMax")

        self.gridLayout.addWidget(self.lbTimeMax, 3, 3, 1, 1)

        self.leTimeMin = QLineEdit(ROIRanges)
        self.leTimeMin.setObjectName("leTimeMin")

        self.gridLayout.addWidget(self.leTimeMin, 3, 2, 1, 1)

        self.leTimeMax = QLineEdit(ROIRanges)
        self.leTimeMax.setObjectName("leTimeMax")

        self.gridLayout.addWidget(self.leTimeMax, 3, 4, 1, 1)

        self.gridLayout_2.addLayout(self.gridLayout, 0, 1, 1, 1)

        self.buttonBox = QDialogButtonBox(ROIRanges)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        self.gridLayout_2.addWidget(self.buttonBox, 2, 0, 1, 2)

        self.verticalSpacer_bottom = QSpacerItem(
            20, 5, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.gridLayout_2.addItem(self.verticalSpacer_bottom, 1, 0, 1, 2)

        self.retranslateUi(ROIRanges)
        self.buttonBox.accepted.connect(ROIRanges.accept)
        self.buttonBox.rejected.connect(ROIRanges.reject)

        QMetaObject.connectSlotsByName(ROIRanges)

    # setupUi

    def retranslateUi(self, ROIRanges):
        self.lbTrLenMax.setText(QCoreApplication.translate("ROIRanges", "max", None))
        self.lbEFOMax.setText(QCoreApplication.translate("ROIRanges", "max", None))
        self.lbTrLenMin.setText(QCoreApplication.translate("ROIRanges", "min", None))
        self.lbMinCFR.setText(QCoreApplication.translate("ROIRanges", "min", None))
        self.lbEFOMin.setText(QCoreApplication.translate("ROIRanges", "min", None))
        self.lbEFO.setText(QCoreApplication.translate("ROIRanges", "EFO", None))
        self.lbCFRMax.setText(QCoreApplication.translate("ROIRanges", "max", None))
        self.lbCFR.setText(QCoreApplication.translate("ROIRanges", "CFR", None))
        self.lbTrLen.setText(
            QCoreApplication.translate("ROIRanges", "Trace length", None)
        )
        self.lbTime.setText(QCoreApplication.translate("ROIRanges", "Time", None))
        self.lbTimeMin.setText(QCoreApplication.translate("ROIRanges", "min", None))
        self.lbTimeMax.setText(QCoreApplication.translate("ROIRanges", "max", None))
        pass

    # retranslateUi
