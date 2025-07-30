# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ViewerButtonsUI.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QPushButton,
    QSizePolicy, QSpacerItem, QWidget)

class Ui_ViewerButtons(object):
    def setupUi(self, ViewerButtons):
        if not ViewerButtons.objectName():
            ViewerButtons.setObjectName(u"ViewerButtons")
        ViewerButtons.resize(280, 26)
        ViewerButtons.setMinimumSize(QSize(280, 24))
        ViewerButtons.setMaximumSize(QSize(280, 26))
        self.gridLayout = QGridLayout(ViewerButtons)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer_5 = QSpacerItem(20, 24, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_5)

        self.pushButton_2 = QPushButton(ViewerButtons)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setMinimumSize(QSize(70, 24))
        self.pushButton_2.setMaximumSize(QSize(70, 24))

        self.horizontalLayout_2.addWidget(self.pushButton_2)

        self.pushButton_3 = QPushButton(ViewerButtons)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setMinimumSize(QSize(70, 24))
        self.pushButton_3.setMaximumSize(QSize(70, 24))

        self.horizontalLayout_2.addWidget(self.pushButton_3)

        self.pushButton = QPushButton(ViewerButtons)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setMinimumSize(QSize(70, 24))
        self.pushButton.setMaximumSize(QSize(70, 24))

        self.horizontalLayout_2.addWidget(self.pushButton)

        self.horizontalSpacer_6 = QSpacerItem(20, 24, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_6)


        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)


        self.retranslateUi(ViewerButtons)

        QMetaObject.connectSlotsByName(ViewerButtons)
    # setupUi

    def retranslateUi(self, ViewerButtons):
        ViewerButtons.setWindowTitle(QCoreApplication.translate("ViewerButtons", u"ViewerButtons", None))
        self.pushButton_2.setText(QCoreApplication.translate("ViewerButtons", u"XY", None))
        self.pushButton_3.setText(QCoreApplication.translate("ViewerButtons", u"YZ", None))
        self.pushButton.setText(QCoreApplication.translate("ViewerButtons", u"ZY", None))
    # retranslateUi

