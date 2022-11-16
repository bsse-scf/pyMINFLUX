# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.4.0
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
    QGridLayout,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1250, 900)
        MainWindow.setMinimumSize(QSize(0, 600))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget_layout = QGridLayout(self.centralwidget)
        self.centralwidget_layout.setObjectName("centralwidget_layout")
        self.dataviewer_widget = QWidget(self.centralwidget)
        self.dataviewer_widget.setObjectName("dataviewer_widget")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.dataviewer_widget.sizePolicy().hasHeightForWidth()
        )
        self.dataviewer_widget.setSizePolicy(sizePolicy)
        self.dataviewer_widget.setMinimumSize(QSize(200, 200))
        self.project_layout = QVBoxLayout(self.dataviewer_widget)
        self.project_layout.setObjectName("project_layout")
        self.wgDataframe = QWidget(self.dataviewer_widget)
        self.wgDataframe.setObjectName("wgDataframe")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.wgDataframe.sizePolicy().hasHeightForWidth())
        self.wgDataframe.setSizePolicy(sizePolicy1)
        self.gridLayout_4 = QGridLayout(self.wgDataframe)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.dataframe_layout = QGridLayout()
        self.dataframe_layout.setObjectName("dataframe_layout")

        self.gridLayout_4.addLayout(self.dataframe_layout, 0, 0, 1, 1)

        self.pbLoadNumpyDataFile = QPushButton(self.wgDataframe)
        self.pbLoadNumpyDataFile.setObjectName("pbLoadNumpyDataFile")

        self.gridLayout_4.addWidget(self.pbLoadNumpyDataFile, 1, 0, 1, 1)

        self.project_layout.addWidget(self.wgDataframe)

        self.centralwidget_layout.addWidget(self.dataviewer_widget, 0, 0, 1, 1)

        self.txConsole = QTextEdit(self.centralwidget)
        self.txConsole.setObjectName("txConsole")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.txConsole.sizePolicy().hasHeightForWidth())
        self.txConsole.setSizePolicy(sizePolicy2)
        self.txConsole.setMinimumSize(QSize(0, 150))
        self.txConsole.setMaximumSize(QSize(16777215, 150))
        self.txConsole.setAcceptDrops(False)
        self.txConsole.setReadOnly(True)

        self.centralwidget_layout.addWidget(self.txConsole, 1, 0, 1, 2)

        self.plotting_widget_container = QWidget(self.centralwidget)
        self.plotting_widget_container.setObjectName("plotting_widget_container")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(4)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(
            self.plotting_widget_container.sizePolicy().hasHeightForWidth()
        )
        self.plotting_widget_container.setSizePolicy(sizePolicy3)
        self.plotting_widget_container.setMinimumSize(QSize(200, 200))
        self.verticalLayout_2 = QVBoxLayout(self.plotting_widget_container)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.plotting_layout = QVBoxLayout()
        self.plotting_layout.setObjectName("plotting_layout")

        self.verticalLayout_2.addLayout(self.plotting_layout)

        self.centralwidget_layout.addWidget(self.plotting_widget_container, 0, 1, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "MainWindow", None)
        )
        self.pbLoadNumpyDataFile.setText(
            QCoreApplication.translate("MainWindow", "Load", None)
        )

    # retranslateUi
