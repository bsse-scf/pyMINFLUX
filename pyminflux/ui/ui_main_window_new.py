# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window_new.ui'
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
from PySide6.QtWidgets import (QApplication, QDockWidget, QGridLayout, QLayout,
    QMainWindow, QMenuBar, QPushButton, QSizePolicy,
    QStatusBar, QTextEdit, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1276, 957)
        MainWindow.setMinimumSize(QSize(1000, 800))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.pbLoadNumpyDataFile = QPushButton(self.centralwidget)
        self.pbLoadNumpyDataFile.setObjectName(u"pbLoadNumpyDataFile")

        self.verticalLayout.addWidget(self.pbLoadNumpyDataFile)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.plotting_layout = QGridLayout()
        self.plotting_layout.setObjectName(u"plotting_layout")

        self.gridLayout.addLayout(self.plotting_layout, 0, 2, 1, 2)

        self.dataframe_layout = QGridLayout()
        self.dataframe_layout.setObjectName(u"dataframe_layout")
        self.dataframe_layout.setSizeConstraint(QLayout.SetDefaultConstraint)

        self.gridLayout.addLayout(self.dataframe_layout, 0, 0, 1, 2)


        self.verticalLayout.addLayout(self.gridLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1276, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.dwBottom = QDockWidget(MainWindow)
        self.dwBottom.setObjectName(u"dwBottom")
        self.dwBottom.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.dockWidgetContents.setMinimumSize(QSize(0, 200))
        self.txConsole = QTextEdit(self.dockWidgetContents)
        self.txConsole.setObjectName(u"txConsole")
        self.txConsole.setGeometry(QRect(10, 10, 1256, 200))
        self.txConsole.setMaximumSize(QSize(16777215, 200))
        self.txConsole.setReadOnly(True)
        self.dwBottom.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(Qt.BottomDockWidgetArea, self.dwBottom)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.pbLoadNumpyDataFile.setText(QCoreApplication.translate("MainWindow", u"Load", None))
    # retranslateUi

