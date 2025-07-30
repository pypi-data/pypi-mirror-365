# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ModelEditor.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QGroupBox, QSizePolicy,
    QWidget)

from sas.qtgui.Utilities.CustomGUI.CodeEditor import QCodeEditor

class Ui_ModelEditor(object):
    def setupUi(self, ModelEditor):
        if not ModelEditor.objectName():
            ModelEditor.setObjectName(u"ModelEditor")
        ModelEditor.resize(549, 632)
        self.gridLayout = QGridLayout(ModelEditor)
        self.gridLayout.setObjectName(u"gridLayout")
        self.groupBox_13 = QGroupBox(ModelEditor)
        self.groupBox_13.setObjectName(u"groupBox_13")
        self.gridLayout_16 = QGridLayout(self.groupBox_13)
        self.gridLayout_16.setObjectName(u"gridLayout_16")
        self.txtEditor = QCodeEditor(self.groupBox_13)
        self.txtEditor.setObjectName(u"txtEditor")

        self.gridLayout_16.addWidget(self.txtEditor, 0, 0, 1, 1)


        self.gridLayout.addWidget(self.groupBox_13, 0, 0, 1, 1)


        self.retranslateUi(ModelEditor)

        QMetaObject.connectSlotsByName(ModelEditor)
    # setupUi

    def retranslateUi(self, ModelEditor):
        ModelEditor.setWindowTitle(QCoreApplication.translate("ModelEditor", u"Model Editor", None))
        self.groupBox_13.setTitle(QCoreApplication.translate("ModelEditor", u"Model", None))
    # retranslateUi

