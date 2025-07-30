# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SmearingWidgetUI.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QSizePolicy, QSpacerItem,
    QWidget)

class Ui_SmearingWidgetUI(object):
    def setupUi(self, SmearingWidgetUI):
        if not SmearingWidgetUI.objectName():
            SmearingWidgetUI.setObjectName(u"SmearingWidgetUI")
        SmearingWidgetUI.resize(702, 242)
        self.gridLayout_4 = QGridLayout(SmearingWidgetUI)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.groupBox_4 = QGroupBox(SmearingWidgetUI)
        self.groupBox_4.setObjectName(u"groupBox_4")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_4.sizePolicy().hasHeightForWidth())
        self.groupBox_4.setSizePolicy(sizePolicy)
        self.gridLayout_3 = QGridLayout(self.groupBox_4)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.cbSmearing = QComboBox(self.groupBox_4)
        self.cbSmearing.addItem("")
        self.cbSmearing.addItem("")
        self.cbSmearing.addItem("")
        self.cbSmearing.addItem("")
        self.cbSmearing.addItem("")
        self.cbSmearing.setObjectName(u"cbSmearing")
        self.cbSmearing.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.gridLayout_2.addWidget(self.cbSmearing, 0, 0, 1, 1)

        self.gridLayout_11 = QGridLayout()
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.lblSmearUp = QLabel(self.groupBox_4)
        self.lblSmearUp.setObjectName(u"lblSmearUp")

        self.gridLayout_11.addWidget(self.lblSmearUp, 0, 0, 1, 1)

        self.txtSmearUp = QLineEdit(self.groupBox_4)
        self.txtSmearUp.setObjectName(u"txtSmearUp")

        self.gridLayout_11.addWidget(self.txtSmearUp, 0, 1, 1, 1)

        self.lblUnitUp = QLabel(self.groupBox_4)
        self.lblUnitUp.setObjectName(u"lblUnitUp")

        self.gridLayout_11.addWidget(self.lblUnitUp, 0, 2, 1, 1)

        self.lblSmearDown = QLabel(self.groupBox_4)
        self.lblSmearDown.setObjectName(u"lblSmearDown")

        self.gridLayout_11.addWidget(self.lblSmearDown, 1, 0, 1, 1)

        self.txtSmearDown = QLineEdit(self.groupBox_4)
        self.txtSmearDown.setObjectName(u"txtSmearDown")

        self.gridLayout_11.addWidget(self.txtSmearDown, 1, 1, 1, 1)

        self.lblUnitDown = QLabel(self.groupBox_4)
        self.lblUnitDown.setObjectName(u"lblUnitDown")

        self.gridLayout_11.addWidget(self.lblUnitDown, 1, 2, 1, 1)


        self.gridLayout_2.addLayout(self.gridLayout_11, 0, 1, 2, 1)

        self.gAccuracy = QGroupBox(self.groupBox_4)
        self.gAccuracy.setObjectName(u"gAccuracy")
        self.gridLayout = QGridLayout(self.gAccuracy)
        self.gridLayout.setObjectName(u"gridLayout")
        self.cbAccuracy = QComboBox(self.gAccuracy)
        self.cbAccuracy.addItem("")
        self.cbAccuracy.addItem("")
        self.cbAccuracy.addItem("")
        self.cbAccuracy.addItem("")
        self.cbAccuracy.setObjectName(u"cbAccuracy")

        self.gridLayout.addWidget(self.cbAccuracy, 0, 0, 1, 1)


        self.gridLayout_2.addWidget(self.gAccuracy, 0, 2, 2, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 18, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer_2, 1, 0, 1, 1)


        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 0, 1, 1)


        self.gridLayout_4.addWidget(self.groupBox_4, 0, 0, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(71, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_2, 0, 1, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 162, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_4.addItem(self.verticalSpacer, 1, 0, 1, 1)


        self.retranslateUi(SmearingWidgetUI)

        self.cbSmearing.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(SmearingWidgetUI)
    # setupUi

    def retranslateUi(self, SmearingWidgetUI):
        SmearingWidgetUI.setWindowTitle(QCoreApplication.translate("SmearingWidgetUI", u"Form", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("SmearingWidgetUI", u"Instrumental Smearing", None))
        self.cbSmearing.setItemText(0, QCoreApplication.translate("SmearingWidgetUI", u"None", None))
        self.cbSmearing.setItemText(1, QCoreApplication.translate("SmearingWidgetUI", u"Use dQ Data", None))
        self.cbSmearing.setItemText(2, QCoreApplication.translate("SmearingWidgetUI", u"Custom Pinhole Smear", None))
        self.cbSmearing.setItemText(3, QCoreApplication.translate("SmearingWidgetUI", u"Custom Slit Smear", None))
        self.cbSmearing.setItemText(4, QCoreApplication.translate("SmearingWidgetUI", u"Hankel Transform", None))

        self.lblSmearUp.setText(QCoreApplication.translate("SmearingWidgetUI", u"<html><head/><body><p>dQ<span style=\" vertical-align:sub;\">low</span></p></body></html>", None))
        self.lblUnitUp.setText(QCoreApplication.translate("SmearingWidgetUI", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.lblSmearDown.setText(QCoreApplication.translate("SmearingWidgetUI", u"<html><head/><body><p>dQ<span style=\" vertical-align:sub;\">high</span></p></body></html>", None))
        self.lblUnitDown.setText(QCoreApplication.translate("SmearingWidgetUI", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.gAccuracy.setTitle(QCoreApplication.translate("SmearingWidgetUI", u"Accuracy", None))
#if QT_CONFIG(tooltip)
        self.gAccuracy.setToolTip(QCoreApplication.translate("SmearingWidgetUI", u"<html><head/><body><p>Higher accuracy is very expensive. Use it with care!</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cbAccuracy.setItemText(0, QCoreApplication.translate("SmearingWidgetUI", u"Low", None))
        self.cbAccuracy.setItemText(1, QCoreApplication.translate("SmearingWidgetUI", u"Medium", None))
        self.cbAccuracy.setItemText(2, QCoreApplication.translate("SmearingWidgetUI", u"High", None))
        self.cbAccuracy.setItemText(3, QCoreApplication.translate("SmearingWidgetUI", u"Extra high", None))

    # retranslateUi

