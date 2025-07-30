# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ModelSelectorUI.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
    QHeaderView, QLabel, QPushButton, QSizePolicy,
    QSpacerItem, QTreeWidget, QTreeWidgetItem, QWidget)

class Ui_ModelSelector(object):
    def setupUi(self, ModelSelector):
        if not ModelSelector.objectName():
            ModelSelector.setObjectName(u"ModelSelector")
        ModelSelector.resize(420, 300)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ModelSelector.sizePolicy().hasHeightForWidth())
        ModelSelector.setSizePolicy(sizePolicy)
        ModelSelector.setMaximumSize(QSize(420, 16777215))
        self.gridLayout_2 = QGridLayout(ModelSelector)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.frame = QFrame(ModelSelector)
        self.frame.setObjectName(u"frame")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy1)
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.gridLayout = QGridLayout(self.frame)
        self.gridLayout.setObjectName(u"gridLayout")
        self.modelTree = QTreeWidget(self.frame)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1");
        self.modelTree.setHeaderItem(__qtreewidgetitem)
        self.modelTree.setObjectName(u"modelTree")
        sizePolicy1.setHeightForWidth(self.modelTree.sizePolicy().hasHeightForWidth())
        self.modelTree.setSizePolicy(sizePolicy1)
        self.modelTree.header().setVisible(False)

        self.gridLayout.addWidget(self.modelTree, 0, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lblSelection = QLabel(self.frame)
        self.lblSelection.setObjectName(u"lblSelection")

        self.horizontalLayout.addWidget(self.lblSelection)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.cmdCancel = QPushButton(self.frame)
        self.cmdCancel.setObjectName(u"cmdCancel")
        self.cmdCancel.setMinimumSize(QSize(75, 0))

        self.horizontalLayout.addWidget(self.cmdCancel)

        self.cmdLoadModel = QPushButton(self.frame)
        self.cmdLoadModel.setObjectName(u"cmdLoadModel")
        self.cmdLoadModel.setMinimumSize(QSize(100, 0))

        self.horizontalLayout.addWidget(self.cmdLoadModel)


        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)


        self.gridLayout_2.addWidget(self.frame, 0, 0, 1, 1)


        self.retranslateUi(ModelSelector)

        QMetaObject.connectSlotsByName(ModelSelector)
    # setupUi

    def retranslateUi(self, ModelSelector):
        ModelSelector.setWindowTitle(QCoreApplication.translate("ModelSelector", u"Select Model", None))
        self.lblSelection.setText("")
        self.cmdCancel.setText(QCoreApplication.translate("ModelSelector", u"Cancel", None))
        self.cmdLoadModel.setText(QCoreApplication.translate("ModelSelector", u"Load Model", None))
    # retranslateUi

