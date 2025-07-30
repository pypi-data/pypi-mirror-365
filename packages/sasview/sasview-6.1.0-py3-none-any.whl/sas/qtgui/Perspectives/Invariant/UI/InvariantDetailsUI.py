# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'InvariantDetailsUI.ui'
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
    QGridLayout, QGroupBox, QLabel, QLineEdit,
    QProgressBar, QSizePolicy, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(511, 458)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.gridLayout_4 = QGridLayout(Dialog)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.groupBox = QGroupBox(Dialog)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_12 = QLabel(self.groupBox)
        self.label_12.setObjectName(u"label_12")

        self.gridLayout_2.addWidget(self.label_12, 0, 0, 1, 1)

        self.progressBarLowQ = QProgressBar(self.groupBox)
        self.progressBarLowQ.setObjectName(u"progressBarLowQ")
        self.progressBarLowQ.setValue(24)

        self.gridLayout_2.addWidget(self.progressBarLowQ, 0, 1, 1, 1)

        self.label_10 = QLabel(self.groupBox)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout_2.addWidget(self.label_10, 1, 0, 1, 1)

        self.progressBarData = QProgressBar(self.groupBox)
        self.progressBarData.setObjectName(u"progressBarData")
        self.progressBarData.setValue(24)

        self.gridLayout_2.addWidget(self.progressBarData, 1, 1, 1, 1)

        self.label_11 = QLabel(self.groupBox)
        self.label_11.setObjectName(u"label_11")

        self.gridLayout_2.addWidget(self.label_11, 2, 0, 1, 1)

        self.progressBarHighQ = QProgressBar(self.groupBox)
        self.progressBarHighQ.setObjectName(u"progressBarHighQ")
        self.progressBarHighQ.setValue(24)

        self.gridLayout_2.addWidget(self.progressBarHighQ, 2, 1, 1, 1)


        self.gridLayout_4.addWidget(self.groupBox, 0, 0, 1, 1)

        self.groupBox_2 = QGroupBox(Dialog)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout = QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(self.groupBox_2)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.txtQLowQ = QLineEdit(self.groupBox_2)
        self.txtQLowQ.setObjectName(u"txtQLowQ")
        self.txtQLowQ.setReadOnly(True)

        self.gridLayout.addWidget(self.txtQLowQ, 0, 1, 1, 1)

        self.label_2 = QLabel(self.groupBox_2)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 0, 2, 1, 1)

        self.txtQLowQErr = QLineEdit(self.groupBox_2)
        self.txtQLowQErr.setObjectName(u"txtQLowQErr")
        self.txtQLowQErr.setReadOnly(True)

        self.gridLayout.addWidget(self.txtQLowQErr, 0, 3, 1, 1)

        self.lblQLowQUnits = QLabel(self.groupBox_2)
        self.lblQLowQUnits.setObjectName(u"lblQLowQUnits")

        self.gridLayout.addWidget(self.lblQLowQUnits, 0, 4, 1, 1)

        self.label_5 = QLabel(self.groupBox_2)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 1, 0, 1, 1)

        self.txtQData = QLineEdit(self.groupBox_2)
        self.txtQData.setObjectName(u"txtQData")
        self.txtQData.setReadOnly(True)

        self.gridLayout.addWidget(self.txtQData, 1, 1, 1, 1)

        self.label_6 = QLabel(self.groupBox_2)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout.addWidget(self.label_6, 1, 2, 1, 1)

        self.txtQDataErr = QLineEdit(self.groupBox_2)
        self.txtQDataErr.setObjectName(u"txtQDataErr")
        self.txtQDataErr.setReadOnly(True)

        self.gridLayout.addWidget(self.txtQDataErr, 1, 3, 1, 1)

        self.lblQDataUnits = QLabel(self.groupBox_2)
        self.lblQDataUnits.setObjectName(u"lblQDataUnits")

        self.gridLayout.addWidget(self.lblQDataUnits, 1, 4, 1, 1)

        self.label_8 = QLabel(self.groupBox_2)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout.addWidget(self.label_8, 2, 0, 1, 1)

        self.txtQHighQ = QLineEdit(self.groupBox_2)
        self.txtQHighQ.setObjectName(u"txtQHighQ")
        self.txtQHighQ.setReadOnly(True)

        self.gridLayout.addWidget(self.txtQHighQ, 2, 1, 1, 1)

        self.label_9 = QLabel(self.groupBox_2)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout.addWidget(self.label_9, 2, 2, 1, 1)

        self.txtQHighQErr = QLineEdit(self.groupBox_2)
        self.txtQHighQErr.setObjectName(u"txtQHighQErr")
        self.txtQHighQErr.setReadOnly(True)

        self.gridLayout.addWidget(self.txtQHighQErr, 2, 3, 1, 1)

        self.lblQHighQUnits = QLabel(self.groupBox_2)
        self.lblQHighQUnits.setObjectName(u"lblQHighQUnits")

        self.gridLayout.addWidget(self.lblQHighQUnits, 2, 4, 1, 1)


        self.gridLayout_4.addWidget(self.groupBox_2, 1, 0, 1, 1)

        self.groupBox_3 = QGroupBox(Dialog)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.gridLayout_3 = QGridLayout(self.groupBox_3)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.lblWarning = QLabel(self.groupBox_3)
        self.lblWarning.setObjectName(u"lblWarning")
        self.lblWarning.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)

        self.gridLayout_3.addWidget(self.lblWarning, 0, 0, 1, 1)


        self.gridLayout_4.addWidget(self.groupBox_3, 2, 0, 1, 1)

        self.cmdOK = QDialogButtonBox(Dialog)
        self.cmdOK.setObjectName(u"cmdOK")
        self.cmdOK.setOrientation(Qt.Horizontal)
        self.cmdOK.setStandardButtons(QDialogButtonBox.Ok)

        self.gridLayout_4.addWidget(self.cmdOK, 3, 0, 1, 1)


        self.retranslateUi(Dialog)
        self.cmdOK.accepted.connect(Dialog.accept)
        self.cmdOK.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.groupBox.setTitle(QCoreApplication.translate("Dialog", u"Invariant chart", None))
        self.label_12.setText(QCoreApplication.translate("Dialog", u"Q* from Low-Q", None))
        self.label_10.setText(QCoreApplication.translate("Dialog", u"Q* from Data", None))
        self.label_11.setText(QCoreApplication.translate("Dialog", u"Q* from High-Q", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("Dialog", u"Numerical values", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Q* from Low-Q", None))
#if QT_CONFIG(tooltip)
        self.txtQLowQ.setToolTip(QCoreApplication.translate("Dialog", u"Extrapolated invariant from low-Q range.", None))
#endif // QT_CONFIG(tooltip)
        self.label_2.setText(QCoreApplication.translate("Dialog", u"+/-", None))
#if QT_CONFIG(tooltip)
        self.txtQLowQErr.setToolTip(QCoreApplication.translate("Dialog", u"Uncertainty on the invariant from low-Q range.", None))
#endif // QT_CONFIG(tooltip)
        self.lblQLowQUnits.setText(QCoreApplication.translate("Dialog", u"<html><head/><body><p>(cm \u00c5<span style=\" vertical-align:super;\">3</span>)<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.label_5.setText(QCoreApplication.translate("Dialog", u"Q* from Data", None))
#if QT_CONFIG(tooltip)
        self.txtQData.setToolTip(QCoreApplication.translate("Dialog", u"Invariant in the data set's Q range.", None))
#endif // QT_CONFIG(tooltip)
        self.label_6.setText(QCoreApplication.translate("Dialog", u"+/-", None))
#if QT_CONFIG(tooltip)
        self.txtQDataErr.setToolTip(QCoreApplication.translate("Dialog", u"Uncertainty on the invariant from data's range.", None))
#endif // QT_CONFIG(tooltip)
        self.lblQDataUnits.setText(QCoreApplication.translate("Dialog", u"<html><head/><body><p>(cm \u00c5<span style=\" vertical-align:super;\">3</span>)<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.label_8.setText(QCoreApplication.translate("Dialog", u"Q* from High-Q", None))
#if QT_CONFIG(tooltip)
        self.txtQHighQ.setToolTip(QCoreApplication.translate("Dialog", u"Extrapolated invariant from high-Q range.", None))
#endif // QT_CONFIG(tooltip)
        self.label_9.setText(QCoreApplication.translate("Dialog", u"+/-", None))
#if QT_CONFIG(tooltip)
        self.txtQHighQErr.setToolTip(QCoreApplication.translate("Dialog", u"Uncertainty on the invariant from high-Q range.", None))
#endif // QT_CONFIG(tooltip)
        self.lblQHighQUnits.setText(QCoreApplication.translate("Dialog", u"<html><head/><body><p>(cm \u00c5<span style=\" vertical-align:super;\">3</span>)<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("Dialog", u"Warnings", None))
        self.lblWarning.setText(QCoreApplication.translate("Dialog", u"<html><head/><body><p>No Details on calculations available...</p></body></html>", None))
    # retranslateUi

