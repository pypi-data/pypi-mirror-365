# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SaveExtrapolated.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QDoubleSpinBox, QLabel,
    QPushButton, QSizePolicy, QWidget)

class Ui_SaveExtrapolatedPanel(object):
    def setupUi(self, SaveExtrapolatedPanel):
        if not SaveExtrapolatedPanel.objectName():
            SaveExtrapolatedPanel.setObjectName(u"SaveExtrapolatedPanel")
        SaveExtrapolatedPanel.resize(246, 214)
        self.spnLow = QDoubleSpinBox(SaveExtrapolatedPanel)
        self.spnLow.setObjectName(u"spnLow")
        self.spnLow.setGeometry(QRect(90, 20, 91, 22))
        self.spnLow.setDecimals(6)
        self.spnLow.setMinimum(0.000001000000000)
        self.spnLow.setMaximum(100.000000000000000)
        self.spnHigh = QDoubleSpinBox(SaveExtrapolatedPanel)
        self.spnHigh.setObjectName(u"spnHigh")
        self.spnHigh.setGeometry(QRect(90, 60, 91, 22))
        self.spnHigh.setDecimals(6)
        self.spnHigh.setMinimum(0.000001000000000)
        self.spnHigh.setMaximum(100.000000000000000)
        self.spnHigh.setValue(1.000000000000000)
        self.spnDelta = QDoubleSpinBox(SaveExtrapolatedPanel)
        self.spnDelta.setObjectName(u"spnDelta")
        self.spnDelta.setGeometry(QRect(90, 100, 91, 22))
        self.spnDelta.setDecimals(6)
        self.spnDelta.setMinimum(0.000001000000000)
        self.spnDelta.setMaximum(100.000000000000000)
        self.lblLow = QLabel(SaveExtrapolatedPanel)
        self.lblLow.setObjectName(u"lblLow")
        self.lblLow.setGeometry(QRect(-6, 20, 71, 20))
        self.lblLow.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lblHigh = QLabel(SaveExtrapolatedPanel)
        self.lblHigh.setObjectName(u"lblHigh")
        self.lblHigh.setGeometry(QRect(-6, 60, 71, 20))
        self.lblHigh.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lblDelta = QLabel(SaveExtrapolatedPanel)
        self.lblDelta.setObjectName(u"lblDelta")
        self.lblDelta.setGeometry(QRect(-10, 100, 71, 20))
        self.lblDelta.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.units1 = QLabel(SaveExtrapolatedPanel)
        self.units1.setObjectName(u"units1")
        self.units1.setGeometry(QRect(190, 20, 15, 22))
        self.units2 = QLabel(SaveExtrapolatedPanel)
        self.units2.setObjectName(u"units2")
        self.units2.setGeometry(QRect(190, 60, 15, 22))
        self.units3 = QLabel(SaveExtrapolatedPanel)
        self.units3.setObjectName(u"units3")
        self.units3.setGeometry(QRect(190, 100, 15, 22))
        self.cmdOK = QPushButton(SaveExtrapolatedPanel)
        self.cmdOK.setObjectName(u"cmdOK")
        self.cmdOK.setGeometry(QRect(20, 160, 93, 28))
        self.cmdCancel = QPushButton(SaveExtrapolatedPanel)
        self.cmdCancel.setObjectName(u"cmdCancel")
        self.cmdCancel.setGeometry(QRect(130, 160, 93, 28))

        self.retranslateUi(SaveExtrapolatedPanel)

        QMetaObject.connectSlotsByName(SaveExtrapolatedPanel)
    # setupUi

    def retranslateUi(self, SaveExtrapolatedPanel):
        SaveExtrapolatedPanel.setWindowTitle(QCoreApplication.translate("SaveExtrapolatedPanel", u"Dialog", None))
        self.lblLow.setText(QCoreApplication.translate("SaveExtrapolatedPanel", u"Lowest Q", None))
        self.lblHigh.setText(QCoreApplication.translate("SaveExtrapolatedPanel", u"Highest Q", None))
        self.lblDelta.setText(QCoreApplication.translate("SaveExtrapolatedPanel", u"Delta Q", None))
        self.units1.setText(QCoreApplication.translate("SaveExtrapolatedPanel", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.units2.setText(QCoreApplication.translate("SaveExtrapolatedPanel", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.units3.setText(QCoreApplication.translate("SaveExtrapolatedPanel", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.cmdOK.setText(QCoreApplication.translate("SaveExtrapolatedPanel", u"OK", None))
        self.cmdCancel.setText(QCoreApplication.translate("SaveExtrapolatedPanel", u"Cancel", None))
    # retranslateUi

