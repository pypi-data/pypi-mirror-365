# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'TabbedInversionUI.ui'
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
    QHBoxLayout, QLabel, QLayout, QLineEdit,
    QPushButton, QRadioButton, QSizePolicy, QSpacerItem,
    QTabWidget, QWidget)

class Ui_PrInversion(object):
    def setupUi(self, PrInversion):
        if not PrInversion.objectName():
            PrInversion.setObjectName(u"PrInversion")
        PrInversion.resize(536, 543)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(PrInversion.sizePolicy().hasHeightForWidth())
        PrInversion.setSizePolicy(sizePolicy)
        PrInversion.setMinimumSize(QSize(0, 0))
        PrInversion.setMaximumSize(QSize(16777215, 16777215))
        self.gridLayout_7 = QGridLayout(PrInversion)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.calculateThisButton = QPushButton(PrInversion)
        self.calculateThisButton.setObjectName(u"calculateThisButton")
        self.calculateThisButton.setEnabled(True)

        self.horizontalLayout_8.addWidget(self.calculateThisButton)

        self.calculateAllButton = QPushButton(PrInversion)
        self.calculateAllButton.setObjectName(u"calculateAllButton")
        self.calculateAllButton.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.calculateAllButton.sizePolicy().hasHeightForWidth())
        self.calculateAllButton.setSizePolicy(sizePolicy1)

        self.horizontalLayout_8.addWidget(self.calculateAllButton)

        self.stopButton = QPushButton(PrInversion)
        self.stopButton.setObjectName(u"stopButton")

        self.horizontalLayout_8.addWidget(self.stopButton)

        self.showResultsButton = QPushButton(PrInversion)
        self.showResultsButton.setObjectName(u"showResultsButton")

        self.horizontalLayout_8.addWidget(self.showResultsButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer)

        self.helpButton = QPushButton(PrInversion)
        self.helpButton.setObjectName(u"helpButton")
        sizePolicy1.setHeightForWidth(self.helpButton.sizePolicy().hasHeightForWidth())
        self.helpButton.setSizePolicy(sizePolicy1)

        self.horizontalLayout_8.addWidget(self.helpButton)


        self.gridLayout_7.addLayout(self.horizontalLayout_8, 2, 0, 1, 1)

        self.PrTabWidget = QTabWidget(PrInversion)
        self.PrTabWidget.setObjectName(u"PrTabWidget")
        sizePolicy.setHeightForWidth(self.PrTabWidget.sizePolicy().hasHeightForWidth())
        self.PrTabWidget.setSizePolicy(sizePolicy)
        self.PrTabWidget.setMinimumSize(QSize(0, 0))
        self.tabMain = QWidget()
        self.tabMain.setObjectName(u"tabMain")
        self.gridLayout_6 = QGridLayout(self.tabMain)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.paramGroupBox = QGroupBox(self.tabMain)
        self.paramGroupBox.setObjectName(u"paramGroupBox")
        sizePolicy.setHeightForWidth(self.paramGroupBox.sizePolicy().hasHeightForWidth())
        self.paramGroupBox.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(self.paramGroupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_12 = QLabel(self.paramGroupBox)
        self.label_12.setObjectName(u"label_12")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_12.sizePolicy().hasHeightForWidth())
        self.label_12.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.label_12, 0, 0, 1, 1)

        self.noOfTermsInput = QLineEdit(self.paramGroupBox)
        self.noOfTermsInput.setObjectName(u"noOfTermsInput")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.noOfTermsInput.sizePolicy().hasHeightForWidth())
        self.noOfTermsInput.setSizePolicy(sizePolicy3)
        self.noOfTermsInput.setMinimumSize(QSize(40, 0))

        self.gridLayout.addWidget(self.noOfTermsInput, 0, 1, 1, 1)

        self.noOfTermsSuggestionButton = QPushButton(self.paramGroupBox)
        self.noOfTermsSuggestionButton.setObjectName(u"noOfTermsSuggestionButton")
        self.noOfTermsSuggestionButton.setEnabled(False)

        self.gridLayout.addWidget(self.noOfTermsSuggestionButton, 0, 2, 1, 1)

        self.label_13 = QLabel(self.paramGroupBox)
        self.label_13.setObjectName(u"label_13")
        sizePolicy2.setHeightForWidth(self.label_13.sizePolicy().hasHeightForWidth())
        self.label_13.setSizePolicy(sizePolicy2)
        self.label_13.setMinimumSize(QSize(80, 0))

        self.gridLayout.addWidget(self.label_13, 1, 0, 1, 1)

        self.regularizationConstantInput = QLineEdit(self.paramGroupBox)
        self.regularizationConstantInput.setObjectName(u"regularizationConstantInput")
        sizePolicy3.setHeightForWidth(self.regularizationConstantInput.sizePolicy().hasHeightForWidth())
        self.regularizationConstantInput.setSizePolicy(sizePolicy3)
        self.regularizationConstantInput.setMinimumSize(QSize(40, 0))

        self.gridLayout.addWidget(self.regularizationConstantInput, 1, 1, 1, 1)

        self.regConstantSuggestionButton = QPushButton(self.paramGroupBox)
        self.regConstantSuggestionButton.setObjectName(u"regConstantSuggestionButton")
        self.regConstantSuggestionButton.setEnabled(False)

        self.gridLayout.addWidget(self.regConstantSuggestionButton, 1, 2, 1, 1)

        self.label_14 = QLabel(self.paramGroupBox)
        self.label_14.setObjectName(u"label_14")
        sizePolicy2.setHeightForWidth(self.label_14.sizePolicy().hasHeightForWidth())
        self.label_14.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.label_14, 2, 0, 1, 1)

        self.maxDistanceInput = QLineEdit(self.paramGroupBox)
        self.maxDistanceInput.setObjectName(u"maxDistanceInput")
        sizePolicy3.setHeightForWidth(self.maxDistanceInput.sizePolicy().hasHeightForWidth())
        self.maxDistanceInput.setSizePolicy(sizePolicy3)
        self.maxDistanceInput.setMinimumSize(QSize(40, 0))

        self.gridLayout.addWidget(self.maxDistanceInput, 2, 1, 1, 1)

        self.explorerButton = QPushButton(self.paramGroupBox)
        self.explorerButton.setObjectName(u"explorerButton")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.explorerButton.sizePolicy().hasHeightForWidth())
        self.explorerButton.setSizePolicy(sizePolicy4)
        self.explorerButton.setMinimumSize(QSize(50, 0))
        self.explorerButton.setLayoutDirection(Qt.LeftToRight)

        self.gridLayout.addWidget(self.explorerButton, 2, 2, 1, 1)

        self.noOfTermsInput.raise_()
        self.noOfTermsSuggestionButton.raise_()
        self.regularizationConstantInput.raise_()
        self.regConstantSuggestionButton.raise_()
        self.maxDistanceInput.raise_()
        self.explorerButton.raise_()
        self.label_13.raise_()
        self.label_12.raise_()
        self.label_14.raise_()

        self.gridLayout_6.addWidget(self.paramGroupBox, 1, 0, 1, 1)

        self.outputsGroupBox = QGroupBox(self.tabMain)
        self.outputsGroupBox.setObjectName(u"outputsGroupBox")
        self.gridLayout_4 = QGridLayout(self.outputsGroupBox)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.label_19 = QLabel(self.outputsGroupBox)
        self.label_19.setObjectName(u"label_19")

        self.gridLayout_4.addWidget(self.label_19, 0, 4, 1, 1)

        self.posFractionValue = QLineEdit(self.outputsGroupBox)
        self.posFractionValue.setObjectName(u"posFractionValue")
        self.posFractionValue.setEnabled(True)
        sizePolicy3.setHeightForWidth(self.posFractionValue.sizePolicy().hasHeightForWidth())
        self.posFractionValue.setSizePolicy(sizePolicy3)
        self.posFractionValue.setReadOnly(True)

        self.gridLayout_4.addWidget(self.posFractionValue, 2, 5, 1, 1)

        self.label_29 = QLabel(self.outputsGroupBox)
        self.label_29.setObjectName(u"label_29")

        self.gridLayout_4.addWidget(self.label_29, 3, 4, 1, 1)

        self.label_27 = QLabel(self.outputsGroupBox)
        self.label_27.setObjectName(u"label_27")

        self.gridLayout_4.addWidget(self.label_27, 3, 2, 1, 1)

        self.label_24 = QLabel(self.outputsGroupBox)
        self.label_24.setObjectName(u"label_24")

        self.gridLayout_4.addWidget(self.label_24, 0, 2, 1, 1)

        self.label_15 = QLabel(self.outputsGroupBox)
        self.label_15.setObjectName(u"label_15")

        self.gridLayout_4.addWidget(self.label_15, 0, 0, 1, 1)

        self.oscillationValue = QLineEdit(self.outputsGroupBox)
        self.oscillationValue.setObjectName(u"oscillationValue")
        self.oscillationValue.setEnabled(True)
        sizePolicy3.setHeightForWidth(self.oscillationValue.sizePolicy().hasHeightForWidth())
        self.oscillationValue.setSizePolicy(sizePolicy3)
        self.oscillationValue.setReadOnly(True)

        self.gridLayout_4.addWidget(self.oscillationValue, 1, 5, 1, 1)

        self.label_17 = QLabel(self.outputsGroupBox)
        self.label_17.setObjectName(u"label_17")

        self.gridLayout_4.addWidget(self.label_17, 2, 0, 1, 1)

        self.label_21 = QLabel(self.outputsGroupBox)
        self.label_21.setObjectName(u"label_21")

        self.gridLayout_4.addWidget(self.label_21, 2, 4, 1, 1)

        self.label_20 = QLabel(self.outputsGroupBox)
        self.label_20.setObjectName(u"label_20")

        self.gridLayout_4.addWidget(self.label_20, 1, 4, 1, 1)

        self.sigmaPosFractionValue = QLineEdit(self.outputsGroupBox)
        self.sigmaPosFractionValue.setObjectName(u"sigmaPosFractionValue")
        self.sigmaPosFractionValue.setEnabled(True)
        sizePolicy3.setHeightForWidth(self.sigmaPosFractionValue.sizePolicy().hasHeightForWidth())
        self.sigmaPosFractionValue.setSizePolicy(sizePolicy3)
        self.sigmaPosFractionValue.setReadOnly(True)

        self.gridLayout_4.addWidget(self.sigmaPosFractionValue, 3, 5, 1, 1)

        self.chiDofValue = QLineEdit(self.outputsGroupBox)
        self.chiDofValue.setObjectName(u"chiDofValue")
        self.chiDofValue.setEnabled(True)
        sizePolicy3.setHeightForWidth(self.chiDofValue.sizePolicy().hasHeightForWidth())
        self.chiDofValue.setSizePolicy(sizePolicy3)
        self.chiDofValue.setReadOnly(True)

        self.gridLayout_4.addWidget(self.chiDofValue, 0, 5, 1, 1)

        self.label_25 = QLabel(self.outputsGroupBox)
        self.label_25.setObjectName(u"label_25")

        self.gridLayout_4.addWidget(self.label_25, 1, 2, 1, 1)

        self.label_18 = QLabel(self.outputsGroupBox)
        self.label_18.setObjectName(u"label_18")

        self.gridLayout_4.addWidget(self.label_18, 3, 0, 1, 1)

        self.label_26 = QLabel(self.outputsGroupBox)
        self.label_26.setObjectName(u"label_26")

        self.gridLayout_4.addWidget(self.label_26, 2, 2, 1, 1)

        self.rgValue = QLineEdit(self.outputsGroupBox)
        self.rgValue.setObjectName(u"rgValue")
        self.rgValue.setEnabled(True)
        sizePolicy3.setHeightForWidth(self.rgValue.sizePolicy().hasHeightForWidth())
        self.rgValue.setSizePolicy(sizePolicy3)
        self.rgValue.setReadOnly(True)

        self.gridLayout_4.addWidget(self.rgValue, 0, 1, 1, 1)

        self.label_16 = QLabel(self.outputsGroupBox)
        self.label_16.setObjectName(u"label_16")

        self.gridLayout_4.addWidget(self.label_16, 1, 0, 1, 1)

        self.label_22 = QLabel(self.outputsGroupBox)
        self.label_22.setObjectName(u"label_22")

        self.gridLayout_4.addWidget(self.label_22, 0, 3, 1, 1)

        self.iQ0Value = QLineEdit(self.outputsGroupBox)
        self.iQ0Value.setObjectName(u"iQ0Value")
        self.iQ0Value.setEnabled(True)
        sizePolicy3.setHeightForWidth(self.iQ0Value.sizePolicy().hasHeightForWidth())
        self.iQ0Value.setSizePolicy(sizePolicy3)
        self.iQ0Value.setReadOnly(True)

        self.gridLayout_4.addWidget(self.iQ0Value, 1, 1, 1, 1)

        self.computationTimeValue = QLineEdit(self.outputsGroupBox)
        self.computationTimeValue.setObjectName(u"computationTimeValue")
        self.computationTimeValue.setEnabled(True)
        sizePolicy3.setHeightForWidth(self.computationTimeValue.sizePolicy().hasHeightForWidth())
        self.computationTimeValue.setSizePolicy(sizePolicy3)
        self.computationTimeValue.setReadOnly(True)

        self.gridLayout_4.addWidget(self.computationTimeValue, 3, 1, 1, 1)

        self.backgroundValue = QLineEdit(self.outputsGroupBox)
        self.backgroundValue.setObjectName(u"backgroundValue")
        self.backgroundValue.setEnabled(True)
        sizePolicy3.setHeightForWidth(self.backgroundValue.sizePolicy().hasHeightForWidth())
        self.backgroundValue.setSizePolicy(sizePolicy3)
        self.backgroundValue.setReadOnly(True)

        self.gridLayout_4.addWidget(self.backgroundValue, 2, 1, 1, 1)


        self.gridLayout_6.addWidget(self.outputsGroupBox, 3, 0, 1, 1)

        self.dataSourceGroupBox = QGroupBox(self.tabMain)
        self.dataSourceGroupBox.setObjectName(u"dataSourceGroupBox")
        sizePolicy.setHeightForWidth(self.dataSourceGroupBox.sizePolicy().hasHeightForWidth())
        self.dataSourceGroupBox.setSizePolicy(sizePolicy)
        self.gridLayout_2 = QGridLayout(self.dataSourceGroupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(self.dataSourceGroupBox)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label)

        self.dataList = QComboBox(self.dataSourceGroupBox)
        self.dataList.setObjectName(u"dataList")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.dataList.sizePolicy().hasHeightForWidth())
        self.dataList.setSizePolicy(sizePolicy5)

        self.horizontalLayout_2.addWidget(self.dataList)

        self.removeButton = QPushButton(self.dataSourceGroupBox)
        self.removeButton.setObjectName(u"removeButton")
        self.removeButton.setEnabled(False)
        sizePolicy4.setHeightForWidth(self.removeButton.sizePolicy().hasHeightForWidth())
        self.removeButton.setSizePolicy(sizePolicy4)

        self.horizontalLayout_2.addWidget(self.removeButton)


        self.gridLayout_2.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)


        self.gridLayout_6.addWidget(self.dataSourceGroupBox, 0, 0, 1, 1)

        self.PrTabWidget.addTab(self.tabMain, "")
        self.tabOptions = QWidget()
        self.tabOptions.setObjectName(u"tabOptions")
        self.gridLayout_9 = QGridLayout(self.tabOptions)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.groupBox = QGroupBox(self.tabOptions)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_8 = QGridLayout(self.groupBox)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.qRangeGroupBox = QGroupBox(self.groupBox)
        self.qRangeGroupBox.setObjectName(u"qRangeGroupBox")
        self.gridLayout_3 = QGridLayout(self.qRangeGroupBox)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_7 = QLabel(self.qRangeGroupBox)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout_4.addWidget(self.label_7)

        self.minQInput = QLineEdit(self.qRangeGroupBox)
        self.minQInput.setObjectName(u"minQInput")
        self.minQInput.setEnabled(True)
        sizePolicy3.setHeightForWidth(self.minQInput.sizePolicy().hasHeightForWidth())
        self.minQInput.setSizePolicy(sizePolicy3)

        self.horizontalLayout_4.addWidget(self.minQInput)

        self.label_11 = QLabel(self.qRangeGroupBox)
        self.label_11.setObjectName(u"label_11")

        self.horizontalLayout_4.addWidget(self.label_11)

        self.label_8 = QLabel(self.qRangeGroupBox)
        self.label_8.setObjectName(u"label_8")

        self.horizontalLayout_4.addWidget(self.label_8)

        self.maxQInput = QLineEdit(self.qRangeGroupBox)
        self.maxQInput.setObjectName(u"maxQInput")
        self.maxQInput.setEnabled(True)
        sizePolicy3.setHeightForWidth(self.maxQInput.sizePolicy().hasHeightForWidth())
        self.maxQInput.setSizePolicy(sizePolicy3)

        self.horizontalLayout_4.addWidget(self.maxQInput)

        self.label_9 = QLabel(self.qRangeGroupBox)
        self.label_9.setObjectName(u"label_9")

        self.horizontalLayout_4.addWidget(self.label_9)


        self.gridLayout_3.addLayout(self.horizontalLayout_4, 0, 0, 1, 1)


        self.gridLayout_8.addWidget(self.qRangeGroupBox, 1, 0, 1, 1)

        self.slitParamsGroupBox = QGroupBox(self.groupBox)
        self.slitParamsGroupBox.setObjectName(u"slitParamsGroupBox")
        self.gridLayout_5 = QGridLayout(self.slitParamsGroupBox)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_3 = QLabel(self.slitParamsGroupBox)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout.addWidget(self.label_3)

        self.slitHeightInput = QLineEdit(self.slitParamsGroupBox)
        self.slitHeightInput.setObjectName(u"slitHeightInput")
        self.slitHeightInput.setEnabled(True)
        sizePolicy3.setHeightForWidth(self.slitHeightInput.sizePolicy().hasHeightForWidth())
        self.slitHeightInput.setSizePolicy(sizePolicy3)

        self.horizontalLayout.addWidget(self.slitHeightInput)

        self.label_6 = QLabel(self.slitParamsGroupBox)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout.addWidget(self.label_6)

        self.label_4 = QLabel(self.slitParamsGroupBox)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout.addWidget(self.label_4)

        self.slitWidthInput = QLineEdit(self.slitParamsGroupBox)
        self.slitWidthInput.setObjectName(u"slitWidthInput")
        self.slitWidthInput.setEnabled(True)
        sizePolicy3.setHeightForWidth(self.slitWidthInput.sizePolicy().hasHeightForWidth())
        self.slitWidthInput.setSizePolicy(sizePolicy3)

        self.horizontalLayout.addWidget(self.slitWidthInput)

        self.label_2 = QLabel(self.slitParamsGroupBox)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout.addWidget(self.label_2)


        self.gridLayout_5.addLayout(self.horizontalLayout, 0, 0, 1, 1)


        self.gridLayout_8.addWidget(self.slitParamsGroupBox, 2, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_3.addWidget(self.label_5)

        self.backgroundInput = QLineEdit(self.groupBox)
        self.backgroundInput.setObjectName(u"backgroundInput")
        self.backgroundInput.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.backgroundInput)

        self.label_10 = QLabel(self.groupBox)
        self.label_10.setObjectName(u"label_10")

        self.horizontalLayout_3.addWidget(self.label_10)

        self.estimateBgd = QRadioButton(self.groupBox)
        self.estimateBgd.setObjectName(u"estimateBgd")

        self.horizontalLayout_3.addWidget(self.estimateBgd)

        self.manualBgd = QRadioButton(self.groupBox)
        self.manualBgd.setObjectName(u"manualBgd")

        self.horizontalLayout_3.addWidget(self.manualBgd)

        self.horizontalLayout_3.setStretch(0, 2)
        self.horizontalLayout_3.setStretch(1, 1)
        self.horizontalLayout_3.setStretch(3, 2)
        self.horizontalLayout_3.setStretch(4, 2)

        self.gridLayout_8.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_8.addItem(self.verticalSpacer, 3, 0, 1, 1)


        self.gridLayout_9.addWidget(self.groupBox, 0, 0, 1, 1)

        self.PrTabWidget.addTab(self.tabOptions, "")

        self.gridLayout_7.addWidget(self.PrTabWidget, 0, 0, 1, 1)


        self.retranslateUi(PrInversion)

        self.PrTabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(PrInversion)
    # setupUi

    def retranslateUi(self, PrInversion):
        PrInversion.setWindowTitle(QCoreApplication.translate("PrInversion", u"P(r) Inversion", None))
        self.calculateThisButton.setText(QCoreApplication.translate("PrInversion", u"Calculate", None))
        self.calculateAllButton.setText(QCoreApplication.translate("PrInversion", u"Calculate All", None))
        self.stopButton.setText(QCoreApplication.translate("PrInversion", u"Stop", None))
        self.showResultsButton.setText(QCoreApplication.translate("PrInversion", u"Show Results", None))
        self.helpButton.setText(QCoreApplication.translate("PrInversion", u"Help", None))
