# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'TabbedFileLoadUI.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QPushButton, QSizePolicy, QSpacerItem, QTabWidget,
    QTreeView, QWidget)

class Ui_DataLoadWidget(object):
    def setupUi(self, DataLoadWidget):
        if not DataLoadWidget.objectName():
            DataLoadWidget.setObjectName(u"DataLoadWidget")
        DataLoadWidget.resize(481, 620)
        icon = QIcon()
        icon.addFile(u":/res/ball.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        DataLoadWidget.setWindowIcon(icon)
        self.dataTab = QWidget()
        self.dataTab.setObjectName(u"dataTab")
        self.gridLayout_6 = QGridLayout(self.dataTab)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.label = QLabel(self.dataTab)
        self.label.setObjectName(u"label")

        self.gridLayout_6.addWidget(self.label, 0, 0, 1, 1)

        self.cbSelect = QComboBox(self.dataTab)
        self.cbSelect.addItem("")
        self.cbSelect.addItem("")
        self.cbSelect.addItem("")
        self.cbSelect.addItem("")
        self.cbSelect.addItem("")
        self.cbSelect.addItem("")
        self.cbSelect.setObjectName(u"cbSelect")

        self.gridLayout_6.addWidget(self.cbSelect, 1, 0, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(352, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_6.addItem(self.horizontalSpacer_2, 1, 1, 1, 2)

        self.groupBox = QGroupBox(self.dataTab)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.treeView = QTreeView(self.groupBox)
        self.treeView.setObjectName(u"treeView")
        self.treeView.header().setVisible(False)

        self.gridLayout.addWidget(self.treeView, 0, 0, 1, 4)

        self.cmdLoad = QPushButton(self.groupBox)
        self.cmdLoad.setObjectName(u"cmdLoad")

        self.gridLayout.addWidget(self.cmdLoad, 1, 0, 1, 1)

        self.cmdFreeze = QPushButton(self.groupBox)
        self.cmdFreeze.setObjectName(u"cmdFreeze")

        self.gridLayout.addWidget(self.cmdFreeze, 1, 1, 1, 1)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_4, 1, 2, 1, 1)

        self.cmdDeleteData = QPushButton(self.groupBox)
        self.cmdDeleteData.setObjectName(u"cmdDeleteData")

        self.gridLayout.addWidget(self.cmdDeleteData, 1, 3, 1, 1)


        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.cmdSendTo = QPushButton(self.groupBox)
        self.cmdSendTo.setObjectName(u"cmdSendTo")

        self.horizontalLayout.addWidget(self.cmdSendTo)

        self.cbFitting = QComboBox(self.groupBox)
        self.cbFitting.addItem("")
        self.cbFitting.addItem("")
        self.cbFitting.addItem("")
        self.cbFitting.setObjectName(u"cbFitting")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbFitting.sizePolicy().hasHeightForWidth())
        self.cbFitting.setSizePolicy(sizePolicy)
        self.cbFitting.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.horizontalLayout.addWidget(self.cbFitting)

        self.chkBatch = QCheckBox(self.groupBox)
        self.chkBatch.setObjectName(u"chkBatch")

        self.horizontalLayout.addWidget(self.chkBatch)

        self.horizontalSpacer = QSpacerItem(197, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 0, 1, 1)


        self.gridLayout_6.addWidget(self.groupBox, 2, 0, 1, 3)

        self.groupBox_3 = QGroupBox(self.dataTab)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.gridLayout_3 = QGridLayout(self.groupBox_3)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.cmdNew = QPushButton(self.groupBox_3)
        self.cmdNew.setObjectName(u"cmdNew")

        self.gridLayout_3.addWidget(self.cmdNew, 0, 0, 1, 1)

        self.cmdAppend = QPushButton(self.groupBox_3)
        self.cmdAppend.setObjectName(u"cmdAppend")

        self.gridLayout_3.addWidget(self.cmdAppend, 1, 0, 1, 1)

        self.cbgraph = QComboBox(self.groupBox_3)
        self.cbgraph.addItem("")
        self.cbgraph.setObjectName(u"cbgraph")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.cbgraph.sizePolicy().hasHeightForWidth())
        self.cbgraph.setSizePolicy(sizePolicy1)
        self.cbgraph.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.gridLayout_3.addWidget(self.cbgraph, 1, 1, 1, 1)


        self.gridLayout_6.addWidget(self.groupBox_3, 3, 0, 1, 2)

        self.horizontalSpacer_3 = QSpacerItem(287, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_6.addItem(self.horizontalSpacer_3, 3, 2, 1, 1)

        DataLoadWidget.addTab(self.dataTab, "")
        self.theoryTab = QWidget()
        self.theoryTab.setObjectName(u"theoryTab")
        self.gridLayout_7 = QGridLayout(self.theoryTab)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.groupBox_2 = QGroupBox(self.theoryTab)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_4 = QGridLayout(self.groupBox_2)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.cmdDeleteTheory = QPushButton(self.groupBox_2)
        self.cmdDeleteTheory.setObjectName(u"cmdDeleteTheory")

        self.gridLayout_4.addWidget(self.cmdDeleteTheory, 1, 0, 1, 1)

        self.horizontalSpacer_5 = QSpacerItem(353, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_5, 1, 1, 1, 1)

        self.freezeView = QTreeView(self.groupBox_2)
        self.freezeView.setObjectName(u"freezeView")
        self.freezeView.header().setVisible(False)

        self.gridLayout_4.addWidget(self.freezeView, 0, 0, 1, 2)


        self.gridLayout_7.addWidget(self.groupBox_2, 0, 0, 1, 2)

        self.groupBox_4 = QGroupBox(self.theoryTab)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.gridLayout_5 = QGridLayout(self.groupBox_4)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.cmdNew_2 = QPushButton(self.groupBox_4)
        self.cmdNew_2.setObjectName(u"cmdNew_2")

        self.gridLayout_5.addWidget(self.cmdNew_2, 0, 0, 1, 1)

        self.cmdAppend_2 = QPushButton(self.groupBox_4)
        self.cmdAppend_2.setObjectName(u"cmdAppend_2")

        self.gridLayout_5.addWidget(self.cmdAppend_2, 1, 0, 1, 1)

        self.cbgraph_2 = QComboBox(self.groupBox_4)
        self.cbgraph_2.addItem("")
        self.cbgraph_2.setObjectName(u"cbgraph_2")
        sizePolicy1.setHeightForWidth(self.cbgraph_2.sizePolicy().hasHeightForWidth())
        self.cbgraph_2.setSizePolicy(sizePolicy1)
        self.cbgraph_2.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.gridLayout_5.addWidget(self.cbgraph_2, 1, 1, 1, 1)


        self.gridLayout_7.addWidget(self.groupBox_4, 1, 0, 1, 1)

        self.horizontalSpacer_6 = QSpacerItem(287, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_7.addItem(self.horizontalSpacer_6, 1, 1, 1, 1)

        DataLoadWidget.addTab(self.theoryTab, "")

        self.retranslateUi(DataLoadWidget)

        DataLoadWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(DataLoadWidget)
    # setupUi

    def retranslateUi(self, DataLoadWidget):
        DataLoadWidget.setWindowTitle(QCoreApplication.translate("DataLoadWidget", u"TabWidget", None))
        self.label.setText(QCoreApplication.translate("DataLoadWidget", u"Selection Options", None))
        self.cbSelect.setItemText(0, QCoreApplication.translate("DataLoadWidget", u"Select all", None))
        self.cbSelect.setItemText(1, QCoreApplication.translate("DataLoadWidget", u"Unselect all", None))
        self.cbSelect.setItemText(2, QCoreApplication.translate("DataLoadWidget", u"Select all 1D", None))
        self.cbSelect.setItemText(3, QCoreApplication.translate("DataLoadWidget", u"Unselect all 1D", None))
        self.cbSelect.setItemText(4, QCoreApplication.translate("DataLoadWidget", u"Select all 2D", None))
        self.cbSelect.setItemText(5, QCoreApplication.translate("DataLoadWidget", u"Unselect all 2D", None))

        self.groupBox.setTitle(QCoreApplication.translate("DataLoadWidget", u"Data", None))
        self.cmdLoad.setText(QCoreApplication.translate("DataLoadWidget", u"Load", None))
        self.cmdFreeze.setText(QCoreApplication.translate("DataLoadWidget", u"Freeze", None))
        self.cmdDeleteData.setText(QCoreApplication.translate("DataLoadWidget", u"Delete", None))
        self.cmdSendTo.setText(QCoreApplication.translate("DataLoadWidget", u"Send to", None))
        self.cbFitting.setItemText(0, QCoreApplication.translate("DataLoadWidget", u"Fitting", None))
        self.cbFitting.setItemText(1, QCoreApplication.translate("DataLoadWidget", u"Pr inversion", None))
        self.cbFitting.setItemText(2, QCoreApplication.translate("DataLoadWidget", u"Invariant", None))

        self.chkBatch.setText(QCoreApplication.translate("DataLoadWidget", u"Batch mode", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("DataLoadWidget", u"Plot", None))
        self.cmdNew.setText(QCoreApplication.translate("DataLoadWidget", u"New", None))
        self.cmdAppend.setText(QCoreApplication.translate("DataLoadWidget", u"Append to", None))
        self.cbgraph.setItemText(0, QCoreApplication.translate("DataLoadWidget", u"Graph1", None))

        DataLoadWidget.setTabText(DataLoadWidget.indexOf(self.dataTab), QCoreApplication.translate("DataLoadWidget", u"Data", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("DataLoadWidget", u"Theory", None))
        self.cmdDeleteTheory.setText(QCoreApplication.translate("DataLoadWidget", u"Delete", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("DataLoadWidget", u"Plot", None))
        self.cmdNew_2.setText(QCoreApplication.translate("DataLoadWidget", u"New", None))
        self.cmdAppend_2.setText(QCoreApplication.translate("DataLoadWidget", u"Append to", None))
        self.cbgraph_2.setItemText(0, QCoreApplication.translate("DataLoadWidget", u"Graph1", None))

        DataLoadWidget.setTabText(DataLoadWidget.indexOf(self.theoryTab), QCoreApplication.translate("DataLoadWidget", u"Theory", None))
    # retranslateUi

