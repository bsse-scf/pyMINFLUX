# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'color_unmixer.ui'
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
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
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
        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.commands_layout.addItem(self.horizontalSpacer)

        self.lbNumFluorophores = QLabel(ColorUnmixer)
        self.lbNumFluorophores.setObjectName("lbNumFluorophores")
        self.lbNumFluorophores.setAlignment(Qt.AlignCenter)

        self.commands_layout.addWidget(self.lbNumFluorophores)

        self.leNumFluorophores = QLineEdit(ColorUnmixer)
        self.leNumFluorophores.setObjectName("leNumFluorophores")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.leNumFluorophores.sizePolicy().hasHeightForWidth()
        )
        self.leNumFluorophores.setSizePolicy(sizePolicy)

        self.commands_layout.addWidget(self.leNumFluorophores)

        self.lbBinSize = QLabel(ColorUnmixer)
        self.lbBinSize.setObjectName("lbBinSize")

        self.commands_layout.addWidget(self.lbBinSize)

        self.leBinSize = QLineEdit(ColorUnmixer)
        self.leBinSize.setObjectName("leBinSize")

        self.commands_layout.addWidget(self.leBinSize)

        self.pbDetect = QPushButton(ColorUnmixer)
        self.pbDetect.setObjectName("pbDetect")
        sizePolicy.setHeightForWidth(self.pbDetect.sizePolicy().hasHeightForWidth())
        self.pbDetect.setSizePolicy(sizePolicy)

        self.commands_layout.addWidget(self.pbDetect)

        self.pbAssign = QPushButton(ColorUnmixer)
        self.pbAssign.setObjectName("pbAssign")

        self.commands_layout.addWidget(self.pbAssign)

        self.horizontalSpacer_2 = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.commands_layout.addItem(self.horizontalSpacer_2)

        self.main_layout.addLayout(self.commands_layout)

        self.verticalLayout_2.addLayout(self.main_layout)

        self.retranslateUi(ColorUnmixer)

        QMetaObject.connectSlotsByName(ColorUnmixer)

    # setupUi

    def retranslateUi(self, ColorUnmixer):
        ColorUnmixer.setWindowTitle(
            QCoreApplication.translate("ColorUnmixer", "Color Unmixer", None)
        )
        self.lbNumFluorophores.setText(
            QCoreApplication.translate("ColorUnmixer", "Number of fluorophores", None)
        )
        self.lbBinSize.setText(
            QCoreApplication.translate(
                "ColorUnmixer", "Bin size (set to 0 for auto)", None
            )
        )
        self.pbDetect.setText(
            QCoreApplication.translate("ColorUnmixer", "Detect", None)
        )
        self.pbAssign.setText(
            QCoreApplication.translate("ColorUnmixer", "Assign", None)
        )

    # retranslateUi
