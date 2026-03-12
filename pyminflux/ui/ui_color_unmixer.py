# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'color_unmixer.ui'
##
## Created by: Qt User Interface Compiler version 6.7.3
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QSpinBox, QTabWidget, QVBoxLayout,
    QWidget)

class Ui_ColorUnmixer(object):
    def setupUi(self, ColorUnmixer):
        if not ColorUnmixer.objectName():
            ColorUnmixer.setObjectName(u"ColorUnmixer")
        ColorUnmixer.resize(800, 600)
        self.verticalLayout_2 = QVBoxLayout(ColorUnmixer)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.main_layout = QVBoxLayout()
        self.main_layout.setObjectName(u"main_layout")
        self.commands_layout = QHBoxLayout()
        self.commands_layout.setObjectName(u"commands_layout")
        self.twMainTabs = QTabWidget(ColorUnmixer)
        self.twMainTabs.setObjectName(u"twMainTabs")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.twMainTabs.sizePolicy().hasHeightForWidth())
        self.twMainTabs.setSizePolicy(sizePolicy)
        self.tabDcrUnmixing = QWidget()
        self.tabDcrUnmixing.setObjectName(u"tabDcrUnmixing")
        self.verticalLayout_3 = QVBoxLayout(self.tabDcrUnmixing)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.twUnmixingOptions = QTabWidget(self.tabDcrUnmixing)
        self.twUnmixingOptions.setObjectName(u"twUnmixingOptions")
        sizePolicy.setHeightForWidth(self.twUnmixingOptions.sizePolicy().hasHeightForWidth())
        self.twUnmixingOptions.setSizePolicy(sizePolicy)
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.horizontalLayout = QHBoxLayout(self.tab)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.lbNumFluorophores = QLabel(self.tab)
        self.lbNumFluorophores.setObjectName(u"lbNumFluorophores")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.lbNumFluorophores.sizePolicy().hasHeightForWidth())
        self.lbNumFluorophores.setSizePolicy(sizePolicy1)
        self.lbNumFluorophores.setAlignment(Qt.AlignCenter)

        self.horizontalLayout.addWidget(self.lbNumFluorophores)

        self.cbNumFluorophores = QComboBox(self.tab)
        self.cbNumFluorophores.addItem("")
        self.cbNumFluorophores.addItem("")
        self.cbNumFluorophores.setObjectName(u"cbNumFluorophores")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.cbNumFluorophores.sizePolicy().hasHeightForWidth())
        self.cbNumFluorophores.setSizePolicy(sizePolicy2)

        self.horizontalLayout.addWidget(self.cbNumFluorophores)

        self.pbDetect = QPushButton(self.tab)
        self.pbDetect.setObjectName(u"pbDetect")
        sizePolicy2.setHeightForWidth(self.pbDetect.sizePolicy().hasHeightForWidth())
        self.pbDetect.setSizePolicy(sizePolicy2)

        self.horizontalLayout.addWidget(self.pbDetect)

        self.pbAssign = QPushButton(self.tab)
        self.pbAssign.setObjectName(u"pbAssign")
        sizePolicy2.setHeightForWidth(self.pbAssign.sizePolicy().hasHeightForWidth())
        self.pbAssign.setSizePolicy(sizePolicy2)

        self.horizontalLayout.addWidget(self.pbAssign)

        self.horizontalSpacer_2 = QSpacerItem(61, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.twUnmixingOptions.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.horizontalLayout_3 = QHBoxLayout(self.tab_2)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_4)

        self.lbManualThreshold = QLabel(self.tab_2)
        self.lbManualThreshold.setObjectName(u"lbManualThreshold")

        self.horizontalLayout_2.addWidget(self.lbManualThreshold)

        self.leManualThreshold = QLineEdit(self.tab_2)
        self.leManualThreshold.setObjectName(u"leManualThreshold")
        sizePolicy2.setHeightForWidth(self.leManualThreshold.sizePolicy().hasHeightForWidth())
        self.leManualThreshold.setSizePolicy(sizePolicy2)

        self.horizontalLayout_2.addWidget(self.leManualThreshold)

        self.pbPreview = QPushButton(self.tab_2)
        self.pbPreview.setObjectName(u"pbPreview")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.pbPreview.sizePolicy().hasHeightForWidth())
        self.pbPreview.setSizePolicy(sizePolicy3)

        self.horizontalLayout_2.addWidget(self.pbPreview)

        self.pbManualAssign = QPushButton(self.tab_2)
        self.pbManualAssign.setObjectName(u"pbManualAssign")

        self.horizontalLayout_2.addWidget(self.pbManualAssign)

        self.horizontalSpacer_3 = QSpacerItem(61, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_3)


        self.horizontalLayout_3.addLayout(self.horizontalLayout_2)

        self.twUnmixingOptions.addTab(self.tab_2, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.horizontalLayout_4 = QHBoxLayout(self.tab_3)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer_5 = QSpacerItem(241, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_5)

        self.lbBinSize = QLabel(self.tab_3)
        self.lbBinSize.setObjectName(u"lbBinSize")
        sizePolicy1.setHeightForWidth(self.lbBinSize.sizePolicy().hasHeightForWidth())
        self.lbBinSize.setSizePolicy(sizePolicy1)

        self.horizontalLayout_4.addWidget(self.lbBinSize)

        self.leBinSize = QLineEdit(self.tab_3)
        self.leBinSize.setObjectName(u"leBinSize")
        sizePolicy2.setHeightForWidth(self.leBinSize.sizePolicy().hasHeightForWidth())
        self.leBinSize.setSizePolicy(sizePolicy2)

        self.horizontalLayout_4.addWidget(self.leBinSize)

        self.horizontalSpacer_6 = QSpacerItem(240, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_6)

        self.twUnmixingOptions.addTab(self.tab_3, "")

        self.verticalLayout_3.addWidget(self.twUnmixingOptions)

        self.twMainTabs.addTab(self.tabDcrUnmixing, "")
        self.tabTimeSplitting = QWidget()
        self.tabTimeSplitting.setObjectName(u"tabTimeSplitting")
        self.verticalLayout_4 = QVBoxLayout(self.tabTimeSplitting)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_7)

        self.lbNumSplits = QLabel(self.tabTimeSplitting)
        self.lbNumSplits.setObjectName(u"lbNumSplits")
        sizePolicy1.setHeightForWidth(self.lbNumSplits.sizePolicy().hasHeightForWidth())
        self.lbNumSplits.setSizePolicy(sizePolicy1)
        self.lbNumSplits.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_5.addWidget(self.lbNumSplits)

        self.sbNumSplits = QSpinBox(self.tabTimeSplitting)
        self.sbNumSplits.setObjectName(u"sbNumSplits")
        sizePolicy2.setHeightForWidth(self.sbNumSplits.sizePolicy().hasHeightForWidth())
        self.sbNumSplits.setSizePolicy(sizePolicy2)
        self.sbNumSplits.setMinimum(2)
        self.sbNumSplits.setMaximum(10)
        self.sbNumSplits.setValue(2)

        self.horizontalLayout_5.addWidget(self.sbNumSplits)

        self.pbSplit = QPushButton(self.tabTimeSplitting)
        self.pbSplit.setObjectName(u"pbSplit")
        sizePolicy2.setHeightForWidth(self.pbSplit.sizePolicy().hasHeightForWidth())
        self.pbSplit.setSizePolicy(sizePolicy2)

        self.horizontalLayout_5.addWidget(self.pbSplit)

        self.pbTimeSplitAssign = QPushButton(self.tabTimeSplitting)
        self.pbTimeSplitAssign.setObjectName(u"pbTimeSplitAssign")
        sizePolicy2.setHeightForWidth(self.pbTimeSplitAssign.sizePolicy().hasHeightForWidth())
        self.pbTimeSplitAssign.setSizePolicy(sizePolicy2)

        self.horizontalLayout_5.addWidget(self.pbTimeSplitAssign)

        self.horizontalSpacer_8 = QSpacerItem(61, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_8)


        self.verticalLayout_4.addLayout(self.horizontalLayout_5)

        self.twMainTabs.addTab(self.tabTimeSplitting, "")

        self.commands_layout.addWidget(self.twMainTabs)


        self.main_layout.addLayout(self.commands_layout)


        self.verticalLayout_2.addLayout(self.main_layout)


        self.retranslateUi(ColorUnmixer)

        self.twMainTabs.setCurrentIndex(0)
        self.twUnmixingOptions.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(ColorUnmixer)
    # setupUi

    def retranslateUi(self, ColorUnmixer):
        ColorUnmixer.setWindowTitle(QCoreApplication.translate("ColorUnmixer", u"Unmixer", None))
        self.lbNumFluorophores.setText(QCoreApplication.translate("ColorUnmixer", u"Number of channels", None))
        self.cbNumFluorophores.setItemText(0, QCoreApplication.translate("ColorUnmixer", u"1", None))
        self.cbNumFluorophores.setItemText(1, QCoreApplication.translate("ColorUnmixer", u"2", None))

        self.pbDetect.setText(QCoreApplication.translate("ColorUnmixer", u"Detect", None))
        self.pbAssign.setText(QCoreApplication.translate("ColorUnmixer", u"Assign", None))
        self.twUnmixingOptions.setTabText(self.twUnmixingOptions.indexOf(self.tab), QCoreApplication.translate("ColorUnmixer", u"Automatic", None))
        self.lbManualThreshold.setText(QCoreApplication.translate("ColorUnmixer", u"DCR threshold", None))
        self.pbPreview.setText(QCoreApplication.translate("ColorUnmixer", u"Preview", None))
        self.pbManualAssign.setText(QCoreApplication.translate("ColorUnmixer", u"Assign", None))
        self.twUnmixingOptions.setTabText(self.twUnmixingOptions.indexOf(self.tab_2), QCoreApplication.translate("ColorUnmixer", u"Manual", None))
        self.lbBinSize.setText(QCoreApplication.translate("ColorUnmixer", u"Bin size (set to 0 for auto)", None))
        self.twUnmixingOptions.setTabText(self.twUnmixingOptions.indexOf(self.tab_3), QCoreApplication.translate("ColorUnmixer", u"Histogram settings", None))
        self.twMainTabs.setTabText(self.twMainTabs.indexOf(self.tabDcrUnmixing), QCoreApplication.translate("ColorUnmixer", u"DCR unmixing", None))
        self.lbNumSplits.setText(QCoreApplication.translate("ColorUnmixer", u"Number of splits", None))
        self.pbSplit.setText(QCoreApplication.translate("ColorUnmixer", u"Show", None))
        self.pbTimeSplitAssign.setText(QCoreApplication.translate("ColorUnmixer", u"Assign", None))
        self.twMainTabs.setTabText(self.twMainTabs.indexOf(self.tabTimeSplitting), QCoreApplication.translate("ColorUnmixer", u"Time splitting", None))
    # retranslateUi

