# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'importer.ui'
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
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QWidget,
)


class Ui_Importer(object):
    def setupUi(self, Importer):
        if not Importer.objectName():
            Importer.setObjectName("Importer")
        Importer.setWindowModality(Qt.NonModal)
        Importer.resize(417, 813)
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Importer.sizePolicy().hasHeightForWidth())
        Importer.setSizePolicy(sizePolicy)
        Importer.setMinimumSize(QSize(260, 0))
        Importer.setModal(True)
        self.gridLayout = QGridLayout(Importer)
        self.gridLayout.setObjectName("gridLayout")
        self.lbIter_13 = QLabel(Importer)
        self.lbIter_13.setObjectName("lbIter_13")
        self.lbIter_13.setEnabled(True)
        sizePolicy1 = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.lbIter_13.sizePolicy().hasHeightForWidth())
        self.lbIter_13.setSizePolicy(sizePolicy1)
        font = QFont()
        font.setBold(True)
        self.lbIter_13.setFont(font)
        self.lbIter_13.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbIter_13, 14, 1, 1, 1)

        self.lbReloc_0 = QLabel(Importer)
        self.lbReloc_0.setObjectName("lbReloc_0")
        sizePolicy1.setHeightForWidth(self.lbReloc_0.sizePolicy().hasHeightForWidth())
        self.lbReloc_0.setSizePolicy(sizePolicy1)
        self.lbReloc_0.setFont(font)
        self.lbReloc_0.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbReloc_0, 1, 2, 1, 1)

        self.lbReloc_15 = QLabel(Importer)
        self.lbReloc_15.setObjectName("lbReloc_15")
        sizePolicy1.setHeightForWidth(self.lbReloc_15.sizePolicy().hasHeightForWidth())
        self.lbReloc_15.setSizePolicy(sizePolicy1)
        self.lbReloc_15.setFont(font)
        self.lbReloc_15.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbReloc_15, 16, 2, 1, 1)

        self.pbIter_7 = QPushButton(Importer)
        self.pbIter_7.setObjectName("pbIter_7")
        self.pbIter_7.setEnabled(True)
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.pbIter_7.sizePolicy().hasHeightForWidth())
        self.pbIter_7.setSizePolicy(sizePolicy2)
        self.pbIter_7.setCheckable(False)

        self.gridLayout.addWidget(self.pbIter_7, 8, 0, 1, 1)

        self.lbIter_5 = QLabel(Importer)
        self.lbIter_5.setObjectName("lbIter_5")
        self.lbIter_5.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.lbIter_5.sizePolicy().hasHeightForWidth())
        self.lbIter_5.setSizePolicy(sizePolicy1)
        self.lbIter_5.setFont(font)
        self.lbIter_5.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbIter_5, 6, 1, 1, 1)

        self.cbTracking = QCheckBox(Importer)
        self.cbTracking.setObjectName("cbTracking")

        self.gridLayout.addWidget(self.cbTracking, 25, 0, 1, 1)

        self.lbIter_8 = QLabel(Importer)
        self.lbIter_8.setObjectName("lbIter_8")
        self.lbIter_8.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.lbIter_8.sizePolicy().hasHeightForWidth())
        self.lbIter_8.setSizePolicy(sizePolicy1)
        self.lbIter_8.setFont(font)
        self.lbIter_8.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbIter_8, 9, 1, 1, 1)

        self.lbReloc_6 = QLabel(Importer)
        self.lbReloc_6.setObjectName("lbReloc_6")
        sizePolicy1.setHeightForWidth(self.lbReloc_6.sizePolicy().hasHeightForWidth())
        self.lbReloc_6.setSizePolicy(sizePolicy1)
        self.lbReloc_6.setFont(font)
        self.lbReloc_6.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbReloc_6, 7, 2, 1, 1)

        self.lbCFRValues = QLabel(Importer)
        self.lbCFRValues.setObjectName("lbCFRValues")
        self.lbCFRValues.setFont(font)
        self.lbCFRValues.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbCFRValues, 0, 1, 1, 1)

        self.lbRelocInfo = QLabel(Importer)
        self.lbRelocInfo.setObjectName("lbRelocInfo")

        self.gridLayout.addWidget(self.lbRelocInfo, 21, 0, 1, 3)

        self.line = QFrame(Importer)
        self.line.setObjectName("line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.gridLayout.addWidget(self.line, 24, 0, 1, 3)

        self.pbIter_8 = QPushButton(Importer)
        self.pbIter_8.setObjectName("pbIter_8")
        self.pbIter_8.setEnabled(True)
        sizePolicy2.setHeightForWidth(self.pbIter_8.sizePolicy().hasHeightForWidth())
        self.pbIter_8.setSizePolicy(sizePolicy2)
        self.pbIter_8.setCheckable(False)

        self.gridLayout.addWidget(self.pbIter_8, 9, 0, 1, 1)

        self.lbReloc_3 = QLabel(Importer)
        self.lbReloc_3.setObjectName("lbReloc_3")
        sizePolicy1.setHeightForWidth(self.lbReloc_3.sizePolicy().hasHeightForWidth())
        self.lbReloc_3.setSizePolicy(sizePolicy1)
        self.lbReloc_3.setFont(font)
        self.lbReloc_3.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbReloc_3, 4, 2, 1, 1)

        self.lbIter_14 = QLabel(Importer)
        self.lbIter_14.setObjectName("lbIter_14")
        self.lbIter_14.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.lbIter_14.sizePolicy().hasHeightForWidth())
        self.lbIter_14.setSizePolicy(sizePolicy1)
        self.lbIter_14.setFont(font)
        self.lbIter_14.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbIter_14, 15, 1, 1, 1)

        self.lbIter_0 = QLabel(Importer)
        self.lbIter_0.setObjectName("lbIter_0")
        self.lbIter_0.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.lbIter_0.sizePolicy().hasHeightForWidth())
        self.lbIter_0.setSizePolicy(sizePolicy1)
        self.lbIter_0.setFont(font)
        self.lbIter_0.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbIter_0, 1, 1, 1, 1)

        self.lbIter_10 = QLabel(Importer)
        self.lbIter_10.setObjectName("lbIter_10")
        self.lbIter_10.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.lbIter_10.sizePolicy().hasHeightForWidth())
        self.lbIter_10.setSizePolicy(sizePolicy1)
        self.lbIter_10.setFont(font)
        self.lbIter_10.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbIter_10, 11, 1, 1, 1)

        self.pbIter_6 = QPushButton(Importer)
        self.pbIter_6.setObjectName("pbIter_6")
        self.pbIter_6.setEnabled(True)
        sizePolicy2.setHeightForWidth(self.pbIter_6.sizePolicy().hasHeightForWidth())
        self.pbIter_6.setSizePolicy(sizePolicy2)
        self.pbIter_6.setCheckable(False)

        self.gridLayout.addWidget(self.pbIter_6, 7, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(Importer)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        self.gridLayout.addWidget(self.buttonBox, 28, 0, 1, 3)

        self.verticalSpacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.gridLayout.addItem(self.verticalSpacer, 27, 0, 1, 1)

        self.line_2 = QFrame(Importer)
        self.line_2.setObjectName("line_2")
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.gridLayout.addWidget(self.line_2, 18, 0, 1, 3)

        self.lbIteration = QLabel(Importer)
        self.lbIteration.setObjectName("lbIteration")
        self.lbIteration.setFont(font)
        self.lbIteration.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbIteration, 0, 0, 1, 1)

        self.lbReloc_2 = QLabel(Importer)
        self.lbReloc_2.setObjectName("lbReloc_2")
        sizePolicy1.setHeightForWidth(self.lbReloc_2.sizePolicy().hasHeightForWidth())
        self.lbReloc_2.setSizePolicy(sizePolicy1)
        self.lbReloc_2.setFont(font)
        self.lbReloc_2.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbReloc_2, 3, 2, 1, 1)

        self.lbIter_3 = QLabel(Importer)
        self.lbIter_3.setObjectName("lbIter_3")
        self.lbIter_3.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.lbIter_3.sizePolicy().hasHeightForWidth())
        self.lbIter_3.setSizePolicy(sizePolicy1)
        self.lbIter_3.setFont(font)
        self.lbIter_3.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbIter_3, 4, 1, 1, 1)

        self.lbLastValidInfo = QLabel(Importer)
        self.lbLastValidInfo.setObjectName("lbLastValidInfo")

        self.gridLayout.addWidget(self.lbLastValidInfo, 20, 0, 1, 3)

        self.lbReloc_4 = QLabel(Importer)
        self.lbReloc_4.setObjectName("lbReloc_4")
        sizePolicy1.setHeightForWidth(self.lbReloc_4.sizePolicy().hasHeightForWidth())
        self.lbReloc_4.setSizePolicy(sizePolicy1)
        self.lbReloc_4.setFont(font)
        self.lbReloc_4.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbReloc_4, 5, 2, 1, 1)

        self.lbIter_12 = QLabel(Importer)
        self.lbIter_12.setObjectName("lbIter_12")
        self.lbIter_12.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.lbIter_12.sizePolicy().hasHeightForWidth())
        self.lbIter_12.setSizePolicy(sizePolicy1)
        self.lbIter_12.setFont(font)
        self.lbIter_12.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbIter_12, 13, 1, 1, 1)

        self.pbIter_0 = QPushButton(Importer)
        self.pbIter_0.setObjectName("pbIter_0")
        self.pbIter_0.setEnabled(True)
        sizePolicy2.setHeightForWidth(self.pbIter_0.sizePolicy().hasHeightForWidth())
        self.pbIter_0.setSizePolicy(sizePolicy2)
        self.pbIter_0.setCheckable(False)

        self.gridLayout.addWidget(self.pbIter_0, 1, 0, 1, 1)

        self.lbReloc_8 = QLabel(Importer)
        self.lbReloc_8.setObjectName("lbReloc_8")
        sizePolicy1.setHeightForWidth(self.lbReloc_8.sizePolicy().hasHeightForWidth())
        self.lbReloc_8.setSizePolicy(sizePolicy1)
        self.lbReloc_8.setFont(font)
        self.lbReloc_8.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbReloc_8, 9, 2, 1, 1)

        self.pbIter_14 = QPushButton(Importer)
        self.pbIter_14.setObjectName("pbIter_14")
        self.pbIter_14.setEnabled(True)
        sizePolicy2.setHeightForWidth(self.pbIter_14.sizePolicy().hasHeightForWidth())
        self.pbIter_14.setSizePolicy(sizePolicy2)
        self.pbIter_14.setCheckable(False)

        self.gridLayout.addWidget(self.pbIter_14, 15, 0, 1, 1)

        self.pbIter_2 = QPushButton(Importer)
        self.pbIter_2.setObjectName("pbIter_2")
        self.pbIter_2.setEnabled(True)
        sizePolicy2.setHeightForWidth(self.pbIter_2.sizePolicy().hasHeightForWidth())
        self.pbIter_2.setSizePolicy(sizePolicy2)
        self.pbIter_2.setCheckable(False)

        self.gridLayout.addWidget(self.pbIter_2, 3, 0, 1, 1)

        self.lbReloc_14 = QLabel(Importer)
        self.lbReloc_14.setObjectName("lbReloc_14")
        sizePolicy1.setHeightForWidth(self.lbReloc_14.sizePolicy().hasHeightForWidth())
        self.lbReloc_14.setSizePolicy(sizePolicy1)
        self.lbReloc_14.setFont(font)
        self.lbReloc_14.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbReloc_14, 15, 2, 1, 1)

        self.pbIter_13 = QPushButton(Importer)
        self.pbIter_13.setObjectName("pbIter_13")
        self.pbIter_13.setEnabled(True)
        sizePolicy2.setHeightForWidth(self.pbIter_13.sizePolicy().hasHeightForWidth())
        self.pbIter_13.setSizePolicy(sizePolicy2)
        self.pbIter_13.setCheckable(False)

        self.gridLayout.addWidget(self.pbIter_13, 14, 0, 1, 1)

        self.lbReloc_1 = QLabel(Importer)
        self.lbReloc_1.setObjectName("lbReloc_1")
        sizePolicy1.setHeightForWidth(self.lbReloc_1.sizePolicy().hasHeightForWidth())
        self.lbReloc_1.setSizePolicy(sizePolicy1)
        self.lbReloc_1.setFont(font)
        self.lbReloc_1.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbReloc_1, 2, 2, 1, 1)

        self.lbReloc_9 = QLabel(Importer)
        self.lbReloc_9.setObjectName("lbReloc_9")
        sizePolicy1.setHeightForWidth(self.lbReloc_9.sizePolicy().hasHeightForWidth())
        self.lbReloc_9.setSizePolicy(sizePolicy1)
        self.lbReloc_9.setFont(font)
        self.lbReloc_9.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbReloc_9, 10, 2, 1, 1)

        self.pbIter_11 = QPushButton(Importer)
        self.pbIter_11.setObjectName("pbIter_11")
        self.pbIter_11.setEnabled(True)
        sizePolicy2.setHeightForWidth(self.pbIter_11.sizePolicy().hasHeightForWidth())
        self.pbIter_11.setSizePolicy(sizePolicy2)
        self.pbIter_11.setCheckable(False)

        self.gridLayout.addWidget(self.pbIter_11, 12, 0, 1, 1)

        self.lbIter_15 = QLabel(Importer)
        self.lbIter_15.setObjectName("lbIter_15")
        self.lbIter_15.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.lbIter_15.sizePolicy().hasHeightForWidth())
        self.lbIter_15.setSizePolicy(sizePolicy1)
        self.lbIter_15.setFont(font)
        self.lbIter_15.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbIter_15, 16, 1, 1, 1)

        self.pbIter_10 = QPushButton(Importer)
        self.pbIter_10.setObjectName("pbIter_10")
        self.pbIter_10.setEnabled(True)
        sizePolicy2.setHeightForWidth(self.pbIter_10.sizePolicy().hasHeightForWidth())
        self.pbIter_10.setSizePolicy(sizePolicy2)
        self.pbIter_10.setCheckable(False)

        self.gridLayout.addWidget(self.pbIter_10, 11, 0, 1, 1)

        self.lbIter_11 = QLabel(Importer)
        self.lbIter_11.setObjectName("lbIter_11")
        self.lbIter_11.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.lbIter_11.sizePolicy().hasHeightForWidth())
        self.lbIter_11.setSizePolicy(sizePolicy1)
        self.lbIter_11.setFont(font)
        self.lbIter_11.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbIter_11, 12, 1, 1, 1)

        self.leDwellTime = QLineEdit(Importer)
        self.leDwellTime.setObjectName("leDwellTime")
        sizePolicy2.setHeightForWidth(self.leDwellTime.sizePolicy().hasHeightForWidth())
        self.leDwellTime.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.leDwellTime, 26, 1, 1, 2)

        self.pbIter_3 = QPushButton(Importer)
        self.pbIter_3.setObjectName("pbIter_3")
        self.pbIter_3.setEnabled(True)
        sizePolicy2.setHeightForWidth(self.pbIter_3.sizePolicy().hasHeightForWidth())
        self.pbIter_3.setSizePolicy(sizePolicy2)
        self.pbIter_3.setCheckable(False)

        self.gridLayout.addWidget(self.pbIter_3, 4, 0, 1, 1)

        self.lbIter_4 = QLabel(Importer)
        self.lbIter_4.setObjectName("lbIter_4")
        self.lbIter_4.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.lbIter_4.sizePolicy().hasHeightForWidth())
        self.lbIter_4.setSizePolicy(sizePolicy1)
        self.lbIter_4.setFont(font)
        self.lbIter_4.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbIter_4, 5, 1, 1, 1)

        self.pbIter_4 = QPushButton(Importer)
        self.pbIter_4.setObjectName("pbIter_4")
        self.pbIter_4.setEnabled(True)
        sizePolicy2.setHeightForWidth(self.pbIter_4.sizePolicy().hasHeightForWidth())
        self.pbIter_4.setSizePolicy(sizePolicy2)
        self.pbIter_4.setCheckable(False)

        self.gridLayout.addWidget(self.pbIter_4, 5, 0, 1, 1)

        self.lbReloc = QLabel(Importer)
        self.lbReloc.setObjectName("lbReloc")
        self.lbReloc.setFont(font)
        self.lbReloc.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbReloc, 0, 2, 1, 1)

        self.pbIter_12 = QPushButton(Importer)
        self.pbIter_12.setObjectName("pbIter_12")
        self.pbIter_12.setEnabled(True)
        sizePolicy2.setHeightForWidth(self.pbIter_12.sizePolicy().hasHeightForWidth())
        self.pbIter_12.setSizePolicy(sizePolicy2)
        self.pbIter_12.setCheckable(False)

        self.gridLayout.addWidget(self.pbIter_12, 13, 0, 1, 1)

        self.lbIter_6 = QLabel(Importer)
        self.lbIter_6.setObjectName("lbIter_6")
        self.lbIter_6.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.lbIter_6.sizePolicy().hasHeightForWidth())
        self.lbIter_6.setSizePolicy(sizePolicy1)
        self.lbIter_6.setFont(font)
        self.lbIter_6.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbIter_6, 7, 1, 1, 1)

        self.pbIter_5 = QPushButton(Importer)
        self.pbIter_5.setObjectName("pbIter_5")
        self.pbIter_5.setEnabled(True)
        sizePolicy2.setHeightForWidth(self.pbIter_5.sizePolicy().hasHeightForWidth())
        self.pbIter_5.setSizePolicy(sizePolicy2)
        self.pbIter_5.setCheckable(False)

        self.gridLayout.addWidget(self.pbIter_5, 6, 0, 1, 1)

        self.pbIter_15 = QPushButton(Importer)
        self.pbIter_15.setObjectName("pbIter_15")
        self.pbIter_15.setEnabled(True)
        sizePolicy2.setHeightForWidth(self.pbIter_15.sizePolicy().hasHeightForWidth())
        self.pbIter_15.setSizePolicy(sizePolicy2)
        self.pbIter_15.setCheckable(False)

        self.gridLayout.addWidget(self.pbIter_15, 16, 0, 1, 1)

        self.lbIter_1 = QLabel(Importer)
        self.lbIter_1.setObjectName("lbIter_1")
        self.lbIter_1.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.lbIter_1.sizePolicy().hasHeightForWidth())
        self.lbIter_1.setSizePolicy(sizePolicy1)
        self.lbIter_1.setFont(font)
        self.lbIter_1.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbIter_1, 2, 1, 1, 1)

        self.pb_last_valid = QPushButton(Importer)
        self.pb_last_valid.setObjectName("pb_last_valid")
        self.pb_last_valid.setCheckable(False)

        self.gridLayout.addWidget(self.pb_last_valid, 19, 0, 1, 3)

        self.lbIter_9 = QLabel(Importer)
        self.lbIter_9.setObjectName("lbIter_9")
        self.lbIter_9.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.lbIter_9.sizePolicy().hasHeightForWidth())
        self.lbIter_9.setSizePolicy(sizePolicy1)
        self.lbIter_9.setFont(font)
        self.lbIter_9.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbIter_9, 10, 1, 1, 1)

        self.pbIter_1 = QPushButton(Importer)
        self.pbIter_1.setObjectName("pbIter_1")
        self.pbIter_1.setEnabled(True)
        sizePolicy2.setHeightForWidth(self.pbIter_1.sizePolicy().hasHeightForWidth())
        self.pbIter_1.setSizePolicy(sizePolicy2)
        self.pbIter_1.setCheckable(False)

        self.gridLayout.addWidget(self.pbIter_1, 2, 0, 1, 1)

        self.lbReloc_13 = QLabel(Importer)
        self.lbReloc_13.setObjectName("lbReloc_13")
        sizePolicy1.setHeightForWidth(self.lbReloc_13.sizePolicy().hasHeightForWidth())
        self.lbReloc_13.setSizePolicy(sizePolicy1)
        self.lbReloc_13.setFont(font)
        self.lbReloc_13.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbReloc_13, 14, 2, 1, 1)

        self.pbIter_9 = QPushButton(Importer)
        self.pbIter_9.setObjectName("pbIter_9")
        self.pbIter_9.setEnabled(True)
        sizePolicy2.setHeightForWidth(self.pbIter_9.sizePolicy().hasHeightForWidth())
        self.pbIter_9.setSizePolicy(sizePolicy2)
        self.pbIter_9.setCheckable(False)

        self.gridLayout.addWidget(self.pbIter_9, 10, 0, 1, 1)

        self.lbDwellTime = QLabel(Importer)
        self.lbDwellTime.setObjectName("lbDwellTime")
        sizePolicy3 = QSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed
        )
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.lbDwellTime.sizePolicy().hasHeightForWidth())
        self.lbDwellTime.setSizePolicy(sizePolicy3)

        self.gridLayout.addWidget(self.lbDwellTime, 26, 0, 1, 1)

        self.lbReloc_12 = QLabel(Importer)
        self.lbReloc_12.setObjectName("lbReloc_12")
        sizePolicy1.setHeightForWidth(self.lbReloc_12.sizePolicy().hasHeightForWidth())
        self.lbReloc_12.setSizePolicy(sizePolicy1)
        self.lbReloc_12.setFont(font)
        self.lbReloc_12.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbReloc_12, 13, 2, 1, 1)

        self.lbIter_7 = QLabel(Importer)
        self.lbIter_7.setObjectName("lbIter_7")
        self.lbIter_7.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.lbIter_7.sizePolicy().hasHeightForWidth())
        self.lbIter_7.setSizePolicy(sizePolicy1)
        self.lbIter_7.setFont(font)
        self.lbIter_7.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbIter_7, 8, 1, 1, 1)

        self.lbReloc_5 = QLabel(Importer)
        self.lbReloc_5.setObjectName("lbReloc_5")
        sizePolicy1.setHeightForWidth(self.lbReloc_5.sizePolicy().hasHeightForWidth())
        self.lbReloc_5.setSizePolicy(sizePolicy1)
        self.lbReloc_5.setFont(font)
        self.lbReloc_5.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbReloc_5, 6, 2, 1, 1)

        self.lbReloc_11 = QLabel(Importer)
        self.lbReloc_11.setObjectName("lbReloc_11")
        sizePolicy1.setHeightForWidth(self.lbReloc_11.sizePolicy().hasHeightForWidth())
        self.lbReloc_11.setSizePolicy(sizePolicy1)
        self.lbReloc_11.setFont(font)
        self.lbReloc_11.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbReloc_11, 12, 2, 1, 1)

        self.lbReloc_7 = QLabel(Importer)
        self.lbReloc_7.setObjectName("lbReloc_7")
        sizePolicy1.setHeightForWidth(self.lbReloc_7.sizePolicy().hasHeightForWidth())
        self.lbReloc_7.setSizePolicy(sizePolicy1)
        self.lbReloc_7.setFont(font)
        self.lbReloc_7.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbReloc_7, 8, 2, 1, 1)

        self.lbIter_2 = QLabel(Importer)
        self.lbIter_2.setObjectName("lbIter_2")
        self.lbIter_2.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.lbIter_2.sizePolicy().hasHeightForWidth())
        self.lbIter_2.setSizePolicy(sizePolicy1)
        self.lbIter_2.setFont(font)
        self.lbIter_2.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbIter_2, 3, 1, 1, 1)

        self.fixedVerticalSpacer = QSpacerItem(
            20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )

        self.gridLayout.addItem(self.fixedVerticalSpacer, 22, 0, 1, 1)

        self.lbReloc_10 = QLabel(Importer)
        self.lbReloc_10.setObjectName("lbReloc_10")
        sizePolicy1.setHeightForWidth(self.lbReloc_10.sizePolicy().hasHeightForWidth())
        self.lbReloc_10.setSizePolicy(sizePolicy1)
        self.lbReloc_10.setFont(font)
        self.lbReloc_10.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbReloc_10, 11, 2, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(
            20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.gridLayout.addItem(self.verticalSpacer_2, 17, 0, 1, 1)

        self.retranslateUi(Importer)
        self.buttonBox.accepted.connect(Importer.accept)
        self.buttonBox.rejected.connect(Importer.reject)

        QMetaObject.connectSlotsByName(Importer)

    # setupUi

    def retranslateUi(self, Importer):
        Importer.setWindowTitle(
            QCoreApplication.translate("Importer", "Importer", None)
        )
        self.lbIter_13.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.lbReloc_0.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.lbReloc_15.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.pbIter_7.setText(
            QCoreApplication.translate("Importer", "Iteration 7", None)
        )
        self.lbIter_5.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.cbTracking.setText(
            QCoreApplication.translate("Importer", "Tracking dataset", None)
        )
        self.lbIter_8.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.lbReloc_6.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.lbCFRValues.setText(
            QCoreApplication.translate("Importer", "CFR values", None)
        )
        self.lbRelocInfo.setText(
            QCoreApplication.translate(
                "Importer",
                "Non-relocalized iterations contain one valid measurement per trace.",
                None,
            )
        )
        self.pbIter_8.setText(
            QCoreApplication.translate("Importer", "Iteration 8", None)
        )
        self.lbReloc_3.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.lbIter_14.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.lbIter_0.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.lbIter_10.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.pbIter_6.setText(
            QCoreApplication.translate("Importer", "Iteration 6", None)
        )
        self.lbIteration.setText(
            QCoreApplication.translate("Importer", "Iteration number", None)
        )
        self.lbReloc_2.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.lbIter_3.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.lbLastValidInfo.setText(
            QCoreApplication.translate(
                "Importer", 'Only "last valid" iteration can be saved.', None
            )
        )
        self.lbReloc_4.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.lbIter_12.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.pbIter_0.setText(
            QCoreApplication.translate("Importer", "Iteration 0", None)
        )
        self.lbReloc_8.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.pbIter_14.setText(
            QCoreApplication.translate("Importer", "Iteration 14", None)
        )
        self.pbIter_2.setText(
            QCoreApplication.translate("Importer", "Iteration 2", None)
        )
        self.lbReloc_14.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.pbIter_13.setText(
            QCoreApplication.translate("Importer", "Iteration 13", None)
        )
        self.lbReloc_1.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.lbReloc_9.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.pbIter_11.setText(
            QCoreApplication.translate("Importer", "Iteration 11", None)
        )
        self.lbIter_15.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.pbIter_10.setText(
            QCoreApplication.translate("Importer", "Iteration 10", None)
        )
        self.lbIter_11.setText(QCoreApplication.translate("Importer", "\u2713", None))
        self.pbIter_3.setText(
            QCoreApplication.translate("Importer", "Iteration 3", None)
        )
        self.lbIter_4.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.pbIter_4.setText(
            QCoreApplication.translate("Importer", "Iteration 4", None)
        )
        self.lbReloc.setText(
            QCoreApplication.translate("Importer", "Relocalized", None)
        )
        self.pbIter_12.setText(
            QCoreApplication.translate("Importer", "Iteration 12", None)
        )
        self.lbIter_6.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.pbIter_5.setText(
            QCoreApplication.translate("Importer", "Iteration 5", None)
        )
        self.pbIter_15.setText(
            QCoreApplication.translate("Importer", "Iteration 15", None)
        )
        self.lbIter_1.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.pb_last_valid.setText(
            QCoreApplication.translate("Importer", "Pick last valid iteration", None)
        )
        self.lbIter_9.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.pbIter_1.setText(
            QCoreApplication.translate("Importer", "Iteration 1", None)
        )
        self.lbReloc_13.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.pbIter_9.setText(
            QCoreApplication.translate("Importer", "Iteration 9", None)
        )
        self.lbDwellTime.setText(
            QCoreApplication.translate("Importer", "Dwell time (ms)", None)
        )
        self.lbReloc_12.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.lbIter_7.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.lbReloc_5.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.lbReloc_11.setText(QCoreApplication.translate("Importer", "\u2713", None))
        self.lbReloc_7.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.lbIter_2.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.lbReloc_10.setText(QCoreApplication.translate("Importer", "\u2a2f", None))

    # retranslateUi
