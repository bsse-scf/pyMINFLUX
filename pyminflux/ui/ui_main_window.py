# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.7.3
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
        self.actionCode_repository = QAction(MainWindow)
        self.actionCode_repository.setObjectName("actionCode_repository")
        self.actionIssues = QAction(MainWindow)
        self.actionIssues.setObjectName("actionIssues")
        self.actionMailing_list = QAction(MainWindow)
        self.actionMailing_list.setObjectName("actionMailing_list")
        self.actionExport_stats = QAction(MainWindow)
        self.actionExport_stats.setObjectName("actionExport_stats")
        self.actionCheck_for_updates = QAction(MainWindow)
        self.actionCheck_for_updates.setObjectName("actionCheck_for_updates")
        self.actionFRC_analyzer = QAction(MainWindow)
        self.actionFRC_analyzer.setObjectName("actionFRC_analyzer")
        self.actionWhat_s_new = QAction(MainWindow)
        self.actionWhat_s_new.setObjectName("actionWhat_s_new")
        self.actionUnmixer = QAction(MainWindow)
        self.actionUnmixer.setObjectName("actionUnmixer")
        self.actionTime_Inspector = QAction(MainWindow)
        self.actionTime_Inspector.setObjectName("actionTime_Inspector")
        self.actionAnalyzer = QAction(MainWindow)
        self.actionAnalyzer.setObjectName("actionAnalyzer")
        self.actionTrace_Stats_Viewer = QAction(MainWindow)
        self.actionTrace_Stats_Viewer.setObjectName("actionTrace_Stats_Viewer")
        self.actionLoad = QAction(MainWindow)
        self.actionLoad.setObjectName("actionLoad")
        self.actionSave = QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionHistogram_Plotter = QAction(MainWindow)
        self.actionHistogram_Plotter.setObjectName("actionHistogram_Plotter")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter_layout = QSplitter(self.centralwidget)
        self.splitter_layout.setObjectName("splitter_layout")
        self.splitter_layout.setMaximumSize(QSize(16777215, 16777215))
        self.splitter_layout.setOrientation(Qt.Orientation.Vertical)

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
        self.menuAnalysis = QMenu(self.menubar)
        self.menuAnalysis.setObjectName("menuAnalysis")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuAnalysis.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionLoad)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExport_data)
        self.menuFile.addAction(self.actionExport_stats)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionOptions)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        self.menuView.addAction(self.actionData_viewer)
        self.menuView.addAction(self.actionConsole)
        self.menuView.addSeparator()
        self.menuView.addAction(self.actionState)
        self.menuHelp.addAction(self.actionManual)
        self.menuHelp.addAction(self.actionWebsite)
        self.menuHelp.addAction(self.actionCode_repository)
        self.menuHelp.addAction(self.actionIssues)
        self.menuHelp.addAction(self.actionMailing_list)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionWhat_s_new)
        self.menuHelp.addAction(self.actionCheck_for_updates)
        self.menuHelp.addAction(self.actionAbout)
        self.menuAnalysis.addAction(self.actionUnmixer)
        self.menuAnalysis.addAction(self.actionTime_Inspector)
        self.menuAnalysis.addAction(self.actionAnalyzer)
        self.menuAnalysis.addSeparator()
        self.menuAnalysis.addAction(self.actionHistogram_Plotter)
        self.menuAnalysis.addAction(self.actionTrace_Stats_Viewer)
        self.menuAnalysis.addAction(self.actionFRC_analyzer)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "MainWindow", None)
        )
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
        self.actionCode_repository.setText(
            QCoreApplication.translate("MainWindow", "Repository", None)
        )
        self.actionIssues.setText(
            QCoreApplication.translate("MainWindow", "Issues", None)
        )
        self.actionMailing_list.setText(
            QCoreApplication.translate("MainWindow", "Mailing list", None)
        )
        self.actionExport_stats.setText(
            QCoreApplication.translate("MainWindow", "Export trace stats", None)
        )
        self.actionCheck_for_updates.setText(
            QCoreApplication.translate("MainWindow", "Check for updates", None)
        )
        self.actionFRC_analyzer.setText(
            QCoreApplication.translate("MainWindow", "FRC Analyzer", None)
        )
        self.actionWhat_s_new.setText(
            QCoreApplication.translate("MainWindow", "What's new?", None)
        )
        self.actionUnmixer.setText(
            QCoreApplication.translate("MainWindow", "Unmixer", None)
        )
        self.actionTime_Inspector.setText(
            QCoreApplication.translate("MainWindow", "Time Inspector", None)
        )
        self.actionAnalyzer.setText(
            QCoreApplication.translate("MainWindow", "Analyzer", None)
        )
        self.actionTrace_Stats_Viewer.setText(
            QCoreApplication.translate("MainWindow", "Trace Stats Viewer", None)
        )
        self.actionLoad.setText(QCoreApplication.translate("MainWindow", "Load", None))
        # if QT_CONFIG(shortcut)
        self.actionLoad.setShortcut(
            QCoreApplication.translate("MainWindow", "Ctrl+L", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionSave.setText(QCoreApplication.translate("MainWindow", "Save", None))
        # if QT_CONFIG(shortcut)
        self.actionSave.setShortcut(
            QCoreApplication.translate("MainWindow", "Ctrl+S", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionHistogram_Plotter.setText(
            QCoreApplication.translate("MainWindow", "Histogram Plotter", None)
        )
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", "File", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", "View", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", "Help", None))
        self.menuAnalysis.setTitle(
            QCoreApplication.translate("MainWindow", "Analysis", None)
        )

    # retranslateUi
