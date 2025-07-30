# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'CorfuncPanel.ui'
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
from PySide6.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QDialog,
    QFrame, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLayout, QLineEdit, QPushButton,
    QRadioButton, QScrollArea, QSizePolicy, QSpacerItem,
    QTabWidget, QVBoxLayout, QWidget)

class Ui_CorfuncDialog(object):
    def setupUi(self, CorfuncDialog):
        if not CorfuncDialog.objectName():
            CorfuncDialog.setObjectName(u"CorfuncDialog")
        CorfuncDialog.resize(1157, 885)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(CorfuncDialog.sizePolicy().hasHeightForWidth())
        CorfuncDialog.setSizePolicy(sizePolicy)
        self.horizontalLayout_3 = QHBoxLayout(CorfuncDialog)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.scrollArea = QScrollArea(CorfuncDialog)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setFrameShadow(QFrame.Plain)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 581, 871))
        self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.controlWidget = QWidget(self.scrollAreaWidgetContents)
        self.controlWidget.setObjectName(u"controlWidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.controlWidget.sizePolicy().hasHeightForWidth())
        self.controlWidget.setSizePolicy(sizePolicy1)
        self.controlWidget.setMinimumSize(QSize(581, 0))
        self.verticalLayout_2 = QVBoxLayout(self.controlWidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.verticalLayout_3.setContentsMargins(-1, -1, -1, 0)
        self.groupBox = QGroupBox(self.controlWidget)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy2)
        self.gridLayout_6 = QGridLayout(self.groupBox)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.frame_5 = QFrame(self.groupBox)
        self.frame_5.setObjectName(u"frame_5")
        self.gridLayout_7 = QGridLayout(self.frame_5)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.label_20 = QLabel(self.frame_5)
        self.label_20.setObjectName(u"label_20")
        self.label_20.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_7.addWidget(self.label_20, 1, 0, 1, 1)

        self.label_18 = QLabel(self.frame_5)
        self.label_18.setObjectName(u"label_18")
        self.label_18.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_7.addWidget(self.label_18, 0, 0, 1, 1)

        self.label_21 = QLabel(self.frame_5)
        self.label_21.setObjectName(u"label_21")
        self.label_21.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_7.addWidget(self.label_21, 2, 0, 1, 1)

        self.radTangentInflection = QRadioButton(self.frame_5)
        self.buttonGroup_2 = QButtonGroup(CorfuncDialog)
        self.buttonGroup_2.setObjectName(u"buttonGroup_2")
        self.buttonGroup_2.addButton(self.radTangentInflection)
        self.radTangentInflection.setObjectName(u"radTangentInflection")

        self.gridLayout_7.addWidget(self.radTangentInflection, 1, 1, 1, 1)

        self.fitPorod = QCheckBox(self.frame_5)
        self.fitPorod.setObjectName(u"fitPorod")
        self.fitPorod.setChecked(True)

        self.gridLayout_7.addWidget(self.fitPorod, 0, 3, 1, 1)

        self.fitBackground = QCheckBox(self.frame_5)
        self.fitBackground.setObjectName(u"fitBackground")
        self.fitBackground.setChecked(True)

        self.gridLayout_7.addWidget(self.fitBackground, 0, 1, 1, 1)

        self.radTangentMidpoint = QRadioButton(self.frame_5)
        self.buttonGroup_2.addButton(self.radTangentMidpoint)
        self.radTangentMidpoint.setObjectName(u"radTangentMidpoint")

        self.gridLayout_7.addWidget(self.radTangentMidpoint, 1, 2, 1, 1)

        self.radLongPeriodAuto = QRadioButton(self.frame_5)
        self.buttonGroup = QButtonGroup(CorfuncDialog)
        self.buttonGroup.setObjectName(u"buttonGroup")
        self.buttonGroup.addButton(self.radLongPeriodAuto)
        self.radLongPeriodAuto.setObjectName(u"radLongPeriodAuto")
        self.radLongPeriodAuto.setChecked(True)

        self.gridLayout_7.addWidget(self.radLongPeriodAuto, 2, 3, 1, 1)

        self.radTangentAuto = QRadioButton(self.frame_5)
        self.buttonGroup_2.addButton(self.radTangentAuto)
        self.radTangentAuto.setObjectName(u"radTangentAuto")
        self.radTangentAuto.setChecked(True)

        self.gridLayout_7.addWidget(self.radTangentAuto, 1, 3, 1, 1)

        self.radLongPeriodDouble = QRadioButton(self.frame_5)
        self.buttonGroup.addButton(self.radLongPeriodDouble)
        self.radLongPeriodDouble.setObjectName(u"radLongPeriodDouble")

        self.gridLayout_7.addWidget(self.radLongPeriodDouble, 2, 2, 1, 1)

        self.fitGuinier = QCheckBox(self.frame_5)
        self.fitGuinier.setObjectName(u"fitGuinier")
        self.fitGuinier.setChecked(True)

        self.gridLayout_7.addWidget(self.fitGuinier, 0, 2, 1, 1)

        self.radLongPeriodMax = QRadioButton(self.frame_5)
        self.buttonGroup.addButton(self.radLongPeriodMax)
        self.radLongPeriodMax.setObjectName(u"radLongPeriodMax")

        self.gridLayout_7.addWidget(self.radLongPeriodMax, 2, 1, 1, 1)


        self.gridLayout_6.addWidget(self.frame_5, 4, 0, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.lblName = QLabel(self.groupBox)
        self.lblName.setObjectName(u"lblName")

        self.horizontalLayout_4.addWidget(self.lblName)

        self.txtFilename = QLineEdit(self.groupBox)
        self.txtFilename.setObjectName(u"txtFilename")
        self.txtFilename.setEnabled(False)
        sizePolicy2.setHeightForWidth(self.txtFilename.sizePolicy().hasHeightForWidth())
        self.txtFilename.setSizePolicy(sizePolicy2)
        self.txtFilename.setFrame(False)
        self.txtFilename.setReadOnly(False)

        self.horizontalLayout_4.addWidget(self.txtFilename)


        self.gridLayout_6.addLayout(self.horizontalLayout_4, 0, 0, 1, 1)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(-1, -1, -1, 0)
        self.lblTotalQUnits_2 = QLabel(self.groupBox)
        self.lblTotalQUnits_2.setObjectName(u"lblTotalQUnits_2")

        self.gridLayout.addWidget(self.lblTotalQUnits_2, 0, 6, 1, 1)

        self.txtUpperQMin = QLineEdit(self.groupBox)
        self.txtUpperQMin.setObjectName(u"txtUpperQMin")
        self.txtUpperQMin.setEnabled(True)
        sizePolicy2.setHeightForWidth(self.txtUpperQMin.sizePolicy().hasHeightForWidth())
        self.txtUpperQMin.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.txtUpperQMin, 0, 3, 1, 1)

        self.lblTotalQMin_2 = QLabel(self.groupBox)
        self.lblTotalQMin_2.setObjectName(u"lblTotalQMin_2")
        self.lblTotalQMin_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.lblTotalQMin_2, 0, 2, 1, 1)

        self.lblTotalQMax_2 = QLabel(self.groupBox)
        self.lblTotalQMax_2.setObjectName(u"lblTotalQMax_2")
        self.lblTotalQMax_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.lblTotalQMax_2, 0, 4, 1, 1)

        self.txtUpperQMax = QLineEdit(self.groupBox)
        self.txtUpperQMax.setObjectName(u"txtUpperQMax")
        self.txtUpperQMax.setEnabled(True)
        sizePolicy2.setHeightForWidth(self.txtUpperQMax.sizePolicy().hasHeightForWidth())
        self.txtUpperQMax.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.txtUpperQMax, 0, 5, 1, 1)

        self.lblTotalQMax = QLabel(self.groupBox)
        self.lblTotalQMax.setObjectName(u"lblTotalQMax")
        self.lblTotalQMax.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.lblTotalQMax, 0, 0, 1, 1)

        self.txtLowerQMax = QLineEdit(self.groupBox)
        self.txtLowerQMax.setObjectName(u"txtLowerQMax")
        self.txtLowerQMax.setEnabled(True)
        sizePolicy2.setHeightForWidth(self.txtLowerQMax.sizePolicy().hasHeightForWidth())
        self.txtLowerQMax.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.txtLowerQMax, 0, 1, 1, 1)


        self.gridLayout_6.addLayout(self.gridLayout, 2, 0, 1, 1)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(-1, 10, -1, 10)
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer_2)

        self.cmdExtract = QPushButton(self.groupBox)
        self.cmdExtract.setObjectName(u"cmdExtract")
        sizePolicy1.setHeightForWidth(self.cmdExtract.sizePolicy().hasHeightForWidth())
        self.cmdExtract.setSizePolicy(sizePolicy1)
        self.cmdExtract.setMinimumSize(QSize(120, 0))

        self.horizontalLayout_7.addWidget(self.cmdExtract)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer_3)


        self.gridLayout_6.addLayout(self.horizontalLayout_7, 5, 0, 1, 1)

        self.sliderLayout = QHBoxLayout()
        self.sliderLayout.setObjectName(u"sliderLayout")
        self.sliderLayout.setContentsMargins(5, 10, 5, 10)
        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.sliderLayout.addWidget(self.label_3)


        self.gridLayout_6.addLayout(self.sliderLayout, 1, 0, 1, 1)


        self.verticalLayout_3.addWidget(self.groupBox)

        self.groupBox_4 = QGroupBox(self.controlWidget)
        self.groupBox_4.setObjectName(u"groupBox_4")
        sizePolicy2.setHeightForWidth(self.groupBox_4.sizePolicy().hasHeightForWidth())
        self.groupBox_4.setSizePolicy(sizePolicy2)
        self.backgroundLayout = QVBoxLayout(self.groupBox_4)
        self.backgroundLayout.setObjectName(u"backgroundLayout")
        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.txtBackground = QLineEdit(self.groupBox_4)
        self.txtBackground.setObjectName(u"txtBackground")
        sizePolicy2.setHeightForWidth(self.txtBackground.sizePolicy().hasHeightForWidth())
        self.txtBackground.setSizePolicy(sizePolicy2)

        self.gridLayout_4.addWidget(self.txtBackground, 0, 1, 1, 1)

        self.label = QLabel(self.groupBox_4)
        self.label.setObjectName(u"label")

        self.gridLayout_4.addWidget(self.label, 0, 0, 1, 1)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_4, 0, 2, 1, 1)


        self.backgroundLayout.addLayout(self.gridLayout_4)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout_5.setContentsMargins(-1, -1, -1, 0)
        self.txtGuinierB = QLineEdit(self.groupBox_4)
        self.txtGuinierB.setObjectName(u"txtGuinierB")
        self.txtGuinierB.setReadOnly(False)

        self.gridLayout_5.addWidget(self.txtGuinierB, 3, 4, 1, 1)

        self.label_8 = QLabel(self.groupBox_4)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_5.addWidget(self.label_8, 3, 0, 1, 1)

        self.label_7 = QLabel(self.groupBox_4)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_5.addWidget(self.label_7, 3, 3, 1, 1)

        self.label_10 = QLabel(self.groupBox_4)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout_5.addWidget(self.label_10, 4, 1, 1, 1)

        self.txtPorodK = QLineEdit(self.groupBox_4)
        self.txtPorodK.setObjectName(u"txtPorodK")
        self.txtPorodK.setReadOnly(False)

        self.gridLayout_5.addWidget(self.txtPorodK, 4, 2, 1, 1)

        self.label_6 = QLabel(self.groupBox_4)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_5.addWidget(self.label_6, 3, 1, 1, 1)

        self.txtGuinierA = QLineEdit(self.groupBox_4)
        self.txtGuinierA.setObjectName(u"txtGuinierA")
        self.txtGuinierA.setReadOnly(False)

        self.gridLayout_5.addWidget(self.txtGuinierA, 3, 2, 1, 1)

        self.label_9 = QLabel(self.groupBox_4)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_5.addWidget(self.label_9, 4, 0, 1, 1)

        self.txtPorodSigma = QLineEdit(self.groupBox_4)
        self.txtPorodSigma.setObjectName(u"txtPorodSigma")
        self.txtPorodSigma.setReadOnly(False)

        self.gridLayout_5.addWidget(self.txtPorodSigma, 4, 4, 1, 1)

        self.label_11 = QLabel(self.groupBox_4)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_5.addWidget(self.label_11, 4, 3, 1, 1)


        self.gridLayout_2.addLayout(self.gridLayout_5, 5, 0, 1, 2)


        self.backgroundLayout.addLayout(self.gridLayout_2)


        self.verticalLayout_3.addWidget(self.groupBox_4)

        self.groupBox_3 = QGroupBox(self.controlWidget)
        self.groupBox_3.setObjectName(u"groupBox_3")
        sizePolicy2.setHeightForWidth(self.groupBox_3.sizePolicy().hasHeightForWidth())
        self.groupBox_3.setSizePolicy(sizePolicy2)
        self.gridLayout_3 = QGridLayout(self.groupBox_3)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_8 = QGridLayout()
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.gridLayout_8.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.gridLayout_8.setVerticalSpacing(10)
        self.gridLayout_8.setContentsMargins(-1, -1, -1, 0)
        self.label_13 = QLabel(self.groupBox_3)
        self.label_13.setObjectName(u"label_13")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_13.sizePolicy().hasHeightForWidth())
        self.label_13.setSizePolicy(sizePolicy3)
        self.label_13.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_8.addWidget(self.label_13, 2, 3, 1, 1)

        self.txtPolyRyan = QLineEdit(self.groupBox_3)
        self.txtPolyRyan.setObjectName(u"txtPolyRyan")
        self.txtPolyRyan.setReadOnly(True)

        self.gridLayout_8.addWidget(self.txtPolyRyan, 2, 2, 1, 1)

        self.txtAvgHardBlock = QLineEdit(self.groupBox_3)
        self.txtAvgHardBlock.setObjectName(u"txtAvgHardBlock")
        sizePolicy2.setHeightForWidth(self.txtAvgHardBlock.sizePolicy().hasHeightForWidth())
        self.txtAvgHardBlock.setSizePolicy(sizePolicy2)
        self.txtAvgHardBlock.setMinimumSize(QSize(20, 20))
        self.txtAvgHardBlock.setReadOnly(True)

        self.gridLayout_8.addWidget(self.txtAvgHardBlock, 0, 2, 1, 1)

        self.label_12 = QLabel(self.groupBox_3)
        self.label_12.setObjectName(u"label_12")
        sizePolicy3.setHeightForWidth(self.label_12.sizePolicy().hasHeightForWidth())
        self.label_12.setSizePolicy(sizePolicy3)
        self.label_12.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_8.addWidget(self.label_12, 2, 1, 1, 1)

        self.txtPolyStribeck = QLineEdit(self.groupBox_3)
        self.txtPolyStribeck.setObjectName(u"txtPolyStribeck")
        self.txtPolyStribeck.setReadOnly(True)

        self.gridLayout_8.addWidget(self.txtPolyStribeck, 2, 4, 1, 1)

        self.label_16 = QLabel(self.groupBox_3)
        self.label_16.setObjectName(u"label_16")
        sizePolicy3.setHeightForWidth(self.label_16.sizePolicy().hasHeightForWidth())
        self.label_16.setSizePolicy(sizePolicy3)
        self.label_16.setMinimumSize(QSize(20, 20))
        self.label_16.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_8.addWidget(self.label_16, 0, 1, 1, 1)

        self.label_4 = QLabel(self.groupBox_3)
        self.label_4.setObjectName(u"label_4")
        sizePolicy3.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy3)
        self.label_4.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_8.addWidget(self.label_4, 0, 0, 1, 1)

        self.label_2 = QLabel(self.groupBox_3)
        self.label_2.setObjectName(u"label_2")
        sizePolicy2.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy2)
        self.label_2.setMinimumSize(QSize(20, 20))
        self.label_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_8.addWidget(self.label_2, 0, 3, 1, 1)

        self.txtAvgSoftBlock = QLineEdit(self.groupBox_3)
        self.txtAvgSoftBlock.setObjectName(u"txtAvgSoftBlock")
        sizePolicy2.setHeightForWidth(self.txtAvgSoftBlock.sizePolicy().hasHeightForWidth())
        self.txtAvgSoftBlock.setSizePolicy(sizePolicy2)
        self.txtAvgSoftBlock.setMinimumSize(QSize(20, 20))
        self.txtAvgSoftBlock.setReadOnly(True)

        self.gridLayout_8.addWidget(self.txtAvgSoftBlock, 0, 4, 1, 1)

        self.label_5 = QLabel(self.groupBox_3)
        self.label_5.setObjectName(u"label_5")
        sizePolicy3.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy3)
        self.label_5.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_8.addWidget(self.label_5, 2, 0, 1, 1)

        self.label_15 = QLabel(self.groupBox_3)
        self.label_15.setObjectName(u"label_15")
        sizePolicy3.setHeightForWidth(self.label_15.sizePolicy().hasHeightForWidth())
        self.label_15.setSizePolicy(sizePolicy3)
        self.label_15.setMinimumSize(QSize(20, 20))
        self.label_15.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_8.addWidget(self.label_15, 1, 1, 1, 1)

        self.label_17 = QLabel(self.groupBox_3)
        self.label_17.setObjectName(u"label_17")
        sizePolicy2.setHeightForWidth(self.label_17.sizePolicy().hasHeightForWidth())
        self.label_17.setSizePolicy(sizePolicy2)
        self.label_17.setMinimumSize(QSize(20, 20))
        self.label_17.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_8.addWidget(self.label_17, 1, 3, 1, 1)

        self.txtAvgIntThick = QLineEdit(self.groupBox_3)
        self.txtAvgIntThick.setObjectName(u"txtAvgIntThick")
        sizePolicy2.setHeightForWidth(self.txtAvgIntThick.sizePolicy().hasHeightForWidth())
        self.txtAvgIntThick.setSizePolicy(sizePolicy2)
        self.txtAvgIntThick.setMinimumSize(QSize(20, 20))
        self.txtAvgIntThick.setReadOnly(True)

        self.gridLayout_8.addWidget(self.txtAvgIntThick, 1, 2, 1, 1)

        self.txtAvgCoreThick = QLineEdit(self.groupBox_3)
        self.txtAvgCoreThick.setObjectName(u"txtAvgCoreThick")
        sizePolicy2.setHeightForWidth(self.txtAvgCoreThick.sizePolicy().hasHeightForWidth())
        self.txtAvgCoreThick.setSizePolicy(sizePolicy2)
        self.txtAvgCoreThick.setMinimumSize(QSize(20, 20))
        self.txtAvgCoreThick.setReadOnly(True)

        self.gridLayout_8.addWidget(self.txtAvgCoreThick, 1, 4, 1, 1)


        self.gridLayout_3.addLayout(self.gridLayout_8, 1, 0, 1, 1)

        self.gridLayout_9 = QGridLayout()
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.gridLayout_9.setContentsMargins(-1, -1, -1, 0)
        self.label_14 = QLabel(self.groupBox_3)
        self.label_14.setObjectName(u"label_14")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.label_14.sizePolicy().hasHeightForWidth())
        self.label_14.setSizePolicy(sizePolicy4)
        self.label_14.setMinimumSize(QSize(20, 20))
        self.label_14.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_9.addWidget(self.label_14, 0, 0, 1, 1)

        self.txtLongPeriod = QLineEdit(self.groupBox_3)
        self.txtLongPeriod.setObjectName(u"txtLongPeriod")
        sizePolicy2.setHeightForWidth(self.txtLongPeriod.sizePolicy().hasHeightForWidth())
        self.txtLongPeriod.setSizePolicy(sizePolicy2)
        self.txtLongPeriod.setMinimumSize(QSize(150, 20))
        self.txtLongPeriod.setReadOnly(True)

        self.gridLayout_9.addWidget(self.txtLongPeriod, 0, 1, 1, 1)

        self.label_19 = QLabel(self.groupBox_3)
        self.label_19.setObjectName(u"label_19")
        sizePolicy4.setHeightForWidth(self.label_19.sizePolicy().hasHeightForWidth())
        self.label_19.setSizePolicy(sizePolicy4)
        self.label_19.setMinimumSize(QSize(20, 20))
        self.label_19.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_9.addWidget(self.label_19, 0, 2, 1, 1)

        self.txtLocalCrystal = QLineEdit(self.groupBox_3)
        self.txtLocalCrystal.setObjectName(u"txtLocalCrystal")
        sizePolicy2.setHeightForWidth(self.txtLocalCrystal.sizePolicy().hasHeightForWidth())
        self.txtLocalCrystal.setSizePolicy(sizePolicy2)
        self.txtLocalCrystal.setMinimumSize(QSize(150, 20))
        self.txtLocalCrystal.setReadOnly(True)

        self.gridLayout_9.addWidget(self.txtLocalCrystal, 0, 3, 1, 1)


        self.gridLayout_3.addLayout(self.gridLayout_9, 2, 0, 1, 1)


        self.verticalLayout_3.addWidget(self.groupBox_3)

        self.groupBox_2 = QGroupBox(self.controlWidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        sizePolicy2.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy2)
        self.horizontalLayout_2 = QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.cmdSaveExtrapolation = QPushButton(self.groupBox_2)
        self.cmdSaveExtrapolation.setObjectName(u"cmdSaveExtrapolation")

        self.horizontalLayout_2.addWidget(self.cmdSaveExtrapolation)

        self.cmdSave = QPushButton(self.groupBox_2)
        self.cmdSave.setObjectName(u"cmdSave")
        sizePolicy3.setHeightForWidth(self.cmdSave.sizePolicy().hasHeightForWidth())
        self.cmdSave.setSizePolicy(sizePolicy3)

        self.horizontalLayout_2.addWidget(self.cmdSave)


        self.verticalLayout_3.addWidget(self.groupBox_2)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_3)

        self.verticalSpacer = QSpacerItem(20, 1, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalSpacer = QSpacerItem(40, 2, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer)

        self.cmdHelp = QPushButton(self.controlWidget)
        self.cmdHelp.setObjectName(u"cmdHelp")

        self.horizontalLayout_5.addWidget(self.cmdHelp)


        self.verticalLayout_3.addLayout(self.horizontalLayout_5)


        self.verticalLayout_2.addLayout(self.verticalLayout_3)


        self.verticalLayout.addWidget(self.controlWidget)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.horizontalLayout_3.addWidget(self.scrollArea)

        self.tabWidget = QTabWidget(CorfuncDialog)
        self.tabWidget.setObjectName(u"tabWidget")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy5)
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout_5 = QVBoxLayout(self.tab)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.qSpaceLayout = QVBoxLayout()
        self.qSpaceLayout.setObjectName(u"qSpaceLayout")

        self.verticalLayout_5.addLayout(self.qSpaceLayout)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.verticalLayout_7 = QVBoxLayout(self.tab_2)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.realSpaceLayout = QVBoxLayout()
        self.realSpaceLayout.setObjectName(u"realSpaceLayout")

        self.verticalLayout_7.addLayout(self.realSpaceLayout)

        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.verticalLayout_420 = QVBoxLayout(self.tab_3)
        self.verticalLayout_420.setObjectName(u"verticalLayout_420")
        self.diagramLayout = QVBoxLayout()
        self.diagramLayout.setObjectName(u"diagramLayout")

        self.verticalLayout_420.addLayout(self.diagramLayout)

        self.tabWidget.addTab(self.tab_3, "")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName(u"tab_4")
        self.verticalLayout_4 = QVBoxLayout(self.tab_4)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.idfLayout = QVBoxLayout()
        self.idfLayout.setObjectName(u"idfLayout")

        self.verticalLayout_4.addLayout(self.idfLayout)

        self.tabWidget.addTab(self.tab_4, "")

        self.horizontalLayout_3.addWidget(self.tabWidget)

        QWidget.setTabOrder(self.cmdExtract, self.txtLowerQMax)
        QWidget.setTabOrder(self.txtLowerQMax, self.txtUpperQMin)
        QWidget.setTabOrder(self.txtUpperQMin, self.txtUpperQMax)
        QWidget.setTabOrder(self.txtUpperQMax, self.fitBackground)
        QWidget.setTabOrder(self.fitBackground, self.fitGuinier)
        QWidget.setTabOrder(self.fitGuinier, self.fitPorod)
        QWidget.setTabOrder(self.fitPorod, self.radTangentInflection)
        QWidget.setTabOrder(self.radTangentInflection, self.radTangentMidpoint)
        QWidget.setTabOrder(self.radTangentMidpoint, self.radTangentAuto)
        QWidget.setTabOrder(self.radTangentAuto, self.radLongPeriodMax)
        QWidget.setTabOrder(self.radLongPeriodMax, self.radLongPeriodDouble)
        QWidget.setTabOrder(self.radLongPeriodDouble, self.radLongPeriodAuto)
        QWidget.setTabOrder(self.radLongPeriodAuto, self.txtBackground)
        QWidget.setTabOrder(self.txtBackground, self.txtGuinierA)
        QWidget.setTabOrder(self.txtGuinierA, self.txtGuinierB)
        QWidget.setTabOrder(self.txtGuinierB, self.txtPorodK)
        QWidget.setTabOrder(self.txtPorodK, self.txtPorodSigma)
        QWidget.setTabOrder(self.txtPorodSigma, self.txtAvgHardBlock)
        QWidget.setTabOrder(self.txtAvgHardBlock, self.txtAvgSoftBlock)
        QWidget.setTabOrder(self.txtAvgSoftBlock, self.txtAvgIntThick)
        QWidget.setTabOrder(self.txtAvgIntThick, self.txtAvgCoreThick)
        QWidget.setTabOrder(self.txtAvgCoreThick, self.txtPolyRyan)
        QWidget.setTabOrder(self.txtPolyRyan, self.txtPolyStribeck)
        QWidget.setTabOrder(self.txtPolyStribeck, self.txtLongPeriod)
        QWidget.setTabOrder(self.txtLongPeriod, self.txtLocalCrystal)
        QWidget.setTabOrder(self.txtLocalCrystal, self.cmdSaveExtrapolation)
        QWidget.setTabOrder(self.cmdSaveExtrapolation, self.cmdSave)
        QWidget.setTabOrder(self.cmdSave, self.cmdHelp)
        QWidget.setTabOrder(self.cmdHelp, self.tabWidget)
        QWidget.setTabOrder(self.tabWidget, self.scrollArea)
        QWidget.setTabOrder(self.scrollArea, self.txtFilename)

        self.retranslateUi(CorfuncDialog)

        self.tabWidget.setCurrentIndex(2)


        QMetaObject.connectSlotsByName(CorfuncDialog)
    # setupUi

    def retranslateUi(self, CorfuncDialog):
        CorfuncDialog.setWindowTitle(QCoreApplication.translate("CorfuncDialog", u"Corfunc", None))
        self.groupBox.setTitle(QCoreApplication.translate("CorfuncDialog", u"Input", None))
        self.label_20.setText(QCoreApplication.translate("CorfuncDialog", u"Tangent Method:  ", None))
        self.label_18.setText(QCoreApplication.translate("CorfuncDialog", u"Fitting:  ", None))
        self.label_21.setText(QCoreApplication.translate("CorfuncDialog", u"Long Period Method:  ", None))
        self.radTangentInflection.setText(QCoreApplication.translate("CorfuncDialog", u"Use Inflection Point", None))
        self.fitPorod.setText(QCoreApplication.translate("CorfuncDialog", u"Fit Porod", None))
        self.fitBackground.setText(QCoreApplication.translate("CorfuncDialog", u"Fit Background", None))
        self.radTangentMidpoint.setText(QCoreApplication.translate("CorfuncDialog", u"Use Halfway Point", None))
        self.radLongPeriodAuto.setText(QCoreApplication.translate("CorfuncDialog", u"Automatic", None))
        self.radTangentAuto.setText(QCoreApplication.translate("CorfuncDialog", u"Automatic", None))
        self.radLongPeriodDouble.setText(QCoreApplication.translate("CorfuncDialog", u"Use 2x Minimum", None))
        self.fitGuinier.setText(QCoreApplication.translate("CorfuncDialog", u"Fit Guinier", None))
        self.radLongPeriodMax.setText(QCoreApplication.translate("CorfuncDialog", u"Use Maximum", None))
        self.lblName.setText(QCoreApplication.translate("CorfuncDialog", u"Name:", None))
        self.lblTotalQUnits_2.setText(QCoreApplication.translate("CorfuncDialog", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.lblTotalQMin_2.setText(QCoreApplication.translate("CorfuncDialog", u"Porod Start:", None))
        self.lblTotalQMax_2.setText(QCoreApplication.translate("CorfuncDialog", u"Porod End:", None))
        self.lblTotalQMax.setText(QCoreApplication.translate("CorfuncDialog", u"Guinier End:", None))
#if QT_CONFIG(tooltip)
        self.cmdExtract.setToolTip(QCoreApplication.translate("CorfuncDialog", u"Extract model parameters from the real space transformed curve.", None))
#endif // QT_CONFIG(tooltip)
        self.cmdExtract.setText(QCoreApplication.translate("CorfuncDialog", u"Go", None))
        self.label_3.setText(QCoreApplication.translate("CorfuncDialog", u"Adjust:", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("CorfuncDialog", u"Extrapolation Parameters", None))
        self.label.setText(QCoreApplication.translate("CorfuncDialog", u"Background:", None))
        self.label_8.setText(QCoreApplication.translate("CorfuncDialog", u"Guinier", None))
        self.label_7.setText(QCoreApplication.translate("CorfuncDialog", u"     B:", None))
        self.label_10.setText(QCoreApplication.translate("CorfuncDialog", u"K:", None))
        self.label_6.setText(QCoreApplication.translate("CorfuncDialog", u"A:", None))
        self.label_9.setText(QCoreApplication.translate("CorfuncDialog", u"Porod", None))
        self.label_11.setText(QCoreApplication.translate("CorfuncDialog", u"\u03c3:", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("CorfuncDialog", u"Lamellar Parameters", None))
        self.label_13.setText(QCoreApplication.translate("CorfuncDialog", u"Stribeck:", None))
        self.label_12.setText(QCoreApplication.translate("CorfuncDialog", u"Eekhaut:", None))
        self.label_16.setText(QCoreApplication.translate("CorfuncDialog", u"    Hard Block:", None))
        self.label_4.setText(QCoreApplication.translate("CorfuncDialog", u"Avg. Thicknesses:", None))
        self.label_2.setText(QCoreApplication.translate("CorfuncDialog", u"         Soft Block:", None))
        self.label_5.setText(QCoreApplication.translate("CorfuncDialog", u"Polydispersity:", None))
        self.label_15.setText(QCoreApplication.translate("CorfuncDialog", u"Interface:", None))
        self.label_17.setText(QCoreApplication.translate("CorfuncDialog", u"Core:", None))
        self.label_14.setText(QCoreApplication.translate("CorfuncDialog", u"Long Period:", None))
        self.label_19.setText(QCoreApplication.translate("CorfuncDialog", u"Local Crystallinity:", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("CorfuncDialog", u"Export", None))
#if QT_CONFIG(tooltip)
        self.cmdSaveExtrapolation.setToolTip(QCoreApplication.translate("CorfuncDialog", u"Save the extrapolated data (non-transformed)", None))
#endif // QT_CONFIG(tooltip)
        self.cmdSaveExtrapolation.setText(QCoreApplication.translate("CorfuncDialog", u"Export Extrapolated", None))
#if QT_CONFIG(tooltip)
        self.cmdSave.setToolTip(QCoreApplication.translate("CorfuncDialog", u"Export the calculated real space correlation function to a file.", None))
#endif // QT_CONFIG(tooltip)
        self.cmdSave.setText(QCoreApplication.translate("CorfuncDialog", u"Export Transformed", None))
        self.cmdHelp.setText(QCoreApplication.translate("CorfuncDialog", u"Help", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("CorfuncDialog", u"Q Space", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("CorfuncDialog", u"Real Space", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QCoreApplication.translate("CorfuncDialog", u"Extraction Diagram", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), QCoreApplication.translate("CorfuncDialog", u"IDF", None))
    # retranslateUi

