# -*- coding: utf-8 -*-

#  Copyright (c) 2022 - 2023 D-BSSE, ETH Zurich.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#   limitations under the License.
#

################################################################################
## Form generated from reading UI file 'color_unmixer.ui'
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
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class Ui_ColorUnmixer(object):
    def setupUi(self, ColorUnmixer):
        if not ColorUnmixer.objectName():
            ColorUnmixer.setObjectName("ColorUnmixer")
        ColorUnmixer.resize(800, 600)
        self.verticalLayout_2 = QVBoxLayout(ColorUnmixer)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.main_layout = QVBoxLayout()
        self.main_layout.setObjectName("main_layout")
        self.commands_layout = QHBoxLayout()
        self.commands_layout.setObjectName("commands_layout")
        self.twUnmixingOptions = QTabWidget(ColorUnmixer)
        self.twUnmixingOptions.setObjectName("twUnmixingOptions")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.twUnmixingOptions.sizePolicy().hasHeightForWidth()
        )
        self.twUnmixingOptions.setSizePolicy(sizePolicy)
        self.tab = QWidget()
        self.tab.setObjectName("tab")
        self.horizontalLayout = QHBoxLayout(self.tab)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.lbNumFluorophores = QLabel(self.tab)
        self.lbNumFluorophores.setObjectName("lbNumFluorophores")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(
            self.lbNumFluorophores.sizePolicy().hasHeightForWidth()
        )
        self.lbNumFluorophores.setSizePolicy(sizePolicy1)
        self.lbNumFluorophores.setAlignment(Qt.AlignCenter)

        self.horizontalLayout.addWidget(self.lbNumFluorophores)

        self.cbNumFluorophores = QComboBox(self.tab)
        self.cbNumFluorophores.addItem("")
        self.cbNumFluorophores.addItem("")
        self.cbNumFluorophores.setObjectName("cbNumFluorophores")
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(
            self.cbNumFluorophores.sizePolicy().hasHeightForWidth()
        )
        self.cbNumFluorophores.setSizePolicy(sizePolicy2)

        self.horizontalLayout.addWidget(self.cbNumFluorophores)

        self.pbDetect = QPushButton(self.tab)
        self.pbDetect.setObjectName("pbDetect")
        sizePolicy2.setHeightForWidth(self.pbDetect.sizePolicy().hasHeightForWidth())
        self.pbDetect.setSizePolicy(sizePolicy2)

        self.horizontalLayout.addWidget(self.pbDetect)

        self.pbAssign = QPushButton(self.tab)
        self.pbAssign.setObjectName("pbAssign")
        sizePolicy2.setHeightForWidth(self.pbAssign.sizePolicy().hasHeightForWidth())
        self.pbAssign.setSizePolicy(sizePolicy2)

        self.horizontalLayout.addWidget(self.pbAssign)

        self.horizontalSpacer_2 = QSpacerItem(
            61, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.twUnmixingOptions.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName("tab_2")
        self.horizontalLayout_3 = QHBoxLayout(self.tab_2)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalSpacer_4 = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout_2.addItem(self.horizontalSpacer_4)

        self.lbManualThreshold = QLabel(self.tab_2)
        self.lbManualThreshold.setObjectName("lbManualThreshold")

        self.horizontalLayout_2.addWidget(self.lbManualThreshold)

        self.leManualThreshold = QLineEdit(self.tab_2)
        self.leManualThreshold.setObjectName("leManualThreshold")
        sizePolicy2.setHeightForWidth(
            self.leManualThreshold.sizePolicy().hasHeightForWidth()
        )
        self.leManualThreshold.setSizePolicy(sizePolicy2)

        self.horizontalLayout_2.addWidget(self.leManualThreshold)

        self.pbPreview = QPushButton(self.tab_2)
        self.pbPreview.setObjectName("pbPreview")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.pbPreview.sizePolicy().hasHeightForWidth())
        self.pbPreview.setSizePolicy(sizePolicy3)

        self.horizontalLayout_2.addWidget(self.pbPreview)

        self.pbManualAssign = QPushButton(self.tab_2)
        self.pbManualAssign.setObjectName("pbManualAssign")

        self.horizontalLayout_2.addWidget(self.pbManualAssign)

        self.horizontalSpacer_3 = QSpacerItem(
            61, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout_2.addItem(self.horizontalSpacer_3)

        self.horizontalLayout_3.addLayout(self.horizontalLayout_2)

        self.twUnmixingOptions.addTab(self.tab_2, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName("tab_3")
        self.horizontalLayout_4 = QHBoxLayout(self.tab_3)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.horizontalSpacer_5 = QSpacerItem(
            241, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout_4.addItem(self.horizontalSpacer_5)

        self.lbBinSize = QLabel(self.tab_3)
        self.lbBinSize.setObjectName("lbBinSize")
        sizePolicy1.setHeightForWidth(self.lbBinSize.sizePolicy().hasHeightForWidth())
        self.lbBinSize.setSizePolicy(sizePolicy1)

        self.horizontalLayout_4.addWidget(self.lbBinSize)

        self.leBinSize = QLineEdit(self.tab_3)
        self.leBinSize.setObjectName("leBinSize")
        sizePolicy2.setHeightForWidth(self.leBinSize.sizePolicy().hasHeightForWidth())
        self.leBinSize.setSizePolicy(sizePolicy2)

        self.horizontalLayout_4.addWidget(self.leBinSize)

        self.horizontalSpacer_6 = QSpacerItem(
            240, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout_4.addItem(self.horizontalSpacer_6)

        self.twUnmixingOptions.addTab(self.tab_3, "")

        self.commands_layout.addWidget(self.twUnmixingOptions)

        self.main_layout.addLayout(self.commands_layout)

        self.verticalLayout_2.addLayout(self.main_layout)

        self.retranslateUi(ColorUnmixer)

        self.twUnmixingOptions.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(ColorUnmixer)

    # setupUi

    def retranslateUi(self, ColorUnmixer):
        ColorUnmixer.setWindowTitle(
            QCoreApplication.translate("ColorUnmixer", "Color Unmixer", None)
        )
        self.lbNumFluorophores.setText(
            QCoreApplication.translate("ColorUnmixer", "Number of fluorophores", None)
        )
        self.cbNumFluorophores.setItemText(
            0, QCoreApplication.translate("ColorUnmixer", "1", None)
        )
        self.cbNumFluorophores.setItemText(
            1, QCoreApplication.translate("ColorUnmixer", "2", None)
        )

        self.pbDetect.setText(
            QCoreApplication.translate("ColorUnmixer", "Detect", None)
        )
        self.pbAssign.setText(
            QCoreApplication.translate("ColorUnmixer", "Assign", None)
        )
        self.twUnmixingOptions.setTabText(
            self.twUnmixingOptions.indexOf(self.tab),
            QCoreApplication.translate("ColorUnmixer", "Automatic", None),
        )
        self.lbManualThreshold.setText(
            QCoreApplication.translate("ColorUnmixer", "DCR threshold", None)
        )
        self.pbPreview.setText(
            QCoreApplication.translate("ColorUnmixer", "Preview", None)
        )
        self.pbManualAssign.setText(
            QCoreApplication.translate("ColorUnmixer", "Assign", None)
        )
        self.twUnmixingOptions.setTabText(
            self.twUnmixingOptions.indexOf(self.tab_2),
            QCoreApplication.translate("ColorUnmixer", "Manual", None),
        )
        self.lbBinSize.setText(
            QCoreApplication.translate(
                "ColorUnmixer", "Bin size (set to 0 for auto)", None
            )
        )
        self.twUnmixingOptions.setTabText(
            self.twUnmixingOptions.indexOf(self.tab_3),
            QCoreApplication.translate("ColorUnmixer", "Histogram settings", None),
        )

    # retranslateUi
