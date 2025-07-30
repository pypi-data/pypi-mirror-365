# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SizeDistributionUI.ui'
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
    QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QLayout, QLineEdit, QPushButton, QRadioButton,
    QSizePolicy, QSpacerItem, QTabWidget, QWidget)

class Ui_SizeDistribution(object):
    def setupUi(self, SizeDistribution):
        if not SizeDistribution.objectName():
            SizeDistribution.setObjectName(u"SizeDistribution")
        SizeDistribution.resize(577, 671)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SizeDistribution.sizePolicy().hasHeightForWidth())
        SizeDistribution.setSizePolicy(sizePolicy)
        SizeDistribution.setMinimumSize(QSize(0, 0))
        SizeDistribution.setMaximumSize(QSize(16777215, 16777215))
        self.gridLayout_7 = QGridLayout(SizeDistribution)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.SizeDistributionTabWidget = QTabWidget(SizeDistribution)
        self.SizeDistributionTabWidget.setObjectName(u"SizeDistributionTabWidget")
        sizePolicy.setHeightForWidth(self.SizeDistributionTabWidget.sizePolicy().hasHeightForWidth())
        self.SizeDistributionTabWidget.setSizePolicy(sizePolicy)
        self.SizeDistributionTabWidget.setMinimumSize(QSize(0, 0))
        self.tabMain = QWidget()
        self.tabMain.setObjectName(u"tabMain")
        self.gridLayout_6 = QGridLayout(self.tabMain)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.boxData = QGroupBox(self.tabMain)
        self.boxData.setObjectName(u"boxData")
        self.gridLayout_2 = QGridLayout(self.boxData)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.lblName = QLabel(self.boxData)
        self.lblName.setObjectName(u"lblName")

        self.horizontalLayout_4.addWidget(self.lblName)

        self.txtName = QLineEdit(self.boxData)
        self.txtName.setObjectName(u"txtName")
        self.txtName.setEnabled(False)
        self.txtName.setFrame(False)
        self.txtName.setReadOnly(False)

        self.horizontalLayout_4.addWidget(self.txtName)


        self.gridLayout_2.addLayout(self.horizontalLayout_4, 0, 0, 1, 1)


        self.gridLayout_6.addWidget(self.boxData, 0, 0, 1, 1)

        self.boxModel = QGroupBox(self.tabMain)
        self.boxModel.setObjectName(u"boxModel")
        self.gridLayout_5 = QGridLayout(self.boxModel)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.lblModel = QLabel(self.boxModel)
        self.lblModel.setObjectName(u"lblModel")

        self.gridLayout_5.addWidget(self.lblModel, 0, 0, 1, 1)

        self.cbModel = QComboBox(self.boxModel)
        self.cbModel.addItem("")
        self.cbModel.setObjectName(u"cbModel")

        self.gridLayout_5.addWidget(self.cbModel, 0, 1, 1, 1)

        self.lblAspectRatio = QLabel(self.boxModel)
        self.lblAspectRatio.setObjectName(u"lblAspectRatio")

        self.gridLayout_5.addWidget(self.lblAspectRatio, 0, 3, 1, 1)

        self.txtAspectRatio = QLineEdit(self.boxModel)
        self.txtAspectRatio.setObjectName(u"txtAspectRatio")
        self.txtAspectRatio.setEnabled(True)

        self.gridLayout_5.addWidget(self.txtAspectRatio, 0, 4, 1, 1)


        self.gridLayout_6.addWidget(self.boxModel, 1, 0, 1, 1)

        self.boxParameters = QGroupBox(self.tabMain)
        self.boxParameters.setObjectName(u"boxParameters")
        self.gridLayout_9 = QGridLayout(self.boxParameters)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.lblMinDiameter = QLabel(self.boxParameters)
        self.lblMinDiameter.setObjectName(u"lblMinDiameter")

        self.gridLayout_9.addWidget(self.lblMinDiameter, 0, 0, 1, 1)

        self.txtMinDiameter = QLineEdit(self.boxParameters)
        self.txtMinDiameter.setObjectName(u"txtMinDiameter")
        self.txtMinDiameter.setEnabled(True)

        self.gridLayout_9.addWidget(self.txtMinDiameter, 0, 1, 1, 1)

        self.label_2 = QLabel(self.boxParameters)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_9.addWidget(self.label_2, 0, 2, 1, 1)

        self.lblMaxDiameter = QLabel(self.boxParameters)
        self.lblMaxDiameter.setObjectName(u"lblMaxDiameter")

        self.gridLayout_9.addWidget(self.lblMaxDiameter, 0, 3, 1, 1)

        self.txtMaxDiameter = QLineEdit(self.boxParameters)
        self.txtMaxDiameter.setObjectName(u"txtMaxDiameter")
        self.txtMaxDiameter.setEnabled(True)

        self.gridLayout_9.addWidget(self.txtMaxDiameter, 0, 4, 1, 1)

        self.label_3 = QLabel(self.boxParameters)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_9.addWidget(self.label_3, 0, 5, 1, 1)

        self.lblBinsDiameter = QLabel(self.boxParameters)
        self.lblBinsDiameter.setObjectName(u"lblBinsDiameter")

        self.gridLayout_9.addWidget(self.lblBinsDiameter, 1, 0, 1, 1)

        self.txtBinsDiameter = QLineEdit(self.boxParameters)
        self.txtBinsDiameter.setObjectName(u"txtBinsDiameter")
        self.txtBinsDiameter.setEnabled(True)

        self.gridLayout_9.addWidget(self.txtBinsDiameter, 1, 1, 1, 1)

        self.chkLogBinning = QCheckBox(self.boxParameters)
        self.chkLogBinning.setObjectName(u"chkLogBinning")
        self.chkLogBinning.setEnabled(True)
        self.chkLogBinning.setCheckable(True)

        self.gridLayout_9.addWidget(self.chkLogBinning, 1, 3, 1, 2)

        self.lblContrast = QLabel(self.boxParameters)
        self.lblContrast.setObjectName(u"lblContrast")

        self.gridLayout_9.addWidget(self.lblContrast, 4, 0, 1, 1)

        self.txtContrast = QLineEdit(self.boxParameters)
        self.txtContrast.setObjectName(u"txtContrast")
        self.txtContrast.setEnabled(True)

        self.gridLayout_9.addWidget(self.txtContrast, 4, 1, 1, 1)

        self.label_4 = QLabel(self.boxParameters)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_9.addWidget(self.label_4, 4, 2, 1, 1)


        self.gridLayout_6.addWidget(self.boxParameters, 2, 0, 1, 1)

        self.boxOutput = QGroupBox(self.tabMain)
        self.boxOutput.setObjectName(u"boxOutput")
        self.gridLayout_8 = QGridLayout(self.boxOutput)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.lblConvergence = QLabel(self.boxOutput)
        self.lblConvergence.setObjectName(u"lblConvergence")

        self.gridLayout_8.addWidget(self.lblConvergence, 0, 0, 1, 4)

        self.lblChiSq = QLabel(self.boxOutput)
        self.lblChiSq.setObjectName(u"lblChiSq")

        self.gridLayout_8.addWidget(self.lblChiSq, 1, 0, 1, 1)

        self.txtChiSq = QLineEdit(self.boxOutput)
        self.txtChiSq.setObjectName(u"txtChiSq")
        self.txtChiSq.setEnabled(True)
        self.txtChiSq.setReadOnly(True)

        self.gridLayout_8.addWidget(self.txtChiSq, 1, 1, 1, 1)

        self.lblVolume = QLabel(self.boxOutput)
        self.lblVolume.setObjectName(u"lblVolume")

        self.gridLayout_8.addWidget(self.lblVolume, 2, 0, 1, 1)

        self.txtVolume = QLineEdit(self.boxOutput)
        self.txtVolume.setObjectName(u"txtVolume")
        self.txtVolume.setEnabled(True)
        self.txtVolume.setReadOnly(True)

        self.gridLayout_8.addWidget(self.txtVolume, 2, 1, 1, 1)

        self.label_5 = QLabel(self.boxOutput)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_8.addWidget(self.label_5, 2, 2, 1, 1)

        self.lblDiameterMean = QLabel(self.boxOutput)
        self.lblDiameterMean.setObjectName(u"lblDiameterMean")

        self.gridLayout_8.addWidget(self.lblDiameterMean, 3, 0, 1, 1)

        self.txtDiameterMean = QLineEdit(self.boxOutput)
        self.txtDiameterMean.setObjectName(u"txtDiameterMean")
        self.txtDiameterMean.setEnabled(True)
        self.txtDiameterMean.setReadOnly(True)

        self.gridLayout_8.addWidget(self.txtDiameterMean, 3, 1, 1, 1)

        self.label_6 = QLabel(self.boxOutput)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_8.addWidget(self.label_6, 3, 2, 1, 1)

        self.lblDiameterMedian = QLabel(self.boxOutput)
        self.lblDiameterMedian.setObjectName(u"lblDiameterMedian")

        self.gridLayout_8.addWidget(self.lblDiameterMedian, 4, 0, 1, 1)

        self.txtDiameterMedian = QLineEdit(self.boxOutput)
        self.txtDiameterMedian.setObjectName(u"txtDiameterMedian")
        self.txtDiameterMedian.setEnabled(True)
        self.txtDiameterMedian.setReadOnly(True)

        self.gridLayout_8.addWidget(self.txtDiameterMedian, 4, 1, 1, 1)

        self.label_19 = QLabel(self.boxOutput)
        self.label_19.setObjectName(u"label_19")

        self.gridLayout_8.addWidget(self.label_19, 4, 2, 1, 1)

        self.lblDiameterMode = QLabel(self.boxOutput)
        self.lblDiameterMode.setObjectName(u"lblDiameterMode")

        self.gridLayout_8.addWidget(self.lblDiameterMode, 5, 0, 1, 1)

        self.txtDiameterMode = QLineEdit(self.boxOutput)
        self.txtDiameterMode.setObjectName(u"txtDiameterMode")
        self.txtDiameterMode.setEnabled(True)
        self.txtDiameterMode.setReadOnly(True)

        self.gridLayout_8.addWidget(self.txtDiameterMode, 5, 1, 1, 1)

        self.label_20 = QLabel(self.boxOutput)
        self.label_20.setObjectName(u"label_20")

        self.gridLayout_8.addWidget(self.label_20, 5, 2, 1, 1)

        self.horizontalSpacer_7 = QSpacerItem(200, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_8.addItem(self.horizontalSpacer_7, 1, 3, 5, 1)


        self.gridLayout_6.addWidget(self.boxOutput, 3, 0, 1, 1, Qt.AlignTop)

        self.SizeDistributionTabWidget.addTab(self.tabMain, "")
        self.tabOptions = QWidget()
        self.tabOptions.setObjectName(u"tabOptions")
        self.gridLayout_10 = QGridLayout(self.tabOptions)
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.boxFittingRange = QGroupBox(self.tabOptions)
        self.boxFittingRange.setObjectName(u"boxFittingRange")
        self.gridLayout_11 = QGridLayout(self.boxFittingRange)
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.gridLayout_13 = QGridLayout()
        self.gridLayout_13.setObjectName(u"gridLayout_13")
        self.lblMinRange = QLabel(self.boxFittingRange)
        self.lblMinRange.setObjectName(u"lblMinRange")

        self.gridLayout_13.addWidget(self.lblMinRange, 0, 0, 1, 1)

        self.txtMinRange = QLineEdit(self.boxFittingRange)
        self.txtMinRange.setObjectName(u"txtMinRange")
        self.txtMinRange.setMinimumSize(QSize(80, 0))

        self.gridLayout_13.addWidget(self.txtMinRange, 0, 1, 1, 1)

        self.label_13 = QLabel(self.boxFittingRange)
        self.label_13.setObjectName(u"label_13")

        self.gridLayout_13.addWidget(self.label_13, 0, 2, 1, 1)

        self.lblMaxRange = QLabel(self.boxFittingRange)
        self.lblMaxRange.setObjectName(u"lblMaxRange")

        self.gridLayout_13.addWidget(self.lblMaxRange, 1, 0, 1, 1)

        self.txtMaxRange = QLineEdit(self.boxFittingRange)
        self.txtMaxRange.setObjectName(u"txtMaxRange")
        self.txtMaxRange.setMinimumSize(QSize(80, 0))

        self.gridLayout_13.addWidget(self.txtMaxRange, 1, 1, 1, 1)

        self.label_15 = QLabel(self.boxFittingRange)
        self.label_15.setObjectName(u"label_15")

        self.gridLayout_13.addWidget(self.label_15, 1, 2, 1, 1)


        self.gridLayout_11.addLayout(self.gridLayout_13, 0, 0, 2, 1)

        self.horizontalSpacer_8 = QSpacerItem(217, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_11.addItem(self.horizontalSpacer_8, 0, 1, 2, 1)

        self.cmdReset = QPushButton(self.boxFittingRange)
        self.cmdReset.setObjectName(u"cmdReset")

        self.gridLayout_11.addWidget(self.cmdReset, 0, 2, 1, 1)


        self.gridLayout_10.addWidget(self.boxFittingRange, 0, 0, 1, 1)

        self.boxAdvancedParameters = QGroupBox(self.tabOptions)
        self.boxAdvancedParameters.setObjectName(u"boxAdvancedParameters")
        self.gridLayout_21 = QGridLayout(self.boxAdvancedParameters)
        self.gridLayout_21.setObjectName(u"gridLayout_21")
        self.lblSkyBackgd = QLabel(self.boxAdvancedParameters)
        self.lblSkyBackgd.setObjectName(u"lblSkyBackgd")

        self.gridLayout_21.addWidget(self.lblSkyBackgd, 0, 0, 1, 1)

        self.txtSkyBackgd = QLineEdit(self.boxAdvancedParameters)
        self.txtSkyBackgd.setObjectName(u"txtSkyBackgd")

        self.gridLayout_21.addWidget(self.txtSkyBackgd, 0, 1, 1, 1)

        self.label_9 = QLabel(self.boxAdvancedParameters)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_21.addWidget(self.label_9, 0, 2, 1, 1)

        self.lblIterations = QLabel(self.boxAdvancedParameters)
        self.lblIterations.setObjectName(u"lblIterations")

        self.gridLayout_21.addWidget(self.lblIterations, 1, 0, 1, 1)

        self.txtIterations = QLineEdit(self.boxAdvancedParameters)
        self.txtIterations.setObjectName(u"txtIterations")

        self.gridLayout_21.addWidget(self.txtIterations, 1, 1, 1, 1)


        self.gridLayout_10.addWidget(self.boxAdvancedParameters, 1, 0, 1, 1)

        self.boxWeighting = QGroupBox(self.tabOptions)
        self.boxWeighting.setObjectName(u"boxWeighting")
        self.gridLayout_20 = QGridLayout(self.boxWeighting)
        self.gridLayout_20.setObjectName(u"gridLayout_20")
        self.verticalLayout = QGridLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.rbWeighting1 = QRadioButton(self.boxWeighting)
        self.rbWeighting1.setObjectName(u"rbWeighting1")
        self.rbWeighting1.setChecked(True)

        self.verticalLayout.addWidget(self.rbWeighting1, 0, 0, 1, 1)

        self.rbWeighting2 = QRadioButton(self.boxWeighting)
        self.rbWeighting2.setObjectName(u"rbWeighting2")

        self.verticalLayout.addWidget(self.rbWeighting2, 1, 0, 1, 1)

        self.rbWeighting3 = QRadioButton(self.boxWeighting)
        self.rbWeighting3.setObjectName(u"rbWeighting3")

        self.verticalLayout.addWidget(self.rbWeighting3, 2, 0, 1, 1)

        self.rbWeighting4 = QRadioButton(self.boxWeighting)
        self.rbWeighting4.setObjectName(u"rbWeighting4")

        self.verticalLayout.addWidget(self.rbWeighting4, 3, 0, 1, 1)

        self.txtWgtPercent = QLineEdit(self.boxWeighting)
        self.txtWgtPercent.setObjectName(u"txtWgtPercent")

        self.verticalLayout.addWidget(self.txtWgtPercent, 3, 1, 1, 1)


        self.gridLayout_20.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.lblWgtFactor = QLabel(self.boxWeighting)
        self.lblWgtFactor.setObjectName(u"lblWgtFactor")

        self.gridLayout_20.addWidget(self.lblWgtFactor, 0, 1, 1, 1)

        self.txtWgtFactor = QLineEdit(self.boxWeighting)
        self.txtWgtFactor.setObjectName(u"txtWgtFactor")

        self.gridLayout_20.addWidget(self.txtWgtFactor, 0, 2, 1, 1)

        self.horizontalSpacer_9 = QSpacerItem(50, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_20.addItem(self.horizontalSpacer_9, 0, 3, 1, 1)


        self.gridLayout_10.addWidget(self.boxWeighting, 2, 0, 1, 1)

        self.boxBackground = QGroupBox(self.tabOptions)
        self.boxBackground.setObjectName(u"boxBackground")
        self.gridLayout_12 = QGridLayout(self.boxBackground)
        self.gridLayout_12.setObjectName(u"gridLayout_12")
        self.lblBackgd = QLabel(self.boxBackground)
        self.lblBackgd.setObjectName(u"lblBackgd")

        self.gridLayout_12.addWidget(self.lblBackgd, 0, 0, 1, 1)

        self.txtBackgd = QLineEdit(self.boxBackground)
        self.txtBackgd.setObjectName(u"txtBackgd")

        self.gridLayout_12.addWidget(self.txtBackgd, 0, 1, 1, 1)

        self.label_8 = QLabel(self.boxBackground)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_12.addWidget(self.label_8, 0, 2, 1, 2)

        self.chkLowQ = QCheckBox(self.boxBackground)
        self.chkLowQ.setObjectName(u"chkLowQ")

        self.gridLayout_12.addWidget(self.chkLowQ, 2, 0, 1, 2)

        self.gridLayout_14 = QGridLayout()
        self.gridLayout_14.setObjectName(u"gridLayout_14")
        self.lblPowerLowQ = QLabel(self.boxBackground)
        self.lblPowerLowQ.setObjectName(u"lblPowerLowQ")

        self.gridLayout_14.addWidget(self.lblPowerLowQ, 0, 0, 1, 1)

        self.txtPowerLowQ = QLineEdit(self.boxBackground)
        self.txtPowerLowQ.setObjectName(u"txtPowerLowQ")

        self.gridLayout_14.addWidget(self.txtPowerLowQ, 0, 1, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.rbFixPower = QRadioButton(self.boxBackground)
        self.rbFixPower.setObjectName(u"rbFixPower")
        self.rbFixPower.setChecked(True)

        self.horizontalLayout.addWidget(self.rbFixPower)

        self.rbFitPower = QRadioButton(self.boxBackground)
        self.rbFitPower.setObjectName(u"rbFitPower")

        self.horizontalLayout.addWidget(self.rbFitPower)


        self.gridLayout_14.addLayout(self.horizontalLayout, 0, 2, 1, 1)

        self.horizontalSpacer = QSpacerItem(100, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_14.addItem(self.horizontalSpacer, 0, 3, 1, 1)

        self.lblScaleLowQ = QLabel(self.boxBackground)
        self.lblScaleLowQ.setObjectName(u"lblScaleLowQ")

        self.gridLayout_14.addWidget(self.lblScaleLowQ, 1, 0, 1, 1)

        self.txtScaleLowQ = QLineEdit(self.boxBackground)
        self.txtScaleLowQ.setObjectName(u"txtScaleLowQ")

        self.gridLayout_14.addWidget(self.txtScaleLowQ, 1, 1, 1, 1)


        self.gridLayout_12.addLayout(self.gridLayout_14, 3, 0, 1, 3)

        self.qRangeGroupBox = QGroupBox(self.boxBackground)
        self.qRangeGroupBox.setObjectName(u"qRangeGroupBox")
        self.gridLayout_3 = QGridLayout(self.qRangeGroupBox)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_18 = QLabel(self.qRangeGroupBox)
        self.label_18.setObjectName(u"label_18")

        self.horizontalLayout_2.addWidget(self.label_18)

        self.txtBackgdQMin = QLineEdit(self.qRangeGroupBox)
        self.txtBackgdQMin.setObjectName(u"txtBackgdQMin")
        self.txtBackgdQMin.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.txtBackgdQMin.sizePolicy().hasHeightForWidth())
        self.txtBackgdQMin.setSizePolicy(sizePolicy1)

        self.horizontalLayout_2.addWidget(self.txtBackgdQMin)

        self.label_11 = QLabel(self.qRangeGroupBox)
        self.label_11.setObjectName(u"label_11")

        self.horizontalLayout_2.addWidget(self.label_11)

        self.label_10 = QLabel(self.qRangeGroupBox)
        self.label_10.setObjectName(u"label_10")

        self.horizontalLayout_2.addWidget(self.label_10)

        self.txtBackgdQMax = QLineEdit(self.qRangeGroupBox)
        self.txtBackgdQMax.setObjectName(u"txtBackgdQMax")
        self.txtBackgdQMax.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.txtBackgdQMax.sizePolicy().hasHeightForWidth())
        self.txtBackgdQMax.setSizePolicy(sizePolicy1)

        self.horizontalLayout_2.addWidget(self.txtBackgdQMax)

        self.label_16 = QLabel(self.qRangeGroupBox)
        self.label_16.setObjectName(u"label_16")

        self.horizontalLayout_2.addWidget(self.label_16)


        self.gridLayout_3.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)


        self.gridLayout_12.addWidget(self.qRangeGroupBox, 1, 0, 1, 2)

        self.cmdFitFlatBackground = QPushButton(self.boxBackground)
        self.cmdFitFlatBackground.setObjectName(u"cmdFitFlatBackground")

        self.gridLayout_12.addWidget(self.cmdFitFlatBackground, 1, 3, 1, 1)

        self.powerLawQRangeGroupBox = QGroupBox(self.boxBackground)
        self.powerLawQRangeGroupBox.setObjectName(u"powerLawQRangeGroupBox")
        self.gridLayout_4 = QGridLayout(self.powerLawQRangeGroupBox)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_7 = QLabel(self.powerLawQRangeGroupBox)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout_3.addWidget(self.label_7)

        self.txtPowerLawQMin = QLineEdit(self.powerLawQRangeGroupBox)
        self.txtPowerLawQMin.setObjectName(u"txtPowerLawQMin")
        self.txtPowerLawQMin.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.txtPowerLawQMin.sizePolicy().hasHeightForWidth())
        self.txtPowerLawQMin.setSizePolicy(sizePolicy1)

        self.horizontalLayout_3.addWidget(self.txtPowerLawQMin)

        self.label_12 = QLabel(self.powerLawQRangeGroupBox)
        self.label_12.setObjectName(u"label_12")

        self.horizontalLayout_3.addWidget(self.label_12)

        self.label_14 = QLabel(self.powerLawQRangeGroupBox)
        self.label_14.setObjectName(u"label_14")

        self.horizontalLayout_3.addWidget(self.label_14)

        self.txtPowerLawQMax = QLineEdit(self.powerLawQRangeGroupBox)
        self.txtPowerLawQMax.setObjectName(u"txtPowerLawQMax")
        self.txtPowerLawQMax.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.txtPowerLawQMax.sizePolicy().hasHeightForWidth())
        self.txtPowerLawQMax.setSizePolicy(sizePolicy1)

        self.horizontalLayout_3.addWidget(self.txtPowerLawQMax)

        self.label_17 = QLabel(self.powerLawQRangeGroupBox)
        self.label_17.setObjectName(u"label_17")

        self.horizontalLayout_3.addWidget(self.label_17)


        self.gridLayout_4.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)


        self.gridLayout_12.addWidget(self.powerLawQRangeGroupBox, 4, 0, 1, 2)

        self.cmdFitPowerLaw = QPushButton(self.boxBackground)
        self.cmdFitPowerLaw.setObjectName(u"cmdFitPowerLaw")

        self.gridLayout_12.addWidget(self.cmdFitPowerLaw, 4, 3, 1, 1)


        self.gridLayout_10.addWidget(self.boxBackground, 3, 0, 1, 1)

        self.SizeDistributionTabWidget.addTab(self.tabOptions, "")

        self.gridLayout_7.addWidget(self.SizeDistributionTabWidget, 0, 0, 1, 1)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.quickFitButton = QPushButton(SizeDistribution)
        self.quickFitButton.setObjectName(u"quickFitButton")

        self.horizontalLayout_8.addWidget(self.quickFitButton)

        self.fullFitButton = QPushButton(SizeDistribution)
        self.fullFitButton.setObjectName(u"fullFitButton")

        self.horizontalLayout_8.addWidget(self.fullFitButton)

        self.horizontalSpacer1 = QSpacerItem(200, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer1)

        self.helpButton = QPushButton(SizeDistribution)
        self.helpButton.setObjectName(u"helpButton")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.helpButton.sizePolicy().hasHeightForWidth())
        self.helpButton.setSizePolicy(sizePolicy2)

        self.horizontalLayout_8.addWidget(self.helpButton)


        self.gridLayout_7.addLayout(self.horizontalLayout_8, 1, 0, 1, 1)

        QWidget.setTabOrder(self.quickFitButton, self.fullFitButton)
        QWidget.setTabOrder(self.fullFitButton, self.helpButton)

        self.retranslateUi(SizeDistribution)

        self.SizeDistributionTabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(SizeDistribution)
    # setupUi

    def retranslateUi(self, SizeDistribution):
        SizeDistribution.setWindowTitle(QCoreApplication.translate("SizeDistribution", u"Size Distribution", None))
        self.boxData.setTitle(QCoreApplication.translate("SizeDistribution", u"I(q) data source", None))
        self.lblName.setText(QCoreApplication.translate("SizeDistribution", u"Name:", None))
        self.boxModel.setTitle(QCoreApplication.translate("SizeDistribution", u"Model", None))
        self.lblModel.setText(QCoreApplication.translate("SizeDistribution", u"Model name", None))
        self.cbModel.setItemText(0, QCoreApplication.translate("SizeDistribution", u"Ellipsoid", None))

