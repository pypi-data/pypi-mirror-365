# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ConstraintsUI.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QSizePolicy, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_Constraints(object):
    def setupUi(self, Constraints):
        if not Constraints.objectName():
            Constraints.setObjectName(u"Constraints")
        Constraints.resize(800, 620)
        Constraints.setMinimumSize(QSize(763, 620))
        self.gridLayout_2 = QGridLayout(Constraints)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, -1, 10, -1)
        self.textEdit_2 = QTextEdit(Constraints)
        self.textEdit_2.setObjectName(u"textEdit_2")
        self.textEdit_2.setMinimumSize(QSize(0, 100))
        self.textEdit_2.setMaximumSize(QSize(16777215, 150))

        self.verticalLayout.addWidget(self.textEdit_2)


        self.gridLayout_2.addLayout(self.verticalLayout, 0, 0, 1, 1)


        self.retranslateUi(Constraints)

        QMetaObject.connectSlotsByName(Constraints)
    # setupUi

    def retranslateUi(self, Constraints):
        Constraints.setWindowTitle(QCoreApplication.translate("Constraints", u"Shape2SAS", None))
    # retranslateUi

