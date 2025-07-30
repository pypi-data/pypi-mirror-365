# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ParameterTableButtonsUI.ui'
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
    QSpacerItem, QWidget)

class Ui_ParameterTableButtons(object):
    def setupUi(self, ParameterTableButtons):
        if not ParameterTableButtons.objectName():
            ParameterTableButtons.setObjectName(u"ParameterTableButtons")
        ParameterTableButtons.resize(364, 20)
        self.horizontalLayout = QHBoxLayout(ParameterTableButtons)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, 0, -1, 0)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.cleanButton = QPushButton(ParameterTableButtons)
        self.cleanButton.setObjectName(u"cleanButton")

        self.horizontalLayout.addWidget(self.cleanButton)

        self.scatterButton = QPushButton(ParameterTableButtons)
        self.scatterButton.setObjectName(u"scatterButton")

        self.horizontalLayout.addWidget(self.scatterButton)

        self.seriesButton = QPushButton(ParameterTableButtons)
        self.seriesButton.setObjectName(u"seriesButton")

        self.horizontalLayout.addWidget(self.seriesButton)


        self.retranslateUi(ParameterTableButtons)

        QMetaObject.connectSlotsByName(ParameterTableButtons)
    # setupUi

    def retranslateUi(self, ParameterTableButtons):
        ParameterTableButtons.setWindowTitle(QCoreApplication.translate("ParameterTableButtons", u"Form", None))
        self.cleanButton.setText(QCoreApplication.translate("ParameterTableButtons", u"Remove Unused", None))
        self.scatterButton.setText(QCoreApplication.translate("ParameterTableButtons", u"Scatter", None))
        self.seriesButton.setText(QCoreApplication.translate("ParameterTableButtons", u"Series", None))
    # retranslateUi

