# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'analyzer.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
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
    QTabWidget,
    QWidget,
)


class Ui_Analyzer(object):
    def setupUi(self, Analyzer):
        if not Analyzer.objectName():
            Analyzer.setObjectName("Analyzer")
        Analyzer.resize(1050, 800)
        Analyzer.setMinimumSize(QSize(800, 600))
        self.gridLayout = QGridLayout(Analyzer)
        self.gridLayout.setObjectName("gridLayout")
        self.tabFilterOptions = QTabWidget(Analyzer)
        self.tabFilterOptions.setObjectName("tabFilterOptions")
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.tabFilterOptions.sizePolicy().hasHeightForWidth()
        )
        self.tabFilterOptions.setSizePolicy(sizePolicy)
        self.tabFilterOptions.setMaximumSize(QSize(16777215, 16777215))
        self.tab_efo_peak_detection = QWidget()
        self.tab_efo_peak_detection.setObjectName("tab_efo_peak_detection")
        sizePolicy1 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(
            self.tab_efo_peak_detection.sizePolicy().hasHeightForWidth()
        )
        self.tab_efo_peak_detection.setSizePolicy(sizePolicy1)
        self.horizontalLayout_3 = QHBoxLayout(self.tab_efo_peak_detection)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.hsEFOPeakBefore = QSpacerItem(
            20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout_3.addItem(self.hsEFOPeakBefore)

        self.checkEFOLowerThreshold = QCheckBox(self.tab_efo_peak_detection)
        self.checkEFOLowerThreshold.setObjectName("checkEFOLowerThreshold")
        sizePolicy2 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(
            self.checkEFOLowerThreshold.sizePolicy().hasHeightForWidth()
        )
        self.checkEFOLowerThreshold.setSizePolicy(sizePolicy2)

        self.horizontalLayout_3.addWidget(self.checkEFOLowerThreshold)

        self.checkEFOUpperThreshold = QCheckBox(self.tab_efo_peak_detection)
        self.checkEFOUpperThreshold.setObjectName("checkEFOUpperThreshold")
        sizePolicy2.setHeightForWidth(
            self.checkEFOUpperThreshold.sizePolicy().hasHeightForWidth()
        )
        self.checkEFOUpperThreshold.setSizePolicy(sizePolicy2)

        self.horizontalLayout_3.addWidget(self.checkEFOUpperThreshold)

        self.lbEFOMedianFilterSupport = QLabel(self.tab_efo_peak_detection)
        self.lbEFOMedianFilterSupport.setObjectName("lbEFOMedianFilterSupport")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(
            self.lbEFOMedianFilterSupport.sizePolicy().hasHeightForWidth()
        )
        self.lbEFOMedianFilterSupport.setSizePolicy(sizePolicy3)

        self.horizontalLayout_3.addWidget(self.lbEFOMedianFilterSupport)

        self.leEFOMedianFilterSupport = QLineEdit(self.tab_efo_peak_detection)
        self.leEFOMedianFilterSupport.setObjectName("leEFOMedianFilterSupport")
        sizePolicy3.setHeightForWidth(
            self.leEFOMedianFilterSupport.sizePolicy().hasHeightForWidth()
        )
        self.leEFOMedianFilterSupport.setSizePolicy(sizePolicy3)

        self.horizontalLayout_3.addWidget(self.leEFOMedianFilterSupport)

        self.lbEFOMinRelativeProminence = QLabel(self.tab_efo_peak_detection)
        self.lbEFOMinRelativeProminence.setObjectName("lbEFOMinRelativeProminence")
        sizePolicy3.setHeightForWidth(
            self.lbEFOMinRelativeProminence.sizePolicy().hasHeightForWidth()
        )
        self.lbEFOMinRelativeProminence.setSizePolicy(sizePolicy3)

        self.horizontalLayout_3.addWidget(self.lbEFOMinRelativeProminence)

        self.leEFOMinRelativeProminence = QLineEdit(self.tab_efo_peak_detection)
        self.leEFOMinRelativeProminence.setObjectName("leEFOMinRelativeProminence")
        sizePolicy3.setHeightForWidth(
            self.leEFOMinRelativeProminence.sizePolicy().hasHeightForWidth()
        )
        self.leEFOMinRelativeProminence.setSizePolicy(sizePolicy3)

        self.horizontalLayout_3.addWidget(self.leEFOMinRelativeProminence)

        self.pbEFORunAutoPeakDetection = QPushButton(self.tab_efo_peak_detection)
        self.pbEFORunAutoPeakDetection.setObjectName("pbEFORunAutoPeakDetection")
        sizePolicy3.setHeightForWidth(
            self.pbEFORunAutoPeakDetection.sizePolicy().hasHeightForWidth()
        )
        self.pbEFORunAutoPeakDetection.setSizePolicy(sizePolicy3)

        self.horizontalLayout_3.addWidget(self.pbEFORunAutoPeakDetection)

        self.pbEFORunFilter = QPushButton(self.tab_efo_peak_detection)
        self.pbEFORunFilter.setObjectName("pbEFORunFilter")
        self.pbEFORunFilter.setEnabled(True)
        sizePolicy3.setHeightForWidth(
            self.pbEFORunFilter.sizePolicy().hasHeightForWidth()
        )
        self.pbEFORunFilter.setSizePolicy(sizePolicy3)

        self.horizontalLayout_3.addWidget(self.pbEFORunFilter)

        self.hshsEFOPeakAfter = QSpacerItem(
            20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout_3.addItem(self.hshsEFOPeakAfter)

        self.tabFilterOptions.addTab(self.tab_efo_peak_detection, "")
        self.tab_cfr_thresholding = QWidget()
        self.tab_cfr_thresholding.setObjectName("tab_cfr_thresholding")
        sizePolicy1.setHeightForWidth(
            self.tab_cfr_thresholding.sizePolicy().hasHeightForWidth()
        )
        self.tab_cfr_thresholding.setSizePolicy(sizePolicy1)
        self.horizontalLayout_4 = QHBoxLayout(self.tab_cfr_thresholding)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.hsCFRFilterBefore = QSpacerItem(
            20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout_4.addItem(self.hsCFRFilterBefore)

        self.checkCFRLowerThreshold = QCheckBox(self.tab_cfr_thresholding)
        self.checkCFRLowerThreshold.setObjectName("checkCFRLowerThreshold")
        sizePolicy2.setHeightForWidth(
            self.checkCFRLowerThreshold.sizePolicy().hasHeightForWidth()
        )
        self.checkCFRLowerThreshold.setSizePolicy(sizePolicy2)

        self.horizontalLayout_4.addWidget(self.checkCFRLowerThreshold)

        self.checkCFRUpperThreshold = QCheckBox(self.tab_cfr_thresholding)
        self.checkCFRUpperThreshold.setObjectName("checkCFRUpperThreshold")
        sizePolicy2.setHeightForWidth(
            self.checkCFRUpperThreshold.sizePolicy().hasHeightForWidth()
        )
        self.checkCFRUpperThreshold.setSizePolicy(sizePolicy2)

        self.horizontalLayout_4.addWidget(self.checkCFRUpperThreshold)

        self.lbCFRFilterThreshFactor = QLabel(self.tab_cfr_thresholding)
        self.lbCFRFilterThreshFactor.setObjectName("lbCFRFilterThreshFactor")
        sizePolicy3.setHeightForWidth(
            self.lbCFRFilterThreshFactor.sizePolicy().hasHeightForWidth()
        )
        self.lbCFRFilterThreshFactor.setSizePolicy(sizePolicy3)

        self.horizontalLayout_4.addWidget(self.lbCFRFilterThreshFactor)

        self.leCFRFilterThreshFactor = QLineEdit(self.tab_cfr_thresholding)
        self.leCFRFilterThreshFactor.setObjectName("leCFRFilterThreshFactor")
        sizePolicy3.setHeightForWidth(
            self.leCFRFilterThreshFactor.sizePolicy().hasHeightForWidth()
        )
        self.leCFRFilterThreshFactor.setSizePolicy(sizePolicy3)

        self.horizontalLayout_4.addWidget(self.leCFRFilterThreshFactor)

        self.pbCFRRunAutoThreshold = QPushButton(self.tab_cfr_thresholding)
        self.pbCFRRunAutoThreshold.setObjectName("pbCFRRunAutoThreshold")
        sizePolicy3.setHeightForWidth(
            self.pbCFRRunAutoThreshold.sizePolicy().hasHeightForWidth()
        )
        self.pbCFRRunAutoThreshold.setSizePolicy(sizePolicy3)

        self.horizontalLayout_4.addWidget(self.pbCFRRunAutoThreshold)

        self.pbCFRRunFilter = QPushButton(self.tab_cfr_thresholding)
        self.pbCFRRunFilter.setObjectName("pbCFRRunFilter")
        sizePolicy3.setHeightForWidth(
            self.pbCFRRunFilter.sizePolicy().hasHeightForWidth()
        )
        self.pbCFRRunFilter.setSizePolicy(sizePolicy3)

        self.horizontalLayout_4.addWidget(self.pbCFRRunFilter)

        self.hsCFRFilterAfter = QSpacerItem(
            20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout_4.addItem(self.hsCFRFilterAfter)

        self.tabFilterOptions.addTab(self.tab_cfr_thresholding, "")

        self.gridLayout.addWidget(self.tabFilterOptions, 0, 0, 1, 1)

        self.localizations_layout = QHBoxLayout()
        self.localizations_layout.setObjectName("localizations_layout")

        self.gridLayout.addLayout(self.localizations_layout, 3, 0, 1, 1)

        self.actions_layout = QHBoxLayout()
        self.actions_layout.setObjectName("actions_layout")
        self.pbReset = QPushButton(Analyzer)
        self.pbReset.setObjectName("pbReset")

        self.actions_layout.addWidget(self.pbReset)

        self.gridLayout.addLayout(self.actions_layout, 6, 0, 1, 1)

        self.parameters_layout = QHBoxLayout()
        self.parameters_layout.setObjectName("parameters_layout")

        self.gridLayout.addLayout(self.parameters_layout, 2, 0, 1, 1)

        self.communication_layout = QHBoxLayout()
        self.communication_layout.setObjectName("communication_layout")

        self.gridLayout.addLayout(self.communication_layout, 1, 0, 1, 1)

        self.retranslateUi(Analyzer)

        self.tabFilterOptions.setCurrentIndex(1)

        QMetaObject.connectSlotsByName(Analyzer)

    # setupUi

    def retranslateUi(self, Analyzer):
        Analyzer.setWindowTitle(
            QCoreApplication.translate("Analyzer", "Analyzer", None)
        )
        self.checkEFOLowerThreshold.setText(
            QCoreApplication.translate("Analyzer", "Lower bound", None)
        )
        self.checkEFOUpperThreshold.setText(
            QCoreApplication.translate("Analyzer", "Upper bound", None)
        )
        self.lbEFOMedianFilterSupport.setText(
            QCoreApplication.translate("Analyzer", "Median filter support", None)
        )
        self.leEFOMedianFilterSupport.setText("")
        self.lbEFOMinRelativeProminence.setText(
            QCoreApplication.translate("Analyzer", "Min peak relative prominence", None)
        )
        self.leEFOMinRelativeProminence.setText("")
        self.pbEFORunAutoPeakDetection.setText(
            QCoreApplication.translate("Analyzer", "Detect", None)
        )
        self.pbEFORunFilter.setText(
            QCoreApplication.translate("Analyzer", "Filter", None)
        )
        self.tabFilterOptions.setTabText(
            self.tabFilterOptions.indexOf(self.tab_efo_peak_detection),
            QCoreApplication.translate("Analyzer", "EFO peak detection", None),
        )
        self.checkCFRLowerThreshold.setText(
            QCoreApplication.translate("Analyzer", "Lower bound", None)
        )
        self.checkCFRUpperThreshold.setText(
            QCoreApplication.translate("Analyzer", "Upper bound", None)
        )
        self.lbCFRFilterThreshFactor.setText(
            QCoreApplication.translate("Analyzer", "Threshold factor", None)
        )
        self.pbCFRRunAutoThreshold.setText(
            QCoreApplication.translate("Analyzer", "Threshold", None)
        )
        self.pbCFRRunFilter.setText(
            QCoreApplication.translate("Analyzer", "Filter", None)
        )
        self.tabFilterOptions.setTabText(
            self.tabFilterOptions.indexOf(self.tab_cfr_thresholding),
            QCoreApplication.translate("Analyzer", "CFR thresholding", None),
        )
        self.pbReset.setText(QCoreApplication.translate("Analyzer", "Reset", None))

    # retranslateUi