#if QT_CONFIG(tooltip)
        self.cbModel.setToolTip(QCoreApplication.translate("SizeDistribution", u"Select a model", None))
#endif // QT_CONFIG(tooltip)
        self.lblAspectRatio.setText(QCoreApplication.translate("SizeDistribution", u"Aspect ratio:", None))
        self.boxParameters.setTitle(QCoreApplication.translate("SizeDistribution", u"Distribution parameters", None))
        self.lblMinDiameter.setText(QCoreApplication.translate("SizeDistribution", u"Minimum diameter:", None))
        self.label_2.setText(QCoreApplication.translate("SizeDistribution", u"<html><head/><body><p>\u00c5</p></body></html>\n"
"             ", None))
        self.lblMaxDiameter.setText(QCoreApplication.translate("SizeDistribution", u"Maximum diameter:", None))
        self.label_3.setText(QCoreApplication.translate("SizeDistribution", u"<html><head/><body><p>\u00c5</p></body></html>\n"
"             ", None))
        self.lblBinsDiameter.setText(QCoreApplication.translate("SizeDistribution", u"Bins in diameter:", None))
#if QT_CONFIG(tooltip)
        self.chkLogBinning.setToolTip(QCoreApplication.translate("SizeDistribution", u"<html><head/><body><p>Switch on logarithmic binning for diameter.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.chkLogBinning.setText(QCoreApplication.translate("SizeDistribution", u"Logarithmic binning?", None))
        self.lblContrast.setText(QCoreApplication.translate("SizeDistribution", u"Contrast:", None))
        self.label_4.setText(QCoreApplication.translate("SizeDistribution", u"<html><head/><body><p>10<span\n"
"              style=\" vertical-align:super;\">-6</span>/\u00c5<span\n"
"              style=\" vertical-align:super;\">-2</span></p></body></html>\n"
"             ", None))
        self.boxOutput.setTitle(QCoreApplication.translate("SizeDistribution", u"Output", None))
        self.lblConvergence.setText("")
        self.lblChiSq.setText(QCoreApplication.translate("SizeDistribution", u"ChiSq: ", None))
        self.lblVolume.setText(QCoreApplication.translate("SizeDistribution", u"Total volume fraction: ", None))
        self.label_5.setText(QCoreApplication.translate("SizeDistribution", u"%", None))
        self.lblDiameterMean.setText(QCoreApplication.translate("SizeDistribution", u"Mean diameter:", None))
        self.label_6.setText(QCoreApplication.translate("SizeDistribution", u"<html><head/><body><p>\u00c5</p></body></html>", None))
        self.lblDiameterMedian.setText(QCoreApplication.translate("SizeDistribution", u"Median diameter:", None))
        self.label_19.setText(QCoreApplication.translate("SizeDistribution", u"<html><head/><body><p>\u00c5</p></body></html>", None))
        self.lblDiameterMode.setText(QCoreApplication.translate("SizeDistribution", u"Mode diameter:", None))
        self.label_20.setText(QCoreApplication.translate("SizeDistribution", u"<html><head/><body><p>\u00c5</p></body></html>", None))
        self.SizeDistributionTabWidget.setTabText(self.SizeDistributionTabWidget.indexOf(self.tabMain), QCoreApplication.translate("SizeDistribution", u"Parameters", None))
        self.boxFittingRange.setTitle(QCoreApplication.translate("SizeDistribution", u"Fitting range", None))
        self.lblMinRange.setText(QCoreApplication.translate("SizeDistribution", u"Min range", None))
#if QT_CONFIG(tooltip)
        self.txtMinRange.setToolTip(QCoreApplication.translate("SizeDistribution", u"<html><head/><body><p>Minimum\n"
"                value of Q.</p></body></html>\n"
"               ", None))
#endif // QT_CONFIG(tooltip)
        self.label_13.setText(QCoreApplication.translate("SizeDistribution", u"<html><head/><body><p>\u00c5<span\n"
"                style=\" vertical-align:super;\">-1</span></p></body></html>\n"
"               ", None))
        self.lblMaxRange.setText(QCoreApplication.translate("SizeDistribution", u"Max range", None))
#if QT_CONFIG(tooltip)
        self.txtMaxRange.setToolTip(QCoreApplication.translate("SizeDistribution", u"<html><head/><body><p>Maximum\n"
"                value of Q.</p></body></html>\n"
"               ", None))
#endif // QT_CONFIG(tooltip)
        self.label_15.setText(QCoreApplication.translate("SizeDistribution", u"<html><head/><body><p>\u00c5<span\n"
"                style=\" vertical-align:super;\">-1</span></p></body></html>\n"
"               ", None))
#if QT_CONFIG(tooltip)
        self.cmdReset.setToolTip(QCoreApplication.translate("SizeDistribution", u"<html><head/><body><p>Reset\n"
"              the Q range to the default.</p></body></html>\n"
"             ", None))
#endif // QT_CONFIG(tooltip)
        self.cmdReset.setText(QCoreApplication.translate("SizeDistribution", u"Reset", None))
        self.boxAdvancedParameters.setTitle(QCoreApplication.translate("SizeDistribution", u"Method parameters", None))
        self.lblSkyBackgd.setText(QCoreApplication.translate("SizeDistribution", u"MaxEnt Sky Background:", None))
        self.label_9.setText(QCoreApplication.translate("SizeDistribution", u"<html><head/><body><p>Suggested: 1e-6</p></body></html>", None))
        self.lblIterations.setText(QCoreApplication.translate("SizeDistribution", u"Iterations:", None))
        self.boxWeighting.setTitle(QCoreApplication.translate("SizeDistribution", u"Weighting", None))
        self.rbWeighting1.setText(QCoreApplication.translate("SizeDistribution", u"None", None))
        self.rbWeighting2.setText(QCoreApplication.translate("SizeDistribution", u"Use dI Data", None))
        self.rbWeighting3.setText(QCoreApplication.translate("SizeDistribution", u"Use |sqrt(I Data)|", None))
        self.rbWeighting4.setText(QCoreApplication.translate("SizeDistribution", u"Use % |I Data|", None))
        self.lblWgtFactor.setText(QCoreApplication.translate("SizeDistribution", u"Weight factor:", None))
        self.boxBackground.setTitle(QCoreApplication.translate("SizeDistribution", u"Background", None))
        self.lblBackgd.setText(QCoreApplication.translate("SizeDistribution", u"Flat background:", None))
        self.label_8.setText(QCoreApplication.translate("SizeDistribution", u"<html><head/><body><p>cm<span style=\"\n"
"              vertical-align:super;\">-1</span></p></body></html>\n"
"             ", None))
#if QT_CONFIG(tooltip)
        self.chkLowQ.setToolTip(QCoreApplication.translate("SizeDistribution", u"Check to subtract low-Q power law", None))
#endif // QT_CONFIG(tooltip)
        self.chkLowQ.setText(QCoreApplication.translate("SizeDistribution", u"Subtract Low-Q power law", None))
        self.lblPowerLowQ.setText(QCoreApplication.translate("SizeDistribution", u"Power:", None))
#if QT_CONFIG(tooltip)
        self.txtPowerLowQ.setToolTip(QCoreApplication.translate("SizeDistribution", u"Exponent to apply to the Power_law function.", None))
#endif // QT_CONFIG(tooltip)
        self.rbFixPower.setText(QCoreApplication.translate("SizeDistribution", u"Fix", None))
        self.rbFitPower.setText(QCoreApplication.translate("SizeDistribution", u"Fit", None))
        self.lblScaleLowQ.setText(QCoreApplication.translate("SizeDistribution", u"Scale:", None))
#if QT_CONFIG(tooltip)
        self.txtScaleLowQ.setToolTip(QCoreApplication.translate("SizeDistribution", u"Scale to apply to the Power_law function.", None))
#endif // QT_CONFIG(tooltip)
        self.qRangeGroupBox.setTitle(QCoreApplication.translate("SizeDistribution", u"Fit flat background Q range", None))
        self.label_18.setText(QCoreApplication.translate("SizeDistribution", u"Min:", None))
        self.label_11.setText(QCoreApplication.translate("SizeDistribution", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.label_10.setText(QCoreApplication.translate("SizeDistribution", u"Max:", None))
        self.label_16.setText(QCoreApplication.translate("SizeDistribution", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.cmdFitFlatBackground.setText(QCoreApplication.translate("SizeDistribution", u"Fit flat background", None))
        self.powerLawQRangeGroupBox.setTitle(QCoreApplication.translate("SizeDistribution", u"Fit power law Q range", None))
        self.label_7.setText(QCoreApplication.translate("SizeDistribution", u"Min:", None))
        self.label_12.setText(QCoreApplication.translate("SizeDistribution", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.label_14.setText(QCoreApplication.translate("SizeDistribution", u"Max:", None))
        self.label_17.setText(QCoreApplication.translate("SizeDistribution", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.cmdFitPowerLaw.setText(QCoreApplication.translate("SizeDistribution", u"Fit power law", None))
        self.SizeDistributionTabWidget.setTabText(self.SizeDistributionTabWidget.indexOf(self.tabOptions), QCoreApplication.translate("SizeDistribution", u"Options", None))
        self.quickFitButton.setText(QCoreApplication.translate("SizeDistribution", u"Quick fit", None))
        self.fullFitButton.setText(QCoreApplication.translate("SizeDistribution", u"Full fit", None))
        self.helpButton.setText(QCoreApplication.translate("SizeDistribution", u"Help", None))
    # retranslateUi

