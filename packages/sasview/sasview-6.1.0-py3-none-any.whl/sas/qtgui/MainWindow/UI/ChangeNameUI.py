# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ChangeNameUI.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QGridLayout, QGroupBox,
    QHBoxLayout, QLineEdit, QPushButton, QRadioButton,
    QSizePolicy, QSpacerItem, QWidget)

class Ui_ChangeCategoryUI(object):
    def setupUi(self, ChangeCategoryUI):
        if not ChangeCategoryUI.objectName():
            ChangeCategoryUI.setObjectName(u"ChangeCategoryUI")
        ChangeCategoryUI.resize(341, 295)
        ChangeCategoryUI.setMinimumSize(QSize(341, 295))
        self.groupBox = QGroupBox(ChangeCategoryUI)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(11, 11, 321, 211))
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.rbDataName = QRadioButton(self.groupBox)
        self.rbDataName.setObjectName(u"rbDataName")

        self.gridLayout.addWidget(self.rbDataName, 1, 0, 1, 1)

        self.txtFileName = QLineEdit(self.groupBox)
        self.txtFileName.setObjectName(u"txtFileName")

        self.gridLayout.addWidget(self.txtFileName, 2, 2, 1, 1)

        self.txtCurrentName = QLineEdit(self.groupBox)
        self.txtCurrentName.setObjectName(u"txtCurrentName")

        self.gridLayout.addWidget(self.txtCurrentName, 0, 2, 1, 1)

        self.txtDataName = QLineEdit(self.groupBox)
        self.txtDataName.setObjectName(u"txtDataName")

        self.gridLayout.addWidget(self.txtDataName, 1, 2, 1, 1)

        self.rbExisting = QRadioButton(self.groupBox)
        self.rbExisting.setObjectName(u"rbExisting")

        self.gridLayout.addWidget(self.rbExisting, 0, 0, 1, 1)

        self.txtNewCategory = QLineEdit(self.groupBox)
        self.txtNewCategory.setObjectName(u"txtNewCategory")

        self.gridLayout.addWidget(self.txtNewCategory, 3, 2, 1, 1)

        self.rbFileName = QRadioButton(self.groupBox)
        self.rbFileName.setObjectName(u"rbFileName")

        self.gridLayout.addWidget(self.rbFileName, 2, 0, 1, 1)

        self.rbNew = QRadioButton(self.groupBox)
        self.rbNew.setObjectName(u"rbNew")

        self.gridLayout.addWidget(self.rbNew, 3, 0, 1, 1)

        self.txtNewCategory.raise_()
        self.rbNew.raise_()
        self.rbExisting.raise_()
        self.txtCurrentName.raise_()
        self.rbDataName.raise_()
        self.rbFileName.raise_()
        self.txtDataName.raise_()
        self.txtFileName.raise_()
        self.horizontalLayoutWidget = QWidget(ChangeCategoryUI)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(10, 230, 321, 41))
        self.horizontalLayout_2 = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.cmdOK = QPushButton(self.horizontalLayoutWidget)
        self.cmdOK.setObjectName(u"cmdOK")

        self.horizontalLayout_2.addWidget(self.cmdOK)

        self.cmdCancel = QPushButton(self.horizontalLayoutWidget)
        self.cmdCancel.setObjectName(u"cmdCancel")

        self.horizontalLayout_2.addWidget(self.cmdCancel)

        QWidget.setTabOrder(self.rbExisting, self.txtCurrentName)
        QWidget.setTabOrder(self.txtCurrentName, self.rbDataName)
        QWidget.setTabOrder(self.rbDataName, self.txtDataName)
        QWidget.setTabOrder(self.txtDataName, self.rbFileName)
        QWidget.setTabOrder(self.rbFileName, self.txtFileName)
        QWidget.setTabOrder(self.txtFileName, self.rbNew)
        QWidget.setTabOrder(self.rbNew, self.txtNewCategory)
        QWidget.setTabOrder(self.txtNewCategory, self.cmdOK)
        QWidget.setTabOrder(self.cmdOK, self.cmdCancel)

        self.retranslateUi(ChangeCategoryUI)

        QMetaObject.connectSlotsByName(ChangeCategoryUI)
    # setupUi

    def retranslateUi(self, ChangeCategoryUI):
        ChangeCategoryUI.setWindowTitle(QCoreApplication.translate("ChangeCategoryUI", u"Change Category:", None))
        self.groupBox.setTitle(QCoreApplication.translate("ChangeCategoryUI", u"Change Display Name", None))
        self.rbDataName.setText(QCoreApplication.translate("ChangeCategoryUI", u"Data name", None))
        self.rbExisting.setText(QCoreApplication.translate("ChangeCategoryUI", u"Current name", None))
        self.rbFileName.setText(QCoreApplication.translate("ChangeCategoryUI", u"File name", None))
        self.rbNew.setText(QCoreApplication.translate("ChangeCategoryUI", u"Create new", None))
        self.cmdOK.setText(QCoreApplication.translate("ChangeCategoryUI", u"OK", None))
        self.cmdCancel.setText(QCoreApplication.translate("ChangeCategoryUI", u"Cancel", None))
    # retranslateUi

