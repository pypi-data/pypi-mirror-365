# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'AcknowledgementsUI.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QSizePolicy,
    QSpacerItem, QTextBrowser, QWidget)

class Ui_Acknowledgements(object):
    def setupUi(self, Acknowledgements):
        if not Acknowledgements.objectName():
            Acknowledgements.setObjectName(u"Acknowledgements")
        Acknowledgements.setWindowModality(Qt.ApplicationModal)
        Acknowledgements.resize(468, 316)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Acknowledgements.sizePolicy().hasHeightForWidth())
        Acknowledgements.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(Acknowledgements)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(Acknowledgements)
        self.label.setObjectName(u"label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy1)
        self.label.setMaximumSize(QSize(16777215, 50))

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.textBrowser = QTextBrowser(Acknowledgements)
        self.textBrowser.setObjectName(u"textBrowser")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.textBrowser.sizePolicy().hasHeightForWidth())
        self.textBrowser.setSizePolicy(sizePolicy2)
        self.textBrowser.setMinimumSize(QSize(0, 85))
        self.textBrowser.setMaximumSize(QSize(16777215, 85))

        self.gridLayout.addWidget(self.textBrowser, 1, 0, 1, 1)

        self.label_2 = QLabel(Acknowledgements)
        self.label_2.setObjectName(u"label_2")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy3)
        self.label_2.setMaximumSize(QSize(16777215, 21))

        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)

        self.textBrowser_2 = QTextBrowser(Acknowledgements)
        self.textBrowser_2.setObjectName(u"textBrowser_2")
        sizePolicy2.setHeightForWidth(self.textBrowser_2.sizePolicy().hasHeightForWidth())
        self.textBrowser_2.setSizePolicy(sizePolicy2)
        self.textBrowser_2.setMaximumSize(QSize(16777215, 31))

        self.gridLayout.addWidget(self.textBrowser_2, 3, 0, 1, 1)

        self.label_3 = QLabel(Acknowledgements)
        self.label_3.setObjectName(u"label_3")
        sizePolicy1.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy1)
        self.label_3.setMaximumSize(QSize(16777215, 50))

        self.gridLayout.addWidget(self.label_3, 4, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 5, 0, 1, 1)


        self.retranslateUi(Acknowledgements)

        QMetaObject.connectSlotsByName(Acknowledgements)
    # setupUi

    def retranslateUi(self, Acknowledgements):
        Acknowledgements.setWindowTitle(QCoreApplication.translate("Acknowledgements", u"Acknowledging SasView", None))
        self.label.setText(QCoreApplication.translate("Acknowledgements", u"<html><head/><body><p>To ensure the long term support and development of this software please remember to:</p><p>(1) Acknowledge its use in your publications as:<br/></p><p><br/></p></body></html>", None))
        self.textBrowser.setHtml(QCoreApplication.translate("Acknowledgements", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'MS Shell Dlg 2'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8.25pt;\">This work benefited from the use of the SasView application, originally developed under NSF Award DMR-0520547. SasView also contains code developed with funding from the EU Horizon 2020 programme under the SINE2020 project Grant No 654000.</span></p></body></html>", None))
        self.label_2.setText(QCoreApplication.translate("Acknowledgements", u"<html><head/><body><p>(2) Reference SasView as:</p><p><br/></p><p><br/></p></body></html>", None))
        self.textBrowser_2.setHtml(QCoreApplication.translate("Acknowledgements", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'MS Shell Dlg 2'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8.25pt;\">M. Doucet et al. SasView Version 5.0.3, Zenodo, 10.5281/zenodo.3930098</span></p></body></html>", None))
        self.label_3.setText(QCoreApplication.translate("Acknowledgements", u"<html><head/><body><p>(3) Reference the model you used if appropriate (see documentation for refs)</p><p>(4) Send us your reference for our records: developers@sasview.org</p></body></html>", None))
    # retranslateUi

