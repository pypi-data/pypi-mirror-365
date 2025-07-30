# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ButtonOptionsUI.ui'
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

class Ui_ButtonOptions(object):
    def setupUi(self, ButtonOptions):
        if not ButtonOptions.objectName():
            ButtonOptions.setObjectName(u"ButtonOptions")
        ButtonOptions.resize(800, 26)
        self.gridLayout = QGridLayout(ButtonOptions)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalSpacer_49 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_49)

        self.reset = QPushButton(ButtonOptions)
        self.reset.setObjectName(u"reset")
        self.reset.setMinimumSize(QSize(75, 24))

        self.horizontalLayout_5.addWidget(self.reset)

        self.closePage = QPushButton(ButtonOptions)
        self.closePage.setObjectName(u"closePage")
        self.closePage.setMinimumSize(QSize(75, 24))

        self.horizontalLayout_5.addWidget(self.closePage)

        self.help = QPushButton(ButtonOptions)
        self.help.setObjectName(u"help")
        self.help.setMinimumSize(QSize(75, 24))

        self.horizontalLayout_5.addWidget(self.help)


        self.gridLayout.addLayout(self.horizontalLayout_5, 0, 0, 1, 1)


        self.retranslateUi(ButtonOptions)

        QMetaObject.connectSlotsByName(ButtonOptions)
    # setupUi

    def retranslateUi(self, ButtonOptions):
        ButtonOptions.setWindowTitle(QCoreApplication.translate("ButtonOptions", u"ButtonOptions", None))
        self.reset.setText(QCoreApplication.translate("ButtonOptions", u"Reset", None))
        self.closePage.setText(QCoreApplication.translate("ButtonOptions", u"Close", None))
        self.help.setText(QCoreApplication.translate("ButtonOptions", u"Help", None))
    # retranslateUi

