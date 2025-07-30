# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'CodeToolBarUI.ui'
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

class Ui_CodeToolBar(object):
    def setupUi(self, CodeToolBar):
        if not CodeToolBar.objectName():
            CodeToolBar.setObjectName(u"CodeToolBar")
        CodeToolBar.resize(460, 20)
        self.horizontalLayout = QHBoxLayout(CodeToolBar)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.loadButton = QPushButton(CodeToolBar)
        self.loadButton.setObjectName(u"loadButton")

        self.horizontalLayout.addWidget(self.loadButton)

        self.saveButton = QPushButton(CodeToolBar)
        self.saveButton.setObjectName(u"saveButton")

        self.horizontalLayout.addWidget(self.saveButton)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.buildButton = QPushButton(CodeToolBar)
        self.buildButton.setObjectName(u"buildButton")

        self.horizontalLayout.addWidget(self.buildButton)

        self.scatterButton = QPushButton(CodeToolBar)
        self.scatterButton.setObjectName(u"scatterButton")

        self.horizontalLayout.addWidget(self.scatterButton)


        self.retranslateUi(CodeToolBar)

        QMetaObject.connectSlotsByName(CodeToolBar)
    # setupUi

    def retranslateUi(self, CodeToolBar):
        CodeToolBar.setWindowTitle(QCoreApplication.translate("CodeToolBar", u"Form", None))
        self.loadButton.setText(QCoreApplication.translate("CodeToolBar", u"Load", None))
        self.saveButton.setText(QCoreApplication.translate("CodeToolBar", u"Save", None))
#if QT_CONFIG(tooltip)
        self.buildButton.setToolTip(QCoreApplication.translate("CodeToolBar", u"<html><head/><body><p>Build the current code</p><p>Shortcut: shift-Enter</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.buildButton.setText(QCoreApplication.translate("CodeToolBar", u"Build", None))
        self.scatterButton.setText(QCoreApplication.translate("CodeToolBar", u"Scatter", None))
    # retranslateUi

