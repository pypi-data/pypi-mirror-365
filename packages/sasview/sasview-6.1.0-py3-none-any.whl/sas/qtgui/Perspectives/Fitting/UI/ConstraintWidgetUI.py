# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ConstraintWidgetUI.ui'
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
    QPushButton, QRadioButton, QSizePolicy, QSpacerItem,
    QTableWidget, QTableWidgetItem, QWidget)

class Ui_ConstraintWidgetUI(object):
    def setupUi(self, ConstraintWidgetUI):
        if not ConstraintWidgetUI.objectName():
            ConstraintWidgetUI.setObjectName(u"ConstraintWidgetUI")
        ConstraintWidgetUI.resize(597, 607)
        self.gridLayout_4 = QGridLayout(ConstraintWidgetUI)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.groupBox = QGroupBox(ConstraintWidgetUI)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_3 = QGridLayout(self.groupBox)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.btnSingle = QRadioButton(self.groupBox)
        self.btnSingle.setObjectName(u"btnSingle")
        self.btnSingle.setChecked(True)

        self.gridLayout_2.addWidget(self.btnSingle, 0, 0, 1, 1)

        self.btnBatch = QRadioButton(self.groupBox)
        self.btnBatch.setObjectName(u"btnBatch")

        self.gridLayout_2.addWidget(self.btnBatch, 0, 1, 1, 1)

        self.chkWeight = QCheckBox(self.groupBox)
        self.chkWeight.setObjectName(u"chkWeight")

        self.gridLayout_2.addWidget(self.chkWeight, 0, 2, 1, 1)

        self.chkChain = QCheckBox(self.groupBox)
        self.chkChain.setObjectName(u"chkChain")

        self.gridLayout_2.addWidget(self.chkChain, 0, 3, 1, 1)

        self.horizontalSpacer = QSpacerItem(160, 13, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer, 0, 4, 1, 1)


        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 0, 1, 1)

        self.tblLayout = QHBoxLayout()
        self.tblLayout.setObjectName(u"tblLayout")

        self.gridLayout_3.addLayout(self.tblLayout, 1, 0, 1, 1)


        self.gridLayout_4.addWidget(self.groupBox, 0, 0, 1, 1)

        self.groupBox_2 = QGroupBox(ConstraintWidgetUI)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout = QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.groupBox_2)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.cbCases = QComboBox(self.groupBox_2)
        self.cbCases.addItem("")
        self.cbCases.setObjectName(u"cbCases")

        self.horizontalLayout.addWidget(self.cbCases)


        self.horizontalLayout_4.addLayout(self.horizontalLayout)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_3)

        self.cmdAdd = QPushButton(self.groupBox_2)
        self.cmdAdd.setObjectName(u"cmdAdd")

        self.horizontalLayout_4.addWidget(self.cmdAdd)


        self.gridLayout.addLayout(self.horizontalLayout_4, 0, 0, 1, 1)

        self.tblConstraints = QTableWidget(self.groupBox_2)
        if (self.tblConstraints.columnCount() < 1):
            self.tblConstraints.setColumnCount(1)
        __qtablewidgetitem = QTableWidgetItem()
        self.tblConstraints.setHorizontalHeaderItem(0, __qtablewidgetitem)
        self.tblConstraints.setObjectName(u"tblConstraints")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tblConstraints.sizePolicy().hasHeightForWidth())
        self.tblConstraints.setSizePolicy(sizePolicy)
        self.tblConstraints.setContextMenuPolicy(Qt.ActionsContextMenu)

        self.gridLayout.addWidget(self.tblConstraints, 1, 0, 1, 1)


        self.gridLayout_4.addWidget(self.groupBox_2, 1, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_2 = QSpacerItem(273, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.cmdFit = QPushButton(ConstraintWidgetUI)
        self.cmdFit.setObjectName(u"cmdFit")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.cmdFit.sizePolicy().hasHeightForWidth())
        self.cmdFit.setSizePolicy(sizePolicy1)
        self.cmdFit.setMinimumSize(QSize(75, 23))

        self.horizontalLayout_3.addWidget(self.cmdFit)

        self.cmdHelp = QPushButton(ConstraintWidgetUI)
        self.cmdHelp.setObjectName(u"cmdHelp")
        sizePolicy1.setHeightForWidth(self.cmdHelp.sizePolicy().hasHeightForWidth())
        self.cmdHelp.setSizePolicy(sizePolicy1)
        self.cmdHelp.setMinimumSize(QSize(75, 23))

        self.horizontalLayout_3.addWidget(self.cmdHelp)


        self.gridLayout_4.addLayout(self.horizontalLayout_3, 2, 0, 1, 1)

        QWidget.setTabOrder(self.btnSingle, self.btnBatch)
        QWidget.setTabOrder(self.btnBatch, self.chkWeight)
        QWidget.setTabOrder(self.chkWeight, self.chkChain)
        QWidget.setTabOrder(self.chkChain, self.cbCases)
        QWidget.setTabOrder(self.cbCases, self.cmdAdd)
        QWidget.setTabOrder(self.cmdAdd, self.tblConstraints)
        QWidget.setTabOrder(self.tblConstraints, self.cmdFit)
        QWidget.setTabOrder(self.cmdFit, self.cmdHelp)

        self.retranslateUi(ConstraintWidgetUI)

        QMetaObject.connectSlotsByName(ConstraintWidgetUI)
    # setupUi

    def retranslateUi(self, ConstraintWidgetUI):
        ConstraintWidgetUI.setWindowTitle(QCoreApplication.translate("ConstraintWidgetUI", u"Constrained and Simultaneous Fit", None))
        self.groupBox.setTitle(QCoreApplication.translate("ConstraintWidgetUI", u"Source choice for simultaneous fitting", None))
        self.btnSingle.setText(QCoreApplication.translate("ConstraintWidgetUI", u"Single fits", None))
        self.btnBatch.setText(QCoreApplication.translate("ConstraintWidgetUI", u"Batch fits", None))
        self.chkWeight.setText(QCoreApplication.translate("ConstraintWidgetUI", u"Modify weighting", None))
        self.chkChain.setText(QCoreApplication.translate("ConstraintWidgetUI", u"Chained fit", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("ConstraintWidgetUI", u"Constraints", None))
        self.label.setText(QCoreApplication.translate("ConstraintWidgetUI", u"Special cases", None))
        self.cbCases.setItemText(0, QCoreApplication.translate("ConstraintWidgetUI", u"None", None))

#if QT_CONFIG(tooltip)
        self.cmdAdd.setToolTip(QCoreApplication.translate("ConstraintWidgetUI", u"Define constraints between two fit pages.", None))
#endif // QT_CONFIG(tooltip)
        self.cmdAdd.setText(QCoreApplication.translate("ConstraintWidgetUI", u"Add constraints", None))
#if QT_CONFIG(tooltip)
        self.cmdFit.setToolTip(QCoreApplication.translate("ConstraintWidgetUI", u"Perform simultaneous fitting of selected fit pages.", None))
#endif // QT_CONFIG(tooltip)
        self.cmdFit.setText(QCoreApplication.translate("ConstraintWidgetUI", u"Fit", None))
#if QT_CONFIG(tooltip)
        self.cmdHelp.setToolTip(QCoreApplication.translate("ConstraintWidgetUI", u"Display help on constrained and simultaneous fitting.", None))
#endif // QT_CONFIG(tooltip)
        self.cmdHelp.setText(QCoreApplication.translate("ConstraintWidgetUI", u"Help", None))
    # retranslateUi

