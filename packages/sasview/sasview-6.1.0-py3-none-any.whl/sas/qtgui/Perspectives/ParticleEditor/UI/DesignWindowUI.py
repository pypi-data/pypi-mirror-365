# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'DesignWindowUI.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFrame, QGridLayout, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QSizePolicy, QSpacerItem,
    QSpinBox, QTabWidget, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget)

class Ui_DesignWindow(object):
    def setupUi(self, DesignWindow):
        if not DesignWindow.objectName():
            DesignWindow.setObjectName(u"DesignWindow")
        DesignWindow.resize(992, 477)
        self.verticalLayout_7 = QVBoxLayout(DesignWindow)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.tabWidget = QTabWidget(DesignWindow)
        self.tabWidget.setObjectName(u"tabWidget")
        self.definitionTab = QWidget()
        self.definitionTab.setObjectName(u"definitionTab")
        self.tabWidget.addTab(self.definitionTab, "")
        self.parametersTab = QWidget()
        self.parametersTab.setObjectName(u"parametersTab")
        self.horizontalLayout_3 = QHBoxLayout(self.parametersTab)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.parameterTabLayout = QVBoxLayout()
        self.parameterTabLayout.setObjectName(u"parameterTabLayout")

        self.horizontalLayout_3.addLayout(self.parameterTabLayout)

        self.horizontalLayout_3.setStretch(0, 3)
        self.tabWidget.addTab(self.parametersTab, "")
        self.calculationTab = QWidget()
        self.calculationTab.setObjectName(u"calculationTab")
        self.verticalLayout_6 = QVBoxLayout(self.calculationTab)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(-1, -1, -1, 0)
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(-1, -1, -1, 10)
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(-1, -1, -1, 10)
        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_6)

        self.topLayout = QGridLayout()
        self.topLayout.setObjectName(u"topLayout")
        self.topLayout.setContentsMargins(-1, 10, -1, 10)
        self.label_5 = QLabel(self.calculationTab)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.topLayout.addWidget(self.label_5, 1, 0, 1, 1)

        self.structureFactorCombo = QComboBox(self.calculationTab)
        self.structureFactorCombo.setObjectName(u"structureFactorCombo")

        self.topLayout.addWidget(self.structureFactorCombo, 1, 1, 1, 1)

        self.label_2 = QLabel(self.calculationTab)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.topLayout.addWidget(self.label_2, 0, 0, 1, 1)

        self.topLayout.setColumnStretch(0, 1)

        self.horizontalLayout_4.addLayout(self.topLayout)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_5)

        self.horizontalLayout_4.setStretch(0, 1)
        self.horizontalLayout_4.setStretch(1, 2)
        self.horizontalLayout_4.setStretch(2, 1)

        self.verticalLayout_3.addLayout(self.horizontalLayout_4)

        self.label_6 = QLabel(self.calculationTab)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setAlignment(Qt.AlignCenter)

        self.verticalLayout_3.addWidget(self.label_6)

        self.structureFactorParametersTable = QTableWidget(self.calculationTab)
        if (self.structureFactorParametersTable.columnCount() < 6):
            self.structureFactorParametersTable.setColumnCount(6)
        if (self.structureFactorParametersTable.rowCount() < 1):
            self.structureFactorParametersTable.setRowCount(1)
        self.structureFactorParametersTable.setObjectName(u"structureFactorParametersTable")
        self.structureFactorParametersTable.setRowCount(1)
        self.structureFactorParametersTable.setColumnCount(6)
        self.structureFactorParametersTable.verticalHeader().setVisible(False)

        self.verticalLayout_3.addWidget(self.structureFactorParametersTable)


        self.horizontalLayout_5.addLayout(self.verticalLayout_3)

        self.horizontalLayout_5.setStretch(0, 3)

        self.verticalLayout_6.addLayout(self.horizontalLayout_5)

        self.tabWidget.addTab(self.calculationTab, "")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout = QVBoxLayout(self.tab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame_2 = QFrame(self.tab)
        self.frame_2.setObjectName(u"frame_2")
        self.horizontalLayout_2 = QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_4)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, -1, -1, -1)
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.frame_3 = QFrame(self.frame_2)
        self.frame_3.setObjectName(u"frame_3")
        self.gridLayout_2 = QGridLayout(self.frame_3)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_11 = QLabel(self.frame_3)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_11, 8, 0, 1, 1)

        self.label_10 = QLabel(self.frame_3)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout_2.addWidget(self.label_10, 8, 3, 1, 1)

        self.qSamplesBox = QSpinBox(self.frame_3)
        self.qSamplesBox.setObjectName(u"qSamplesBox")
        self.qSamplesBox.setMinimum(10)
        self.qSamplesBox.setMaximum(10000)
        self.qSamplesBox.setSingleStep(10)
        self.qSamplesBox.setValue(200)

        self.gridLayout_2.addWidget(self.qSamplesBox, 9, 2, 1, 1)

        self.useLogQ = QCheckBox(self.frame_3)
        self.useLogQ.setObjectName(u"useLogQ")
        self.useLogQ.setChecked(True)

        self.gridLayout_2.addWidget(self.useLogQ, 10, 2, 1, 1)

        self.label_12 = QLabel(self.frame_3)
        self.label_12.setObjectName(u"label_12")

        self.gridLayout_2.addWidget(self.label_12, 11, 0, 1, 1)

        self.qMaxBox = QLineEdit(self.frame_3)
        self.qMaxBox.setObjectName(u"qMaxBox")

        self.gridLayout_2.addWidget(self.qMaxBox, 8, 2, 1, 1)

        self.label_7 = QLabel(self.frame_3)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_7, 9, 0, 1, 1)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.lineEdit = QLineEdit(self.frame_3)
        self.lineEdit.setObjectName(u"lineEdit")

        self.horizontalLayout_10.addWidget(self.lineEdit)

        self.lineEdit_2 = QLineEdit(self.frame_3)
        self.lineEdit_2.setObjectName(u"lineEdit_2")

        self.horizontalLayout_10.addWidget(self.lineEdit_2)

        self.lineEdit_3 = QLineEdit(self.frame_3)
        self.lineEdit_3.setObjectName(u"lineEdit_3")

        self.horizontalLayout_10.addWidget(self.lineEdit_3)


        self.gridLayout_2.addLayout(self.horizontalLayout_10, 11, 2, 1, 1)

        self.continuityCheck = QCheckBox(self.frame_3)
        self.continuityCheck.setObjectName(u"continuityCheck")
        self.continuityCheck.setChecked(True)

        self.gridLayout_2.addWidget(self.continuityCheck, 12, 2, 1, 1)

        self.timeEstimateLabel = QLabel(self.frame_3)
        self.timeEstimateLabel.setObjectName(u"timeEstimateLabel")
        self.timeEstimateLabel.setAlignment(Qt.AlignCenter)

        self.gridLayout_2.addWidget(self.timeEstimateLabel, 13, 2, 1, 1)

        self.methodCombo = QComboBox(self.frame_3)
        self.methodCombo.setObjectName(u"methodCombo")

        self.gridLayout_2.addWidget(self.methodCombo, 4, 2, 1, 1)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.sampleRadius = QDoubleSpinBox(self.frame_3)
        self.sampleRadius.setObjectName(u"sampleRadius")
        self.sampleRadius.setEnabled(False)
        self.sampleRadius.setMinimum(0.100000000000000)
        self.sampleRadius.setMaximum(100000.000000000000000)
        self.sampleRadius.setValue(100.000000000000000)

        self.horizontalLayout_6.addWidget(self.sampleRadius)

        self.radiusFromParticleTab = QCheckBox(self.frame_3)
        self.radiusFromParticleTab.setObjectName(u"radiusFromParticleTab")
        self.radiusFromParticleTab.setChecked(True)

        self.horizontalLayout_6.addWidget(self.radiusFromParticleTab)


        self.gridLayout_2.addLayout(self.horizontalLayout_6, 3, 2, 1, 1)

        self.label_14 = QLabel(self.frame_3)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_14, 3, 0, 1, 1)

        self.label_8 = QLabel(self.frame_3)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_8, 7, 0, 1, 1)

        self.label_4 = QLabel(self.frame_3)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_4, 5, 0, 1, 1)

        self.label_3 = QLabel(self.frame_3)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_3, 4, 0, 1, 1)

        self.label_16 = QLabel(self.frame_3)
        self.label_16.setObjectName(u"label_16")
        self.label_16.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_16, 6, 0, 1, 1)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.randomSeed = QLineEdit(self.frame_3)
        self.randomSeed.setObjectName(u"randomSeed")

        self.horizontalLayout_9.addWidget(self.randomSeed)

        self.fixRandomSeed = QCheckBox(self.frame_3)
        self.fixRandomSeed.setObjectName(u"fixRandomSeed")

        self.horizontalLayout_9.addWidget(self.fixRandomSeed)


        self.gridLayout_2.addLayout(self.horizontalLayout_9, 6, 2, 1, 1)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.nSamplePoints = QSpinBox(self.frame_3)
        self.nSamplePoints.setObjectName(u"nSamplePoints")
        self.nSamplePoints.setMaximum(100000000)
        self.nSamplePoints.setSingleStep(1000)
        self.nSamplePoints.setValue(100000)

        self.horizontalLayout_8.addWidget(self.nSamplePoints)

        self.sampleDetails = QLabel(self.frame_3)
        self.sampleDetails.setObjectName(u"sampleDetails")

        self.horizontalLayout_8.addWidget(self.sampleDetails)


        self.gridLayout_2.addLayout(self.horizontalLayout_8, 5, 2, 1, 1)

        self.label_9 = QLabel(self.frame_3)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_2.addWidget(self.label_9, 7, 3, 1, 1)

        self.qMinBox = QLineEdit(self.frame_3)
        self.qMinBox.setObjectName(u"qMinBox")

        self.gridLayout_2.addWidget(self.qMinBox, 7, 2, 1, 1)


        self.verticalLayout_2.addWidget(self.frame_3)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)


        self.horizontalLayout_2.addLayout(self.verticalLayout_2)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)


        self.verticalLayout.addWidget(self.frame_2)

        self.tabWidget.addTab(self.tab, "")
        self.fittingTab = QWidget()
        self.fittingTab.setObjectName(u"fittingTab")
        self.tabWidget.addTab(self.fittingTab, "")
        self.qSpaceTab = QWidget()
        self.qSpaceTab.setObjectName(u"qSpaceTab")
        self.tabWidget.addTab(self.qSpaceTab, "")

        self.verticalLayout_7.addWidget(self.tabWidget)


        self.retranslateUi(DesignWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(DesignWindow)
    # setupUi

    def retranslateUi(self, DesignWindow):
        DesignWindow.setWindowTitle(QCoreApplication.translate("DesignWindow", u"Form", None))
#if QT_CONFIG(tooltip)
        self.tabWidget.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.definitionTab), QCoreApplication.translate("DesignWindow", u"Definition", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.parametersTab), QCoreApplication.translate("DesignWindow", u"Parameters", None))
        self.label_5.setText(QCoreApplication.translate("DesignWindow", u"Structure Factor", None))
        self.label_2.setText(QCoreApplication.translate("DesignWindow", u"Orientational Distribution", None))
        self.label_6.setText(QCoreApplication.translate("DesignWindow", u"Structure Factor Parameters", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.calculationTab), QCoreApplication.translate("DesignWindow", u"Ensemble", None))
        self.label_11.setText(QCoreApplication.translate("DesignWindow", u"Q Max", None))
        self.label_10.setText(QCoreApplication.translate("DesignWindow", u"Ang<sup>-1</sup>", None))
        self.useLogQ.setText(QCoreApplication.translate("DesignWindow", u"Logaritmic", None))
        self.label_12.setText(QCoreApplication.translate("DesignWindow", u"Neutron Polarisation", None))
        self.qMaxBox.setText(QCoreApplication.translate("DesignWindow", u"0.5", None))
        self.label_7.setText(QCoreApplication.translate("DesignWindow", u"Q Samples", None))
        self.lineEdit.setText(QCoreApplication.translate("DesignWindow", u"1", None))
        self.lineEdit_2.setText(QCoreApplication.translate("DesignWindow", u"0", None))
        self.lineEdit_3.setText(QCoreApplication.translate("DesignWindow", u"0", None))
        self.continuityCheck.setText(QCoreApplication.translate("DesignWindow", u"Check sampling boundary for SLD continuity", None))
        self.timeEstimateLabel.setText("")
        self.radiusFromParticleTab.setText(QCoreApplication.translate("DesignWindow", u"Get From 'Definition' Tab", None))
        self.label_14.setText(QCoreApplication.translate("DesignWindow", u"Sample Radius", None))
        self.label_8.setText(QCoreApplication.translate("DesignWindow", u"Q Min", None))
        self.label_4.setText(QCoreApplication.translate("DesignWindow", u"Sample Points", None))
        self.label_3.setText(QCoreApplication.translate("DesignWindow", u"Sample Method", None))
        self.label_16.setText(QCoreApplication.translate("DesignWindow", u"Random Seed", None))
        self.randomSeed.setText(QCoreApplication.translate("DesignWindow", u"0", None))
        self.fixRandomSeed.setText(QCoreApplication.translate("DesignWindow", u"Fix Seed", None))
        self.sampleDetails.setText("")
        self.label_9.setText(QCoreApplication.translate("DesignWindow", u"Ang<sup>-1</sup>", None))
        self.qMinBox.setText(QCoreApplication.translate("DesignWindow", u"0.0005", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("DesignWindow", u"Calculation", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.fittingTab), QCoreApplication.translate("DesignWindow", u"Fitting", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.qSpaceTab), QCoreApplication.translate("DesignWindow", u"Q Space", None))
    # retranslateUi

