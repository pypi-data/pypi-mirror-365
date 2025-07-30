# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'AddTextUI.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QGridLayout, QGroupBox, QHBoxLayout, QPushButton,
    QSizePolicy, QSpacerItem, QTextEdit, QWidget)

class Ui_AddText(object):
    def setupUi(self, AddText):
        if not AddText.objectName():
            AddText.setObjectName(u"AddText")
        AddText.setWindowModality(Qt.ApplicationModal)
        AddText.resize(432, 324)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AddText.sizePolicy().hasHeightForWidth())
        AddText.setSizePolicy(sizePolicy)
        self.gridLayout_2 = QGridLayout(AddText)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.groupBox = QGroupBox(AddText)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy1)
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.textEdit = QTextEdit(self.groupBox)
        self.textEdit.setObjectName(u"textEdit")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.textEdit.sizePolicy().hasHeightForWidth())
        self.textEdit.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.textEdit, 0, 0, 1, 1)


        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 44, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer, 1, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.btnFont = QPushButton(AddText)
        self.btnFont.setObjectName(u"btnFont")

        self.horizontalLayout.addWidget(self.btnFont)

        self.btnColor = QPushButton(AddText)
        self.btnColor.setObjectName(u"btnColor")

        self.horizontalLayout.addWidget(self.btnColor)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.buttonBox = QDialogButtonBox(AddText)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.horizontalLayout.addWidget(self.buttonBox)


        self.gridLayout_2.addLayout(self.horizontalLayout, 2, 0, 1, 1)


        self.retranslateUi(AddText)
        self.buttonBox.accepted.connect(AddText.accept)
        self.buttonBox.rejected.connect(AddText.reject)

        QMetaObject.connectSlotsByName(AddText)
    # setupUi

    def retranslateUi(self, AddText):
        AddText.setWindowTitle(QCoreApplication.translate("AddText", u"Add Text", None))
        self.groupBox.setTitle(QCoreApplication.translate("AddText", u"Custom Text ", None))
        self.btnFont.setText(QCoreApplication.translate("AddText", u"Font...", None))
        self.btnColor.setText(QCoreApplication.translate("AddText", u"Color...", None))
    # retranslateUi

