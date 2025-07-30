# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ViewerModelRadiusUI.ui'
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
from PySide6.QtWidgets import (QApplication, QDoubleSpinBox, QGridLayout, QHBoxLayout,
    QLabel, QSizePolicy, QSpacerItem, QWidget)

class Ui_ViewerModelRadius(object):
    def setupUi(self, ViewerModelRadius):
        if not ViewerModelRadius.objectName():
            ViewerModelRadius.setObjectName(u"ViewerModelRadius")
        ViewerModelRadius.resize(283, 24)
        ViewerModelRadius.setMinimumSize(QSize(283, 24))
        ViewerModelRadius.setMaximumSize(QSize(283, 24))
        self.gridLayout = QGridLayout(ViewerModelRadius)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer = QSpacerItem(50, 22, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.label_2 = QLabel(ViewerModelRadius)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(60, 22))
        self.label_2.setMaximumSize(QSize(60, 22))

        self.horizontalLayout_3.addWidget(self.label_2)

        self.doubleSpinBox = QDoubleSpinBox(ViewerModelRadius)
        self.doubleSpinBox.setObjectName(u"doubleSpinBox")
        self.doubleSpinBox.setMinimumSize(QSize(80, 22))
        self.doubleSpinBox.setMaximumSize(QSize(80, 22))

        self.horizontalLayout_3.addWidget(self.doubleSpinBox)

        self.label_3 = QLabel(ViewerModelRadius)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMinimumSize(QSize(13, 22))
        self.label_3.setMaximumSize(QSize(13, 22))

        self.horizontalLayout_3.addWidget(self.label_3)

        self.horizontalSpacer_2 = QSpacerItem(50, 22, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)


        self.gridLayout.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)


        self.retranslateUi(ViewerModelRadius)

        QMetaObject.connectSlotsByName(ViewerModelRadius)
    # setupUi

    def retranslateUi(self, ViewerModelRadius):
        ViewerModelRadius.setWindowTitle(QCoreApplication.translate("ViewerModelRadius", u"ViewerModelRadius", None))
        self.label_2.setText(QCoreApplication.translate("ViewerModelRadius", u"View radius", None))
        self.label_3.setText(QCoreApplication.translate("ViewerModelRadius", u"\u00c5", None))
    # retranslateUi

