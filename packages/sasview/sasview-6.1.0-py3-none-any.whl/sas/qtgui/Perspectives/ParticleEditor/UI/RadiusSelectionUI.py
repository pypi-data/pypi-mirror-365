# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'RadiusSelectionUI.ui'
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
from PySide6.QtWidgets import (QApplication, QDoubleSpinBox, QHBoxLayout, QLabel,
    QSizePolicy, QSpacerItem, QWidget)

class Ui_RadiusSelection(object):
    def setupUi(self, RadiusSelection):
        if not RadiusSelection.objectName():
            RadiusSelection.setObjectName(u"RadiusSelection")
        RadiusSelection.resize(265, 20)
        self.horizontalLayout = QHBoxLayout(RadiusSelection)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.label = QLabel(RadiusSelection)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.radiusField = QDoubleSpinBox(RadiusSelection)
        self.radiusField.setObjectName(u"radiusField")
        self.radiusField.setMinimum(0.100000000000000)
        self.radiusField.setMaximum(100000.000000000000000)
        self.radiusField.setValue(100.000000000000000)

        self.horizontalLayout.addWidget(self.radiusField)

        self.label_2 = QLabel(RadiusSelection)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout.addWidget(self.label_2)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.retranslateUi(RadiusSelection)

        QMetaObject.connectSlotsByName(RadiusSelection)
    # setupUi

    def retranslateUi(self, RadiusSelection):
        RadiusSelection.setWindowTitle(QCoreApplication.translate("RadiusSelection", u"Form", None))
        self.label.setText(QCoreApplication.translate("RadiusSelection", u"Radius", None))
        self.label_2.setText(QCoreApplication.translate("RadiusSelection", u"\u00c5", None))
    # retranslateUi

