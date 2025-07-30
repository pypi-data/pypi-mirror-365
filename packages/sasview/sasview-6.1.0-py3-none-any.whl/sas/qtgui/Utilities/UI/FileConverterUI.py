# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'FileConverterUI.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
    QFrame, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QTabWidget, QTextEdit, QVBoxLayout,
    QWidget)

class Ui_FileConverterUI(object):
    def setupUi(self, FileConverterUI):
        if not FileConverterUI.objectName():
            FileConverterUI.setObjectName(u"FileConverterUI")
        FileConverterUI.setWindowModality(Qt.NonModal)
        FileConverterUI.resize(457, 384)
        self.gridLayout_8 = QGridLayout(FileConverterUI)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.tabWidget = QTabWidget(FileConverterUI)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.gridLayout_2 = QGridLayout(self.tab)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.groupBox = QGroupBox(self.tab)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_6 = QLabel(self.groupBox)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout.addWidget(self.label_6, 0, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.cbInputFormat = QComboBox(self.groupBox)
        self.cbInputFormat.addItem("")
        self.cbInputFormat.addItem("")
        self.cbInputFormat.addItem("")
        self.cbInputFormat.addItem("")
        self.cbInputFormat.setObjectName(u"cbInputFormat")
        self.cbInputFormat.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.horizontalLayout_2.addWidget(self.cbInputFormat)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)


        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 1, 1, 1)

        self.label_7 = QLabel(self.groupBox)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout.addWidget(self.label_7, 1, 0, 1, 1)

        self.txtQFile = QLineEdit(self.groupBox)
        self.txtQFile.setObjectName(u"txtQFile")

        self.gridLayout.addWidget(self.txtQFile, 1, 1, 1, 1)

        self.btnQFile = QPushButton(self.groupBox)
        self.btnQFile.setObjectName(u"btnQFile")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnQFile.sizePolicy().hasHeightForWidth())
        self.btnQFile.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.btnQFile, 1, 2, 1, 1)

        self.label_8 = QLabel(self.groupBox)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout.addWidget(self.label_8, 2, 0, 1, 1)

        self.txtIFile = QLineEdit(self.groupBox)
        self.txtIFile.setObjectName(u"txtIFile")

        self.gridLayout.addWidget(self.txtIFile, 2, 1, 1, 1)

        self.btnIFile = QPushButton(self.groupBox)
        self.btnIFile.setObjectName(u"btnIFile")
        sizePolicy.setHeightForWidth(self.btnIFile.sizePolicy().hasHeightForWidth())
        self.btnIFile.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.btnIFile, 2, 2, 1, 1)

        self.label_9 = QLabel(self.groupBox)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout.addWidget(self.label_9, 3, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.cbRadiation = QComboBox(self.groupBox)
        self.cbRadiation.addItem("")
        self.cbRadiation.addItem("")
        self.cbRadiation.addItem("")
        self.cbRadiation.addItem("")
        self.cbRadiation.setObjectName(u"cbRadiation")
        self.cbRadiation.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.horizontalLayout.addWidget(self.cbRadiation)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.gridLayout.addLayout(self.horizontalLayout, 3, 1, 1, 1)

        self.label_10 = QLabel(self.groupBox)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout.addWidget(self.label_10, 4, 0, 1, 1)

        self.txtOutputFile = QLineEdit(self.groupBox)
        self.txtOutputFile.setObjectName(u"txtOutputFile")

        self.gridLayout.addWidget(self.txtOutputFile, 4, 1, 1, 1)

        self.btnOutputFile = QPushButton(self.groupBox)
        self.btnOutputFile.setObjectName(u"btnOutputFile")
        sizePolicy.setHeightForWidth(self.btnOutputFile.sizePolicy().hasHeightForWidth())
        self.btnOutputFile.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.btnOutputFile, 4, 2, 1, 1)


        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)

        self.chkLoadFile = QCheckBox(self.tab)
        self.chkLoadFile.setObjectName(u"chkLoadFile")
        self.chkLoadFile.setChecked(True)
        self.chkLoadFile.setTristate(False)

        self.gridLayout_2.addWidget(self.chkLoadFile, 1, 0, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 90, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer_2, 2, 0, 1, 1)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.gridLayout_4 = QGridLayout(self.tab_2)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.tabWidget_2 = QTabWidget(self.tab_2)
        self.tabWidget_2.setObjectName(u"tabWidget_2")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.gridLayout_9 = QGridLayout(self.tab_3)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.label_2 = QLabel(self.tab_3)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_5.addWidget(self.label_2, 0, 0, 1, 1)

        self.txtMG_Title = QLineEdit(self.tab_3)
        self.txtMG_Title.setObjectName(u"txtMG_Title")

        self.gridLayout_5.addWidget(self.txtMG_Title, 0, 1, 1, 1)

        self.label_3 = QLabel(self.tab_3)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_5.addWidget(self.label_3, 1, 0, 1, 1)

        self.txtMG_RunNumber = QLineEdit(self.tab_3)
        self.txtMG_RunNumber.setObjectName(u"txtMG_RunNumber")

        self.gridLayout_5.addWidget(self.txtMG_RunNumber, 1, 1, 1, 1)

        self.label_4 = QLabel(self.tab_3)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_5.addWidget(self.label_4, 2, 0, 1, 1)

        self.txtMG_RunName = QLineEdit(self.tab_3)
        self.txtMG_RunName.setObjectName(u"txtMG_RunName")

        self.gridLayout_5.addWidget(self.txtMG_RunName, 2, 1, 1, 1)

        self.label_5 = QLabel(self.tab_3)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_5.addWidget(self.label_5, 3, 0, 1, 1)

        self.txtMG_Instrument = QLineEdit(self.tab_3)
        self.txtMG_Instrument.setObjectName(u"txtMG_Instrument")

        self.gridLayout_5.addWidget(self.txtMG_Instrument, 3, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout_5)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.gridLayout_9.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.tabWidget_2.addTab(self.tab_3, "")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName(u"tab_4")
        self.gridLayout_7 = QGridLayout(self.tab_4)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.gridLayout_6 = QGridLayout()
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.label = QLabel(self.tab_4)
        self.label.setObjectName(u"label")

        self.gridLayout_6.addWidget(self.label, 0, 0, 1, 1)

        self.txtMD_Name = QLineEdit(self.tab_4)
        self.txtMD_Name.setObjectName(u"txtMD_Name")

        self.gridLayout_6.addWidget(self.txtMD_Name, 0, 1, 1, 1)

        self.label_11 = QLabel(self.tab_4)
        self.label_11.setObjectName(u"label_11")

        self.gridLayout_6.addWidget(self.label_11, 1, 0, 1, 1)

        self.txtMD_Distance = QLineEdit(self.tab_4)
        self.txtMD_Distance.setObjectName(u"txtMD_Distance")

        self.gridLayout_6.addWidget(self.txtMD_Distance, 1, 1, 1, 1)

        self.label_12 = QLabel(self.tab_4)
        self.label_12.setObjectName(u"label_12")

        self.gridLayout_6.addWidget(self.label_12, 2, 0, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_13 = QLabel(self.tab_4)
        self.label_13.setObjectName(u"label_13")

        self.horizontalLayout_4.addWidget(self.label_13)

        self.txtMD_OffsetX = QLineEdit(self.tab_4)
        self.txtMD_OffsetX.setObjectName(u"txtMD_OffsetX")

        self.horizontalLayout_4.addWidget(self.txtMD_OffsetX)

        self.label_14 = QLabel(self.tab_4)
        self.label_14.setObjectName(u"label_14")

        self.horizontalLayout_4.addWidget(self.label_14)

        self.txtMD_OffsetY = QLineEdit(self.tab_4)
        self.txtMD_OffsetY.setObjectName(u"txtMD_OffsetY")

        self.horizontalLayout_4.addWidget(self.txtMD_OffsetY)


        self.gridLayout_6.addLayout(self.horizontalLayout_4, 2, 1, 1, 1)

        self.label_15 = QLabel(self.tab_4)
        self.label_15.setObjectName(u"label_15")

        self.gridLayout_6.addWidget(self.label_15, 3, 0, 1, 1)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_16 = QLabel(self.tab_4)
        self.label_16.setObjectName(u"label_16")

        self.horizontalLayout_5.addWidget(self.label_16)

        self.txtMD_OrientRoll = QLineEdit(self.tab_4)
        self.txtMD_OrientRoll.setObjectName(u"txtMD_OrientRoll")

        self.horizontalLayout_5.addWidget(self.txtMD_OrientRoll)

        self.label_17 = QLabel(self.tab_4)
        self.label_17.setObjectName(u"label_17")

        self.horizontalLayout_5.addWidget(self.label_17)

        self.txtMD_OrientPitch = QLineEdit(self.tab_4)
        self.txtMD_OrientPitch.setObjectName(u"txtMD_OrientPitch")

        self.horizontalLayout_5.addWidget(self.txtMD_OrientPitch)

        self.label_18 = QLabel(self.tab_4)
        self.label_18.setObjectName(u"label_18")

        self.horizontalLayout_5.addWidget(self.label_18)

        self.txtMD_OrientYaw = QLineEdit(self.tab_4)
        self.txtMD_OrientYaw.setObjectName(u"txtMD_OrientYaw")

        self.horizontalLayout_5.addWidget(self.txtMD_OrientYaw)


        self.gridLayout_6.addLayout(self.horizontalLayout_5, 3, 1, 1, 1)

        self.label_19 = QLabel(self.tab_4)
        self.label_19.setObjectName(u"label_19")

        self.gridLayout_6.addWidget(self.label_19, 4, 0, 1, 1)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_21 = QLabel(self.tab_4)
        self.label_21.setObjectName(u"label_21")

        self.horizontalLayout_6.addWidget(self.label_21)

        self.txtMD_PixelX = QLineEdit(self.tab_4)
        self.txtMD_PixelX.setObjectName(u"txtMD_PixelX")

        self.horizontalLayout_6.addWidget(self.txtMD_PixelX)

        self.label_20 = QLabel(self.tab_4)
        self.label_20.setObjectName(u"label_20")

        self.horizontalLayout_6.addWidget(self.label_20)

        self.txtMD_PixelY = QLineEdit(self.tab_4)
        self.txtMD_PixelY.setObjectName(u"txtMD_PixelY")

        self.horizontalLayout_6.addWidget(self.txtMD_PixelY)


        self.gridLayout_6.addLayout(self.horizontalLayout_6, 4, 1, 1, 1)

        self.label_22 = QLabel(self.tab_4)
        self.label_22.setObjectName(u"label_22")

        self.gridLayout_6.addWidget(self.label_22, 5, 0, 1, 1)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_23 = QLabel(self.tab_4)
        self.label_23.setObjectName(u"label_23")

        self.horizontalLayout_7.addWidget(self.label_23)

        self.txtMD_BeamX = QLineEdit(self.tab_4)
        self.txtMD_BeamX.setObjectName(u"txtMD_BeamX")

        self.horizontalLayout_7.addWidget(self.txtMD_BeamX)

        self.label_24 = QLabel(self.tab_4)
        self.label_24.setObjectName(u"label_24")

        self.horizontalLayout_7.addWidget(self.label_24)

        self.txtMD_BeamY = QLineEdit(self.tab_4)
        self.txtMD_BeamY.setObjectName(u"txtMD_BeamY")

        self.horizontalLayout_7.addWidget(self.txtMD_BeamY)


        self.gridLayout_6.addLayout(self.horizontalLayout_7, 5, 1, 1, 1)

        self.label_25 = QLabel(self.tab_4)
        self.label_25.setObjectName(u"label_25")

        self.gridLayout_6.addWidget(self.label_25, 6, 0, 1, 1)

        self.txtMD_SlitLength = QLineEdit(self.tab_4)
        self.txtMD_SlitLength.setObjectName(u"txtMD_SlitLength")

        self.gridLayout_6.addWidget(self.txtMD_SlitLength, 6, 1, 1, 1)


        self.gridLayout_7.addLayout(self.gridLayout_6, 0, 0, 1, 1)

        self.verticalSpacer_3 = QSpacerItem(20, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_7.addItem(self.verticalSpacer_3, 1, 0, 1, 1)

        self.tabWidget_2.addTab(self.tab_4, "")
        self.tab_5 = QWidget()
        self.tab_5.setObjectName(u"tab_5")
        self.gridLayout_3 = QGridLayout(self.tab_5)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label_26 = QLabel(self.tab_5)
        self.label_26.setObjectName(u"label_26")

        self.gridLayout_3.addWidget(self.label_26, 0, 0, 1, 1)

        self.txtMSa_Name = QLineEdit(self.tab_5)
        self.txtMSa_Name.setObjectName(u"txtMSa_Name")

        self.gridLayout_3.addWidget(self.txtMSa_Name, 0, 1, 1, 1)

        self.label_27 = QLabel(self.tab_5)
        self.label_27.setObjectName(u"label_27")

        self.gridLayout_3.addWidget(self.label_27, 1, 0, 1, 1)

        self.txtMSa_Thickness = QLineEdit(self.tab_5)
        self.txtMSa_Thickness.setObjectName(u"txtMSa_Thickness")

        self.gridLayout_3.addWidget(self.txtMSa_Thickness, 1, 1, 1, 1)

        self.label_29 = QLabel(self.tab_5)
        self.label_29.setObjectName(u"label_29")

        self.gridLayout_3.addWidget(self.label_29, 2, 0, 1, 1)

        self.txtMSa_Transmission = QLineEdit(self.tab_5)
        self.txtMSa_Transmission.setObjectName(u"txtMSa_Transmission")

        self.gridLayout_3.addWidget(self.txtMSa_Transmission, 2, 1, 1, 1)

        self.label_30 = QLabel(self.tab_5)
        self.label_30.setObjectName(u"label_30")

        self.gridLayout_3.addWidget(self.label_30, 3, 0, 1, 1)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.txtMSa_Temperature = QLineEdit(self.tab_5)
        self.txtMSa_Temperature.setObjectName(u"txtMSa_Temperature")

        self.horizontalLayout_9.addWidget(self.txtMSa_Temperature)

        self.label_28 = QLabel(self.tab_5)
        self.label_28.setObjectName(u"label_28")

        self.horizontalLayout_9.addWidget(self.label_28)

        self.txtMSa_TempUnit = QLineEdit(self.tab_5)
        self.txtMSa_TempUnit.setObjectName(u"txtMSa_TempUnit")

        self.horizontalLayout_9.addWidget(self.txtMSa_TempUnit)


        self.gridLayout_3.addLayout(self.horizontalLayout_9, 3, 1, 1, 1)

        self.label_31 = QLabel(self.tab_5)
        self.label_31.setObjectName(u"label_31")

        self.gridLayout_3.addWidget(self.label_31, 4, 0, 1, 1)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.label_32 = QLabel(self.tab_5)
        self.label_32.setObjectName(u"label_32")

        self.horizontalLayout_11.addWidget(self.label_32)

        self.txtMSa_PositionX = QLineEdit(self.tab_5)
        self.txtMSa_PositionX.setObjectName(u"txtMSa_PositionX")

        self.horizontalLayout_11.addWidget(self.txtMSa_PositionX)

        self.label_33 = QLabel(self.tab_5)
        self.label_33.setObjectName(u"label_33")

        self.horizontalLayout_11.addWidget(self.label_33)

        self.txtMSa_PositionY = QLineEdit(self.tab_5)
        self.txtMSa_PositionY.setObjectName(u"txtMSa_PositionY")

        self.horizontalLayout_11.addWidget(self.txtMSa_PositionY)


        self.gridLayout_3.addLayout(self.horizontalLayout_11, 4, 1, 1, 1)

        self.label_36 = QLabel(self.tab_5)
        self.label_36.setObjectName(u"label_36")

        self.gridLayout_3.addWidget(self.label_36, 5, 0, 1, 1)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.label_35 = QLabel(self.tab_5)
        self.label_35.setObjectName(u"label_35")

        self.horizontalLayout_12.addWidget(self.label_35)

        self.txtMSa_OrientR = QLineEdit(self.tab_5)
        self.txtMSa_OrientR.setObjectName(u"txtMSa_OrientR")

        self.horizontalLayout_12.addWidget(self.txtMSa_OrientR)

        self.label_34 = QLabel(self.tab_5)
        self.label_34.setObjectName(u"label_34")

        self.horizontalLayout_12.addWidget(self.label_34)

        self.txtMSa_OrientP = QLineEdit(self.tab_5)
        self.txtMSa_OrientP.setObjectName(u"txtMSa_OrientP")

        self.horizontalLayout_12.addWidget(self.txtMSa_OrientP)

        self.label_37 = QLabel(self.tab_5)
        self.label_37.setObjectName(u"label_37")

        self.horizontalLayout_12.addWidget(self.label_37)

        self.txtMSa_OrientY = QLineEdit(self.tab_5)
        self.txtMSa_OrientY.setObjectName(u"txtMSa_OrientY")

        self.horizontalLayout_12.addWidget(self.txtMSa_OrientY)


        self.gridLayout_3.addLayout(self.horizontalLayout_12, 5, 1, 1, 1)

        self.label_38 = QLabel(self.tab_5)
        self.label_38.setObjectName(u"label_38")

        self.gridLayout_3.addWidget(self.label_38, 6, 0, 1, 1)

        self.txtMSa_Details = QTextEdit(self.tab_5)
        self.txtMSa_Details.setObjectName(u"txtMSa_Details")
        self.txtMSa_Details.setMinimumSize(QSize(0, 20))

        self.gridLayout_3.addWidget(self.txtMSa_Details, 6, 1, 1, 1)

        self.verticalSpacer_4 = QSpacerItem(20, 33, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer_4, 7, 1, 1, 1)

        self.tabWidget_2.addTab(self.tab_5, "")
        self.tab_6 = QWidget()
        self.tab_6.setObjectName(u"tab_6")
        self.gridLayout_11 = QGridLayout(self.tab_6)
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.gridLayout_10 = QGridLayout()
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.label_39 = QLabel(self.tab_6)
        self.label_39.setObjectName(u"label_39")

        self.gridLayout_10.addWidget(self.label_39, 0, 0, 1, 1)

        self.txtMSo_Name = QLineEdit(self.tab_6)
        self.txtMSo_Name.setObjectName(u"txtMSo_Name")

        self.gridLayout_10.addWidget(self.txtMSo_Name, 0, 1, 1, 2)

        self.label_40 = QLabel(self.tab_6)
        self.label_40.setObjectName(u"label_40")

        self.gridLayout_10.addWidget(self.label_40, 1, 0, 1, 1)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_42 = QLabel(self.tab_6)
        self.label_42.setObjectName(u"label_42")

        self.horizontalLayout_8.addWidget(self.label_42)

        self.txtMSo_BeamSizeX = QLineEdit(self.tab_6)
        self.txtMSo_BeamSizeX.setObjectName(u"txtMSo_BeamSizeX")

        self.horizontalLayout_8.addWidget(self.txtMSo_BeamSizeX)

        self.label_41 = QLabel(self.tab_6)
        self.label_41.setObjectName(u"label_41")

        self.horizontalLayout_8.addWidget(self.label_41)

        self.txtMSo_BeamSizeY = QLineEdit(self.tab_6)
        self.txtMSo_BeamSizeY.setObjectName(u"txtMSo_BeamSizeY")

        self.horizontalLayout_8.addWidget(self.txtMSo_BeamSizeY)


        self.gridLayout_10.addLayout(self.horizontalLayout_8, 1, 1, 1, 2)

        self.label_43 = QLabel(self.tab_6)
        self.label_43.setObjectName(u"label_43")

        self.gridLayout_10.addWidget(self.label_43, 2, 0, 1, 1)

        self.txtMSo_BeamShape = QLineEdit(self.tab_6)
        self.txtMSo_BeamShape.setObjectName(u"txtMSo_BeamShape")

        self.gridLayout_10.addWidget(self.txtMSo_BeamShape, 2, 1, 1, 2)

        self.label_44 = QLabel(self.tab_6)
        self.label_44.setObjectName(u"label_44")

        self.gridLayout_10.addWidget(self.label_44, 3, 0, 1, 1)

        self.txtMSo_BeamWavelength = QLineEdit(self.tab_6)
        self.txtMSo_BeamWavelength.setObjectName(u"txtMSo_BeamWavelength")

        self.gridLayout_10.addWidget(self.txtMSo_BeamWavelength, 3, 1, 1, 2)

        self.label_45 = QLabel(self.tab_6)
        self.label_45.setObjectName(u"label_45")

        self.gridLayout_10.addWidget(self.label_45, 4, 0, 1, 1)

        self.txtMSo_MinWavelength = QLineEdit(self.tab_6)
        self.txtMSo_MinWavelength.setObjectName(u"txtMSo_MinWavelength")

        self.gridLayout_10.addWidget(self.txtMSo_MinWavelength, 4, 1, 1, 2)

        self.label_46 = QLabel(self.tab_6)
        self.label_46.setObjectName(u"label_46")

        self.gridLayout_10.addWidget(self.label_46, 5, 0, 1, 1)

        self.txtMSo_MaxWavelength = QLineEdit(self.tab_6)
        self.txtMSo_MaxWavelength.setObjectName(u"txtMSo_MaxWavelength")

        self.gridLayout_10.addWidget(self.txtMSo_MaxWavelength, 5, 1, 1, 2)

        self.label_47 = QLabel(self.tab_6)
        self.label_47.setObjectName(u"label_47")

        self.gridLayout_10.addWidget(self.label_47, 6, 0, 1, 2)

        self.txtMSo_Spread = QLineEdit(self.tab_6)
        self.txtMSo_Spread.setObjectName(u"txtMSo_Spread")

        self.gridLayout_10.addWidget(self.txtMSo_Spread, 6, 2, 1, 1)


        self.gridLayout_11.addLayout(self.gridLayout_10, 0, 0, 1, 1)

        self.verticalSpacer_5 = QSpacerItem(20, 36, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_11.addItem(self.verticalSpacer_5, 1, 0, 1, 1)

        self.tabWidget_2.addTab(self.tab_6, "")

        self.gridLayout_4.addWidget(self.tabWidget_2, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_2, "")
        self.tab_7 = QWidget()
        self.tab_7.setObjectName(u"tab_7")
        self.gridLayout_12 = QGridLayout(self.tab_7)
        self.gridLayout_12.setObjectName(u"gridLayout_12")
        self.label_48 = QLabel(self.tab_7)
        self.label_48.setObjectName(u"label_48")
        self.label_48.setFrameShape(QFrame.Box)
        self.label_48.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.label_48.setWordWrap(True)

        self.gridLayout_12.addWidget(self.label_48, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_7, "")

        self.gridLayout_8.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.cmdConvert = QPushButton(FileConverterUI)
        self.cmdConvert.setObjectName(u"cmdConvert")

        self.horizontalLayout_3.addWidget(self.cmdConvert)

        self.cmdClose = QPushButton(FileConverterUI)
        self.cmdClose.setObjectName(u"cmdClose")

        self.horizontalLayout_3.addWidget(self.cmdClose)

        self.cmdHelp = QPushButton(FileConverterUI)
        self.cmdHelp.setObjectName(u"cmdHelp")

        self.horizontalLayout_3.addWidget(self.cmdHelp)


        self.gridLayout_8.addLayout(self.horizontalLayout_3, 1, 0, 1, 1)


        self.retranslateUi(FileConverterUI)

        self.tabWidget.setCurrentIndex(0)
        self.tabWidget_2.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(FileConverterUI)
    # setupUi

    def retranslateUi(self, FileConverterUI):
        FileConverterUI.setWindowTitle(QCoreApplication.translate("FileConverterUI", u"File Converter", None))
        self.groupBox.setTitle(QCoreApplication.translate("FileConverterUI", u"Input data", None))
        self.label_6.setText(QCoreApplication.translate("FileConverterUI", u"Input Format:", None))
        self.cbInputFormat.setItemText(0, QCoreApplication.translate("FileConverterUI", u"ASCII 1D", None))
        self.cbInputFormat.setItemText(1, QCoreApplication.translate("FileConverterUI", u"ASCII 2D", None))
        self.cbInputFormat.setItemText(2, QCoreApplication.translate("FileConverterUI", u"BSL 1D", None))
        self.cbInputFormat.setItemText(3, QCoreApplication.translate("FileConverterUI", u"BSL 2D", None))

        self.label_7.setText(QCoreApplication.translate("FileConverterUI", u"Q-Axis Data:", None))
        self.btnQFile.setText(QCoreApplication.translate("FileConverterUI", u"...", None))
        self.label_8.setText(QCoreApplication.translate("FileConverterUI", u"Intensity Data:", None))
        self.btnIFile.setText(QCoreApplication.translate("FileConverterUI", u"...", None))
        self.label_9.setText(QCoreApplication.translate("FileConverterUI", u"Radiation Type:", None))
        self.cbRadiation.setItemText(0, QCoreApplication.translate("FileConverterUI", u"Neutron", None))
        self.cbRadiation.setItemText(1, QCoreApplication.translate("FileConverterUI", u"X-Ray", None))
        self.cbRadiation.setItemText(2, QCoreApplication.translate("FileConverterUI", u"Muon", None))
        self.cbRadiation.setItemText(3, QCoreApplication.translate("FileConverterUI", u"Electron", None))

        self.label_10.setText(QCoreApplication.translate("FileConverterUI", u"Output File:", None))
        self.btnOutputFile.setText(QCoreApplication.translate("FileConverterUI", u"...", None))
        self.chkLoadFile.setText(QCoreApplication.translate("FileConverterUI", u"Load file into SasView after conversion", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("FileConverterUI", u"I/O", None))
        self.label_2.setText(QCoreApplication.translate("FileConverterUI", u"Title", None))
        self.label_3.setText(QCoreApplication.translate("FileConverterUI", u"Run Number", None))
        self.label_4.setText(QCoreApplication.translate("FileConverterUI", u"Run Name", None))
        self.label_5.setText(QCoreApplication.translate("FileConverterUI", u"Instrument", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_3), QCoreApplication.translate("FileConverterUI", u"General", None))
        self.label.setText(QCoreApplication.translate("FileConverterUI", u"Name:", None))
        self.label_11.setText(QCoreApplication.translate("FileConverterUI", u"Distance [mm]:", None))
        self.label_12.setText(QCoreApplication.translate("FileConverterUI", u"Offset [m]", None))
        self.label_13.setText(QCoreApplication.translate("FileConverterUI", u"X:", None))
        self.label_14.setText(QCoreApplication.translate("FileConverterUI", u"Y:", None))
        self.label_15.setText(QCoreApplication.translate("FileConverterUI", u"<html><head/><body><p>Orientation [\u00b0]</p></body></html>", None))
        self.label_16.setText(QCoreApplication.translate("FileConverterUI", u"Roll:", None))
        self.label_17.setText(QCoreApplication.translate("FileConverterUI", u"Pitch:", None))
        self.label_18.setText(QCoreApplication.translate("FileConverterUI", u"Yaw:", None))
        self.label_19.setText(QCoreApplication.translate("FileConverterUI", u"Pixel size [mm]", None))
        self.label_21.setText(QCoreApplication.translate("FileConverterUI", u"X:", None))
        self.label_20.setText(QCoreApplication.translate("FileConverterUI", u"Y:", None))
        self.label_22.setText(QCoreApplication.translate("FileConverterUI", u"Beam center [mm]", None))
        self.label_23.setText(QCoreApplication.translate("FileConverterUI", u"X:", None))
        self.label_24.setText(QCoreApplication.translate("FileConverterUI", u"Y:", None))
        self.label_25.setText(QCoreApplication.translate("FileConverterUI", u"Slit length [mm]:", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_4), QCoreApplication.translate("FileConverterUI", u"Detector", None))
        self.label_26.setText(QCoreApplication.translate("FileConverterUI", u"Name:", None))
        self.label_27.setText(QCoreApplication.translate("FileConverterUI", u"Thickness [mm]:", None))
        self.label_29.setText(QCoreApplication.translate("FileConverterUI", u"Transmission:", None))
        self.txtMSa_Transmission.setText("")
        self.label_30.setText(QCoreApplication.translate("FileConverterUI", u"Temperature:", None))
        self.txtMSa_Temperature.setText("")
        self.label_28.setText(QCoreApplication.translate("FileConverterUI", u"Unit", None))
        self.label_31.setText(QCoreApplication.translate("FileConverterUI", u"Position [mm]", None))
        self.label_32.setText(QCoreApplication.translate("FileConverterUI", u"X:", None))
        self.label_33.setText(QCoreApplication.translate("FileConverterUI", u"Y:", None))
        self.label_36.setText(QCoreApplication.translate("FileConverterUI", u"<html><head/><body><p>Orientation [\u00b0]</p></body></html>", None))
        self.label_35.setText(QCoreApplication.translate("FileConverterUI", u"Roll:", None))
        self.label_34.setText(QCoreApplication.translate("FileConverterUI", u"Pitch:", None))
        self.label_37.setText(QCoreApplication.translate("FileConverterUI", u"Yaw:", None))
        self.label_38.setText(QCoreApplication.translate("FileConverterUI", u"Details:", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_5), QCoreApplication.translate("FileConverterUI", u"Sample", None))
        self.label_39.setText(QCoreApplication.translate("FileConverterUI", u"Name:", None))
        self.label_40.setText(QCoreApplication.translate("FileConverterUI", u"Beam size [mm]", None))
        self.label_42.setText(QCoreApplication.translate("FileConverterUI", u"X:", None))
        self.label_41.setText(QCoreApplication.translate("FileConverterUI", u"Y:", None))
        self.label_43.setText(QCoreApplication.translate("FileConverterUI", u"Beam shape:", None))
        self.label_44.setText(QCoreApplication.translate("FileConverterUI", u"Wavelength [Ang]:", None))
        self.label_45.setText(QCoreApplication.translate("FileConverterUI", u"Min. wavelength [nm]:", None))
        self.label_46.setText(QCoreApplication.translate("FileConverterUI", u"Max. wavelength [nm]:", None))
        self.label_47.setText(QCoreApplication.translate("FileConverterUI", u"Wavelength spread [%]:", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_6), QCoreApplication.translate("FileConverterUI", u"Source", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("FileConverterUI", u"Metadata", None))
        self.label_48.setText(QCoreApplication.translate("FileConverterUI", u"<html><head/><body><p>If converting a 1D dataset, select linked single-column ASCII files containing the Q-axis and intensity-axis data, or a 1D BSL/OTOKO file.</p><p>If converting 2D data, select an ASCII file in the ISIS 2D file format, or a 2D BSL/OTOKO file.</p><p>Choose where to save the converted file and click convert.</p><p>One dimensional ASCII and BSL/OTOKO files can be converted to CanSAS (XML) or NXcanSAS (HDF5) formats. Two dimensional datasets can only be converted to the NXcanSAS format.</p><p>Metadata can also be optionally added to the output file.<br/></p></body></html>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_7), QCoreApplication.translate("FileConverterUI", u"Instructions", None))
        self.cmdConvert.setText(QCoreApplication.translate("FileConverterUI", u"Convert", None))
        self.cmdClose.setText(QCoreApplication.translate("FileConverterUI", u"Close", None))
        self.cmdHelp.setText(QCoreApplication.translate("FileConverterUI", u"Help", None))
    # retranslateUi

