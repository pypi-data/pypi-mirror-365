# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'OrderWidgetUI.ui'
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
    QLabel, QListWidget, QListWidgetItem, QSizePolicy,
    QWidget)

class Ui_OrderWidgetUI(object):
    def setupUi(self, OrderWidgetUI):
        if not OrderWidgetUI.objectName():
            OrderWidgetUI.setObjectName(u"OrderWidgetUI")
        OrderWidgetUI.resize(511, 417)
        self.gridLayout_2 = QGridLayout(OrderWidgetUI)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.groupBox = QGroupBox(OrderWidgetUI)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.lstOrder = QListWidget(self.groupBox)
        self.lstOrder.setObjectName(u"lstOrder")
        self.lstOrder.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.lstOrder.setDragDropMode(QAbstractItemView.InternalMove)
        self.lstOrder.setDefaultDropAction(Qt.MoveAction)
        self.lstOrder.setAlternatingRowColors(True)
        self.lstOrder.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.gridLayout.addWidget(self.lstOrder, 1, 0, 1, 1)


        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)


        self.retranslateUi(OrderWidgetUI)

        QMetaObject.connectSlotsByName(OrderWidgetUI)
    # setupUi

    def retranslateUi(self, OrderWidgetUI):
        OrderWidgetUI.setWindowTitle(QCoreApplication.translate("OrderWidgetUI", u"Dataset Ordering", None))
        self.groupBox.setTitle(QCoreApplication.translate("OrderWidgetUI", u"Data Order", None))
        self.label.setText(QCoreApplication.translate("OrderWidgetUI", u"<html><head/><body><p>Drag and move items to define the order of fitting.</p></body></html>", None))
    # retranslateUi

