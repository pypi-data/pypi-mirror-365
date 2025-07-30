# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'AxisButtonsUI.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QPushButton, QSizePolicy,
    QWidget)

class Ui_AxisSelection(object):
    def setupUi(self, AxisSelection):
        if not AxisSelection.objectName():
            AxisSelection.setObjectName(u"AxisSelection")
        AxisSelection.resize(100, 19)
        self.horizontalLayout = QHBoxLayout(AxisSelection)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.selectX = QPushButton(AxisSelection)
        self.selectX.setObjectName(u"selectX")
        self.selectX.setMinimumSize(QSize(30, 0))

        self.horizontalLayout.addWidget(self.selectX)

        self.selectY = QPushButton(AxisSelection)
        self.selectY.setObjectName(u"selectY")
        self.selectY.setMinimumSize(QSize(30, 0))

        self.horizontalLayout.addWidget(self.selectY)

        self.selectZ = QPushButton(AxisSelection)
        self.selectZ.setObjectName(u"selectZ")
        self.selectZ.setMinimumSize(QSize(30, 0))

        self.horizontalLayout.addWidget(self.selectZ)


        self.retranslateUi(AxisSelection)

        QMetaObject.connectSlotsByName(AxisSelection)
    # setupUi

    def retranslateUi(self, AxisSelection):
        AxisSelection.setWindowTitle(QCoreApplication.translate("AxisSelection", u"Form", None))
        self.selectX.setText(QCoreApplication.translate("AxisSelection", u"X", None))
        self.selectY.setText(QCoreApplication.translate("AxisSelection", u"Y", None))
        self.selectZ.setText(QCoreApplication.translate("AxisSelection", u"Z", None))
    # retranslateUi