#if QT_CONFIG(tooltip)
        self.paramGroupBox.setToolTip(QCoreApplication.translate("PrInversion", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'MS Shell Dlg 2'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<pre style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;><span style=\" font-family:'Courier New'; font-size:9pt; color:#000000;\">P(r) is found by fitting a set of base functions to I(Q). The minimization involves a regularization term to ensure a smooth P(r). The regularization constant gives the size of that term. The suggested value is the value above which the output P(r) will have only one peak.</span></pre></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.paramGroupBox.setTitle(QCoreApplication.translate("PrInversion", u"Parameters", None))
        self.label_12.setText(QCoreApplication.translate("PrInversion", u"Number of terms", None))
        self.noOfTermsSuggestionButton.setText("")
        self.label_13.setText(QCoreApplication.translate("PrInversion", u"Reg. constant", None))
        self.regConstantSuggestionButton.setText("")
        self.label_14.setText(QCoreApplication.translate("PrInversion", u"Max distance [\u00c5]", None))
#if QT_CONFIG(tooltip)
        self.explorerButton.setToolTip(QCoreApplication.translate("PrInversion", u"<html><head/><body><p>Open the D<span style=\" vertical-align:sub;\">max</span> explorer window.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.explorerButton.setText(QCoreApplication.translate("PrInversion", u"Explore", None))
        self.outputsGroupBox.setTitle(QCoreApplication.translate("PrInversion", u"Outputs", None))
        self.label_19.setText(QCoreApplication.translate("PrInversion", u"<html><head/><body><p>\u03c7<span style=\" vertical-align:super;\">2</span>/dof</p></body></html>", None))
        self.label_29.setText(QCoreApplication.translate("PrInversion", u"<html><head/><body><p>P<span style=\" vertical-align:super;\">+</span><span style=\" vertical-align:sub;\">1-\u03c3</span> fraction</p></body></html>", None))
        self.label_27.setText(QCoreApplication.translate("PrInversion", u"secs", None))
        self.label_24.setText(QCoreApplication.translate("PrInversion", u"\u00c5", None))
        self.label_15.setText(QCoreApplication.translate("PrInversion", u"<html><head/><body><p>R<span style=\" vertical-align:sub;\">g</span></p></body></html>", None))
        self.label_17.setText(QCoreApplication.translate("PrInversion", u"Background", None))
        self.label_21.setText(QCoreApplication.translate("PrInversion", u"<html><head/><body><p>P<span style=\" vertical-align:super;\">+</span> Fraction</p></body></html>", None))
        self.label_20.setText(QCoreApplication.translate("PrInversion", u"Oscillations", None))
        self.label_25.setText(QCoreApplication.translate("PrInversion", u"<html><head/><body><p>cm<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.label_18.setText(QCoreApplication.translate("PrInversion", u"Calc. Time", None))
        self.label_26.setText(QCoreApplication.translate("PrInversion", u"<html><head/><body><p>cm<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.label_16.setText(QCoreApplication.translate("PrInversion", u"I(Q=0)", None))
        self.label_22.setText("")
        self.dataSourceGroupBox.setTitle(QCoreApplication.translate("PrInversion", u"I(q) data source", None))
        self.label.setText(QCoreApplication.translate("PrInversion", u"Data File Name:", None))
        self.removeButton.setText(QCoreApplication.translate("PrInversion", u"Remove", None))
        self.PrTabWidget.setTabText(self.PrTabWidget.indexOf(self.tabMain), QCoreApplication.translate("PrInversion", u"Parameters", None))
        self.groupBox.setTitle(QCoreApplication.translate("PrInversion", u"Options", None))
        self.qRangeGroupBox.setTitle(QCoreApplication.translate("PrInversion", u"Total Q range", None))
        self.label_7.setText(QCoreApplication.translate("PrInversion", u"Min:", None))
        self.label_11.setText(QCoreApplication.translate("PrInversion", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.label_8.setText(QCoreApplication.translate("PrInversion", u"Max:", None))
        self.label_9.setText(QCoreApplication.translate("PrInversion", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.slitParamsGroupBox.setTitle(QCoreApplication.translate("PrInversion", u"Slit Parameters", None))
        self.label_3.setText(QCoreApplication.translate("PrInversion", u"Height", None))
        self.label_6.setText(QCoreApplication.translate("PrInversion", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.label_4.setText(QCoreApplication.translate("PrInversion", u"Width", None))
        self.label_2.setText(QCoreApplication.translate("PrInversion", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.label_5.setText(QCoreApplication.translate("PrInversion", u"Background Level:", None))
        self.backgroundInput.setText(QCoreApplication.translate("PrInversion", u"0.0", None))
        self.label_10.setText(QCoreApplication.translate("PrInversion", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.estimateBgd.setText(QCoreApplication.translate("PrInversion", u"Estimate", None))
        self.manualBgd.setText(QCoreApplication.translate("PrInversion", u"Manual Input", None))
        self.PrTabWidget.setTabText(self.PrTabWidget.indexOf(self.tabOptions), QCoreApplication.translate("PrInversion", u"Options", None))
    # retranslateUi

