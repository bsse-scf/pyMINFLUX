# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'frc_tool.ui'
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
    QLayout,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QWidget,
)


class Ui_FRCTool(object):
    def setupUi(self, FRCTool):
        if not FRCTool.objectName():
            FRCTool.setObjectName("FRCTool")
        FRCTool.resize(1050, 800)
        FRCTool.setMinimumSize(QSize(800, 600))
        self.gridLayout = QGridLayout(FRCTool)
        self.gridLayout.setObjectName("gridLayout")
        self.hlParameters = QHBoxLayout()
        self.hlParameters.setObjectName("hlParameters")
        self.hlParameters.setSizeConstraint(QLayout.SetFixedSize)
        self.hsCFRFilterBefore = QSpacerItem(
            20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.hlParameters.addItem(self.hsCFRFilterBefore)

        self.lbLateralResolution = QLabel(FRCTool)
        self.lbLateralResolution.setObjectName("lbLateralResolution")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.lbLateralResolution.sizePolicy().hasHeightForWidth()
        )
        self.lbLateralResolution.setSizePolicy(sizePolicy)

        self.hlParameters.addWidget(self.lbLateralResolution)

        self.leLateralResolution = QLineEdit(FRCTool)
        self.leLateralResolution.setObjectName("leLateralResolution")
        sizePolicy.setHeightForWidth(
            self.leLateralResolution.sizePolicy().hasHeightForWidth()
        )
        self.leLateralResolution.setSizePolicy(sizePolicy)

        self.hlParameters.addWidget(self.leLateralResolution)

        self.cbEndpoint = QCheckBox(FRCTool)
        self.cbEndpoint.setObjectName("cbEndpoint")

        self.hlParameters.addWidget(self.cbEndpoint)

        self.lbTemporalResolution = QLabel(FRCTool)
        self.lbTemporalResolution.setObjectName("lbTemporalResolution")
        sizePolicy.setHeightForWidth(
            self.lbTemporalResolution.sizePolicy().hasHeightForWidth()
        )
        self.lbTemporalResolution.setSizePolicy(sizePolicy)

        self.hlParameters.addWidget(self.lbTemporalResolution)

        self.leTemporalResolution = QLineEdit(FRCTool)
        self.leTemporalResolution.setObjectName("leTemporalResolution")

        self.hlParameters.addWidget(self.leTemporalResolution)

        self.lbNumRepeats = QLabel(FRCTool)
        self.lbNumRepeats.setObjectName("lbNumRepeats")
        sizePolicy.setHeightForWidth(self.lbNumRepeats.sizePolicy().hasHeightForWidth())
        self.lbNumRepeats.setSizePolicy(sizePolicy)

        self.hlParameters.addWidget(self.lbNumRepeats)

        self.leNumRepeats = QLineEdit(FRCTool)
        self.leNumRepeats.setObjectName("leNumRepeats")
        sizePolicy.setHeightForWidth(self.leNumRepeats.sizePolicy().hasHeightForWidth())
        self.leNumRepeats.setSizePolicy(sizePolicy)

        self.hlParameters.addWidget(self.leNumRepeats)

        self.pbRunFRCAnalysis = QPushButton(FRCTool)
        self.pbRunFRCAnalysis.setObjectName("pbRunFRCAnalysis")
        sizePolicy.setHeightForWidth(
            self.pbRunFRCAnalysis.sizePolicy().hasHeightForWidth()
        )
        self.pbRunFRCAnalysis.setSizePolicy(sizePolicy)

        self.hlParameters.addWidget(self.pbRunFRCAnalysis)

        self.hsCFRFilterAfter = QSpacerItem(
            20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.hlParameters.addItem(self.hsCFRFilterAfter)

        self.gridLayout.addLayout(self.hlParameters, 0, 0, 1, 1)

        self.hlPlot = QHBoxLayout()
        self.hlPlot.setObjectName("hlPlot")

        self.gridLayout.addLayout(self.hlPlot, 1, 0, 1, 1)

        self.hlProgress = QHBoxLayout()
        self.hlProgress.setObjectName("hlProgress")
        self.progress_bar = QProgressBar(FRCTool)
        self.progress_bar.setObjectName("progress_bar")
        self.progress_bar.setValue(0)

        self.hlProgress.addWidget(self.progress_bar)

        self.pbInterrupt = QPushButton(FRCTool)
        self.pbInterrupt.setObjectName("pbInterrupt")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.pbInterrupt.sizePolicy().hasHeightForWidth())
        self.pbInterrupt.setSizePolicy(sizePolicy1)

        self.hlProgress.addWidget(self.pbInterrupt)

        self.gridLayout.addLayout(self.hlProgress, 2, 0, 1, 1)

        self.retranslateUi(FRCTool)

        QMetaObject.connectSlotsByName(FRCTool)

    # setupUi

    def retranslateUi(self, FRCTool):
        FRCTool.setWindowTitle(
            QCoreApplication.translate("FRCTool", "FRC Analyzer", None)
        )
        self.lbLateralResolution.setText(
            QCoreApplication.translate("FRCTool", "Spatial (xy) resolution (nm)", None)
        )
        self.cbEndpoint.setText(
            QCoreApplication.translate("FRCTool", "Endpoint estimation", None)
        )
        self.lbTemporalResolution.setText(
            QCoreApplication.translate("FRCTool", "Temporal resoluton (s)", None)
        )
        self.lbNumRepeats.setText(
            QCoreApplication.translate("FRCTool", "Number of repeats", None)
        )
        self.pbRunFRCAnalysis.setText(
            QCoreApplication.translate("FRCTool", "Run", None)
        )
        self.pbInterrupt.setText(QCoreApplication.translate("FRCTool", "Cancel", None))

    # retranslateUi
