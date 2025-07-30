# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'TabbedInvariantUI.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog, QFrame,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QRadioButton, QSizePolicy,
    QSpacerItem, QTabWidget, QVBoxLayout, QWidget)

class Ui_tabbedInvariantUI(object):
    def setupUi(self, tabbedInvariantUI):
        if not tabbedInvariantUI.objectName():
            tabbedInvariantUI.setObjectName(u"tabbedInvariantUI")
        tabbedInvariantUI.resize(544, 489)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(tabbedInvariantUI.sizePolicy().hasHeightForWidth())
        tabbedInvariantUI.setSizePolicy(sizePolicy)
        self.gridLayout_11 = QGridLayout(tabbedInvariantUI)
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.verticalSpacer = QSpacerItem(20, 2, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_11.addItem(self.verticalSpacer, 1, 0, 1, 1)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.cmdCalculate = QPushButton(tabbedInvariantUI)
        self.cmdCalculate.setObjectName(u"cmdCalculate")

        self.horizontalLayout_8.addWidget(self.cmdCalculate)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer)

        self.cmdStatus = QPushButton(tabbedInvariantUI)
        self.cmdStatus.setObjectName(u"cmdStatus")
        self.cmdStatus.setEnabled(False)

        self.horizontalLayout_8.addWidget(self.cmdStatus)

        self.cmdHelp = QPushButton(tabbedInvariantUI)
        self.cmdHelp.setObjectName(u"cmdHelp")

        self.horizontalLayout_8.addWidget(self.cmdHelp)


        self.gridLayout_11.addLayout(self.horizontalLayout_8, 2, 0, 1, 1)

        self.tabWidget = QTabWidget(tabbedInvariantUI)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabMain = QWidget()
        self.tabMain.setObjectName(u"tabMain")
        self.gridLayout_9 = QGridLayout(self.tabMain)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.groupBox = QGroupBox(self.tabMain)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.lblName = QLabel(self.groupBox)
        self.lblName.setObjectName(u"lblName")

        self.horizontalLayout_4.addWidget(self.lblName)

        self.txtName = QLineEdit(self.groupBox)
        self.txtName.setObjectName(u"txtName")
        self.txtName.setEnabled(False)
        self.txtName.setFrame(False)
        self.txtName.setReadOnly(False)

        self.horizontalLayout_4.addWidget(self.txtName)


        self.gridLayout_2.addLayout(self.horizontalLayout_4, 0, 0, 1, 1)

        self.groupBox_2 = QGroupBox(self.groupBox)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout = QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lblTotalQMin = QLabel(self.groupBox_2)
        self.lblTotalQMin.setObjectName(u"lblTotalQMin")

        self.horizontalLayout.addWidget(self.lblTotalQMin)

        self.txtTotalQMin = QLineEdit(self.groupBox_2)
        self.txtTotalQMin.setObjectName(u"txtTotalQMin")
        self.txtTotalQMin.setEnabled(True)
        self.txtTotalQMin.setReadOnly(True)

        self.horizontalLayout.addWidget(self.txtTotalQMin)

        self.lblTotalQMax = QLabel(self.groupBox_2)
        self.lblTotalQMax.setObjectName(u"lblTotalQMax")

        self.horizontalLayout.addWidget(self.lblTotalQMax)

        self.txtTotalQMax = QLineEdit(self.groupBox_2)
        self.txtTotalQMax.setObjectName(u"txtTotalQMax")
        self.txtTotalQMax.setEnabled(True)
        self.txtTotalQMax.setReadOnly(True)

        self.horizontalLayout.addWidget(self.txtTotalQMax)

        self.lblTotalQUnits = QLabel(self.groupBox_2)
        self.lblTotalQUnits.setObjectName(u"lblTotalQUnits")

        self.horizontalLayout.addWidget(self.lblTotalQUnits)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)


        self.gridLayout_2.addWidget(self.groupBox_2, 1, 0, 1, 1)


        self.gridLayout_9.addWidget(self.groupBox, 0, 0, 1, 1)

        self.groupBox_7 = QGroupBox(self.tabMain)
        self.groupBox_7.setObjectName(u"groupBox_7")
        self.gridLayout_5 = QGridLayout(self.groupBox_7)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.label_21 = QLabel(self.groupBox_7)
        self.label_21.setObjectName(u"label_21")

        self.gridLayout_5.addWidget(self.label_21, 0, 0, 1, 1)

        self.txtVolFract = QLineEdit(self.groupBox_7)
        self.txtVolFract.setObjectName(u"txtVolFract")
        self.txtVolFract.setEnabled(True)
        self.txtVolFract.setFocusPolicy(Qt.ClickFocus)
        self.txtVolFract.setAutoFillBackground(True)
        self.txtVolFract.setStyleSheet(u"")
        self.txtVolFract.setFrame(True)
        self.txtVolFract.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.txtVolFract.setReadOnly(True)

        self.gridLayout_5.addWidget(self.txtVolFract, 0, 1, 1, 1)

        self.label_20 = QLabel(self.groupBox_7)
        self.label_20.setObjectName(u"label_20")

        self.gridLayout_5.addWidget(self.label_20, 0, 2, 1, 1)

        self.txtVolFractErr = QLineEdit(self.groupBox_7)
        self.txtVolFractErr.setObjectName(u"txtVolFractErr")
        self.txtVolFractErr.setEnabled(True)
        self.txtVolFractErr.setFocusPolicy(Qt.ClickFocus)
        self.txtVolFractErr.setFrame(True)
        self.txtVolFractErr.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.txtVolFractErr.setReadOnly(True)

        self.gridLayout_5.addWidget(self.txtVolFractErr, 0, 3, 1, 1)

        self.label_22 = QLabel(self.groupBox_7)
        self.label_22.setObjectName(u"label_22")

        self.gridLayout_5.addWidget(self.label_22, 1, 0, 1, 1)

        self.txtSpecSurf = QLineEdit(self.groupBox_7)
        self.txtSpecSurf.setObjectName(u"txtSpecSurf")
        self.txtSpecSurf.setEnabled(True)
        self.txtSpecSurf.setFocusPolicy(Qt.ClickFocus)
        self.txtSpecSurf.setFrame(True)
        self.txtSpecSurf.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.txtSpecSurf.setReadOnly(True)

        self.gridLayout_5.addWidget(self.txtSpecSurf, 1, 1, 1, 1)

        self.label_23 = QLabel(self.groupBox_7)
        self.label_23.setObjectName(u"label_23")

        self.gridLayout_5.addWidget(self.label_23, 1, 2, 1, 1)

        self.txtSpecSurfErr = QLineEdit(self.groupBox_7)
        self.txtSpecSurfErr.setObjectName(u"txtSpecSurfErr")
        self.txtSpecSurfErr.setEnabled(True)
        self.txtSpecSurfErr.setFocusPolicy(Qt.ClickFocus)
        self.txtSpecSurfErr.setFrame(True)
        self.txtSpecSurfErr.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.txtSpecSurfErr.setReadOnly(True)

        self.gridLayout_5.addWidget(self.txtSpecSurfErr, 1, 3, 1, 1)

        self.lblSpecificSurfaceUnits = QLabel(self.groupBox_7)
        self.lblSpecificSurfaceUnits.setObjectName(u"lblSpecificSurfaceUnits")

        self.gridLayout_5.addWidget(self.lblSpecificSurfaceUnits, 1, 4, 1, 1)

        self.line = QFrame(self.groupBox_7)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_5.addWidget(self.line, 2, 0, 1, 5)

        self.label_25 = QLabel(self.groupBox_7)
        self.label_25.setObjectName(u"label_25")

        self.gridLayout_5.addWidget(self.label_25, 3, 0, 1, 1)

        self.txtInvariantTot = QLineEdit(self.groupBox_7)
        self.txtInvariantTot.setObjectName(u"txtInvariantTot")
        self.txtInvariantTot.setEnabled(True)
        self.txtInvariantTot.setFocusPolicy(Qt.ClickFocus)
        self.txtInvariantTot.setFrame(True)
        self.txtInvariantTot.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.txtInvariantTot.setReadOnly(True)

        self.gridLayout_5.addWidget(self.txtInvariantTot, 3, 1, 1, 1)

        self.label_26 = QLabel(self.groupBox_7)
        self.label_26.setObjectName(u"label_26")

        self.gridLayout_5.addWidget(self.label_26, 3, 2, 1, 1)

        self.txtInvariantTotErr = QLineEdit(self.groupBox_7)
        self.txtInvariantTotErr.setObjectName(u"txtInvariantTotErr")
        self.txtInvariantTotErr.setEnabled(True)
        self.txtInvariantTotErr.setFocusPolicy(Qt.ClickFocus)
        self.txtInvariantTotErr.setFrame(True)
        self.txtInvariantTotErr.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.txtInvariantTotErr.setReadOnly(True)

        self.gridLayout_5.addWidget(self.txtInvariantTotErr, 3, 3, 1, 1)

        self.lblInvariantTotalQUnits = QLabel(self.groupBox_7)
        self.lblInvariantTotalQUnits.setObjectName(u"lblInvariantTotalQUnits")

        self.gridLayout_5.addWidget(self.lblInvariantTotalQUnits, 3, 4, 1, 1)


        self.gridLayout_9.addWidget(self.groupBox_7, 1, 0, 1, 1)

        self.tabWidget.addTab(self.tabMain, "")
        self.tabOptions = QWidget()
        self.tabOptions.setObjectName(u"tabOptions")
        self.gridLayout_6 = QGridLayout(self.tabOptions)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.groupBox_3 = QGroupBox(self.tabOptions)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.gridLayout_4 = QGridLayout(self.groupBox_3)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label_5 = QLabel(self.groupBox_3)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_3.addWidget(self.label_5, 0, 0, 1, 1)

        self.txtBackgd = QLineEdit(self.groupBox_3)
        self.txtBackgd.setObjectName(u"txtBackgd")

        self.gridLayout_3.addWidget(self.txtBackgd, 0, 1, 1, 1)

        self.label_8 = QLabel(self.groupBox_3)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_3.addWidget(self.label_8, 0, 2, 1, 1)

        self.label_9 = QLabel(self.groupBox_3)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_3.addWidget(self.label_9, 0, 3, 1, 1)

        self.txtScale = QLineEdit(self.groupBox_3)
        self.txtScale.setObjectName(u"txtScale")

        self.gridLayout_3.addWidget(self.txtScale, 0, 4, 1, 1)

        self.label_6 = QLabel(self.groupBox_3)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_3.addWidget(self.label_6, 1, 0, 1, 1)

        self.txtContrast = QLineEdit(self.groupBox_3)
        self.txtContrast.setObjectName(u"txtContrast")

        self.gridLayout_3.addWidget(self.txtContrast, 1, 1, 1, 1)

        self.lblContrastUnits = QLabel(self.groupBox_3)
        self.lblContrastUnits.setObjectName(u"lblContrastUnits")

        self.gridLayout_3.addWidget(self.lblContrastUnits, 1, 2, 1, 1)

        self.label_10 = QLabel(self.groupBox_3)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout_3.addWidget(self.label_10, 1, 3, 1, 1)

        self.txtPorodCst = QLineEdit(self.groupBox_3)
        self.txtPorodCst.setObjectName(u"txtPorodCst")

        self.gridLayout_3.addWidget(self.txtPorodCst, 1, 4, 1, 1)

        self.lblPorodCstUnits = QLabel(self.groupBox_3)
        self.lblPorodCstUnits.setObjectName(u"lblPorodCstUnits")

        self.gridLayout_3.addWidget(self.lblPorodCstUnits, 1, 5, 1, 1)


        self.gridLayout_4.addLayout(self.gridLayout_3, 0, 0, 1, 1)


        self.gridLayout_6.addWidget(self.groupBox_3, 0, 0, 1, 1)

        self.groupBox_4 = QGroupBox(self.tabOptions)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.gridLayout_10 = QGridLayout(self.groupBox_4)
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_12 = QLabel(self.groupBox_4)
        self.label_12.setObjectName(u"label_12")

        self.horizontalLayout_2.addWidget(self.label_12)

        self.label_14 = QLabel(self.groupBox_4)
        self.label_14.setObjectName(u"label_14")

        self.horizontalLayout_2.addWidget(self.label_14)

        self.txtExtrapolQMin = QLineEdit(self.groupBox_4)
        self.txtExtrapolQMin.setObjectName(u"txtExtrapolQMin")
        self.txtExtrapolQMin.setEnabled(True)
        self.txtExtrapolQMin.setReadOnly(False)

        self.horizontalLayout_2.addWidget(self.txtExtrapolQMin)

        self.label_13 = QLabel(self.groupBox_4)
        self.label_13.setObjectName(u"label_13")

        self.horizontalLayout_2.addWidget(self.label_13)

        self.txtExtrapolQMax = QLineEdit(self.groupBox_4)
        self.txtExtrapolQMax.setObjectName(u"txtExtrapolQMax")
        self.txtExtrapolQMax.setEnabled(True)
        self.txtExtrapolQMax.setReadOnly(False)

        self.horizontalLayout_2.addWidget(self.txtExtrapolQMax)

        self.lblExtrapolQUnits = QLabel(self.groupBox_4)
        self.lblExtrapolQUnits.setObjectName(u"lblExtrapolQUnits")

        self.horizontalLayout_2.addWidget(self.lblExtrapolQUnits)


        self.gridLayout_10.addLayout(self.horizontalLayout_2, 0, 0, 1, 2)

        self.groupBox_lowQ = QGroupBox(self.groupBox_4)
        self.groupBox_lowQ.setObjectName(u"groupBox_lowQ")
        self.gridLayout_7 = QGridLayout(self.groupBox_lowQ)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_16 = QLabel(self.groupBox_lowQ)
        self.label_16.setObjectName(u"label_16")

        self.horizontalLayout_3.addWidget(self.label_16)

        self.txtNptsLowQ = QLineEdit(self.groupBox_lowQ)
        self.txtNptsLowQ.setObjectName(u"txtNptsLowQ")

        self.horizontalLayout_3.addWidget(self.txtNptsLowQ)


        self.gridLayout_7.addLayout(self.horizontalLayout_3, 1, 0, 1, 2)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.rbGuinier = QRadioButton(self.groupBox_lowQ)
        self.rbGuinier.setObjectName(u"rbGuinier")
        self.rbGuinier.setChecked(True)
        self.rbGuinier.setAutoExclusive(False)

        self.verticalLayout_2.addWidget(self.rbGuinier)

        self.rbPowerLawLowQ = QRadioButton(self.groupBox_lowQ)
        self.rbPowerLawLowQ.setObjectName(u"rbPowerLawLowQ")
        self.rbPowerLawLowQ.setChecked(False)
        self.rbPowerLawLowQ.setAutoExclusive(False)

        self.verticalLayout_2.addWidget(self.rbPowerLawLowQ)


        self.gridLayout_7.addLayout(self.verticalLayout_2, 2, 0, 1, 1)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_17 = QLabel(self.groupBox_lowQ)
        self.label_17.setObjectName(u"label_17")

        self.horizontalLayout_6.addWidget(self.label_17)

        self.txtPowerLowQ = QLineEdit(self.groupBox_lowQ)
        self.txtPowerLowQ.setObjectName(u"txtPowerLowQ")

        self.horizontalLayout_6.addWidget(self.txtPowerLowQ)


        self.gridLayout_7.addLayout(self.horizontalLayout_6, 3, 0, 1, 2)

        self.chkLowQ = QCheckBox(self.groupBox_lowQ)
        self.chkLowQ.setObjectName(u"chkLowQ")

        self.gridLayout_7.addWidget(self.chkLowQ, 0, 0, 1, 2)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.rbFitLowQ = QRadioButton(self.groupBox_lowQ)
        self.rbFitLowQ.setObjectName(u"rbFitLowQ")
        self.rbFitLowQ.setEnabled(True)
        self.rbFitLowQ.setCheckable(True)
        self.rbFitLowQ.setChecked(True)
        self.rbFitLowQ.setAutoExclusive(True)

        self.verticalLayout.addWidget(self.rbFitLowQ)

        self.rbFixLowQ = QRadioButton(self.groupBox_lowQ)
        self.rbFixLowQ.setObjectName(u"rbFixLowQ")
        self.rbFixLowQ.setCheckable(True)
        self.rbFixLowQ.setChecked(False)
        self.rbFixLowQ.setAutoExclusive(True)

        self.verticalLayout.addWidget(self.rbFixLowQ)


        self.gridLayout_7.addLayout(self.verticalLayout, 2, 1, 1, 1)


        self.gridLayout_10.addWidget(self.groupBox_lowQ, 1, 0, 1, 1)

        self.groupBox_highQ = QGroupBox(self.groupBox_4)
        self.groupBox_highQ.setObjectName(u"groupBox_highQ")
        self.gridLayout_8 = QGridLayout(self.groupBox_highQ)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.chkHighQ = QCheckBox(self.groupBox_highQ)
        self.chkHighQ.setObjectName(u"chkHighQ")

        self.gridLayout_8.addWidget(self.chkHighQ, 0, 0, 1, 1)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_18 = QLabel(self.groupBox_highQ)
        self.label_18.setObjectName(u"label_18")

        self.horizontalLayout_5.addWidget(self.label_18)

        self.txtNptsHighQ = QLineEdit(self.groupBox_highQ)
        self.txtNptsHighQ.setObjectName(u"txtNptsHighQ")

        self.horizontalLayout_5.addWidget(self.txtNptsHighQ)


        self.gridLayout_8.addLayout(self.horizontalLayout_5, 1, 0, 1, 1)

        self.gridLayout_13 = QGridLayout()
        self.gridLayout_13.setObjectName(u"gridLayout_13")
        self.rbFitHighQ = QRadioButton(self.groupBox_highQ)
        self.rbFitHighQ.setObjectName(u"rbFitHighQ")
        self.rbFitHighQ.setCheckable(True)
        self.rbFitHighQ.setChecked(False)

        self.gridLayout_13.addWidget(self.rbFitHighQ, 0, 0, 1, 1)

        self.rbFixHighQ = QRadioButton(self.groupBox_highQ)
        self.rbFixHighQ.setObjectName(u"rbFixHighQ")
        self.rbFixHighQ.setChecked(True)

        self.gridLayout_13.addWidget(self.rbFixHighQ, 1, 0, 1, 1)


        self.gridLayout_8.addLayout(self.gridLayout_13, 2, 0, 1, 1)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_19 = QLabel(self.groupBox_highQ)
        self.label_19.setObjectName(u"label_19")

        self.horizontalLayout_7.addWidget(self.label_19)

        self.txtPowerHighQ = QLineEdit(self.groupBox_highQ)
        self.txtPowerHighQ.setObjectName(u"txtPowerHighQ")

        self.horizontalLayout_7.addWidget(self.txtPowerHighQ)


        self.gridLayout_8.addLayout(self.horizontalLayout_7, 3, 0, 1, 1)


        self.gridLayout_10.addWidget(self.groupBox_highQ, 1, 1, 1, 1)


        self.gridLayout_6.addWidget(self.groupBox_4, 1, 0, 1, 1)

        self.tabWidget.addTab(self.tabOptions, "")

        self.gridLayout_11.addWidget(self.tabWidget, 0, 0, 1, 1)

        QWidget.setTabOrder(self.tabWidget, self.txtName)
        QWidget.setTabOrder(self.txtName, self.txtTotalQMin)
        QWidget.setTabOrder(self.txtTotalQMin, self.txtTotalQMax)
        QWidget.setTabOrder(self.txtTotalQMax, self.txtVolFract)
        QWidget.setTabOrder(self.txtVolFract, self.txtVolFractErr)
        QWidget.setTabOrder(self.txtVolFractErr, self.txtSpecSurf)
        QWidget.setTabOrder(self.txtSpecSurf, self.txtSpecSurfErr)
        QWidget.setTabOrder(self.txtSpecSurfErr, self.txtInvariantTot)
        QWidget.setTabOrder(self.txtInvariantTot, self.txtInvariantTotErr)
        QWidget.setTabOrder(self.txtInvariantTotErr, self.cmdCalculate)
        QWidget.setTabOrder(self.cmdCalculate, self.cmdStatus)
        QWidget.setTabOrder(self.cmdStatus, self.cmdHelp)
        QWidget.setTabOrder(self.cmdHelp, self.txtBackgd)
        QWidget.setTabOrder(self.txtBackgd, self.txtScale)
        QWidget.setTabOrder(self.txtScale, self.txtContrast)
        QWidget.setTabOrder(self.txtContrast, self.txtPorodCst)
        QWidget.setTabOrder(self.txtPorodCst, self.txtExtrapolQMin)
        QWidget.setTabOrder(self.txtExtrapolQMin, self.txtExtrapolQMax)
        QWidget.setTabOrder(self.txtExtrapolQMax, self.chkLowQ)
        QWidget.setTabOrder(self.chkLowQ, self.txtNptsLowQ)
        QWidget.setTabOrder(self.txtNptsLowQ, self.chkHighQ)
        QWidget.setTabOrder(self.chkHighQ, self.txtNptsHighQ)
        QWidget.setTabOrder(self.txtNptsHighQ, self.rbGuinier)
        QWidget.setTabOrder(self.rbGuinier, self.rbFitLowQ)
        QWidget.setTabOrder(self.rbFitLowQ, self.rbFitHighQ)
        QWidget.setTabOrder(self.rbFitHighQ, self.rbPowerLawLowQ)
        QWidget.setTabOrder(self.rbPowerLawLowQ, self.rbFixLowQ)
        QWidget.setTabOrder(self.rbFixLowQ, self.rbFixHighQ)
        QWidget.setTabOrder(self.rbFixHighQ, self.txtPowerLowQ)
        QWidget.setTabOrder(self.txtPowerLowQ, self.txtPowerHighQ)

        self.retranslateUi(tabbedInvariantUI)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(tabbedInvariantUI)
    # setupUi

    def retranslateUi(self, tabbedInvariantUI):
        tabbedInvariantUI.setWindowTitle(QCoreApplication.translate("tabbedInvariantUI", u"Dialog", None))
