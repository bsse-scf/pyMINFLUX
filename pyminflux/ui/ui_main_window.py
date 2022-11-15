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
from PySide6.QtWidgets import (QApplication, QCheckBox, QGraphicsView, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLayout,
    QMainWindow, QPushButton, QRadioButton, QSizePolicy,
    QTextEdit, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1250, 900)
        MainWindow.setMinimumSize(QSize(0, 600))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
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

        self.pbSaveProject = QPushButton(self.dataviewer_widget)
        self.pbSaveProject.setObjectName(u"pbSaveProject")

        self.project_layout.addWidget(self.pbSaveProject)

        self.pbExportResults = QPushButton(self.dataviewer_widget)
        self.pbExportResults.setObjectName(u"pbExportResults")

        self.project_layout.addWidget(self.pbExportResults)

        self.lbData = QLabel(self.dataviewer_widget)
        self.lbData.setObjectName(u"lbData")
        sizePolicy1.setHeightForWidth(self.lbData.sizePolicy().hasHeightForWidth())
        self.lbData.setSizePolicy(sizePolicy1)
        self.lbData.setMinimumSize(QSize(0, 16))
        self.lbData.setMaximumSize(QSize(16777215, 16))
        font1 = QFont()
        font1.setUnderline(True)
        self.lbData.setFont(font1)

        self.project_layout.addWidget(self.lbData)

        self.wgData = QWidget(self.dataviewer_widget)
        self.wgData.setObjectName(u"wgData")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.wgData.sizePolicy().hasHeightForWidth())
        self.wgData.setSizePolicy(sizePolicy2)
        self.gridLayout_3 = QGridLayout(self.wgData)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.data_layout = QGridLayout()
        self.data_layout.setObjectName(u"data_layout")

        self.gridLayout_3.addLayout(self.data_layout, 0, 0, 1, 1)


        self.project_layout.addWidget(self.wgData)

        self.wgInputFiles = QWidget(self.dataviewer_widget)
        self.wgInputFiles.setObjectName(u"wgInputFiles")
        sizePolicy1.setHeightForWidth(self.wgInputFiles.sizePolicy().hasHeightForWidth())
        self.wgInputFiles.setSizePolicy(sizePolicy1)
        self.wgInputFiles.setMinimumSize(QSize(0, 40))
        self.wgInputFiles.setMaximumSize(QSize(16777215, 184))
        self.gridLayout_2 = QGridLayout(self.wgInputFiles)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetFixedSize)
        self.pbSelectData = QPushButton(self.wgInputFiles)
        self.pbSelectData.setObjectName(u"pbSelectData")

        self.horizontalLayout.addWidget(self.pbSelectData)

        self.pbSelectImages = QPushButton(self.wgInputFiles)
        self.pbSelectImages.setObjectName(u"pbSelectImages")

        self.horizontalLayout.addWidget(self.pbSelectImages)


        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 0, 1, 1)


        self.project_layout.addWidget(self.wgInputFiles)

        self.lbAnalysis = QLabel(self.dataviewer_widget)
        self.lbAnalysis.setObjectName(u"lbAnalysis")
        font2 = QFont()
        font2.setItalic(False)
        font2.setUnderline(True)
        self.lbAnalysis.setFont(font2)

        self.project_layout.addWidget(self.lbAnalysis)

        self.wgAnalysis = QWidget(self.dataviewer_widget)
        self.wgAnalysis.setObjectName(u"wgAnalysis")
        sizePolicy1.setHeightForWidth(self.wgAnalysis.sizePolicy().hasHeightForWidth())
        self.wgAnalysis.setSizePolicy(sizePolicy1)
        self.gridLayout_6 = QGridLayout(self.wgAnalysis)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.pbSettings = QPushButton(self.wgAnalysis)
        self.pbSettings.setObjectName(u"pbSettings")

        self.gridLayout_5.addWidget(self.pbSettings, 0, 0, 1, 1)

        self.pbRunTracker = QPushButton(self.wgAnalysis)
        self.pbRunTracker.setObjectName(u"pbRunTracker")

        self.gridLayout_5.addWidget(self.pbRunTracker, 0, 1, 1, 1)


        self.gridLayout_6.addLayout(self.gridLayout_5, 0, 0, 1, 1)


        self.project_layout.addWidget(self.wgAnalysis)

        self.lbResults = QLabel(self.dataviewer_widget)
        self.lbResults.setObjectName(u"lbResults")
        sizePolicy1.setHeightForWidth(self.lbResults.sizePolicy().hasHeightForWidth())
        self.lbResults.setSizePolicy(sizePolicy1)
        self.lbResults.setMinimumSize(QSize(0, 16))
        self.lbResults.setMaximumSize(QSize(16777215, 16))
        self.lbResults.setFont(font1)

        self.project_layout.addWidget(self.lbResults)

        self.wgResults = QWidget(self.dataviewer_widget)
        self.wgResults.setObjectName(u"wgResults")
        sizePolicy2.setHeightForWidth(self.wgResults.sizePolicy().hasHeightForWidth())
        self.wgResults.setSizePolicy(sizePolicy2)
        self.gridLayout_4 = QGridLayout(self.wgResults)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.result_layout = QGridLayout()
        self.result_layout.setObjectName(u"result_layout")

        self.gridLayout_4.addLayout(self.result_layout, 0, 0, 1, 1)


        self.project_layout.addWidget(self.wgResults)


        self.gridLayout.addWidget(self.dataviewer_widget, 1, 0, 1, 1)

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

        self.gridLayout.addWidget(self.txConsole, 2, 0, 1, 2)

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

        self.widget_3 = QWidget(self.plotting_widget_container)
        self.widget_3.setObjectName(u"widget_3")
        sizePolicy5 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.widget_3.sizePolicy().hasHeightForWidth())
        self.widget_3.setSizePolicy(sizePolicy5)
        self.gridLayout_8 = QGridLayout(self.widget_3)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.gridLayout_7 = QGridLayout()
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.gbDisplayOptions = QGroupBox(self.widget_3)
        self.gbDisplayOptions.setObjectName(u"gbDisplayOptions")
        sizePolicy5.setHeightForWidth(self.gbDisplayOptions.sizePolicy().hasHeightForWidth())
        self.gbDisplayOptions.setSizePolicy(sizePolicy5)
        self.horizontalLayout_2 = QHBoxLayout(self.gbDisplayOptions)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.rbPlotCellIndex = QRadioButton(self.gbDisplayOptions)
        self.rbPlotCellIndex.setObjectName(u"rbPlotCellIndex")
        self.rbPlotCellIndex.setChecked(True)

        self.horizontalLayout_2.addWidget(self.rbPlotCellIndex)

        self.rbPlotTrackIndex = QRadioButton(self.gbDisplayOptions)
        self.rbPlotTrackIndex.setObjectName(u"rbPlotTrackIndex")

        self.horizontalLayout_2.addWidget(self.rbPlotTrackIndex)

        self.cbPlotFiltVectors = QCheckBox(self.gbDisplayOptions)
        self.cbPlotFiltVectors.setObjectName(u"cbPlotFiltVectors")
        self.cbPlotFiltVectors.setChecked(True)

        self.horizontalLayout_2.addWidget(self.cbPlotFiltVectors)

        self.cbPlotRawVectors = QCheckBox(self.gbDisplayOptions)
        self.cbPlotRawVectors.setObjectName(u"cbPlotRawVectors")
        self.cbPlotRawVectors.setChecked(True)

        self.horizontalLayout_2.addWidget(self.cbPlotRawVectors)


        self.gridLayout_7.addWidget(self.gbDisplayOptions, 0, 0, 1, 1)


        self.gridLayout_8.addLayout(self.gridLayout_7, 0, 0, 1, 1)


        self.verticalLayout_2.addWidget(self.widget_3)


        self.gridLayout.addWidget(self.plotting_widget_container, 1, 1, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.lbDataViewer.setText(QCoreApplication.translate("MainWindow", u"Data Viewer", None))
        self.pbLoadNumpyDataFile.setText(QCoreApplication.translate("MainWindow", u"Load", None))
        self.pbSaveProject.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.pbExportResults.setText(QCoreApplication.translate("MainWindow", u"Export", None))
        self.lbData.setText(QCoreApplication.translate("MainWindow", u"Data frames", None))
        self.pbSelectData.setText(QCoreApplication.translate("MainWindow", u"Select CellX results", None))
        self.pbSelectImages.setText(QCoreApplication.translate("MainWindow", u"Select images", None))
        self.lbAnalysis.setText(QCoreApplication.translate("MainWindow", u"Analysis", None))
        self.pbSettings.setText(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.pbRunTracker.setText(QCoreApplication.translate("MainWindow", u"Run", None))
        self.lbResults.setText(QCoreApplication.translate("MainWindow", u"Results", None))
        self.gbDisplayOptions.setTitle(QCoreApplication.translate("MainWindow", u"Options", None))
        self.rbPlotCellIndex.setText(QCoreApplication.translate("MainWindow", u"Plot cell index", None))
        self.rbPlotTrackIndex.setText(QCoreApplication.translate("MainWindow", u"Plot track index", None))
        self.cbPlotFiltVectors.setText(QCoreApplication.translate("MainWindow", u"Plot filtered vectors", None))
        self.cbPlotRawVectors.setText(QCoreApplication.translate("MainWindow", u"Plot raw vectors", None))
    # retranslateUi

