# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'LinearFitUI.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QFormLayout, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QSpacerItem, QWidget)

class Ui_LinearFitUI(object):
    def setupUi(self, LinearFitUI):
        if not LinearFitUI.objectName():
            LinearFitUI.setObjectName(u"LinearFitUI")
        LinearFitUI.resize(503, 564)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(LinearFitUI.sizePolicy().hasHeightForWidth())
        LinearFitUI.setSizePolicy(sizePolicy)
        icon = QIcon()
        icon.addFile(u":/res/ball.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        LinearFitUI.setWindowIcon(icon)
        self.gridLayout_5 = QGridLayout(LinearFitUI)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.label = QLabel(LinearFitUI)
        self.label.setObjectName(u"label")

        self.gridLayout_5.addWidget(self.label, 0, 0, 1, 1)

        self.groupBox_2 = QGroupBox(LinearFitUI)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_3 = QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_9 = QLabel(self.groupBox_2)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_2.addWidget(self.label_9, 0, 1, 1, 1)

        self.label_10 = QLabel(self.groupBox_2)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout_2.addWidget(self.label_10, 0, 2, 1, 1)

        self.label_8 = QLabel(self.groupBox_2)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_2.addWidget(self.label_8, 1, 0, 1, 1)

        self.txtRangeMin = QLineEdit(self.groupBox_2)
        self.txtRangeMin.setObjectName(u"txtRangeMin")
        self.txtRangeMin.setEnabled(False)
        self.txtRangeMin.setAutoFillBackground(True)
        self.txtRangeMin.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.txtRangeMin.setReadOnly(True)

        self.gridLayout_2.addWidget(self.txtRangeMin, 1, 1, 1, 1)

        self.txtRangeMax = QLineEdit(self.groupBox_2)
        self.txtRangeMax.setObjectName(u"txtRangeMax")
        self.txtRangeMax.setEnabled(False)
        self.txtRangeMax.setAutoFillBackground(False)
        self.txtRangeMax.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.txtRangeMax.setReadOnly(True)

        self.gridLayout_2.addWidget(self.txtRangeMax, 1, 2, 1, 1)

        self.lblRange = QLabel(self.groupBox_2)
        self.lblRange.setObjectName(u"lblRange")

        self.gridLayout_2.addWidget(self.lblRange, 2, 0, 1, 1)

        self.txtFitRangeMin = QLineEdit(self.groupBox_2)
        self.txtFitRangeMin.setObjectName(u"txtFitRangeMin")

        self.gridLayout_2.addWidget(self.txtFitRangeMin, 2, 1, 1, 1)

        self.txtFitRangeMax = QLineEdit(self.groupBox_2)
        self.txtFitRangeMax.setObjectName(u"txtFitRangeMax")

        self.gridLayout_2.addWidget(self.txtFitRangeMax, 2, 2, 1, 1)


        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 0, 1, 1)


        self.gridLayout_5.addWidget(self.groupBox_2, 1, 0, 1, 2)

        self.groupBox = QGroupBox(LinearFitUI)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.txtA = QLineEdit(self.groupBox)
        self.txtA.setObjectName(u"txtA")
        self.txtA.setEnabled(False)
        self.txtA.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.txtA.setReadOnly(True)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.txtA)

        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_4)

        self.txtB = QLineEdit(self.groupBox)
        self.txtB.setObjectName(u"txtB")
        self.txtB.setEnabled(False)
        self.txtB.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.txtB.setReadOnly(True)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.txtB)

        self.label_7 = QLabel(self.groupBox)
        self.label_7.setObjectName(u"label_7")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_7)

        self.txtChi2 = QLineEdit(self.groupBox)
        self.txtChi2.setObjectName(u"txtChi2")
        self.txtChi2.setEnabled(False)
        self.txtChi2.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.txtChi2.setReadOnly(True)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.txtChi2)


        self.gridLayout.addLayout(self.formLayout, 0, 0, 1, 1)

        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_5)

        self.txtAerr = QLineEdit(self.groupBox)
        self.txtAerr.setObjectName(u"txtAerr")
        self.txtAerr.setEnabled(False)
        self.txtAerr.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.txtAerr.setReadOnly(True)

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.txtAerr)

        self.label_6 = QLabel(self.groupBox)
        self.label_6.setObjectName(u"label_6")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_6)

        self.txtBerr = QLineEdit(self.groupBox)
        self.txtBerr.setObjectName(u"txtBerr")
        self.txtBerr.setEnabled(False)
        self.txtBerr.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.txtBerr.setReadOnly(True)

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.txtBerr)


        self.gridLayout.addLayout(self.formLayout_2, 0, 1, 1, 1)


        self.gridLayout_5.addWidget(self.groupBox, 2, 0, 1, 2)

        self.guinier_box = QGroupBox(LinearFitUI)
        self.guinier_box.setObjectName(u"guinier_box")
        self.guinier_box.setEnabled(True)
        self.gridLayout_4 = QGridLayout(self.guinier_box)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.formLayout_4 = QFormLayout()
        self.formLayout_4.setObjectName(u"formLayout_4")
        self.label_11 = QLabel(self.guinier_box)
        self.label_11.setObjectName(u"label_11")

        self.formLayout_4.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_11)

        self.txtGuinier_1 = QLineEdit(self.guinier_box)
        self.txtGuinier_1.setObjectName(u"txtGuinier_1")
        self.txtGuinier_1.setEnabled(False)
        self.txtGuinier_1.setStyleSheet(u"color: rgb(0, 0, 0);")

        self.formLayout_4.setWidget(0, QFormLayout.ItemRole.FieldRole, self.txtGuinier_1)

        self.label_12 = QLabel(self.guinier_box)
        self.label_12.setObjectName(u"label_12")

        self.formLayout_4.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_12)

        self.txtGuinier_2 = QLineEdit(self.guinier_box)
        self.txtGuinier_2.setObjectName(u"txtGuinier_2")
        self.txtGuinier_2.setEnabled(False)
        self.txtGuinier_2.setStyleSheet(u"color: rgb(0, 0, 0);")

        self.formLayout_4.setWidget(1, QFormLayout.ItemRole.FieldRole, self.txtGuinier_2)

        self.label_15 = QLabel(self.guinier_box)
        self.label_15.setObjectName(u"label_15")

        self.formLayout_4.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_15)

        self.txtGuinier_3 = QLineEdit(self.guinier_box)
        self.txtGuinier_3.setObjectName(u"txtGuinier_3")
        self.txtGuinier_3.setEnabled(False)
        self.txtGuinier_3.setStyleSheet(u"color: rgb(0, 0, 0);")

        self.formLayout_4.setWidget(2, QFormLayout.ItemRole.FieldRole, self.txtGuinier_3)

        self.label_16 = QLabel(self.guinier_box)
        self.label_16.setObjectName(u"label_16")

        self.formLayout_4.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_16)

        self.txtGuinier_4 = QLineEdit(self.guinier_box)
        self.txtGuinier_4.setObjectName(u"txtGuinier_4")
        self.txtGuinier_4.setEnabled(False)
        self.txtGuinier_4.setStyleSheet(u"color: rgb(0, 0, 0);")

        self.formLayout_4.setWidget(3, QFormLayout.ItemRole.FieldRole, self.txtGuinier_4)


        self.gridLayout_4.addLayout(self.formLayout_4, 0, 0, 1, 1)

        self.formLayout_3 = QFormLayout()
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.label_13 = QLabel(self.guinier_box)
        self.label_13.setObjectName(u"label_13")

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_13)

        self.txtGuinier1_Err = QLineEdit(self.guinier_box)
        self.txtGuinier1_Err.setObjectName(u"txtGuinier1_Err")
        self.txtGuinier1_Err.setEnabled(False)
        self.txtGuinier1_Err.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.txtGuinier1_Err.setReadOnly(True)

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.FieldRole, self.txtGuinier1_Err)

        self.label_14 = QLabel(self.guinier_box)
        self.label_14.setObjectName(u"label_14")

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_14)

        self.txtGuinier2_Err = QLineEdit(self.guinier_box)
        self.txtGuinier2_Err.setObjectName(u"txtGuinier2_Err")
        self.txtGuinier2_Err.setEnabled(False)
        self.txtGuinier2_Err.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.txtGuinier2_Err.setReadOnly(True)

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.FieldRole, self.txtGuinier2_Err)


        self.gridLayout_4.addLayout(self.formLayout_3, 0, 1, 1, 1)


        self.gridLayout_5.addWidget(self.guinier_box, 3, 0, 1, 2)

        self.label_2 = QLabel(LinearFitUI)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_5.addWidget(self.label_2, 4, 0, 1, 2)

        self.verticalSpacer = QSpacerItem(20, 3, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_5.addItem(self.verticalSpacer, 5, 1, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.cmdFit = QPushButton(LinearFitUI)
        self.cmdFit.setObjectName(u"cmdFit")

        self.horizontalLayout.addWidget(self.cmdFit)

        self.cmdClose = QPushButton(LinearFitUI)
        self.cmdClose.setObjectName(u"cmdClose")

        self.horizontalLayout.addWidget(self.cmdClose)


        self.horizontalLayout_2.addLayout(self.horizontalLayout)


        self.gridLayout_5.addLayout(self.horizontalLayout_2, 6, 0, 1, 2)

        self.guinier_box.raise_()
        self.label.raise_()
        self.groupBox_2.raise_()
        self.groupBox.raise_()
        self.label_2.raise_()

        self.retranslateUi(LinearFitUI)
        self.cmdClose.clicked.connect(LinearFitUI.accept)

        QMetaObject.connectSlotsByName(LinearFitUI)
    # setupUi

    def retranslateUi(self, LinearFitUI):
        LinearFitUI.setWindowTitle(QCoreApplication.translate("LinearFitUI", u"Linear Fit", None))
        self.label.setText(QCoreApplication.translate("LinearFitUI", u"<html><head/><body><p>Perform fit for <span style=\" font-weight:600; font-style:italic;\">y(x) = ax + b</span></p></body></html>", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("LinearFitUI", u"Fit ranges", None))
        self.label_9.setText(QCoreApplication.translate("LinearFitUI", u"Min", None))
        self.label_10.setText(QCoreApplication.translate("LinearFitUI", u"Max", None))
        self.label_8.setText(QCoreApplication.translate("LinearFitUI", u"Range (linear scale)", None))
#if QT_CONFIG(tooltip)
        self.txtRangeMin.setToolTip(QCoreApplication.translate("LinearFitUI", u"<html><head/><body><p>Minimum value on the x-axis for the plotted data.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.txtRangeMax.setToolTip(QCoreApplication.translate("LinearFitUI", u"<html><head/><body><p>Maximum value on the x-axis for the plotted data.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblRange.setText(QCoreApplication.translate("LinearFitUI", u"<html><head/><body><p>Fit range</p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.txtFitRangeMin.setToolTip(QCoreApplication.translate("LinearFitUI", u"<html><head/><body><p>Enter the minimum value on the x-axis to be included in the fit.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.txtFitRangeMax.setToolTip(QCoreApplication.translate("LinearFitUI", u"<html><head/><body><p>Enter the maximum value on the x-axis to be included in the fit.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.groupBox.setTitle(QCoreApplication.translate("LinearFitUI", u"Fit parameters", None))
        self.label_3.setText(QCoreApplication.translate("LinearFitUI", u"a", None))
#if QT_CONFIG(tooltip)
        self.txtA.setToolTip(QCoreApplication.translate("LinearFitUI", u"<html><head/><body><p>Fit value for the slope parameter.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_4.setText(QCoreApplication.translate("LinearFitUI", u"b", None))
#if QT_CONFIG(tooltip)
        self.txtB.setToolTip(QCoreApplication.translate("LinearFitUI", u"<html><head/><body><p>Fit value for the constant parameter.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_7.setText(QCoreApplication.translate("LinearFitUI", u"<html><head/><body><p>\u03c7<span style=\" vertical-align:super;\">2</span>/dof</p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.txtChi2.setToolTip(QCoreApplication.translate("LinearFitUI", u"<html><head/><body><p>\u03c7<span style=\" vertical-align:super;\">2</span> over degrees of freedom.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_5.setText(QCoreApplication.translate("LinearFitUI", u"+/-", None))
#if QT_CONFIG(tooltip)
        self.txtAerr.setToolTip(QCoreApplication.translate("LinearFitUI", u"<html><head/><body><p>Error on the slope parameter.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_6.setText(QCoreApplication.translate("LinearFitUI", u"+/-", None))
#if QT_CONFIG(tooltip)
        self.txtBerr.setToolTip(QCoreApplication.translate("LinearFitUI", u"<html><head/><body><p>Error on the constant parameter.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.guinier_box.setTitle(QCoreApplication.translate("LinearFitUI", u"Guinier analysis ", None))
        self.label_11.setText(QCoreApplication.translate("LinearFitUI", u"I(q=0)", None))
        self.label_12.setText(QCoreApplication.translate("LinearFitUI", u"<html><head/><body><p>R<span style=\" vertical-align:sub;\">g </span>[\u00c5]</p></body></html>", None))
        self.label_15.setText(QCoreApplication.translate("LinearFitUI", u"<html><head/><body><p>R<span style=\" vertical-align:sub;\">g</span>*Q<span style=\" vertical-align:sub;\">max</span></p></body></html>", None))
        self.label_16.setText(QCoreApplication.translate("LinearFitUI", u"<html><head/><body><p>R<span style=\" vertical-align:sub;\">g</span>*Q<span style=\" vertical-align:sub;\">min</span></p></body></html>", None))
        self.label_13.setText(QCoreApplication.translate("LinearFitUI", u"+/-", None))
#if QT_CONFIG(tooltip)
        self.txtGuinier1_Err.setToolTip(QCoreApplication.translate("LinearFitUI", u"<html><head/><body><p>Error on the slope parameter.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_14.setText(QCoreApplication.translate("LinearFitUI", u"+/-", None))
#if QT_CONFIG(tooltip)
        self.txtGuinier2_Err.setToolTip(QCoreApplication.translate("LinearFitUI", u"<html><head/><body><p>Error on the constant parameter.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_2.setText(QCoreApplication.translate("LinearFitUI", u"<html><head/><body><p><span style=\" color:#000000;\">Resolution is NOT accounted for.<br/>Slit smeared data will give very wrong answers!</span></p></body></html>", None))
        self.cmdFit.setText(QCoreApplication.translate("LinearFitUI", u"Fit", None))
        self.cmdClose.setText(QCoreApplication.translate("LinearFitUI", u"Close", None))
    # retranslateUi

