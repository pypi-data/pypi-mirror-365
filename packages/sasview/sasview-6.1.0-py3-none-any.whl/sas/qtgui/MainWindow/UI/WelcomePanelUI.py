# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'WelcomePanelUI.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QGridLayout,
    QLabel, QSizePolicy, QWidget)

class Ui_WelcomePanelUI(object):
    def setupUi(self, WelcomePanelUI):
        if not WelcomePanelUI.objectName():
            WelcomePanelUI.setObjectName(u"WelcomePanelUI")
        WelcomePanelUI.resize(658, 737)
        self.gridLayout = QGridLayout(WelcomePanelUI)
        self.gridLayout.setObjectName(u"gridLayout")
        self.imgSasView = QLabel(WelcomePanelUI)
        self.imgSasView.setObjectName(u"imgSasView")
        self.imgSasView.setPixmap(QPixmap(u":/res/SVwelcome.png"))
        self.imgSasView.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.imgSasView, 0, 0, 1, 1)

        self.line = QFrame(WelcomePanelUI)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line, 1, 0, 1, 1)

        self.lblAcknowledgements = QLabel(WelcomePanelUI)
        self.lblAcknowledgements.setObjectName(u"lblAcknowledgements")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblAcknowledgements.sizePolicy().hasHeightForWidth())
        self.lblAcknowledgements.setSizePolicy(sizePolicy)
        self.lblAcknowledgements.setWordWrap(True)

        self.gridLayout.addWidget(self.lblAcknowledgements, 2, 0, 1, 1)

        self.lblVersion = QLabel(WelcomePanelUI)
        self.lblVersion.setObjectName(u"lblVersion")
        sizePolicy.setHeightForWidth(self.lblVersion.sizePolicy().hasHeightForWidth())
        self.lblVersion.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.lblVersion, 3, 0, 1, 1)

        self.lblLink = QLabel(WelcomePanelUI)
        self.lblLink.setObjectName(u"lblLink")
        sizePolicy.setHeightForWidth(self.lblLink.sizePolicy().hasHeightForWidth())
        self.lblLink.setSizePolicy(sizePolicy)
        self.lblLink.setOpenExternalLinks(True)

        self.gridLayout.addWidget(self.lblLink, 4, 0, 1, 1)


        self.retranslateUi(WelcomePanelUI)

        QMetaObject.connectSlotsByName(WelcomePanelUI)
    # setupUi

    def retranslateUi(self, WelcomePanelUI):
        WelcomePanelUI.setWindowTitle(QCoreApplication.translate("WelcomePanelUI", u"Dialog", None))
        self.imgSasView.setText("")
        self.lblAcknowledgements.setText(QCoreApplication.translate("WelcomePanelUI", u"This work originally developed as part of the DANSE project funded by the NSF under grant DMR-0520547, and currently maintained by UTK, UMD, ESS, NIST, ORNL, ISIS, ILL, DLS, TUD, BAM and ANSTO.", None))
        self.lblVersion.setText(QCoreApplication.translate("WelcomePanelUI", u"<html><head/><body><p>SasView 4.0.0-Alpha<br/>Build: 1<br/>(c) 2009 - 2017, UTK, UMD, NIST, ORNL, ISIS, ESS, ILL and ANSTO</p><p><br/></p></body></html>", None))
        self.lblLink.setText(QCoreApplication.translate("WelcomePanelUI", u"<html><head/><body><p>Comments? Bugs? Requests?</p>\n"
"<p>Send us a ticket at: <a href=\"mailto:help@sasview.org\"><span style=\" text-decoration: underline; color:#0000ff;\"> help@sasview.org</span></a></p></body></html>", None))
    # retranslateUi

