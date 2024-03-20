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
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLayout,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class Ui_Importer(object):
    def setupUi(self, Importer):
        if not Importer.objectName():
            Importer.setObjectName("Importer")
        Importer.setWindowModality(Qt.NonModal)
        Importer.resize(260, 764)
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
        self.mainLayout = QVBoxLayout()
        self.mainLayout.setObjectName("mainLayout")
        self.titleLayout = QHBoxLayout()
        self.titleLayout.setObjectName("titleLayout")
        self.lbIteration = QLabel(Importer)
        self.lbIteration.setObjectName("lbIteration")
        font = QFont()
        font.setBold(True)
        self.lbIteration.setFont(font)
        self.lbIteration.setAlignment(Qt.AlignCenter)

        self.titleLayout.addWidget(self.lbIteration)

        self.lbCFRStatus = QLabel(Importer)
        self.lbCFRStatus.setObjectName("lbCFRStatus")
        self.lbCFRStatus.setFont(font)
        self.lbCFRStatus.setAlignment(Qt.AlignCenter)

        self.titleLayout.addWidget(self.lbCFRStatus)

        self.mainLayout.addLayout(self.titleLayout)

        self.iteration_0_layout = QHBoxLayout()
        self.iteration_0_layout.setObjectName("iteration_0_layout")
        self.pbIter_0 = QPushButton(Importer)
        self.pbIter_0.setObjectName("pbIter_0")
        self.pbIter_0.setEnabled(True)
        self.pbIter_0.setCheckable(False)

        self.iteration_0_layout.addWidget(self.pbIter_0)

        self.lbIter_0 = QLabel(Importer)
        self.lbIter_0.setObjectName("lbIter_0")
        self.lbIter_0.setEnabled(True)
        self.lbIter_0.setAlignment(Qt.AlignCenter)

        self.iteration_0_layout.addWidget(self.lbIter_0)

        self.mainLayout.addLayout(self.iteration_0_layout)

        self.iteration_1_layout = QHBoxLayout()
        self.iteration_1_layout.setObjectName("iteration_1_layout")
        self.pbIter_1 = QPushButton(Importer)
        self.pbIter_1.setObjectName("pbIter_1")
        self.pbIter_1.setEnabled(True)
        self.pbIter_1.setCheckable(False)

        self.iteration_1_layout.addWidget(self.pbIter_1)

        self.lbIter_1 = QLabel(Importer)
        self.lbIter_1.setObjectName("lbIter_1")
        self.lbIter_1.setEnabled(True)
        self.lbIter_1.setFont(font)
        self.lbIter_1.setAlignment(Qt.AlignCenter)

        self.iteration_1_layout.addWidget(self.lbIter_1)

        self.mainLayout.addLayout(self.iteration_1_layout)

        self.iteration_2_layout = QHBoxLayout()
        self.iteration_2_layout.setObjectName("iteration_2_layout")
        self.pbIter_2 = QPushButton(Importer)
        self.pbIter_2.setObjectName("pbIter_2")
        self.pbIter_2.setEnabled(True)
        self.pbIter_2.setCheckable(False)

        self.iteration_2_layout.addWidget(self.pbIter_2)

        self.lbIter_2 = QLabel(Importer)
        self.lbIter_2.setObjectName("lbIter_2")
        self.lbIter_2.setEnabled(True)
        self.lbIter_2.setFont(font)
        self.lbIter_2.setAlignment(Qt.AlignCenter)

        self.iteration_2_layout.addWidget(self.lbIter_2)

        self.mainLayout.addLayout(self.iteration_2_layout)

        self.iteration_3_layout = QHBoxLayout()
        self.iteration_3_layout.setObjectName("iteration_3_layout")
        self.pbIter_3 = QPushButton(Importer)
        self.pbIter_3.setObjectName("pbIter_3")
        self.pbIter_3.setEnabled(True)
        self.pbIter_3.setCheckable(False)

        self.iteration_3_layout.addWidget(self.pbIter_3)

        self.lbIter_3 = QLabel(Importer)
        self.lbIter_3.setObjectName("lbIter_3")
        self.lbIter_3.setEnabled(True)
        self.lbIter_3.setFont(font)
        self.lbIter_3.setAlignment(Qt.AlignCenter)

        self.iteration_3_layout.addWidget(self.lbIter_3)

        self.mainLayout.addLayout(self.iteration_3_layout)

        self.iteration_4_layout = QHBoxLayout()
        self.iteration_4_layout.setObjectName("iteration_4_layout")
        self.pbIter_4 = QPushButton(Importer)
        self.pbIter_4.setObjectName("pbIter_4")
        self.pbIter_4.setEnabled(True)
        self.pbIter_4.setCheckable(False)

        self.iteration_4_layout.addWidget(self.pbIter_4)

        self.lbIter_4 = QLabel(Importer)
        self.lbIter_4.setObjectName("lbIter_4")
        self.lbIter_4.setEnabled(True)
        self.lbIter_4.setFont(font)
        self.lbIter_4.setAlignment(Qt.AlignCenter)

        self.iteration_4_layout.addWidget(self.lbIter_4)

        self.mainLayout.addLayout(self.iteration_4_layout)

        self.iteration_5_layout = QHBoxLayout()
        self.iteration_5_layout.setObjectName("iteration_5_layout")
        self.pbIter_5 = QPushButton(Importer)
        self.pbIter_5.setObjectName("pbIter_5")
        self.pbIter_5.setEnabled(True)
        self.pbIter_5.setCheckable(False)

        self.iteration_5_layout.addWidget(self.pbIter_5)

        self.lbIter_5 = QLabel(Importer)
        self.lbIter_5.setObjectName("lbIter_5")
        self.lbIter_5.setEnabled(True)
        self.lbIter_5.setFont(font)
        self.lbIter_5.setAlignment(Qt.AlignCenter)

        self.iteration_5_layout.addWidget(self.lbIter_5)

        self.mainLayout.addLayout(self.iteration_5_layout)

        self.iteration_6_layout = QHBoxLayout()
        self.iteration_6_layout.setObjectName("iteration_6_layout")
        self.pbIter_6 = QPushButton(Importer)
        self.pbIter_6.setObjectName("pbIter_6")
        self.pbIter_6.setEnabled(True)
        self.pbIter_6.setCheckable(False)

        self.iteration_6_layout.addWidget(self.pbIter_6)

        self.lbIter_6 = QLabel(Importer)
        self.lbIter_6.setObjectName("lbIter_6")
        self.lbIter_6.setEnabled(True)
        self.lbIter_6.setFont(font)
        self.lbIter_6.setAlignment(Qt.AlignCenter)

        self.iteration_6_layout.addWidget(self.lbIter_6)

        self.mainLayout.addLayout(self.iteration_6_layout)

        self.iteration_7_layout = QHBoxLayout()
        self.iteration_7_layout.setObjectName("iteration_7_layout")
        self.pbIter_7 = QPushButton(Importer)
        self.pbIter_7.setObjectName("pbIter_7")
        self.pbIter_7.setEnabled(True)
        self.pbIter_7.setCheckable(False)

        self.iteration_7_layout.addWidget(self.pbIter_7)

        self.lbIter_7 = QLabel(Importer)
        self.lbIter_7.setObjectName("lbIter_7")
        self.lbIter_7.setEnabled(True)
        self.lbIter_7.setFont(font)
        self.lbIter_7.setAlignment(Qt.AlignCenter)

        self.iteration_7_layout.addWidget(self.lbIter_7)

        self.mainLayout.addLayout(self.iteration_7_layout)

        self.itaeration_9_layout = QHBoxLayout()
        self.itaeration_9_layout.setObjectName("itaeration_9_layout")
        self.pbIter_8 = QPushButton(Importer)
        self.pbIter_8.setObjectName("pbIter_8")
        self.pbIter_8.setEnabled(True)
        self.pbIter_8.setCheckable(False)

        self.itaeration_9_layout.addWidget(self.pbIter_8)

        self.lbIter_8 = QLabel(Importer)
        self.lbIter_8.setObjectName("lbIter_8")
        self.lbIter_8.setEnabled(True)
        self.lbIter_8.setFont(font)
        self.lbIter_8.setAlignment(Qt.AlignCenter)

        self.itaeration_9_layout.addWidget(self.lbIter_8)

        self.mainLayout.addLayout(self.itaeration_9_layout)

        self.iteration_9_layout = QHBoxLayout()
        self.iteration_9_layout.setObjectName("iteration_9_layout")
        self.pbIter_9 = QPushButton(Importer)
        self.pbIter_9.setObjectName("pbIter_9")
        self.pbIter_9.setEnabled(True)
        self.pbIter_9.setCheckable(False)

        self.iteration_9_layout.addWidget(self.pbIter_9)

        self.lbIter_9 = QLabel(Importer)
        self.lbIter_9.setObjectName("lbIter_9")
        self.lbIter_9.setEnabled(True)
        self.lbIter_9.setFont(font)
        self.lbIter_9.setAlignment(Qt.AlignCenter)

        self.iteration_9_layout.addWidget(self.lbIter_9)

        self.mainLayout.addLayout(self.iteration_9_layout)

        self.iteration_10_layout = QHBoxLayout()
        self.iteration_10_layout.setObjectName("iteration_10_layout")
        self.pbIter_10 = QPushButton(Importer)
        self.pbIter_10.setObjectName("pbIter_10")
        self.pbIter_10.setEnabled(True)
        self.pbIter_10.setCheckable(False)

        self.iteration_10_layout.addWidget(self.pbIter_10)

        self.lbIter_10 = QLabel(Importer)
        self.lbIter_10.setObjectName("lbIter_10")
        self.lbIter_10.setEnabled(True)
        self.lbIter_10.setFont(font)
        self.lbIter_10.setAlignment(Qt.AlignCenter)

        self.iteration_10_layout.addWidget(self.lbIter_10)

        self.mainLayout.addLayout(self.iteration_10_layout)

        self.iteration_11_layout = QHBoxLayout()
        self.iteration_11_layout.setObjectName("iteration_11_layout")
        self.pbIter_11 = QPushButton(Importer)
        self.pbIter_11.setObjectName("pbIter_11")
        self.pbIter_11.setEnabled(True)
        self.pbIter_11.setCheckable(False)

        self.iteration_11_layout.addWidget(self.pbIter_11)

        self.lbIter_11 = QLabel(Importer)
        self.lbIter_11.setObjectName("lbIter_11")
        self.lbIter_11.setEnabled(True)
        self.lbIter_11.setFont(font)
        self.lbIter_11.setAlignment(Qt.AlignCenter)

        self.iteration_11_layout.addWidget(self.lbIter_11)

        self.mainLayout.addLayout(self.iteration_11_layout)

        self.iteration_12_layout = QHBoxLayout()
        self.iteration_12_layout.setObjectName("iteration_12_layout")
        self.pbIter_12 = QPushButton(Importer)
        self.pbIter_12.setObjectName("pbIter_12")
        self.pbIter_12.setEnabled(True)
        self.pbIter_12.setCheckable(False)

        self.iteration_12_layout.addWidget(self.pbIter_12)

        self.lbIter_12 = QLabel(Importer)
        self.lbIter_12.setObjectName("lbIter_12")
        self.lbIter_12.setEnabled(True)
        self.lbIter_12.setFont(font)
        self.lbIter_12.setAlignment(Qt.AlignCenter)

        self.iteration_12_layout.addWidget(self.lbIter_12)

        self.mainLayout.addLayout(self.iteration_12_layout)

        self.iteration_13_layout = QHBoxLayout()
        self.iteration_13_layout.setObjectName("iteration_13_layout")
        self.pbIter_13 = QPushButton(Importer)
        self.pbIter_13.setObjectName("pbIter_13")
        self.pbIter_13.setEnabled(True)
        self.pbIter_13.setCheckable(False)

        self.iteration_13_layout.addWidget(self.pbIter_13)

        self.lbIter_13 = QLabel(Importer)
        self.lbIter_13.setObjectName("lbIter_13")
        self.lbIter_13.setEnabled(True)
        self.lbIter_13.setFont(font)
        self.lbIter_13.setAlignment(Qt.AlignCenter)

        self.iteration_13_layout.addWidget(self.lbIter_13)

        self.mainLayout.addLayout(self.iteration_13_layout)

        self.iteration_14_layout = QHBoxLayout()
        self.iteration_14_layout.setObjectName("iteration_14_layout")
        self.pbIter_14 = QPushButton(Importer)
        self.pbIter_14.setObjectName("pbIter_14")
        self.pbIter_14.setEnabled(True)
        self.pbIter_14.setCheckable(False)

        self.iteration_14_layout.addWidget(self.pbIter_14)

        self.lbIter_14 = QLabel(Importer)
        self.lbIter_14.setObjectName("lbIter_14")
        self.lbIter_14.setEnabled(True)
        self.lbIter_14.setFont(font)
        self.lbIter_14.setAlignment(Qt.AlignCenter)

        self.iteration_14_layout.addWidget(self.lbIter_14)

        self.mainLayout.addLayout(self.iteration_14_layout)

        self.iteration_15_layout = QHBoxLayout()
        self.iteration_15_layout.setObjectName("iteration_15_layout")
        self.pbIter_15 = QPushButton(Importer)
        self.pbIter_15.setObjectName("pbIter_15")
        self.pbIter_15.setEnabled(True)
        self.pbIter_15.setCheckable(False)

        self.iteration_15_layout.addWidget(self.pbIter_15)

        self.lbIter_15 = QLabel(Importer)
        self.lbIter_15.setObjectName("lbIter_15")
        self.lbIter_15.setEnabled(True)
        self.lbIter_15.setFont(font)
        self.lbIter_15.setAlignment(Qt.AlignCenter)

        self.iteration_15_layout.addWidget(self.lbIter_15)

        self.mainLayout.addLayout(self.iteration_15_layout)

        self.last_valid_layout = QHBoxLayout()
        self.last_valid_layout.setObjectName("last_valid_layout")
        self.pb_last_valid = QPushButton(Importer)
        self.pb_last_valid.setObjectName("pb_last_valid")
        self.pb_last_valid.setCheckable(False)

        self.last_valid_layout.addWidget(self.pb_last_valid)

        self.pl_last_valid = QLabel(Importer)
        self.pl_last_valid.setObjectName("pl_last_valid")
        self.pl_last_valid.setFont(font)
        self.pl_last_valid.setAlignment(Qt.AlignCenter)

        self.last_valid_layout.addWidget(self.pl_last_valid)

        self.mainLayout.addLayout(self.last_valid_layout)

        self.lbInfo = QLabel(Importer)
        self.lbInfo.setObjectName("lbInfo")

        self.mainLayout.addWidget(self.lbInfo)

        self.fixedVerticalSpacer = QSpacerItem(
            20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )

        self.mainLayout.addItem(self.fixedVerticalSpacer)

        self.cbTracking = QCheckBox(Importer)
        self.cbTracking.setObjectName("cbTracking")

        self.mainLayout.addWidget(self.cbTracking)

        self.dwellLayout = QHBoxLayout()
        self.dwellLayout.setObjectName("dwellLayout")
        self.dwellLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.lbDwellTime = QLabel(Importer)
        self.lbDwellTime.setObjectName("lbDwellTime")
        sizePolicy1 = QSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed
        )
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.lbDwellTime.sizePolicy().hasHeightForWidth())
        self.lbDwellTime.setSizePolicy(sizePolicy1)

        self.dwellLayout.addWidget(self.lbDwellTime)

        self.leDwellTime = QLineEdit(Importer)
        self.leDwellTime.setObjectName("leDwellTime")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.leDwellTime.sizePolicy().hasHeightForWidth())
        self.leDwellTime.setSizePolicy(sizePolicy2)

        self.dwellLayout.addWidget(self.leDwellTime)

        self.mainLayout.addLayout(self.dwellLayout)

        self.gridLayout.addLayout(self.mainLayout, 0, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(Importer)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(Importer)
        self.buttonBox.accepted.connect(Importer.accept)
        self.buttonBox.rejected.connect(Importer.reject)

        QMetaObject.connectSlotsByName(Importer)

    # setupUi

    def retranslateUi(self, Importer):
        Importer.setWindowTitle(
            QCoreApplication.translate("Importer", "Importer", None)
        )
        self.lbIteration.setText(
            QCoreApplication.translate("Importer", "Iteration number", None)
        )
        self.lbCFRStatus.setText(
            QCoreApplication.translate("Importer", "CFR status", None)
        )
        self.pbIter_0.setText(
            QCoreApplication.translate("Importer", "Iteration 0", None)
        )
        self.lbIter_0.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.pbIter_1.setText(
            QCoreApplication.translate("Importer", "Iteration 1", None)
        )
        self.lbIter_1.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.pbIter_2.setText(
            QCoreApplication.translate("Importer", "Iteration 2", None)
        )
        self.lbIter_2.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.pbIter_3.setText(
            QCoreApplication.translate("Importer", "Iteration 3", None)
        )
        self.lbIter_3.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.pbIter_4.setText(
            QCoreApplication.translate("Importer", "Iteration 4", None)
        )
        self.lbIter_4.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.pbIter_5.setText(
            QCoreApplication.translate("Importer", "Iteration 5", None)
        )
        self.lbIter_5.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.pbIter_6.setText(
            QCoreApplication.translate("Importer", "Iteration 6", None)
        )
        self.lbIter_6.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.pbIter_7.setText(
            QCoreApplication.translate("Importer", "Iteration 7", None)
        )
        self.lbIter_7.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.pbIter_8.setText(
            QCoreApplication.translate("Importer", "Iteration 8", None)
        )
        self.lbIter_8.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.pbIter_9.setText(
            QCoreApplication.translate("Importer", "Iteration 9", None)
        )
        self.lbIter_9.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.pbIter_10.setText(
            QCoreApplication.translate("Importer", "Iteration 10", None)
        )
        self.lbIter_10.setText(QCoreApplication.translate("Importer", "\u2a2f", None))
        self.pbIter_11.setText(
            QCoreApplication.translate("Importer", "Iteration 11", None)
        )
        self.lbIter_11.setText(QCoreApplication.translate("Importer", "\u2713", None))
        self.pbIter_12.setText(
            QCoreApplication.translate("Importer", "Iteration 12", None)
        )
        self.lbIter_12.setText(QCoreApplication.translate("Importer", "\u2713", None))
        self.pbIter_13.setText(
            QCoreApplication.translate("Importer", "Iteration 13", None)
        )
        self.lbIter_13.setText(QCoreApplication.translate("Importer", "\u2713", None))
        self.pbIter_14.setText(
            QCoreApplication.translate("Importer", "Iteration 14", None)
        )
        self.lbIter_14.setText(QCoreApplication.translate("Importer", "\u2713", None))
        self.pbIter_15.setText(
            QCoreApplication.translate("Importer", "Iteration 15", None)
        )
        self.lbIter_15.setText(QCoreApplication.translate("Importer", "\u2713", None))
        self.pb_last_valid.setText(
            QCoreApplication.translate("Importer", "Last valid", None)
        )
        self.pl_last_valid.setText("")
        self.lbInfo.setText(
            QCoreApplication.translate(
                "Importer", 'Only "last valid" iteration can be saved.', None
            )
        )
        self.cbTracking.setText(
            QCoreApplication.translate("Importer", "Tracking dataset", None)
        )
        self.lbDwellTime.setText(
            QCoreApplication.translate("Importer", "Dwell time (ms)", None)
        )

    # retranslateUi
