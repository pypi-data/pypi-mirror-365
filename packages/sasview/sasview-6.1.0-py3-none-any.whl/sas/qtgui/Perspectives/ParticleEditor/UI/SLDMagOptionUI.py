# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SLDMagOptionUI.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QRadioButton, QSizePolicy,
    QWidget)

class Ui_SLDMagnetismOption(object):
    def setupUi(self, SLDMagnetismOption):
        if not SLDMagnetismOption.objectName():
            SLDMagnetismOption.setObjectName(u"SLDMagnetismOption")
        SLDMagnetismOption.resize(104, 16)
        self.horizontalLayout = QHBoxLayout(SLDMagnetismOption)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.sldOption = QRadioButton(SLDMagnetismOption)
        self.sldOption.setObjectName(u"sldOption")
        self.sldOption.setChecked(True)

        self.horizontalLayout.addWidget(self.sldOption)

        self.magnetismOption = QRadioButton(SLDMagnetismOption)
        self.magnetismOption.setObjectName(u"magnetismOption")

        self.horizontalLayout.addWidget(self.magnetismOption)


        self.retranslateUi(SLDMagnetismOption)

        QMetaObject.connectSlotsByName(SLDMagnetismOption)
    # setupUi

    def retranslateUi(self, SLDMagnetismOption):
        SLDMagnetismOption.setWindowTitle(QCoreApplication.translate("SLDMagnetismOption", u"Form", None))
        self.sldOption.setText(QCoreApplication.translate("SLDMagnetismOption", u"SLD", None))
        self.magnetismOption.setText(QCoreApplication.translate("SLDMagnetismOption", u"Magnetism", None))
    # retranslateUi

