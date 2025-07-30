# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MagnetismWidget.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QGroupBox, QHeaderView,
    QPushButton, QSizePolicy, QSpacerItem, QTableView,
    QWidget)

class Ui_MagnetismWidgetUI(object):
    def setupUi(self, MagnetismWidgetUI):
        if not MagnetismWidgetUI.objectName():
            MagnetismWidgetUI.setObjectName(u"MagnetismWidgetUI")
        MagnetismWidgetUI.resize(571, 515)
        self.gridLayout = QGridLayout(MagnetismWidgetUI)
        self.gridLayout.setObjectName(u"gridLayout")
        self.groupBox_10 = QGroupBox(MagnetismWidgetUI)
        self.groupBox_10.setObjectName(u"groupBox_10")
        self.gridLayout_21 = QGridLayout(self.groupBox_10)
        self.gridLayout_21.setObjectName(u"gridLayout_21")
        self.lstMagnetic = QTableView(self.groupBox_10)
        self.lstMagnetic.setObjectName(u"lstMagnetic")

        self.gridLayout_21.addWidget(self.lstMagnetic, 0, 0, 1, 3)

        self.horizontalSpacer_6 = QSpacerItem(498, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_21.addItem(self.horizontalSpacer_6, 1, 1, 1, 1)

        self.cmdMagneticDisplay = QPushButton(self.groupBox_10)
        self.cmdMagneticDisplay.setObjectName(u"cmdMagneticDisplay")

        self.gridLayout_21.addWidget(self.cmdMagneticDisplay, 1, 2, 1, 1)


        self.gridLayout.addWidget(self.groupBox_10, 0, 0, 1, 1)


        self.retranslateUi(MagnetismWidgetUI)

        QMetaObject.connectSlotsByName(MagnetismWidgetUI)
    # setupUi

    def retranslateUi(self, MagnetismWidgetUI):
        MagnetismWidgetUI.setWindowTitle(QCoreApplication.translate("MagnetismWidgetUI", u"Magnetism", None))
        self.groupBox_10.setTitle(QCoreApplication.translate("MagnetismWidgetUI", u"Polarisation/Magnetic Scattering ", None))
        self.cmdMagneticDisplay.setText(QCoreApplication.translate("MagnetismWidgetUI", u"Display\n"
"magnetic\n"
"angles", None))
    # retranslateUi

