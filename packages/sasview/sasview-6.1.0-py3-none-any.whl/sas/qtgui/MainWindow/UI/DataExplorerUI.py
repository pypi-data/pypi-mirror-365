# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'DataExplorerUI.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QComboBox,
    QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
    QPushButton, QSizePolicy, QSpacerItem, QTabWidget,
    QToolButton, QTreeView, QVBoxLayout, QWidget)

class Ui_DataLoadWidget(object):
    def setupUi(self, DataLoadWidget):
        if not DataLoadWidget.objectName():
            DataLoadWidget.setObjectName(u"DataLoadWidget")
        DataLoadWidget.resize(501, 630)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(5)
        sizePolicy.setHeightForWidth(DataLoadWidget.sizePolicy().hasHeightForWidth())
        DataLoadWidget.setSizePolicy(sizePolicy)
        icon = QIcon()
        icon.addFile(u":/res/ball.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        DataLoadWidget.setWindowIcon(icon)
        self.actionDataInfo = QAction(DataLoadWidget)
        self.actionDataInfo.setObjectName(u"actionDataInfo")
        self.actionSaveAs = QAction(DataLoadWidget)
        self.actionSaveAs.setObjectName(u"actionSaveAs")
        self.actionQuickPlot = QAction(DataLoadWidget)
        self.actionQuickPlot.setObjectName(u"actionQuickPlot")
        self.actionQuick3DPlot = QAction(DataLoadWidget)
        self.actionQuick3DPlot.setObjectName(u"actionQuick3DPlot")
        self.actionEditMask = QAction(DataLoadWidget)
        self.actionEditMask.setObjectName(u"actionEditMask")
        self.actionDelete = QAction(DataLoadWidget)
        self.actionDelete.setObjectName(u"actionDelete")
        self.actionFreezeResults = QAction(DataLoadWidget)
        self.actionFreezeResults.setObjectName(u"actionFreezeResults")
        self.actionSelect = QAction(DataLoadWidget)
        self.actionSelect.setObjectName(u"actionSelect")
        self.actionDeselect = QAction(DataLoadWidget)
        self.actionDeselect.setObjectName(u"actionDeselect")
        self.actionChangeName = QAction(DataLoadWidget)
        self.actionChangeName.setObjectName(u"actionChangeName")
        self.dataTab = QWidget()
        self.dataTab.setObjectName(u"dataTab")
        self.gridLayout_9 = QGridLayout(self.dataTab)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.groupBox = QGroupBox(self.dataTab)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalSpacer_7 = QSpacerItem(92, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.verticalLayout.addItem(self.horizontalSpacer_7)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.cmdLoad = QPushButton(self.groupBox)
        self.cmdLoad.setObjectName(u"cmdLoad")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(5)
        sizePolicy1.setHeightForWidth(self.cmdLoad.sizePolicy().hasHeightForWidth())
        self.cmdLoad.setSizePolicy(sizePolicy1)
        self.cmdLoad.setMinimumSize(QSize(120, 40))
        self.cmdLoad.setBaseSize(QSize(100, 50))
        self.cmdLoad.setStyleSheet(u"font: 11pt \"MS Shell Dlg 2\";")
        icon1 = QIcon()
        icon1.addFile(u":/res/down-grey.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.cmdLoad.setIcon(icon1)
        self.cmdLoad.setIconSize(QSize(32, 32))

        self.gridLayout.addWidget(self.cmdLoad, 0, 0, 2, 1)

        self.cmdDeleteData = QPushButton(self.groupBox)
        self.cmdDeleteData.setObjectName(u"cmdDeleteData")

        self.gridLayout.addWidget(self.cmdDeleteData, 0, 1, 1, 1)

        self.cbSelect = QComboBox(self.groupBox)
        self.cbSelect.addItem("")
        self.cbSelect.addItem("")
        self.cbSelect.addItem("")
        self.cbSelect.addItem("")
        self.cbSelect.addItem("")
        self.cbSelect.addItem("")
        self.cbSelect.setObjectName(u"cbSelect")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.cbSelect.sizePolicy().hasHeightForWidth())
        self.cbSelect.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.cbSelect, 1, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.treeView = QTreeView(self.groupBox)
        self.treeView.setObjectName(u"treeView")
        self.treeView.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.treeView.setAcceptDrops(True)
        self.treeView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.treeView.setDragEnabled(True)
        self.treeView.setDragDropOverwriteMode(True)
        self.treeView.setDragDropMode(QAbstractItemView.DropOnly)
        self.treeView.setDefaultDropAction(Qt.CopyAction)
        self.treeView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeView.header().setVisible(False)

        self.verticalLayout.addWidget(self.treeView)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.cmdSendTo = QToolButton(self.groupBox)
        self.cmdSendTo.setObjectName(u"cmdSendTo")
        sizePolicy1.setHeightForWidth(self.cmdSendTo.sizePolicy().hasHeightForWidth())
        self.cmdSendTo.setSizePolicy(sizePolicy1)
        self.cmdSendTo.setMinimumSize(QSize(145, 40))
        self.cmdSendTo.setBaseSize(QSize(100, 50))
        font = QFont()
        font.setFamilies([u"MS Shell Dlg 2"])
        font.setPointSize(11)
        font.setBold(False)
        font.setItalic(False)
        self.cmdSendTo.setFont(font)
        self.cmdSendTo.setStyleSheet(u"")
        icon2 = QIcon()
        icon2.addFile(u":/res/right-grey.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.cmdSendTo.setIcon(icon2)
        self.cmdSendTo.setIconSize(QSize(32, 32))
        self.cmdSendTo.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.gridLayout_2.addWidget(self.cmdSendTo, 0, 0, 1, 1)

        self.cbFitting = QComboBox(self.groupBox)
        self.cbFitting.addItem("")
        self.cbFitting.addItem("")
        self.cbFitting.addItem("")
        self.cbFitting.setObjectName(u"cbFitting")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Ignored)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.cbFitting.sizePolicy().hasHeightForWidth())
        self.cbFitting.setSizePolicy(sizePolicy3)
        font1 = QFont()
        font1.setPointSize(11)
        self.cbFitting.setFont(font1)
        self.cbFitting.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.gridLayout_2.addWidget(self.cbFitting, 0, 1, 1, 1)

        self.chkBatch = QCheckBox(self.groupBox)
        self.chkBatch.setObjectName(u"chkBatch")

        self.gridLayout_2.addWidget(self.chkBatch, 1, 0, 1, 1)

        self.chkSwap = QCheckBox(self.groupBox)
        self.chkSwap.setObjectName(u"chkSwap")
        self.chkSwap.setEnabled(False)

        self.gridLayout_2.addWidget(self.chkSwap, 1, 1, 1, 1)


        self.horizontalLayout.addLayout(self.gridLayout_2)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.gridLayout_9.addWidget(self.groupBox, 0, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.gridLayout_6 = QGridLayout()
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.groupBox_3 = QGroupBox(self.dataTab)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setFlat(False)
        self.groupBox_3.setCheckable(False)
        self.gridLayout_3 = QGridLayout(self.groupBox_3)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.cmdNew = QPushButton(self.groupBox_3)
        self.cmdNew.setObjectName(u"cmdNew")

        self.gridLayout_3.addWidget(self.cmdNew, 0, 0, 1, 1)

        self.cmdAppend = QPushButton(self.groupBox_3)
        self.cmdAppend.setObjectName(u"cmdAppend")

        self.gridLayout_3.addWidget(self.cmdAppend, 1, 0, 1, 1)

        self.cbgraph = QComboBox(self.groupBox_3)
        self.cbgraph.setObjectName(u"cbgraph")
        sizePolicy2.setHeightForWidth(self.cbgraph.sizePolicy().hasHeightForWidth())
        self.cbgraph.setSizePolicy(sizePolicy2)
        self.cbgraph.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.gridLayout_3.addWidget(self.cbgraph, 1, 1, 1, 1)


        self.gridLayout_6.addWidget(self.groupBox_3, 0, 0, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(103, 48, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_6.addItem(self.horizontalSpacer_3, 0, 1, 1, 1)


        self.horizontalLayout_2.addLayout(self.gridLayout_6)

        self.cmdHelp = QPushButton(self.dataTab)
        self.cmdHelp.setObjectName(u"cmdHelp")

        self.horizontalLayout_2.addWidget(self.cmdHelp, 0, Qt.AlignBottom)


        self.gridLayout_9.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)

        DataLoadWidget.addTab(self.dataTab, "")
        self.theoryTab = QWidget()
        self.theoryTab.setObjectName(u"theoryTab")
        self.gridLayout_8 = QGridLayout(self.theoryTab)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.groupBox_2 = QGroupBox(self.theoryTab)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_4 = QGridLayout(self.groupBox_2)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.cmdFreeze = QPushButton(self.groupBox_2)
        self.cmdFreeze.setObjectName(u"cmdFreeze")

        self.horizontalLayout_3.addWidget(self.cmdFreeze)

        self.horizontalSpacer_5 = QSpacerItem(218, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_5)

        self.cmdDeleteTheory = QPushButton(self.groupBox_2)
        self.cmdDeleteTheory.setObjectName(u"cmdDeleteTheory")

        self.horizontalLayout_3.addWidget(self.cmdDeleteTheory)


        self.gridLayout_4.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)

        self.freezeView = QTreeView(self.groupBox_2)
        self.freezeView.setObjectName(u"freezeView")
        self.freezeView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.freezeView.header().setVisible(False)

        self.gridLayout_4.addWidget(self.freezeView, 1, 0, 1, 1)


        self.gridLayout_8.addWidget(self.groupBox_2, 0, 0, 1, 1)

        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.groupBox_4 = QGroupBox(self.theoryTab)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.gridLayout_7 = QGridLayout(self.groupBox_4)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.cmdNew_2 = QPushButton(self.groupBox_4)
        self.cmdNew_2.setObjectName(u"cmdNew_2")

        self.gridLayout_7.addWidget(self.cmdNew_2, 0, 0, 1, 1)

        self.cmdAppend_2 = QPushButton(self.groupBox_4)
        self.cmdAppend_2.setObjectName(u"cmdAppend_2")

        self.gridLayout_7.addWidget(self.cmdAppend_2, 1, 0, 1, 1)

        self.cbgraph_2 = QComboBox(self.groupBox_4)
        self.cbgraph_2.addItem("")
        self.cbgraph_2.setObjectName(u"cbgraph_2")
        sizePolicy2.setHeightForWidth(self.cbgraph_2.sizePolicy().hasHeightForWidth())
        self.cbgraph_2.setSizePolicy(sizePolicy2)
        self.cbgraph_2.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.gridLayout_7.addWidget(self.cbgraph_2, 1, 1, 1, 1)


        self.gridLayout_5.addWidget(self.groupBox_4, 0, 0, 1, 1)

        self.horizontalSpacer_4 = QSpacerItem(108, 111, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_5.addItem(self.horizontalSpacer_4, 0, 1, 1, 1)

        self.cmdHelp_2 = QPushButton(self.theoryTab)
        self.cmdHelp_2.setObjectName(u"cmdHelp_2")

        self.gridLayout_5.addWidget(self.cmdHelp_2, 0, 2, 1, 1, Qt.AlignBottom)


        self.gridLayout_8.addLayout(self.gridLayout_5, 1, 0, 1, 1)

        DataLoadWidget.addTab(self.theoryTab, "")

        self.retranslateUi(DataLoadWidget)

        DataLoadWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(DataLoadWidget)
    # setupUi

    def retranslateUi(self, DataLoadWidget):
        DataLoadWidget.setWindowTitle(QCoreApplication.translate("DataLoadWidget", u"TabWidget", None))
        self.actionDataInfo.setText(QCoreApplication.translate("DataLoadWidget", u"Data Info", None))
        self.actionSaveAs.setText(QCoreApplication.translate("DataLoadWidget", u"Save As", None))
        self.actionQuickPlot.setText(QCoreApplication.translate("DataLoadWidget", u"Quick Plot", None))
        self.actionQuick3DPlot.setText(QCoreApplication.translate("DataLoadWidget", u"Quick 3DPlot (slow)", None))
        self.actionEditMask.setText(QCoreApplication.translate("DataLoadWidget", u"Edit Mask", None))
        self.actionDelete.setText(QCoreApplication.translate("DataLoadWidget", u"Delete", None))
        self.actionFreezeResults.setText(QCoreApplication.translate("DataLoadWidget", u"Freeze Results", None))
        self.actionSelect.setText(QCoreApplication.translate("DataLoadWidget", u"Select items", None))
        self.actionDeselect.setText(QCoreApplication.translate("DataLoadWidget", u"Deselect items", None))
        self.actionChangeName.setText(QCoreApplication.translate("DataLoadWidget", u"Change Name", None))
#if QT_CONFIG(tooltip)
        self.actionChangeName.setToolTip(QCoreApplication.translate("DataLoadWidget", u"Change Display Name", None))
#endif // QT_CONFIG(tooltip)
        self.groupBox.setTitle(QCoreApplication.translate("DataLoadWidget", u"Data", None))
#if QT_CONFIG(tooltip)
        self.cmdLoad.setToolTip(QCoreApplication.translate("DataLoadWidget", u"<html><head/><body><p><span style=\" font-size:8pt;\">Load a file with data</span></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cmdLoad.setText(QCoreApplication.translate("DataLoadWidget", u"Load data", None))
#if QT_CONFIG(shortcut)
        self.cmdLoad.setShortcut(QCoreApplication.translate("DataLoadWidget", u"Ctrl+R", None))
#endif // QT_CONFIG(shortcut)
        self.cmdDeleteData.setText(QCoreApplication.translate("DataLoadWidget", u"Delete Data", None))
        self.cbSelect.setItemText(0, QCoreApplication.translate("DataLoadWidget", u"Select all", None))
        self.cbSelect.setItemText(1, QCoreApplication.translate("DataLoadWidget", u"Unselect all", None))
        self.cbSelect.setItemText(2, QCoreApplication.translate("DataLoadWidget", u"Select all 1D", None))
        self.cbSelect.setItemText(3, QCoreApplication.translate("DataLoadWidget", u"Unselect all 1D", None))
        self.cbSelect.setItemText(4, QCoreApplication.translate("DataLoadWidget", u"Select all 2D", None))
        self.cbSelect.setItemText(5, QCoreApplication.translate("DataLoadWidget", u"Unselect all 2D", None))

#if QT_CONFIG(tooltip)
        self.cmdSendTo.setToolTip(QCoreApplication.translate("DataLoadWidget", u"<html><head/><body><p><span style=\" font-size:8pt;\">Send data to a new tab</span></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cmdSendTo.setText(QCoreApplication.translate("DataLoadWidget", u"    Send to", None))
        self.cbFitting.setItemText(0, QCoreApplication.translate("DataLoadWidget", u"Fitting", None))
        self.cbFitting.setItemText(1, QCoreApplication.translate("DataLoadWidget", u"Pr inversion", None))
        self.cbFitting.setItemText(2, QCoreApplication.translate("DataLoadWidget", u"Invariant", None))

        self.chkBatch.setText(QCoreApplication.translate("DataLoadWidget", u"Batch mode", None))
        self.chkSwap.setText(QCoreApplication.translate("DataLoadWidget", u"Swap data", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("DataLoadWidget", u"Plot", None))
        self.cmdNew.setText(QCoreApplication.translate("DataLoadWidget", u"Create New", None))
        self.cmdAppend.setText(QCoreApplication.translate("DataLoadWidget", u"Append to", None))
        self.cmdHelp.setText(QCoreApplication.translate("DataLoadWidget", u"Help", None))
        DataLoadWidget.setTabText(DataLoadWidget.indexOf(self.dataTab), QCoreApplication.translate("DataLoadWidget", u"Data", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("DataLoadWidget", u"Theory", None))
        self.cmdFreeze.setText(QCoreApplication.translate("DataLoadWidget", u"Freeze Theory", None))
        self.cmdDeleteTheory.setText(QCoreApplication.translate("DataLoadWidget", u"Delete", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("DataLoadWidget", u"Plot", None))
        self.cmdNew_2.setText(QCoreApplication.translate("DataLoadWidget", u"Create New", None))
        self.cmdAppend_2.setText(QCoreApplication.translate("DataLoadWidget", u"Append to", None))
        self.cbgraph_2.setItemText(0, QCoreApplication.translate("DataLoadWidget", u"Graph1", None))

        self.cmdHelp_2.setText(QCoreApplication.translate("DataLoadWidget", u"Help", None))
        DataLoadWidget.setTabText(DataLoadWidget.indexOf(self.theoryTab), QCoreApplication.translate("DataLoadWidget", u"Theory", None))
    # retranslateUi

