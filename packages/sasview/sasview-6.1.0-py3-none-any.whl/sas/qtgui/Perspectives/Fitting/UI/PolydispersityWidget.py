# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PolydispersityWidget.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QGridLayout, QGroupBox,
    QHeaderView, QSizePolicy, QTableView, QWidget)

class Ui_PolydispersityWidgetUI(object):
    def setupUi(self, PolydispersityWidgetUI):
        if not PolydispersityWidgetUI.objectName():
            PolydispersityWidgetUI.setObjectName(u"PolydispersityWidgetUI")
        PolydispersityWidgetUI.resize(521, 526)
        self.gridLayout = QGridLayout(PolydispersityWidgetUI)
        self.gridLayout.setObjectName(u"gridLayout")
        self.groupBox_3 = QGroupBox(PolydispersityWidgetUI)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.gridLayout_9 = QGridLayout(self.groupBox_3)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.lstPoly = QTableView(self.groupBox_3)
        self.lstPoly.setObjectName(u"lstPoly")
        self.lstPoly.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.lstPoly.setAlternatingRowColors(True)
        self.lstPoly.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.lstPoly.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.gridLayout_9.addWidget(self.lstPoly, 0, 0, 1, 1)


        self.gridLayout.addWidget(self.groupBox_3, 0, 0, 1, 1)


        self.retranslateUi(PolydispersityWidgetUI)

        QMetaObject.connectSlotsByName(PolydispersityWidgetUI)
    # setupUi

    def retranslateUi(self, PolydispersityWidgetUI):
        PolydispersityWidgetUI.setWindowTitle(QCoreApplication.translate("PolydispersityWidgetUI", u"Polydispersity", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("PolydispersityWidgetUI", u"Polydispersity and Orientational Distribution", None))
    # retranslateUi

