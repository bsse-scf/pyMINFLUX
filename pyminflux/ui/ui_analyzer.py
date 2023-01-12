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

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.pbReset = QPushButton(Analyzer)
        self.pbReset.setObjectName(u"pbReset")

        self.horizontalLayout_2.addWidget(self.pbReset)


        self.gridLayout.addLayout(self.horizontalLayout_2, 6, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_5)

        self.lbCFRBoundsDetector = QLabel(Analyzer)
        self.lbCFRBoundsDetector.setObjectName(u"lbCFRBoundsDetector")
        font = QFont()
        font.setBold(True)
        self.lbCFRBoundsDetector.setFont(font)
        self.lbCFRBoundsDetector.setTextFormat(Qt.AutoText)

        self.horizontalLayout_3.addWidget(self.lbCFRBoundsDetector)

        self.checkCFRLowerThreshold = QCheckBox(Analyzer)
        self.checkCFRLowerThreshold.setObjectName(u"checkCFRLowerThreshold")

        self.horizontalLayout_3.addWidget(self.checkCFRLowerThreshold)

        self.checkCFRUpperThreshold = QCheckBox(Analyzer)
        self.checkCFRUpperThreshold.setObjectName(u"checkCFRUpperThreshold")

        self.horizontalLayout_3.addWidget(self.checkCFRUpperThreshold)

        self.lbCFRFilterThreshFactor = QLabel(Analyzer)
        self.lbCFRFilterThreshFactor.setObjectName(u"lbCFRFilterThreshFactor")

        self.horizontalLayout_3.addWidget(self.lbCFRFilterThreshFactor)

        self.leCFRFilterThreshFactor = QLineEdit(Analyzer)
        self.leCFRFilterThreshFactor.setObjectName(u"leCFRFilterThreshFactor")

        self.horizontalLayout_3.addWidget(self.leCFRFilterThreshFactor)

        self.pbCFRRunAutoThreshold = QPushButton(Analyzer)
        self.pbCFRRunAutoThreshold.setObjectName(u"pbCFRRunAutoThreshold")

        self.horizontalLayout_3.addWidget(self.pbCFRRunAutoThreshold)

        self.pbCFRRunFilter = QPushButton(Analyzer)
        self.pbCFRRunFilter.setObjectName(u"pbCFRRunFilter")

        self.horizontalLayout_3.addWidget(self.pbCFRRunFilter)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_6)


        self.gridLayout.addLayout(self.horizontalLayout_3, 1, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.lbEFOPeakDetection = QLabel(Analyzer)
        self.lbEFOPeakDetection.setObjectName(u"lbEFOPeakDetection")
        self.lbEFOPeakDetection.setFont(font)
        self.lbEFOPeakDetection.setTextFormat(Qt.AutoText)

        self.horizontalLayout.addWidget(self.lbEFOPeakDetection)

        self.checkEFOLowerThreshold = QCheckBox(Analyzer)
        self.checkEFOLowerThreshold.setObjectName(u"checkEFOLowerThreshold")

        self.horizontalLayout.addWidget(self.checkEFOLowerThreshold)

        self.checkEFOUpperThreshold = QCheckBox(Analyzer)
        self.checkEFOUpperThreshold.setObjectName(u"checkEFOUpperThreshold")

        self.horizontalLayout.addWidget(self.checkEFOUpperThreshold)

        self.lbEFOMedianFilterSupport = QLabel(Analyzer)
        self.lbEFOMedianFilterSupport.setObjectName(u"lbEFOMedianFilterSupport")

        self.horizontalLayout.addWidget(self.lbEFOMedianFilterSupport)

        self.leEFOMedianFilterSupport = QLineEdit(Analyzer)
        self.leEFOMedianFilterSupport.setObjectName(u"leEFOMedianFilterSupport")
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.leEFOMedianFilterSupport.sizePolicy().hasHeightForWidth())
        self.leEFOMedianFilterSupport.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.leEFOMedianFilterSupport)

        self.lbEFOMinRelativeProminence = QLabel(Analyzer)
        self.lbEFOMinRelativeProminence.setObjectName(u"lbEFOMinRelativeProminence")

        self.horizontalLayout.addWidget(self.lbEFOMinRelativeProminence)

        self.leEFOMinRelativeProminence = QLineEdit(Analyzer)
        self.leEFOMinRelativeProminence.setObjectName(u"leEFOMinRelativeProminence")

        self.horizontalLayout.addWidget(self.leEFOMinRelativeProminence)

        self.pbEFORunAutoPeakDetection = QPushButton(Analyzer)
        self.pbEFORunAutoPeakDetection.setObjectName(u"pbEFORunAutoPeakDetection")

        self.horizontalLayout.addWidget(self.pbEFORunAutoPeakDetection)

        self.pbEFORunFilter = QPushButton(Analyzer)
        self.pbEFORunFilter.setObjectName(u"pbEFORunFilter")
        self.pbEFORunFilter.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.pbEFORunFilter.sizePolicy().hasHeightForWidth())
        self.pbEFORunFilter.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.pbEFORunFilter)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.parameters_layout = QHBoxLayout()
        self.parameters_layout.setObjectName(u"parameters_layout")

        self.gridLayout.addLayout(self.parameters_layout, 2, 0, 1, 1)


        self.retranslateUi(Analyzer)

        QMetaObject.connectSlotsByName(Analyzer)
    # setupUi

    def retranslateUi(self, Analyzer):
        Analyzer.setWindowTitle(QCoreApplication.translate("Analyzer", u"Analyzer", None))
        self.pbReset.setText(QCoreApplication.translate("Analyzer", u"Reset", None))
        self.lbCFRBoundsDetector.setText(QCoreApplication.translate("Analyzer", u"CFR thresholding:", None))
        self.checkCFRLowerThreshold.setText(QCoreApplication.translate("Analyzer", u"Lower bound", None))
        self.checkCFRUpperThreshold.setText(QCoreApplication.translate("Analyzer", u"Upper bound", None))
        self.lbCFRFilterThreshFactor.setText(QCoreApplication.translate("Analyzer", u"Threshold factor", None))
        self.pbCFRRunAutoThreshold.setText(QCoreApplication.translate("Analyzer", u"Threshold", None))
        self.pbCFRRunFilter.setText(QCoreApplication.translate("Analyzer", u"Filter", None))
        self.lbEFOPeakDetection.setText(QCoreApplication.translate("Analyzer", u"EFO peak detection:", None))
        self.checkEFOLowerThreshold.setText(QCoreApplication.translate("Analyzer", u"Lower bound", None))
        self.checkEFOUpperThreshold.setText(QCoreApplication.translate("Analyzer", u"Upper bound", None))
        self.lbEFOMedianFilterSupport.setText(QCoreApplication.translate("Analyzer", u"Median filter support", None))
        self.leEFOMedianFilterSupport.setText("")
        self.lbEFOMinRelativeProminence.setText(QCoreApplication.translate("Analyzer", u"Min peak relative prominence", None))
        self.leEFOMinRelativeProminence.setText("")
        self.pbEFORunAutoPeakDetection.setText(QCoreApplication.translate("Analyzer", u"Detect", None))
        self.pbEFORunFilter.setText(QCoreApplication.translate("Analyzer", u"Filter", None))
    # retranslateUi

