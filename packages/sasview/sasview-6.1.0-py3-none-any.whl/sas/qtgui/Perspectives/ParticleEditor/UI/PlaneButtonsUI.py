# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PlaneButtonsUI.ui'
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

class Ui_PlaneSelection(object):
    def setupUi(self, PlaneSelection):
        if not PlaneSelection.objectName():
            PlaneSelection.setObjectName(u"PlaneSelection")
        PlaneSelection.resize(100, 19)
        self.horizontalLayout = QHBoxLayout(PlaneSelection)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.selectXY = QPushButton(PlaneSelection)
        self.selectXY.setObjectName(u"selectXY")
        self.selectXY.setMinimumSize(QSize(30, 0))

        self.horizontalLayout.addWidget(self.selectXY)

        self.selectYZ = QPushButton(PlaneSelection)
        self.selectYZ.setObjectName(u"selectYZ")
        self.selectYZ.setMinimumSize(QSize(30, 0))

        self.horizontalLayout.addWidget(self.selectYZ)

        self.selectXZ = QPushButton(PlaneSelection)
        self.selectXZ.setObjectName(u"selectXZ")
        self.selectXZ.setMinimumSize(QSize(30, 0))

        self.horizontalLayout.addWidget(self.selectXZ)


        self.retranslateUi(PlaneSelection)

        QMetaObject.connectSlotsByName(PlaneSelection)
    # setupUi

    def retranslateUi(self, PlaneSelection):
        PlaneSelection.setWindowTitle(QCoreApplication.translate("PlaneSelection", u"Form", None))
        self.selectXY.setText(QCoreApplication.translate("PlaneSelection", u"XY", None))
        self.selectYZ.setText(QCoreApplication.translate("PlaneSelection", u"YZ", None))
        self.selectXZ.setText(QCoreApplication.translate("PlaneSelection", u"XZ", None))
    # retranslateUi

