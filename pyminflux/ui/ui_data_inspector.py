# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'data_inspector.ui'
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
    QComboBox,
    QDialog,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class Ui_DataInspector(object):
    def setupUi(self, DataInspector):
        if not DataInspector.objectName():
            DataInspector.setObjectName("DataInspector")
        DataInspector.resize(800, 600)
        self.verticalLayout_2 = QVBoxLayout(DataInspector)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.main_layout = QVBoxLayout()
        self.main_layout.setObjectName("main_layout")
        self.commands_layout = QHBoxLayout()
        self.commands_layout.setObjectName("commands_layout")
        self.cbFirstParam = QComboBox(DataInspector)
        self.cbFirstParam.setObjectName("cbFirstParam")

        self.commands_layout.addWidget(self.cbFirstParam)

        self.cbSecondParam = QComboBox(DataInspector)
        self.cbSecondParam.setObjectName("cbSecondParam")

        self.commands_layout.addWidget(self.cbSecondParam)

        self.pbPlot = QPushButton(DataInspector)
        self.pbPlot.setObjectName("pbPlot")

        self.commands_layout.addWidget(self.pbPlot)

        self.main_layout.addLayout(self.commands_layout)

        self.verticalLayout_2.addLayout(self.main_layout)

        self.retranslateUi(DataInspector)

        QMetaObject.connectSlotsByName(DataInspector)

    # setupUi

    def retranslateUi(self, DataInspector):
        DataInspector.setWindowTitle(
            QCoreApplication.translate("DataInspector", "Data Inspector", None)
        )
        self.pbPlot.setText(QCoreApplication.translate("DataInspector", "Plot", None))

    # retranslateUi
