# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SldPanel.ui'
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
    QGroupBox, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QWidget)

class Ui_SldPanel(object):
    def setupUi(self, SldPanel):
        if not SldPanel.objectName():
            SldPanel.setObjectName(u"SldPanel")
        SldPanel.resize(552, 495)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SldPanel.sizePolicy().hasHeightForWidth())
        SldPanel.setSizePolicy(sizePolicy)
        icon = QIcon()
        icon.addFile(u":/res/ball.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        SldPanel.setWindowIcon(icon)
        self.gridLayout_2 = QGridLayout(SldPanel)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer, 3, 0, 1, 1)

        self.groupBoxOutput = QGroupBox(SldPanel)
        self.groupBoxOutput.setObjectName(u"groupBoxOutput")
        self.gridLayoutOutput = QGridLayout(self.groupBoxOutput)
        self.gridLayoutOutput.setObjectName(u"gridLayoutOutput")
        self.editNeutronSldReal = QLineEdit(self.groupBoxOutput)
        self.editNeutronSldReal.setObjectName(u"editNeutronSldReal")
        self.editNeutronSldReal.setEnabled(True)
        self.editNeutronSldReal.setReadOnly(True)

        self.gridLayoutOutput.addWidget(self.editNeutronSldReal, 0, 1, 1, 1)

        self.label_17 = QLabel(self.groupBoxOutput)
        self.label_17.setObjectName(u"label_17")

        self.gridLayoutOutput.addWidget(self.label_17, 0, 0, 1, 1)

        self.label_3 = QLabel(self.groupBoxOutput)
        self.label_3.setObjectName(u"label_3")

        self.gridLayoutOutput.addWidget(self.label_3, 5, 0, 1, 1)

        self.editNeutronIncXs = QLineEdit(self.groupBoxOutput)
        self.editNeutronIncXs.setObjectName(u"editNeutronIncXs")
        self.editNeutronIncXs.setEnabled(True)
        self.editNeutronIncXs.setReadOnly(True)

        self.gridLayoutOutput.addWidget(self.editNeutronIncXs, 3, 1, 1, 1)

        self.label_21 = QLabel(self.groupBoxOutput)
        self.label_21.setObjectName(u"label_21")

        self.gridLayoutOutput.addWidget(self.label_21, 3, 0, 1, 1)

        self.label_18 = QLabel(self.groupBoxOutput)
        self.label_18.setObjectName(u"label_18")

        self.gridLayoutOutput.addWidget(self.label_18, 0, 2, 1, 1)

        self.label_20 = QLabel(self.groupBoxOutput)
        self.label_20.setObjectName(u"label_20")

        self.gridLayoutOutput.addWidget(self.label_20, 1, 2, 1, 1)

        self.editNeutronSldImag = QLineEdit(self.groupBoxOutput)
        self.editNeutronSldImag.setObjectName(u"editNeutronSldImag")
        self.editNeutronSldImag.setEnabled(True)
        self.editNeutronSldImag.setReadOnly(True)

        self.gridLayoutOutput.addWidget(self.editNeutronSldImag, 0, 3, 1, 1)

        self.label_4 = QLabel(self.groupBoxOutput)
        self.label_4.setObjectName(u"label_4")

        self.gridLayoutOutput.addWidget(self.label_4, 5, 2, 1, 2)

        self.editNeutronLength = QLineEdit(self.groupBoxOutput)
        self.editNeutronLength.setObjectName(u"editNeutronLength")
        self.editNeutronLength.setEnabled(True)
        self.editNeutronLength.setReadOnly(True)

        self.gridLayoutOutput.addWidget(self.editNeutronLength, 5, 1, 1, 1)

        self.label_24 = QLabel(self.groupBoxOutput)
        self.label_24.setObjectName(u"label_24")

        self.gridLayoutOutput.addWidget(self.label_24, 4, 2, 1, 2)

        self.editNeutronAbsXs = QLineEdit(self.groupBoxOutput)
        self.editNeutronAbsXs.setObjectName(u"editNeutronAbsXs")
        self.editNeutronAbsXs.setEnabled(True)
        self.editNeutronAbsXs.setReadOnly(True)

        self.gridLayoutOutput.addWidget(self.editNeutronAbsXs, 4, 1, 1, 1)

        self.label_23 = QLabel(self.groupBoxOutput)
        self.label_23.setObjectName(u"label_23")

        self.gridLayoutOutput.addWidget(self.label_23, 4, 0, 1, 1)

        self.label_22 = QLabel(self.groupBoxOutput)
        self.label_22.setObjectName(u"label_22")

        self.gridLayoutOutput.addWidget(self.label_22, 3, 2, 1, 2)

        self.label_6 = QLabel(self.groupBoxOutput)
        self.label_6.setObjectName(u"label_6")

        self.gridLayoutOutput.addWidget(self.label_6, 1, 4, 1, 1)

        self.label_19 = QLabel(self.groupBoxOutput)
        self.label_19.setObjectName(u"label_19")

        self.gridLayoutOutput.addWidget(self.label_19, 1, 0, 1, 1)

        self.label_5 = QLabel(self.groupBoxOutput)
        self.label_5.setObjectName(u"label_5")

        self.gridLayoutOutput.addWidget(self.label_5, 0, 4, 1, 1)

        self.frame = QFrame(self.groupBoxOutput)
        self.frame.setObjectName(u"frame")
        self.frame.setMinimumSize(QSize(0, 5))
        self.frame.setFrameShape(QFrame.HLine)
        self.frame.setFrameShadow(QFrame.Raised)
        self.frame.setLineWidth(1)
        self.frame.setMidLineWidth(0)

        self.gridLayoutOutput.addWidget(self.frame, 2, 0, 1, 5)

        self.editXraySldReal = QLineEdit(self.groupBoxOutput)
        self.editXraySldReal.setObjectName(u"editXraySldReal")
        self.editXraySldReal.setEnabled(True)
        self.editXraySldReal.setReadOnly(True)

        self.gridLayoutOutput.addWidget(self.editXraySldReal, 1, 1, 1, 1)

        self.editXraySldImag = QLineEdit(self.groupBoxOutput)
        self.editXraySldImag.setObjectName(u"editXraySldImag")
        self.editXraySldImag.setEnabled(True)
        self.editXraySldImag.setReadOnly(True)

        self.gridLayoutOutput.addWidget(self.editXraySldImag, 1, 3, 1, 1)


        self.gridLayout_2.addWidget(self.groupBoxOutput, 1, 0, 1, 1)

        self.groupBoxInput = QGroupBox(SldPanel)
        self.groupBoxInput.setObjectName(u"groupBoxInput")
        self.gridLayoutInput = QGridLayout(self.groupBoxInput)
        self.gridLayoutInput.setObjectName(u"gridLayoutInput")
        self.label_8 = QLabel(self.groupBoxInput)
        self.label_8.setObjectName(u"label_8")

        self.gridLayoutInput.addWidget(self.label_8, 1, 0, 1, 1)

        self.label_16 = QLabel(self.groupBoxInput)
        self.label_16.setObjectName(u"label_16")

        self.gridLayoutInput.addWidget(self.label_16, 1, 2, 1, 1)

        self.label_10 = QLabel(self.groupBoxInput)
        self.label_10.setObjectName(u"label_10")

        self.gridLayoutInput.addWidget(self.label_10, 0, 2, 1, 1)

        self.editMolecularFormula = QLineEdit(self.groupBoxInput)
        self.editMolecularFormula.setObjectName(u"editMolecularFormula")

        self.gridLayoutInput.addWidget(self.editMolecularFormula, 0, 1, 1, 1)

        self.editMassDensity = QLineEdit(self.groupBoxInput)
        self.editMassDensity.setObjectName(u"editMassDensity")

        self.gridLayoutInput.addWidget(self.editMassDensity, 1, 1, 1, 1)

        self.label_12 = QLabel(self.groupBoxInput)
        self.label_12.setObjectName(u"label_12")

        self.gridLayoutInput.addWidget(self.label_12, 2, 2, 1, 1)

        self.label_9 = QLabel(self.groupBoxInput)
        self.label_9.setObjectName(u"label_9")

        self.gridLayoutInput.addWidget(self.label_9, 0, 0, 1, 1)

        self.label_11 = QLabel(self.groupBoxInput)
        self.label_11.setObjectName(u"label_11")

        self.gridLayoutInput.addWidget(self.label_11, 2, 0, 1, 1)

        self.editNeutronWavelength = QLineEdit(self.groupBoxInput)
        self.editNeutronWavelength.setObjectName(u"editNeutronWavelength")
        self.editNeutronWavelength.setStyleSheet(u"")
        self.editNeutronWavelength.setReadOnly(False)

        self.gridLayoutInput.addWidget(self.editNeutronWavelength, 2, 1, 1, 1)

        self.editXrayWavelength = QLineEdit(self.groupBoxInput)
        self.editXrayWavelength.setObjectName(u"editXrayWavelength")

        self.gridLayoutInput.addWidget(self.editXrayWavelength, 3, 1, 1, 1)

        self.label_13 = QLabel(self.groupBoxInput)
        self.label_13.setObjectName(u"label_13")

        self.gridLayoutInput.addWidget(self.label_13, 3, 0, 1, 1)

        self.label = QLabel(self.groupBoxInput)
        self.label.setObjectName(u"label")

        self.gridLayoutInput.addWidget(self.label, 3, 2, 1, 1)


        self.gridLayout_2.addWidget(self.groupBoxInput, 0, 0, 1, 1)

        self.widget = QWidget(SldPanel)
        self.widget.setObjectName(u"widget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy1)
        self.widget.setMinimumSize(QSize(466, 50))
        self.gridLayout = QGridLayout(self.widget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.calculateButton = QPushButton(self.widget)
        self.calculateButton.setObjectName(u"calculateButton")
        self.calculateButton.setEnabled(True)
        self.calculateButton.setMinimumSize(QSize(0, 28))
        self.calculateButton.setFocusPolicy(Qt.NoFocus)
        self.calculateButton.setAutoDefault(True)

        self.gridLayout.addWidget(self.calculateButton, 0, 0, 1, 1)

        self.horizontalSpacer = QSpacerItem(208, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 0, 1, 1, 1)

        self.closeButton = QPushButton(self.widget)
        self.closeButton.setObjectName(u"closeButton")
        self.closeButton.setMinimumSize(QSize(0, 28))
        self.closeButton.setAutoDefault(False)

        self.gridLayout.addWidget(self.closeButton, 0, 2, 1, 1)

        self.helpButton = QPushButton(self.widget)
        self.helpButton.setObjectName(u"helpButton")
        self.helpButton.setMinimumSize(QSize(0, 28))
        self.helpButton.setAutoDefault(False)

        self.gridLayout.addWidget(self.helpButton, 0, 3, 1, 1)


        self.gridLayout_2.addWidget(self.widget, 4, 0, 1, 1)

        QWidget.setTabOrder(self.editMolecularFormula, self.editMassDensity)
        QWidget.setTabOrder(self.editMassDensity, self.editNeutronWavelength)
        QWidget.setTabOrder(self.editNeutronWavelength, self.editXrayWavelength)
        QWidget.setTabOrder(self.editXrayWavelength, self.editNeutronSldReal)
        QWidget.setTabOrder(self.editNeutronSldReal, self.editNeutronSldImag)
        QWidget.setTabOrder(self.editNeutronSldImag, self.editXraySldReal)
        QWidget.setTabOrder(self.editXraySldReal, self.editXraySldImag)
        QWidget.setTabOrder(self.editXraySldImag, self.editNeutronIncXs)
        QWidget.setTabOrder(self.editNeutronIncXs, self.editNeutronAbsXs)
        QWidget.setTabOrder(self.editNeutronAbsXs, self.editNeutronLength)
        QWidget.setTabOrder(self.editNeutronLength, self.closeButton)
        QWidget.setTabOrder(self.closeButton, self.helpButton)
        QWidget.setTabOrder(self.helpButton, self.calculateButton)

        self.retranslateUi(SldPanel)

        QMetaObject.connectSlotsByName(SldPanel)
    # setupUi

    def retranslateUi(self, SldPanel):
        SldPanel.setWindowTitle(QCoreApplication.translate("SldPanel", u"SLD Calculator", None))
        self.groupBoxOutput.setTitle(QCoreApplication.translate("SldPanel", u"Output", None))
        self.label_17.setText(QCoreApplication.translate("SldPanel", u"Neutron SLD", None))
        self.label_3.setText(QCoreApplication.translate("SldPanel", u"Neutron 1/e length", None))
        self.label_21.setText(QCoreApplication.translate("SldPanel", u"Neutron Inc. Xs", None))
        self.label_18.setText(QCoreApplication.translate("SldPanel", u"-i", None))
        self.label_20.setText(QCoreApplication.translate("SldPanel", u"-i", None))
        self.label_4.setText(QCoreApplication.translate("SldPanel", u"cm", None))
        self.label_24.setText(QCoreApplication.translate("SldPanel", u"1/cm", None))
        self.label_23.setText(QCoreApplication.translate("SldPanel", u"Neutron Abs. Xs", None))
        self.label_22.setText(QCoreApplication.translate("SldPanel", u"1/cm", None))
        self.label_6.setText(QCoreApplication.translate("SldPanel", u"1/\u00c5\u00b2", None))
        self.label_19.setText(QCoreApplication.translate("SldPanel", u"X-Ray SLD", None))
        self.label_5.setText(QCoreApplication.translate("SldPanel", u"1/\u00c5\u00b2", None))
        self.groupBoxInput.setTitle(QCoreApplication.translate("SldPanel", u"Input", None))
        self.label_8.setText(QCoreApplication.translate("SldPanel", u"Mass Density", None))
        self.label_16.setText(QCoreApplication.translate("SldPanel", u"g/cm\u00b3", None))
        self.label_10.setText(QCoreApplication.translate("SldPanel", u"e.g. H2O", None))
        self.label_12.setText(QCoreApplication.translate("SldPanel", u"\u00c5", None))
        self.label_9.setText(QCoreApplication.translate("SldPanel", u"Molecular Formula", None))
        self.label_11.setText(QCoreApplication.translate("SldPanel", u"Neutron Wavelength", None))
        self.label_13.setText(QCoreApplication.translate("SldPanel", u"X-Ray Wavelength", None))
        self.label.setText(QCoreApplication.translate("SldPanel", u"\u00c5", None))
        self.calculateButton.setText(QCoreApplication.translate("SldPanel", u"Calculate", None))
        self.closeButton.setText(QCoreApplication.translate("SldPanel", u"Close", None))
        self.helpButton.setText(QCoreApplication.translate("SldPanel", u"Help", None))
    # retranslateUi

