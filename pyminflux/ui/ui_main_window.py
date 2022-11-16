# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
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
from PySide6.QtWidgets import (QApplication, QGraphicsView, QGridLayout, QLabel,
    QMainWindow, QPushButton, QSizePolicy, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1250, 900)
        MainWindow.setMinimumSize(QSize(0, 600))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget_layout = QGridLayout(self.centralwidget)
        self.centralwidget_layout.setObjectName(u"centralwidget_layout")
        self.dataviewer_widget = QWidget(self.centralwidget)
        self.dataviewer_widget.setObjectName(u"dataviewer_widget")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dataviewer_widget.sizePolicy().hasHeightForWidth())
        self.dataviewer_widget.setSizePolicy(sizePolicy)
        self.dataviewer_widget.setMinimumSize(QSize(200, 200))
        self.project_layout = QVBoxLayout(self.dataviewer_widget)
        self.project_layout.setObjectName(u"project_layout")
        self.lbDataViewer = QLabel(self.dataviewer_widget)
        self.lbDataViewer.setObjectName(u"lbDataViewer")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.lbDataViewer.sizePolicy().hasHeightForWidth())
        self.lbDataViewer.setSizePolicy(sizePolicy1)
        self.lbDataViewer.setMinimumSize(QSize(0, 24))
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.lbDataViewer.setFont(font)

        self.project_layout.addWidget(self.lbDataViewer)

        self.pbLoadNumpyDataFile = QPushButton(self.dataviewer_widget)
        self.pbLoadNumpyDataFile.setObjectName(u"pbLoadNumpyDataFile")

        self.project_layout.addWidget(self.pbLoadNumpyDataFile)

        self.wgResults = QWidget(self.dataviewer_widget)
        self.wgResults.setObjectName(u"wgResults")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.wgResults.sizePolicy().hasHeightForWidth())
        self.wgResults.setSizePolicy(sizePolicy2)
        self.gridLayout_4 = QGridLayout(self.wgResults)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.dataframe_layout = QGridLayout()
        self.dataframe_layout.setObjectName(u"dataframe_layout")

        self.gridLayout_4.addLayout(self.dataframe_layout, 0, 0, 1, 1)


        self.project_layout.addWidget(self.wgResults)


        self.centralwidget_layout.addWidget(self.dataviewer_widget, 0, 0, 1, 1)

        self.txConsole = QTextEdit(self.centralwidget)
        self.txConsole.setObjectName(u"txConsole")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.txConsole.sizePolicy().hasHeightForWidth())
        self.txConsole.setSizePolicy(sizePolicy3)
        self.txConsole.setMinimumSize(QSize(0, 150))
        self.txConsole.setMaximumSize(QSize(16777215, 150))
        self.txConsole.setAcceptDrops(False)
        self.txConsole.setReadOnly(True)

        self.centralwidget_layout.addWidget(self.txConsole, 1, 0, 1, 2)

        self.plotting_widget_container = QWidget(self.centralwidget)
        self.plotting_widget_container.setObjectName(u"plotting_widget_container")
        sizePolicy4 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy4.setHorizontalStretch(4)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.plotting_widget_container.sizePolicy().hasHeightForWidth())
        self.plotting_widget_container.setSizePolicy(sizePolicy4)
        self.plotting_widget_container.setMinimumSize(QSize(200, 200))
        self.verticalLayout_2 = QVBoxLayout(self.plotting_widget_container)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.plotting_widget = QWidget(self.plotting_widget_container)
        self.plotting_widget.setObjectName(u"plotting_widget")
        sizePolicy2.setHeightForWidth(self.plotting_widget.sizePolicy().hasHeightForWidth())
        self.plotting_widget.setSizePolicy(sizePolicy2)
        self.gridLayout_10 = QGridLayout(self.plotting_widget)
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.graphicsView = QGraphicsView(self.plotting_widget)
        self.graphicsView.setObjectName(u"graphicsView")

        self.gridLayout_10.addWidget(self.graphicsView, 0, 0, 1, 1)


        self.verticalLayout.addWidget(self.plotting_widget)


        self.verticalLayout_2.addLayout(self.verticalLayout)


        self.centralwidget_layout.addWidget(self.plotting_widget_container, 0, 1, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.lbDataViewer.setText(QCoreApplication.translate("MainWindow", u"Data Viewer", None))
        self.pbLoadNumpyDataFile.setText(QCoreApplication.translate("MainWindow", u"Load", None))
    # retranslateUi

