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
## Form generated from reading UI file 'main_window.ui'
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
    QAction,
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
    QMenu,
    QMenuBar,
    QSizePolicy,
    QSplitter,
    QStatusBar,
    QWidget,
)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 800)
        MainWindow.setMinimumSize(QSize(640, 480))
        self.actionLoad = QAction(MainWindow)
        self.actionLoad.setObjectName("actionLoad")
        self.actionQuit = QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")
        self.actionConsole = QAction(MainWindow)
        self.actionConsole.setObjectName("actionConsole")
        self.actionConsole.setCheckable(True)
        self.actionConsole.setChecked(False)
        self.actionData_viewer = QAction(MainWindow)
        self.actionData_viewer.setObjectName("actionData_viewer")
        self.actionData_viewer.setCheckable(True)
        self.actionData_viewer.setChecked(True)
        self.action3D_Plotter = QAction(MainWindow)
        self.action3D_Plotter.setObjectName("action3D_Plotter")
        self.action3D_Plotter.setCheckable(False)
        self.actionState = QAction(MainWindow)
        self.actionState.setObjectName("actionState")
        self.actionOptions = QAction(MainWindow)
        self.actionOptions.setObjectName("actionOptions")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionExport_data = QAction(MainWindow)
        self.actionExport_data.setObjectName("actionExport_data")
        self.actionManual = QAction(MainWindow)
        self.actionManual.setObjectName("actionManual")
        self.actionWebsite = QAction(MainWindow)
        self.actionWebsite.setObjectName("actionWebsite")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter_layout = QSplitter(self.centralwidget)
        self.splitter_layout.setObjectName("splitter_layout")
        self.splitter_layout.setMaximumSize(QSize(16777215, 16777215))
        self.splitter_layout.setOrientation(Qt.Vertical)

        self.gridLayout.addWidget(self.splitter_layout, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 1000, 23))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuView = QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionLoad)
        self.menuFile.addAction(self.actionExport_data)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionOptions)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        self.menuView.addAction(self.actionData_viewer)
        self.menuView.addAction(self.actionConsole)
        self.menuView.addSeparator()
        self.menuView.addAction(self.action3D_Plotter)
        self.menuView.addSeparator()
        self.menuView.addSeparator()
        self.menuView.addAction(self.actionState)
        self.menuHelp.addAction(self.actionManual)
        self.menuHelp.addAction(self.actionWebsite)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionAbout)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "MainWindow", None)
        )
        self.actionLoad.setText(
            QCoreApplication.translate("MainWindow", "&Load data", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionLoad.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Load MinFlux binary NumPy data", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.actionLoad.setShortcut(
            QCoreApplication.translate("MainWindow", "Ctrl+L", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionQuit.setText(QCoreApplication.translate("MainWindow", "Quit", None))
        # if QT_CONFIG(tooltip)
        self.actionQuit.setToolTip(
            QCoreApplication.translate("MainWindow", "Quit application", None)
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.actionQuit.setShortcut("")
        # endif // QT_CONFIG(shortcut)
        self.actionConsole.setText(
            QCoreApplication.translate("MainWindow", "Console", None)
        )
        self.actionData_viewer.setText(
            QCoreApplication.translate("MainWindow", "Data viewer", None)
        )
        self.action3D_Plotter.setText(
            QCoreApplication.translate("MainWindow", "3D plotter", None)
        )
        self.actionState.setText(
            QCoreApplication.translate("MainWindow", "[DEBUG] Show state", None)
        )
        self.actionOptions.setText(
            QCoreApplication.translate("MainWindow", "Options", None)
        )
        self.actionAbout.setText(
            QCoreApplication.translate("MainWindow", "About", None)
        )
        self.actionExport_data.setText(
            QCoreApplication.translate("MainWindow", "Export data", None)
        )
        self.actionManual.setText(
            QCoreApplication.translate("MainWindow", "Manual", None)
        )
        self.actionWebsite.setText(
            QCoreApplication.translate("MainWindow", "Website", None)
        )
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", "File", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", "View", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", "Help", None))

    # retranslateUi
