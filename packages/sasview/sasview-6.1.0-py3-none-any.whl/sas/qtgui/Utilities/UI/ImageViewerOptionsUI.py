# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ImageViewerOptionsUI.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QSizePolicy, QSpacerItem,
    QTextBrowser, QWidget)

class Ui_ImageViewerOptionsUI(object):
    def setupUi(self, ImageViewerOptionsUI):
        if not ImageViewerOptionsUI.objectName():
            ImageViewerOptionsUI.setObjectName(u"ImageViewerOptionsUI")
        ImageViewerOptionsUI.resize(454, 246)
        self.gridLayout_4 = QGridLayout(ImageViewerOptionsUI)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.groupBox = QGroupBox(ImageViewerOptionsUI)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_3 = QGridLayout(self.groupBox)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.label_6 = QLabel(self.groupBox)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout.addWidget(self.label_6, 0, 1, 1, 1)

        self.txtXmin = QLineEdit(self.groupBox)
        self.txtXmin.setObjectName(u"txtXmin")

        self.gridLayout.addWidget(self.txtXmin, 0, 2, 1, 1)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.label_7 = QLabel(self.groupBox)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout.addWidget(self.label_7, 1, 1, 1, 1)

        self.txtYmin = QLineEdit(self.groupBox)
        self.txtYmin.setObjectName(u"txtYmin")

        self.gridLayout.addWidget(self.txtYmin, 1, 2, 1, 1)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)

        self.label_8 = QLabel(self.groupBox)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout.addWidget(self.label_8, 2, 1, 1, 1)

        self.txtZmax = QLineEdit(self.groupBox)
        self.txtZmax.setObjectName(u"txtZmax")

        self.gridLayout.addWidget(self.txtZmax, 2, 2, 1, 1)


        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_4)

        self.txtXmax = QLineEdit(self.groupBox)
        self.txtXmax.setObjectName(u"txtXmax")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.txtXmax)

        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_5)

        self.txtYmax = QLineEdit(self.groupBox)
        self.txtYmax.setObjectName(u"txtYmax")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.txtYmax)


        self.gridLayout_2.addLayout(self.formLayout_2, 0, 1, 1, 1)


        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 0, 1, 1)


        self.gridLayout_4.addWidget(self.groupBox, 0, 0, 1, 1)

        self.textBrowser = QTextBrowser(ImageViewerOptionsUI)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setEnabled(True)

        self.gridLayout_4.addWidget(self.textBrowser, 1, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.buttonBox = QDialogButtonBox(ImageViewerOptionsUI)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.horizontalLayout.addWidget(self.buttonBox)


        self.gridLayout_4.addLayout(self.horizontalLayout, 2, 0, 1, 1)

        self.groupBox.raise_()
        self.buttonBox.raise_()
        self.textBrowser.raise_()

        self.retranslateUi(ImageViewerOptionsUI)
        self.buttonBox.accepted.connect(ImageViewerOptionsUI.accept)
        self.buttonBox.rejected.connect(ImageViewerOptionsUI.reject)

        QMetaObject.connectSlotsByName(ImageViewerOptionsUI)
    # setupUi

    def retranslateUi(self, ImageViewerOptionsUI):
        ImageViewerOptionsUI.setWindowTitle(QCoreApplication.translate("ImageViewerOptionsUI", u"Image Conversion Options", None))
        self.groupBox.setTitle(QCoreApplication.translate("ImageViewerOptionsUI", u"GroupBox", None))
        self.label.setText(QCoreApplication.translate("ImageViewerOptionsUI", u"x values from pixel # to:", None))
        self.label_6.setText(QCoreApplication.translate("ImageViewerOptionsUI", u"<html><head/><body><p>X<span style=\" vertical-align:sub;\">min</span></p></body></html>", None))
        self.label_2.setText(QCoreApplication.translate("ImageViewerOptionsUI", u"y values from pixel # to:", None))
        self.label_7.setText(QCoreApplication.translate("ImageViewerOptionsUI", u"<html><head/><body><p>Y<span style=\" vertical-align:sub;\">min</span></p></body></html>", None))
        self.label_3.setText(QCoreApplication.translate("ImageViewerOptionsUI", u"<html><head/><body><p>z value range</p></body></html>", None))
        self.label_8.setText(QCoreApplication.translate("ImageViewerOptionsUI", u"<html><head/><body><p>From 0 to:</p></body></html>", None))
        self.label_4.setText(QCoreApplication.translate("ImageViewerOptionsUI", u"<html><head/><body><p>X<span style=\" vertical-align:sub;\">max</span></p></body></html>", None))
        self.label_5.setText(QCoreApplication.translate("ImageViewerOptionsUI", u"<html><head/><body><p>Y<span style=\" vertical-align:sub;\">max</span></p></body></html>", None))
        self.textBrowser.setHtml(QCoreApplication.translate("ImageViewerOptionsUI", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'MS Shell Dlg 2'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600;\">Note</span><span style=\" font-size:8pt;\">:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Recommend to use an image with 8 bit Grey scale (and with No. of pixels &lt; 300 x 300).</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Otherwise, z = 0.299R + 0.587G + 0.114B.</"
                        "span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p></body></html>", None))
    # retranslateUi