#if QT_CONFIG(tooltip)
        self.cmdCalculate.setToolTip(QCoreApplication.translate("tabbedInvariantUI", u"Compute invariant", None))
#endif // QT_CONFIG(tooltip)
        self.cmdCalculate.setText(QCoreApplication.translate("tabbedInvariantUI", u"Calculate", None))
#if QT_CONFIG(tooltip)
        self.cmdStatus.setToolTip(QCoreApplication.translate("tabbedInvariantUI", u"Get more details of computation such as fraction from extrapolation", None))
#endif // QT_CONFIG(tooltip)
        self.cmdStatus.setText(QCoreApplication.translate("tabbedInvariantUI", u"Status", None))
#if QT_CONFIG(tooltip)
        self.cmdHelp.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.cmdHelp.setText(QCoreApplication.translate("tabbedInvariantUI", u"Help", None))
        self.groupBox.setTitle(QCoreApplication.translate("tabbedInvariantUI", u"I(q) data source", None))
        self.lblName.setText(QCoreApplication.translate("tabbedInvariantUI", u"Name:", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("tabbedInvariantUI", u"Total Q range", None))
        self.lblTotalQMin.setText(QCoreApplication.translate("tabbedInvariantUI", u"Min:", None))
        self.lblTotalQMax.setText(QCoreApplication.translate("tabbedInvariantUI", u"Max:", None))
        self.lblTotalQUnits.setText(QCoreApplication.translate("tabbedInvariantUI", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.groupBox_7.setTitle(QCoreApplication.translate("tabbedInvariantUI", u"Output", None))
        self.label_21.setText(QCoreApplication.translate("tabbedInvariantUI", u"Volume fraction:", None))
        self.label_20.setText(QCoreApplication.translate("tabbedInvariantUI", u"+/-", None))
        self.label_22.setText(QCoreApplication.translate("tabbedInvariantUI", u"Specific Surface:", None))
        self.label_23.setText(QCoreApplication.translate("tabbedInvariantUI", u"+/-", None))
        self.lblSpecificSurfaceUnits.setText(QCoreApplication.translate("tabbedInvariantUI", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.label_25.setText(QCoreApplication.translate("tabbedInvariantUI", u"Invariant Total [Q]:", None))
#if QT_CONFIG(tooltip)
        self.txtInvariantTot.setToolTip(QCoreApplication.translate("tabbedInvariantUI", u"Total invariant [Q*], including extrapolated regions.", None))
#endif // QT_CONFIG(tooltip)
        self.label_26.setText(QCoreApplication.translate("tabbedInvariantUI", u"+/-", None))
        self.lblInvariantTotalQUnits.setText(QCoreApplication.translate("tabbedInvariantUI", u"<html><head/><body><p>(cm \u00c5<span style=\" vertical-align:super;\">3</span>)<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabMain), QCoreApplication.translate("tabbedInvariantUI", u"Invariant", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("tabbedInvariantUI", u"Customized input", None))
        self.label_5.setText(QCoreApplication.translate("tabbedInvariantUI", u"Background:", None))
        self.label_8.setText(QCoreApplication.translate("tabbedInvariantUI", u"<html><head/><body><p>cm<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.label_9.setText(QCoreApplication.translate("tabbedInvariantUI", u"Scale:", None))
        self.label_6.setText(QCoreApplication.translate("tabbedInvariantUI", u"Contrast:", None))
        self.lblContrastUnits.setText(QCoreApplication.translate("tabbedInvariantUI", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-2</span></p></body></html>", None))
        self.label_10.setText(QCoreApplication.translate("tabbedInvariantUI", u"<html><head/><body><p>Porod<br/>constant:</p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.txtPorodCst.setToolTip(QCoreApplication.translate("tabbedInvariantUI", u"Porod constant (optional)", None))
#endif // QT_CONFIG(tooltip)
        self.lblPorodCstUnits.setText(QCoreApplication.translate("tabbedInvariantUI", u"<html><head/><body><p>(cm \u00c5<span style=\" vertical-align:super;\">4</span>)<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("tabbedInvariantUI", u"Extrapolation", None))
        self.label_12.setText(QCoreApplication.translate("tabbedInvariantUI", u"Q Range:", None))
        self.label_14.setText(QCoreApplication.translate("tabbedInvariantUI", u"Min", None))
#if QT_CONFIG(tooltip)
        self.txtExtrapolQMin.setToolTip(QCoreApplication.translate("tabbedInvariantUI", u"The minimum extrapolated q value.", None))
#endif // QT_CONFIG(tooltip)
        self.label_13.setText(QCoreApplication.translate("tabbedInvariantUI", u"Max", None))
        self.lblExtrapolQUnits.setText(QCoreApplication.translate("tabbedInvariantUI", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.groupBox_lowQ.setTitle(QCoreApplication.translate("tabbedInvariantUI", u"Low Q", None))
        self.label_16.setText(QCoreApplication.translate("tabbedInvariantUI", u"Npts:", None))
#if QT_CONFIG(tooltip)
        self.txtNptsLowQ.setToolTip(QCoreApplication.translate("tabbedInvariantUI", u"Number of Q points to consider\n"
"while extrapolating the low-Q region", None))
#endif // QT_CONFIG(tooltip)
        self.rbGuinier.setText(QCoreApplication.translate("tabbedInvariantUI", u"Guinier", None))
        self.rbPowerLawLowQ.setText(QCoreApplication.translate("tabbedInvariantUI", u"Power law", None))
        self.label_17.setText(QCoreApplication.translate("tabbedInvariantUI", u"Power:", None))
#if QT_CONFIG(tooltip)
        self.txtPowerLowQ.setToolTip(QCoreApplication.translate("tabbedInvariantUI", u"Exponent to apply to the Power_law function.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.chkLowQ.setToolTip(QCoreApplication.translate("tabbedInvariantUI", u"Check to extrapolate data at low-Q", None))
#endif // QT_CONFIG(tooltip)
        self.chkLowQ.setText(QCoreApplication.translate("tabbedInvariantUI", u"Enable Low-Q extrapolation", None))
        self.rbFitLowQ.setText(QCoreApplication.translate("tabbedInvariantUI", u"Fit", None))
        self.rbFixLowQ.setText(QCoreApplication.translate("tabbedInvariantUI", u"Fix", None))
        self.groupBox_highQ.setTitle(QCoreApplication.translate("tabbedInvariantUI", u"High Q", None))
#if QT_CONFIG(tooltip)
        self.chkHighQ.setToolTip(QCoreApplication.translate("tabbedInvariantUI", u"Check to extrapolate data at high-Q", None))
#endif // QT_CONFIG(tooltip)
        self.chkHighQ.setText(QCoreApplication.translate("tabbedInvariantUI", u"Enable High-Q extrapolation", None))
        self.label_18.setText(QCoreApplication.translate("tabbedInvariantUI", u"Npts:", None))
#if QT_CONFIG(tooltip)
        self.txtNptsHighQ.setToolTip(QCoreApplication.translate("tabbedInvariantUI", u"Number of Q points to consider\n"
" while extrapolating the high-Q region", None))
#endif // QT_CONFIG(tooltip)
        self.rbFitHighQ.setText(QCoreApplication.translate("tabbedInvariantUI", u"Fit", None))
        self.rbFixHighQ.setText(QCoreApplication.translate("tabbedInvariantUI", u"Fix", None))
        self.label_19.setText(QCoreApplication.translate("tabbedInvariantUI", u"Power:", None))
#if QT_CONFIG(tooltip)
        self.txtPowerHighQ.setToolTip(QCoreApplication.translate("tabbedInvariantUI", u"Exponent to apply to the Power_law function.", None))
#endif // QT_CONFIG(tooltip)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabOptions), QCoreApplication.translate("tabbedInvariantUI", u"Options", None))
    # retranslateUi

