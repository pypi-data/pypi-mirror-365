# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ReportDialogUI.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QGridLayout, QHBoxLayout,
    QPushButton, QSizePolicy, QSpacerItem, QTextBrowser,
    QWidget)

class Ui_ReportDialogUI(object):
    def setupUi(self, ReportDialogUI):
        if not ReportDialogUI.objectName():
            ReportDialogUI.setObjectName(u"ReportDialogUI")
        ReportDialogUI.resize(519, 461)
        self.gridLayout = QGridLayout(ReportDialogUI)
        self.gridLayout.setObjectName(u"gridLayout")
        self.txtBrowser = QTextBrowser(ReportDialogUI)
        self.txtBrowser.setObjectName(u"txtBrowser")

        self.gridLayout.addWidget(self.txtBrowser, 0, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.cmdPrint = QPushButton(ReportDialogUI)
        self.cmdPrint.setObjectName(u"cmdPrint")

        self.horizontalLayout.addWidget(self.cmdPrint)

        self.cmdSave = QPushButton(ReportDialogUI)
        self.cmdSave.setObjectName(u"cmdSave")

        self.horizontalLayout.addWidget(self.cmdSave)

        self.cmdClose = QPushButton(ReportDialogUI)
        self.cmdClose.setObjectName(u"cmdClose")

        self.horizontalLayout.addWidget(self.cmdClose)


        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)


        self.retranslateUi(ReportDialogUI)
        self.cmdClose.clicked.connect(ReportDialogUI.close)

        QMetaObject.connectSlotsByName(ReportDialogUI)
    # setupUi

    def retranslateUi(self, ReportDialogUI):
        ReportDialogUI.setWindowTitle(QCoreApplication.translate("ReportDialogUI", u"Report", None))
        self.cmdPrint.setText(QCoreApplication.translate("ReportDialogUI", u"Print", None))
        self.cmdSave.setText(QCoreApplication.translate("ReportDialogUI", u"Save", None))
        self.cmdClose.setText(QCoreApplication.translate("ReportDialogUI", u"Close", None))
    # retranslateUi

