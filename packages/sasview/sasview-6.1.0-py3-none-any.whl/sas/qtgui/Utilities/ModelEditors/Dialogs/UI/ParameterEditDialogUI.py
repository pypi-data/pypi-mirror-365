# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ParameterEditDialogUI.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QSpacerItem,
    QTableWidget, QTableWidgetItem, QWidget)

class Ui_ParameterEditDialog(object):
    def setupUi(self, ParameterEditDialog):
        if not ParameterEditDialog.objectName():
            ParameterEditDialog.setObjectName(u"ParameterEditDialog")
        ParameterEditDialog.resize(400, 300)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ParameterEditDialog.sizePolicy().hasHeightForWidth())
        ParameterEditDialog.setSizePolicy(sizePolicy)
        ParameterEditDialog.setMaximumSize(QSize(16777215, 300))
        self.gridLayout_3 = QGridLayout(ParameterEditDialog)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.groupBox = QGroupBox(ParameterEditDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.txtName = QLineEdit(self.groupBox)
        self.txtName.setObjectName(u"txtName")
        self.txtName.setMinimumSize(QSize(0, 0))

        self.horizontalLayout.addWidget(self.txtName)


        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 0, 1, 1)


        self.gridLayout_3.addWidget(self.groupBox, 0, 0, 1, 1)

        self.frame = QFrame(ParameterEditDialog)
        self.frame.setObjectName(u"frame")
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.gridLayout = QGridLayout(self.frame)
        self.gridLayout.setObjectName(u"gridLayout")
        self.valuesTable = QTableWidget(self.frame)
        if (self.valuesTable.columnCount() < 2):
            self.valuesTable.setColumnCount(2)
        if (self.valuesTable.rowCount() < 6):
            self.valuesTable.setRowCount(6)
        __qtablewidgetitem = QTableWidgetItem()
        __qtablewidgetitem.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem.setFlags(Qt.ItemIsSelectable|Qt.ItemIsDragEnabled|Qt.ItemIsDropEnabled|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled);
        self.valuesTable.setItem(0, 0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.valuesTable.setItem(0, 1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        __qtablewidgetitem2.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem2.setFlags(Qt.ItemIsSelectable|Qt.ItemIsDragEnabled|Qt.ItemIsDropEnabled|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled);
        self.valuesTable.setItem(1, 0, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.valuesTable.setItem(1, 1, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        __qtablewidgetitem4.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem4.setFlags(Qt.ItemIsSelectable|Qt.ItemIsDragEnabled|Qt.ItemIsDropEnabled|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled);
        self.valuesTable.setItem(2, 0, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.valuesTable.setItem(2, 1, __qtablewidgetitem5)
        font = QFont()
        font.setBold(False)
        __qtablewidgetitem6 = QTableWidgetItem()
        __qtablewidgetitem6.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem6.setFont(font);
        __qtablewidgetitem6.setFlags(Qt.ItemIsSelectable|Qt.ItemIsDragEnabled|Qt.ItemIsDropEnabled|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled);
        self.valuesTable.setItem(3, 0, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.valuesTable.setItem(3, 1, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        __qtablewidgetitem8.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem8.setFont(font);
        __qtablewidgetitem8.setFlags(Qt.ItemIsSelectable|Qt.ItemIsDragEnabled|Qt.ItemIsDropEnabled|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled);
        self.valuesTable.setItem(4, 0, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.valuesTable.setItem(4, 1, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        __qtablewidgetitem10.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem10.setFont(font);
        __qtablewidgetitem10.setFlags(Qt.ItemIsSelectable|Qt.ItemIsDragEnabled|Qt.ItemIsDropEnabled|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled);
        self.valuesTable.setItem(5, 0, __qtablewidgetitem10)
        self.valuesTable.setObjectName(u"valuesTable")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.valuesTable.sizePolicy().hasHeightForWidth())
        self.valuesTable.setSizePolicy(sizePolicy1)
        self.valuesTable.setSelectionMode(QAbstractItemView.NoSelection)
        self.valuesTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.valuesTable.setTextElideMode(Qt.ElideNone)
        self.valuesTable.setWordWrap(False)
        self.valuesTable.setRowCount(6)
        self.valuesTable.setColumnCount(2)
        self.valuesTable.horizontalHeader().setVisible(False)
        self.valuesTable.horizontalHeader().setCascadingSectionResizes(True)
        self.valuesTable.horizontalHeader().setStretchLastSection(True)
        self.valuesTable.verticalHeader().setVisible(False)
        self.valuesTable.verticalHeader().setCascadingSectionResizes(False)
        self.valuesTable.verticalHeader().setProperty(u"showSortIndicator", False)

        self.gridLayout.addWidget(self.valuesTable, 0, 0, 1, 1)


        self.gridLayout_3.addWidget(self.frame, 1, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.cmdCancel = QPushButton(ParameterEditDialog)
        self.cmdCancel.setObjectName(u"cmdCancel")

        self.horizontalLayout_2.addWidget(self.cmdCancel)

        self.cmdSave = QPushButton(ParameterEditDialog)
        self.cmdSave.setObjectName(u"cmdSave")

        self.horizontalLayout_2.addWidget(self.cmdSave)


        self.gridLayout_3.addLayout(self.horizontalLayout_2, 2, 0, 1, 1)


        self.retranslateUi(ParameterEditDialog)

        QMetaObject.connectSlotsByName(ParameterEditDialog)
    # setupUi

    def retranslateUi(self, ParameterEditDialog):
        ParameterEditDialog.setWindowTitle(QCoreApplication.translate("ParameterEditDialog", u"New Parameter", None))
        self.groupBox.setTitle(QCoreApplication.translate("ParameterEditDialog", u"Parameter Definition", None))
        self.label.setText(QCoreApplication.translate("ParameterEditDialog", u"Parameter Name", None))

        __sortingEnabled = self.valuesTable.isSortingEnabled()
        self.valuesTable.setSortingEnabled(False)
        ___qtablewidgetitem = self.valuesTable.item(0, 0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("ParameterEditDialog", u"Default Value", None));
        ___qtablewidgetitem1 = self.valuesTable.item(0, 1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("ParameterEditDialog", u"0", None));
        ___qtablewidgetitem2 = self.valuesTable.item(1, 0)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("ParameterEditDialog", u"Minimum", None));
        ___qtablewidgetitem3 = self.valuesTable.item(1, 1)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("ParameterEditDialog", u"-inf", None));
        ___qtablewidgetitem4 = self.valuesTable.item(2, 0)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("ParameterEditDialog", u"Maximum", None));
        ___qtablewidgetitem5 = self.valuesTable.item(2, 1)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("ParameterEditDialog", u"inf", None));
        ___qtablewidgetitem6 = self.valuesTable.item(3, 0)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("ParameterEditDialog", u"Units", None));
        ___qtablewidgetitem7 = self.valuesTable.item(4, 0)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("ParameterEditDialog", u"Type", None));
        ___qtablewidgetitem8 = self.valuesTable.item(5, 0)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("ParameterEditDialog", u"Description", None));
        self.valuesTable.setSortingEnabled(__sortingEnabled)

        self.cmdCancel.setText(QCoreApplication.translate("ParameterEditDialog", u"Cancel", None))
        self.cmdSave.setText(QCoreApplication.translate("ParameterEditDialog", u"Save", None))
    # retranslateUi

