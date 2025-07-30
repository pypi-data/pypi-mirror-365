# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ChangeCategoryUI.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QDialog,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QPushButton,
    QRadioButton, QSizePolicy, QSpacerItem, QWidget)

class Ui_ChangeCategoryUI(object):
    def setupUi(self, ChangeCategoryUI):
        if not ChangeCategoryUI.objectName():
            ChangeCategoryUI.setObjectName(u"ChangeCategoryUI")
        ChangeCategoryUI.resize(357, 485)
        self.gridLayout_2 = QGridLayout(ChangeCategoryUI)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.lblTitle = QLabel(ChangeCategoryUI)
        self.lblTitle.setObjectName(u"lblTitle")

        self.gridLayout_2.addWidget(self.lblTitle, 0, 0, 1, 1)

        self.lstCategories = QListWidget(ChangeCategoryUI)
        self.lstCategories.setObjectName(u"lstCategories")
        self.lstCategories.setSelectionMode(QAbstractItemView.MultiSelection)
        self.lstCategories.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.gridLayout_2.addWidget(self.lstCategories, 1, 0, 1, 1)

        self.groupBox = QGroupBox(ChangeCategoryUI)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.rbExisting = QRadioButton(self.groupBox)
        self.rbExisting.setObjectName(u"rbExisting")

        self.gridLayout.addWidget(self.rbExisting, 0, 0, 1, 1)

        self.txtNewCategory = QLineEdit(self.groupBox)
        self.txtNewCategory.setObjectName(u"txtNewCategory")

        self.gridLayout.addWidget(self.txtNewCategory, 1, 1, 1, 2)

        self.cbCategories = QComboBox(self.groupBox)
        self.cbCategories.setObjectName(u"cbCategories")

        self.gridLayout.addWidget(self.cbCategories, 0, 1, 1, 2)

        self.rbNew = QRadioButton(self.groupBox)
        self.rbNew.setObjectName(u"rbNew")

        self.gridLayout.addWidget(self.rbNew, 1, 0, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(208, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 2, 0, 1, 2)

        self.cmdAdd = QPushButton(self.groupBox)
        self.cmdAdd.setObjectName(u"cmdAdd")

        self.gridLayout.addWidget(self.cmdAdd, 2, 2, 1, 1)

        self.cbCategories.raise_()
        self.txtNewCategory.raise_()
        self.cmdAdd.raise_()
        self.rbNew.raise_()
        self.rbExisting.raise_()

        self.gridLayout_2.addWidget(self.groupBox, 2, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.cmdRemove = QPushButton(ChangeCategoryUI)
        self.cmdRemove.setObjectName(u"cmdRemove")

        self.horizontalLayout.addWidget(self.cmdRemove)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.cmdOK = QPushButton(ChangeCategoryUI)
        self.cmdOK.setObjectName(u"cmdOK")

        self.horizontalLayout.addWidget(self.cmdOK)

        self.cmdCancel = QPushButton(ChangeCategoryUI)
        self.cmdCancel.setObjectName(u"cmdCancel")

        self.horizontalLayout.addWidget(self.cmdCancel)


        self.gridLayout_2.addLayout(self.horizontalLayout, 3, 0, 1, 1)

        QWidget.setTabOrder(self.lstCategories, self.rbExisting)
        QWidget.setTabOrder(self.rbExisting, self.cbCategories)
        QWidget.setTabOrder(self.cbCategories, self.rbNew)
        QWidget.setTabOrder(self.rbNew, self.txtNewCategory)
        QWidget.setTabOrder(self.txtNewCategory, self.cmdAdd)
        QWidget.setTabOrder(self.cmdAdd, self.cmdRemove)
        QWidget.setTabOrder(self.cmdRemove, self.cmdOK)
        QWidget.setTabOrder(self.cmdOK, self.cmdCancel)

        self.retranslateUi(ChangeCategoryUI)

        QMetaObject.connectSlotsByName(ChangeCategoryUI)
    # setupUi

    def retranslateUi(self, ChangeCategoryUI):
        ChangeCategoryUI.setWindowTitle(QCoreApplication.translate("ChangeCategoryUI", u"Change Category:", None))
        self.lblTitle.setText(QCoreApplication.translate("ChangeCategoryUI", u"Current categories for ", None))
        self.groupBox.setTitle(QCoreApplication.translate("ChangeCategoryUI", u"Add Category", None))
        self.rbExisting.setText(QCoreApplication.translate("ChangeCategoryUI", u"Choose existing", None))
        self.rbNew.setText(QCoreApplication.translate("ChangeCategoryUI", u"Create new", None))
        self.cmdAdd.setText(QCoreApplication.translate("ChangeCategoryUI", u"Add", None))
        self.cmdRemove.setText(QCoreApplication.translate("ChangeCategoryUI", u"Remove", None))
        self.cmdOK.setText(QCoreApplication.translate("ChangeCategoryUI", u"OK", None))
        self.cmdCancel.setText(QCoreApplication.translate("ChangeCategoryUI", u"Cancel", None))
    # retranslateUi

