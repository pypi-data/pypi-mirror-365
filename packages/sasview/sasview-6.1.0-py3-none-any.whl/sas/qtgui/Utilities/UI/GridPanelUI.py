# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'GridPanelUI.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QGridLayout, QHBoxLayout,
    QHeaderView, QMainWindow, QMenu, QMenuBar,
    QPushButton, QSizePolicy, QSpacerItem, QTabWidget,
    QTableWidget, QTableWidgetItem, QWidget)

class Ui_GridPanelUI(object):
    def setupUi(self, GridPanelUI):
        if not GridPanelUI.objectName():
            GridPanelUI.setObjectName(u"GridPanelUI")
        GridPanelUI.resize(939, 330)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(GridPanelUI.sizePolicy().hasHeightForWidth())
        GridPanelUI.setSizePolicy(sizePolicy)
        self.actionOpen = QAction(GridPanelUI)
        self.actionOpen.setObjectName(u"actionOpen")
        self.actionOpen_with_Excel = QAction(GridPanelUI)
        self.actionOpen_with_Excel.setObjectName(u"actionOpen_with_Excel")
        self.actionSave = QAction(GridPanelUI)
        self.actionSave.setObjectName(u"actionSave")
        self.centralwidget = QWidget(GridPanelUI)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_2 = QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.saveButton = QPushButton(self.centralwidget)
        self.saveButton.setObjectName(u"saveButton")

        self.horizontalLayout.addWidget(self.saveButton)

        self.cmdPlot = QPushButton(self.centralwidget)
        self.cmdPlot.setObjectName(u"cmdPlot")

        self.horizontalLayout.addWidget(self.cmdPlot)

        self.cmdOK = QPushButton(self.centralwidget)
        self.cmdOK.setObjectName(u"cmdOK")

        self.horizontalLayout.addWidget(self.cmdOK)

        self.cmdHelp = QPushButton(self.centralwidget)
        self.cmdHelp.setObjectName(u"cmdHelp")

        self.horizontalLayout.addWidget(self.cmdHelp)


        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setTabPosition(QTabWidget.South)
        self.tabWidget.setTabsClosable(True)
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.gridLayout = QGridLayout(self.tab)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.tblParams = QTableWidget(self.tab)
        self.tblParams.setObjectName(u"tblParams")
        self.tblParams.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tblParams.setAlternatingRowColors(True)
        self.tblParams.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.gridLayout.addWidget(self.tblParams, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab, "")

        self.gridLayout_2.addWidget(self.tabWidget, 0, 0, 1, 1)

        GridPanelUI.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(GridPanelUI)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 939, 21))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        GridPanelUI.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionOpen_with_Excel)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave)

        self.retranslateUi(GridPanelUI)
        self.cmdOK.clicked.connect(GridPanelUI.close)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(GridPanelUI)
    # setupUi

    def retranslateUi(self, GridPanelUI):
        GridPanelUI.setWindowTitle(QCoreApplication.translate("GridPanelUI", u"Batch Fitting Results", None))
        self.actionOpen.setText(QCoreApplication.translate("GridPanelUI", u"Open", None))
        self.actionOpen_with_Excel.setText(QCoreApplication.translate("GridPanelUI", u"Open in CSV Viewer", None))
        self.actionSave.setText(QCoreApplication.translate("GridPanelUI", u"Save", None))
        self.saveButton.setText(QCoreApplication.translate("GridPanelUI", u"Save", None))
        self.cmdPlot.setText(QCoreApplication.translate("GridPanelUI", u"Plot", None))
        self.cmdOK.setText(QCoreApplication.translate("GridPanelUI", u"Close", None))
        self.cmdHelp.setText(QCoreApplication.translate("GridPanelUI", u"Help", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("GridPanelUI", u"Batch Result 1", None))
        self.menuFile.setTitle(QCoreApplication.translate("GridPanelUI", u"File", None))
    # retranslateUi

