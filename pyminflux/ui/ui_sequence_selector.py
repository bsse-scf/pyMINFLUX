# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'sequence_selector.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QDialog,
    QDialogButtonBox, QGridLayout, QHBoxLayout, QLabel,
    QLayout, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_SequenceSelector(object):
    def setupUi(self, SequenceSelector):
        if not SequenceSelector.objectName():
            SequenceSelector.setObjectName(u"SequenceSelector")
        SequenceSelector.setWindowModality(Qt.NonModal)
        SequenceSelector.resize(260, 604)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SequenceSelector.sizePolicy().hasHeightForWidth())
        SequenceSelector.setSizePolicy(sizePolicy)
        SequenceSelector.setMinimumSize(QSize(260, 0))
        SequenceSelector.setModal(True)
        self.gridLayout = QGridLayout(SequenceSelector)
        self.gridLayout.setObjectName(u"gridLayout")
        self.mainLayout = QVBoxLayout()
        self.mainLayout.setObjectName(u"mainLayout")
        self.titleLayout = QHBoxLayout()
        self.titleLayout.setObjectName(u"titleLayout")
        self.lbIteration = QLabel(SequenceSelector)
        self.lbIteration.setObjectName(u"lbIteration")
        font = QFont()
        font.setBold(True)
        self.lbIteration.setFont(font)
        self.lbIteration.setAlignment(Qt.AlignCenter)

        self.titleLayout.addWidget(self.lbIteration)

        self.lbCFRStatus = QLabel(SequenceSelector)
        self.lbCFRStatus.setObjectName(u"lbCFRStatus")
        self.lbCFRStatus.setFont(font)
        self.lbCFRStatus.setAlignment(Qt.AlignCenter)

        self.titleLayout.addWidget(self.lbCFRStatus)


        self.mainLayout.addLayout(self.titleLayout)

        self.iteration_0_layout = QHBoxLayout()
        self.iteration_0_layout.setObjectName(u"iteration_0_layout")
        self.pbIter_0 = QPushButton(SequenceSelector)
        self.pbIter_0.setObjectName(u"pbIter_0")
        self.pbIter_0.setEnabled(True)
        self.pbIter_0.setCheckable(False)

        self.iteration_0_layout.addWidget(self.pbIter_0)

        self.lbIter_0 = QLabel(SequenceSelector)
        self.lbIter_0.setObjectName(u"lbIter_0")
        self.lbIter_0.setEnabled(True)
        self.lbIter_0.setAlignment(Qt.AlignCenter)

        self.iteration_0_layout.addWidget(self.lbIter_0)


        self.mainLayout.addLayout(self.iteration_0_layout)

        self.iteration_1_layout = QHBoxLayout()
        self.iteration_1_layout.setObjectName(u"iteration_1_layout")
        self.pbIter_1 = QPushButton(SequenceSelector)
        self.pbIter_1.setObjectName(u"pbIter_1")
        self.pbIter_1.setEnabled(True)
        self.pbIter_1.setCheckable(False)

        self.iteration_1_layout.addWidget(self.pbIter_1)

        self.lbIter_1 = QLabel(SequenceSelector)
        self.lbIter_1.setObjectName(u"lbIter_1")
        self.lbIter_1.setEnabled(True)
        self.lbIter_1.setFont(font)
        self.lbIter_1.setAlignment(Qt.AlignCenter)

        self.iteration_1_layout.addWidget(self.lbIter_1)


        self.mainLayout.addLayout(self.iteration_1_layout)

        self.iteration_2_layout = QHBoxLayout()
        self.iteration_2_layout.setObjectName(u"iteration_2_layout")
        self.pbIter_2 = QPushButton(SequenceSelector)
        self.pbIter_2.setObjectName(u"pbIter_2")
        self.pbIter_2.setEnabled(True)
        self.pbIter_2.setCheckable(False)

        self.iteration_2_layout.addWidget(self.pbIter_2)

        self.lbIter_2 = QLabel(SequenceSelector)
        self.lbIter_2.setObjectName(u"lbIter_2")
        self.lbIter_2.setEnabled(True)
        self.lbIter_2.setFont(font)
        self.lbIter_2.setAlignment(Qt.AlignCenter)

        self.iteration_2_layout.addWidget(self.lbIter_2)


        self.mainLayout.addLayout(self.iteration_2_layout)

        self.iteration_3_layout = QHBoxLayout()
        self.iteration_3_layout.setObjectName(u"iteration_3_layout")
        self.pbIter_3 = QPushButton(SequenceSelector)
        self.pbIter_3.setObjectName(u"pbIter_3")
        self.pbIter_3.setEnabled(True)
        self.pbIter_3.setCheckable(False)

        self.iteration_3_layout.addWidget(self.pbIter_3)

        self.lbIter_3 = QLabel(SequenceSelector)
        self.lbIter_3.setObjectName(u"lbIter_3")
        self.lbIter_3.setEnabled(True)
        self.lbIter_3.setFont(font)
        self.lbIter_3.setAlignment(Qt.AlignCenter)

        self.iteration_3_layout.addWidget(self.lbIter_3)


        self.mainLayout.addLayout(self.iteration_3_layout)

        self.iteration_4_layout = QHBoxLayout()
        self.iteration_4_layout.setObjectName(u"iteration_4_layout")
        self.pbIter_4 = QPushButton(SequenceSelector)
        self.pbIter_4.setObjectName(u"pbIter_4")
        self.pbIter_4.setEnabled(True)
        self.pbIter_4.setCheckable(False)

        self.iteration_4_layout.addWidget(self.pbIter_4)

        self.lbIter_4 = QLabel(SequenceSelector)
        self.lbIter_4.setObjectName(u"lbIter_4")
        self.lbIter_4.setEnabled(True)
        self.lbIter_4.setFont(font)
        self.lbIter_4.setAlignment(Qt.AlignCenter)

        self.iteration_4_layout.addWidget(self.lbIter_4)


        self.mainLayout.addLayout(self.iteration_4_layout)

        self.iteration_5_layout = QHBoxLayout()
        self.iteration_5_layout.setObjectName(u"iteration_5_layout")
        self.pbIter_5 = QPushButton(SequenceSelector)
        self.pbIter_5.setObjectName(u"pbIter_5")
        self.pbIter_5.setEnabled(True)
        self.pbIter_5.setCheckable(False)

        self.iteration_5_layout.addWidget(self.pbIter_5)

        self.lbIter_5 = QLabel(SequenceSelector)
        self.lbIter_5.setObjectName(u"lbIter_5")
        self.lbIter_5.setEnabled(True)
        self.lbIter_5.setFont(font)
        self.lbIter_5.setAlignment(Qt.AlignCenter)

        self.iteration_5_layout.addWidget(self.lbIter_5)


        self.mainLayout.addLayout(self.iteration_5_layout)

        self.iteration_6_layout = QHBoxLayout()
        self.iteration_6_layout.setObjectName(u"iteration_6_layout")
        self.pbIter_6 = QPushButton(SequenceSelector)
        self.pbIter_6.setObjectName(u"pbIter_6")
        self.pbIter_6.setEnabled(True)
        self.pbIter_6.setCheckable(False)

        self.iteration_6_layout.addWidget(self.pbIter_6)

        self.lbIter_6 = QLabel(SequenceSelector)
        self.lbIter_6.setObjectName(u"lbIter_6")
        self.lbIter_6.setEnabled(True)
        self.lbIter_6.setFont(font)
        self.lbIter_6.setAlignment(Qt.AlignCenter)

        self.iteration_6_layout.addWidget(self.lbIter_6)


        self.mainLayout.addLayout(self.iteration_6_layout)

        self.iteration_7_layout = QHBoxLayout()
        self.iteration_7_layout.setObjectName(u"iteration_7_layout")
        self.pbIter_7 = QPushButton(SequenceSelector)
        self.pbIter_7.setObjectName(u"pbIter_7")
        self.pbIter_7.setEnabled(True)
        self.pbIter_7.setCheckable(False)

        self.iteration_7_layout.addWidget(self.pbIter_7)

        self.lbIter_7 = QLabel(SequenceSelector)
        self.lbIter_7.setObjectName(u"lbIter_7")
        self.lbIter_7.setEnabled(True)
        self.lbIter_7.setFont(font)
        self.lbIter_7.setAlignment(Qt.AlignCenter)

        self.iteration_7_layout.addWidget(self.lbIter_7)


        self.mainLayout.addLayout(self.iteration_7_layout)

        self.itaeration_9_layout = QHBoxLayout()
        self.itaeration_9_layout.setObjectName(u"itaeration_9_layout")
        self.pbIter_8 = QPushButton(SequenceSelector)
        self.pbIter_8.setObjectName(u"pbIter_8")
        self.pbIter_8.setEnabled(True)
        self.pbIter_8.setCheckable(False)

        self.itaeration_9_layout.addWidget(self.pbIter_8)

        self.lbIter_8 = QLabel(SequenceSelector)
        self.lbIter_8.setObjectName(u"lbIter_8")
        self.lbIter_8.setEnabled(True)
        self.lbIter_8.setFont(font)
        self.lbIter_8.setAlignment(Qt.AlignCenter)

        self.itaeration_9_layout.addWidget(self.lbIter_8)


        self.mainLayout.addLayout(self.itaeration_9_layout)

        self.iteration_9_layout = QHBoxLayout()
        self.iteration_9_layout.setObjectName(u"iteration_9_layout")
        self.pbIter_9 = QPushButton(SequenceSelector)
        self.pbIter_9.setObjectName(u"pbIter_9")
        self.pbIter_9.setEnabled(True)
        self.pbIter_9.setCheckable(False)

        self.iteration_9_layout.addWidget(self.pbIter_9)

        self.lbIter_9 = QLabel(SequenceSelector)
        self.lbIter_9.setObjectName(u"lbIter_9")
        self.lbIter_9.setEnabled(True)
        self.lbIter_9.setFont(font)
        self.lbIter_9.setAlignment(Qt.AlignCenter)

        self.iteration_9_layout.addWidget(self.lbIter_9)


        self.mainLayout.addLayout(self.iteration_9_layout)

        self.iteration_10_layout = QHBoxLayout()
        self.iteration_10_layout.setObjectName(u"iteration_10_layout")
        self.pbIter_10 = QPushButton(SequenceSelector)
        self.pbIter_10.setObjectName(u"pbIter_10")
        self.pbIter_10.setEnabled(True)
        self.pbIter_10.setCheckable(False)

        self.iteration_10_layout.addWidget(self.pbIter_10)

        self.lbIter_10 = QLabel(SequenceSelector)
        self.lbIter_10.setObjectName(u"lbIter_10")
        self.lbIter_10.setEnabled(True)
        self.lbIter_10.setFont(font)
        self.lbIter_10.setAlignment(Qt.AlignCenter)

        self.iteration_10_layout.addWidget(self.lbIter_10)


        self.mainLayout.addLayout(self.iteration_10_layout)

        self.iteration_11_layout = QHBoxLayout()
        self.iteration_11_layout.setObjectName(u"iteration_11_layout")
        self.pbIter_11 = QPushButton(SequenceSelector)
        self.pbIter_11.setObjectName(u"pbIter_11")
        self.pbIter_11.setEnabled(True)
        self.pbIter_11.setCheckable(False)

        self.iteration_11_layout.addWidget(self.pbIter_11)

        self.lbIter_11 = QLabel(SequenceSelector)
        self.lbIter_11.setObjectName(u"lbIter_11")
        self.lbIter_11.setEnabled(True)
        self.lbIter_11.setFont(font)
        self.lbIter_11.setAlignment(Qt.AlignCenter)

        self.iteration_11_layout.addWidget(self.lbIter_11)


        self.mainLayout.addLayout(self.iteration_11_layout)

        self.last_valid_layout = QHBoxLayout()
        self.last_valid_layout.setObjectName(u"last_valid_layout")
        self.pb_last_valid = QPushButton(SequenceSelector)
        self.pb_last_valid.setObjectName(u"pb_last_valid")
        self.pb_last_valid.setCheckable(False)

        self.last_valid_layout.addWidget(self.pb_last_valid)

        self.pl_last_valid = QLabel(SequenceSelector)
        self.pl_last_valid.setObjectName(u"pl_last_valid")
        self.pl_last_valid.setFont(font)
        self.pl_last_valid.setAlignment(Qt.AlignCenter)

        self.last_valid_layout.addWidget(self.pl_last_valid)


        self.mainLayout.addLayout(self.last_valid_layout)

        self.lbInfo = QLabel(SequenceSelector)
        self.lbInfo.setObjectName(u"lbInfo")

        self.mainLayout.addWidget(self.lbInfo)

        self.fixedVerticalSpacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.mainLayout.addItem(self.fixedVerticalSpacer)

        self.cbTracking = QCheckBox(SequenceSelector)
        self.cbTracking.setObjectName(u"cbTracking")

        self.mainLayout.addWidget(self.cbTracking)

        self.dwellLayout = QHBoxLayout()
        self.dwellLayout.setObjectName(u"dwellLayout")
        self.dwellLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.lbDwellTime = QLabel(SequenceSelector)
        self.lbDwellTime.setObjectName(u"lbDwellTime")
        sizePolicy1 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.lbDwellTime.sizePolicy().hasHeightForWidth())
        self.lbDwellTime.setSizePolicy(sizePolicy1)

        self.dwellLayout.addWidget(self.lbDwellTime)

        self.leDwellTime = QLineEdit(SequenceSelector)
        self.leDwellTime.setObjectName(u"leDwellTime")
        sizePolicy2 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.leDwellTime.sizePolicy().hasHeightForWidth())
        self.leDwellTime.setSizePolicy(sizePolicy2)

        self.dwellLayout.addWidget(self.leDwellTime)


        self.mainLayout.addLayout(self.dwellLayout)


        self.gridLayout.addLayout(self.mainLayout, 0, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(SequenceSelector)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)


        self.retranslateUi(SequenceSelector)
        self.buttonBox.accepted.connect(SequenceSelector.accept)
        self.buttonBox.rejected.connect(SequenceSelector.reject)

        QMetaObject.connectSlotsByName(SequenceSelector)
    # setupUi

    def retranslateUi(self, SequenceSelector):
        SequenceSelector.setWindowTitle(QCoreApplication.translate("SequenceSelector", u"Sequence Selector", None))
        self.lbIteration.setText(QCoreApplication.translate("SequenceSelector", u"Iteration number", None))
        self.lbCFRStatus.setText(QCoreApplication.translate("SequenceSelector", u"CFR status", None))
        self.pbIter_0.setText(QCoreApplication.translate("SequenceSelector", u"Iteration 0", None))
        self.lbIter_0.setText(QCoreApplication.translate("SequenceSelector", u"\u2a2f", None))
        self.pbIter_1.setText(QCoreApplication.translate("SequenceSelector", u"Iteration 1", None))
        self.lbIter_1.setText(QCoreApplication.translate("SequenceSelector", u"\u2a2f", None))
        self.pbIter_2.setText(QCoreApplication.translate("SequenceSelector", u"Iteration 2", None))
        self.lbIter_2.setText(QCoreApplication.translate("SequenceSelector", u"\u2a2f", None))
        self.pbIter_3.setText(QCoreApplication.translate("SequenceSelector", u"Iteration 3", None))
        self.lbIter_3.setText(QCoreApplication.translate("SequenceSelector", u"\u2a2f", None))
        self.pbIter_4.setText(QCoreApplication.translate("SequenceSelector", u"Iteration 4", None))
        self.lbIter_4.setText(QCoreApplication.translate("SequenceSelector", u"\u2a2f", None))
        self.pbIter_5.setText(QCoreApplication.translate("SequenceSelector", u"Iteration 5", None))
        self.lbIter_5.setText(QCoreApplication.translate("SequenceSelector", u"\u2a2f", None))
        self.pbIter_6.setText(QCoreApplication.translate("SequenceSelector", u"Iteration 6", None))
        self.lbIter_6.setText(QCoreApplication.translate("SequenceSelector", u"\u2a2f", None))
        self.pbIter_7.setText(QCoreApplication.translate("SequenceSelector", u"Iteration 7", None))
        self.lbIter_7.setText(QCoreApplication.translate("SequenceSelector", u"\u2a2f", None))
        self.pbIter_8.setText(QCoreApplication.translate("SequenceSelector", u"Iteration 8", None))
        self.lbIter_8.setText(QCoreApplication.translate("SequenceSelector", u"\u2a2f", None))
        self.pbIter_9.setText(QCoreApplication.translate("SequenceSelector", u"Iteration 9", None))
        self.lbIter_9.setText(QCoreApplication.translate("SequenceSelector", u"\u2a2f", None))
        self.pbIter_10.setText(QCoreApplication.translate("SequenceSelector", u"Iteration 10", None))
        self.lbIter_10.setText(QCoreApplication.translate("SequenceSelector", u"\u2a2f", None))
        self.pbIter_11.setText(QCoreApplication.translate("SequenceSelector", u"Iteration 11", None))
        self.lbIter_11.setText(QCoreApplication.translate("SequenceSelector", u"\u2713", None))
        self.pb_last_valid.setText(QCoreApplication.translate("SequenceSelector", u"Last valid", None))
        self.pl_last_valid.setText("")
        self.lbInfo.setText(QCoreApplication.translate("SequenceSelector", u"Only \"last valid\" iteration can be saved.", None))
        self.cbTracking.setText(QCoreApplication.translate("SequenceSelector", u"Tracking dataset", None))
        self.lbDwellTime.setText(QCoreApplication.translate("SequenceSelector", u"Dwell time (ms)", None))
    # retranslateUi

