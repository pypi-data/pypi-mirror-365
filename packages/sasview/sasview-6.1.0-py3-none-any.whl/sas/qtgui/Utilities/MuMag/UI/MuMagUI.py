# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MuMagUI.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDoubleSpinBox, QFormLayout,
    QFrame, QGroupBox, QHBoxLayout, QLabel,
    QMainWindow, QMenuBar, QPushButton, QSizePolicy,
    QSpacerItem, QSpinBox, QStatusBar, QTabWidget,
    QVBoxLayout, QWidget)

class Ui_MuMagTool(object):
    def setupUi(self, MuMagTool):
        if not MuMagTool.objectName():
            MuMagTool.setObjectName(u"MuMagTool")
        MuMagTool.resize(819, 480)
        self.centralwidget = QWidget(MuMagTool)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_6 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout_2 = QHBoxLayout(self.widget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.frame = QFrame(self.widget)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox_3 = QGroupBox(self.frame)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.horizontalLayout_11 = QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.ImportDataButton = QPushButton(self.groupBox_3)
        self.ImportDataButton.setObjectName(u"ImportDataButton")

        self.horizontalLayout_11.addWidget(self.ImportDataButton)

        self.SimpleFitButton = QPushButton(self.groupBox_3)
        self.SimpleFitButton.setObjectName(u"SimpleFitButton")

        self.horizontalLayout_11.addWidget(self.SimpleFitButton)

        self.SaveResultsButton = QPushButton(self.groupBox_3)
        self.SaveResultsButton.setObjectName(u"SaveResultsButton")

        self.horizontalLayout_11.addWidget(self.SaveResultsButton)


        self.verticalLayout.addWidget(self.groupBox_3)

        self.groupBox_2 = QGroupBox(self.frame)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.widget_2 = QWidget(self.groupBox_2)
        self.widget_2.setObjectName(u"widget_2")
        self.formLayout = QFormLayout(self.widget_2)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setLabelAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.formLayout.setContentsMargins(-1, -1, 7, -1)
        self.label_9 = QLabel(self.widget_2)
        self.label_9.setObjectName(u"label_9")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_9)

        self.widget_6 = QWidget(self.widget_2)
        self.widget_6.setObjectName(u"widget_6")
        self.horizontalLayout = QHBoxLayout(self.widget_6)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, 0, -1, -1)
        self.ScatteringGeometrySelect = QComboBox(self.widget_6)
        self.ScatteringGeometrySelect.addItem("")
        self.ScatteringGeometrySelect.addItem("")
        self.ScatteringGeometrySelect.setObjectName(u"ScatteringGeometrySelect")

        self.horizontalLayout.addWidget(self.ScatteringGeometrySelect)

        self.horizontalSpacer_9 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_9)


        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.widget_6)

        self.label_5 = QLabel(self.widget_2)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_5)

        self.widget_4 = QWidget(self.widget_2)
        self.widget_4.setObjectName(u"widget_4")
        self.horizontalLayout_3 = QHBoxLayout(self.widget_4)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(-1, 0, -1, -1)
        self.qMaxSpinBox = QDoubleSpinBox(self.widget_4)
        self.qMaxSpinBox.setObjectName(u"qMaxSpinBox")
        self.qMaxSpinBox.setDecimals(5)
        self.qMaxSpinBox.setMinimum(0.000010000000000)
        self.qMaxSpinBox.setSingleStep(0.010000000000000)
        self.qMaxSpinBox.setValue(0.600000000000000)

        self.horizontalLayout_3.addWidget(self.qMaxSpinBox)

        self.label_2 = QLabel(self.widget_4)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_3.addWidget(self.label_2)


        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.widget_4)

        self.label_6 = QLabel(self.widget_2)
        self.label_6.setObjectName(u"label_6")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_6)

        self.widget_3 = QWidget(self.widget_2)
        self.widget_3.setObjectName(u"widget_3")
        self.horizontalLayout_4 = QHBoxLayout(self.widget_3)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(-1, 0, -1, -1)
        self.hMinSpinBox = QDoubleSpinBox(self.widget_3)
        self.hMinSpinBox.setObjectName(u"hMinSpinBox")
        self.hMinSpinBox.setDecimals(5)
        self.hMinSpinBox.setMaximum(10000.000000000000000)
        self.hMinSpinBox.setValue(75.000000000000000)

        self.horizontalLayout_4.addWidget(self.hMinSpinBox)

        self.label_3 = QLabel(self.widget_3)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_4.addWidget(self.label_3)


        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.widget_3)

        self.label = QLabel(self.widget_2)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label)

        self.widget_5 = QWidget(self.widget_2)
        self.widget_5.setObjectName(u"widget_5")
        self.horizontalLayout_5 = QHBoxLayout(self.widget_5)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(-1, 0, -1, 0)
        self.aMinSpinBox = QDoubleSpinBox(self.widget_5)
        self.aMinSpinBox.setObjectName(u"aMinSpinBox")
        self.aMinSpinBox.setMaximum(100000.000000000000000)
        self.aMinSpinBox.setValue(5.000000000000000)

        self.horizontalLayout_5.addWidget(self.aMinSpinBox)

        self.label_4 = QLabel(self.widget_5)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_5.addWidget(self.label_4)

        self.aMaxSpinBox = QDoubleSpinBox(self.widget_5)
        self.aMaxSpinBox.setObjectName(u"aMaxSpinBox")
        self.aMaxSpinBox.setMaximum(100000.000000000000000)
        self.aMaxSpinBox.setValue(20.000000000000000)

        self.horizontalLayout_5.addWidget(self.aMaxSpinBox)

        self.label_7 = QLabel(self.widget_5)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout_5.addWidget(self.label_7)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_8)


        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.widget_5)

        self.widget_10 = QWidget(self.widget_2)
        self.widget_10.setObjectName(u"widget_10")
        self.horizontalLayout_10 = QHBoxLayout(self.widget_10)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalLayout_10.setContentsMargins(7, 0, 0, 0)
        self.aSamplesSpinBox = QSpinBox(self.widget_10)
        self.aSamplesSpinBox.setObjectName(u"aSamplesSpinBox")
        self.aSamplesSpinBox.setMaximum(10000)
        self.aSamplesSpinBox.setValue(200)

        self.horizontalLayout_10.addWidget(self.aSamplesSpinBox)

        self.label_8 = QLabel(self.widget_10)
        self.label_8.setObjectName(u"label_8")

        self.horizontalLayout_10.addWidget(self.label_8)

        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_10.addItem(self.horizontalSpacer_7)


        self.formLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.widget_10)


        self.verticalLayout_3.addWidget(self.widget_2)


        self.verticalLayout.addWidget(self.groupBox_2)

        self.groupBox = QGroupBox(self.frame)
        self.groupBox.setObjectName(u"groupBox")
        self.formLayout_3 = QFormLayout(self.groupBox)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.formLayout_3.setLabelAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_10 = QLabel(self.groupBox)
        self.label_10.setObjectName(u"label_10")

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_10)

        self.label_11 = QLabel(self.groupBox)
        self.label_11.setObjectName(u"label_11")

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_11)

        self.exchange_a_display = QLabel(self.groupBox)
        self.exchange_a_display.setObjectName(u"exchange_a_display")

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.FieldRole, self.exchange_a_display)

        self.exchange_a_std_display = QLabel(self.groupBox)
        self.exchange_a_std_display.setObjectName(u"exchange_a_std_display")

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.FieldRole, self.exchange_a_std_display)


        self.verticalLayout.addWidget(self.groupBox)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.widget_7 = QWidget(self.frame)
        self.widget_7.setObjectName(u"widget_7")
        self.horizontalLayout_7 = QHBoxLayout(self.widget_7)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer)

        self.helpButton = QPushButton(self.widget_7)
        self.helpButton.setObjectName(u"helpButton")

        self.horizontalLayout_7.addWidget(self.helpButton)


        self.verticalLayout.addWidget(self.widget_7)


        self.horizontalLayout_2.addWidget(self.frame)


        self.horizontalLayout_6.addWidget(self.widget)

        self.plot_tabs = QTabWidget(self.centralwidget)
        self.plot_tabs.setObjectName(u"plot_tabs")
        self.data_tab = QWidget()
        self.data_tab.setObjectName(u"data_tab")
        self.plot_tabs.addTab(self.data_tab, "")
        self.fit_results_tab = QWidget()
        self.fit_results_tab.setObjectName(u"fit_results_tab")
        self.plot_tabs.addTab(self.fit_results_tab, "")
        self.comparison_tab = QWidget()
        self.comparison_tab.setObjectName(u"comparison_tab")
        self.plot_tabs.addTab(self.comparison_tab, "")

        self.horizontalLayout_6.addWidget(self.plot_tabs)

        self.horizontalLayout_6.setStretch(0, 1)
        self.horizontalLayout_6.setStretch(1, 2)
        MuMagTool.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MuMagTool)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 819, 20))
        MuMagTool.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MuMagTool)
        self.statusbar.setObjectName(u"statusbar")
        MuMagTool.setStatusBar(self.statusbar)

        self.retranslateUi(MuMagTool)

        self.plot_tabs.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MuMagTool)
    # setupUi

    def retranslateUi(self, MuMagTool):
        MuMagTool.setWindowTitle(QCoreApplication.translate("MuMagTool", u"MuMagTool (Experimental)", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MuMagTool", u"GroupBox", None))
        self.ImportDataButton.setText(QCoreApplication.translate("MuMagTool", u"Import Data", None))
        self.SimpleFitButton.setText(QCoreApplication.translate("MuMagTool", u"Fit", None))
        self.SaveResultsButton.setText(QCoreApplication.translate("MuMagTool", u"Save Result", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MuMagTool", u"Parameters", None))
        self.label_9.setText(QCoreApplication.translate("MuMagTool", u"Analysis Method:", None))
        self.ScatteringGeometrySelect.setItemText(0, QCoreApplication.translate("MuMagTool", u"Perpendicular", None))
        self.ScatteringGeometrySelect.setItemText(1, QCoreApplication.translate("MuMagTool", u"Parallel", None))

        self.ScatteringGeometrySelect.setCurrentText(QCoreApplication.translate("MuMagTool", u"Perpendicular", None))
        self.label_5.setText(QCoreApplication.translate("MuMagTool", u"Maximum q:", None))
        self.label_2.setText(QCoreApplication.translate("MuMagTool", u"nm<sup>-1</sup>", None))
        self.label_6.setText(QCoreApplication.translate("MuMagTool", u"Applied Field (\u03bc<sub>0</sub> H<sub>min</sub>):", None))
        self.label_3.setText(QCoreApplication.translate("MuMagTool", u"mT", None))
        self.label.setText(QCoreApplication.translate("MuMagTool", u"Scan Range for A:", None))
        self.label_4.setText(QCoreApplication.translate("MuMagTool", u"to", None))
        self.label_7.setText(QCoreApplication.translate("MuMagTool", u"pJ/m", None))
        self.label_8.setText(QCoreApplication.translate("MuMagTool", u"steps", None))
        self.groupBox.setTitle(QCoreApplication.translate("MuMagTool", u"Results", None))
        self.label_10.setText(QCoreApplication.translate("MuMagTool", u"A value:", None))
        self.label_11.setText(QCoreApplication.translate("MuMagTool", u"A uncertainty:", None))
        self.exchange_a_display.setText("")
        self.exchange_a_std_display.setText("")
        self.helpButton.setText(QCoreApplication.translate("MuMagTool", u"Help", None))
        self.plot_tabs.setTabText(self.plot_tabs.indexOf(self.data_tab), QCoreApplication.translate("MuMagTool", u"Data", None))
        self.plot_tabs.setTabText(self.plot_tabs.indexOf(self.fit_results_tab), QCoreApplication.translate("MuMagTool", u"Fit Results", None))
        self.plot_tabs.setTabText(self.plot_tabs.indexOf(self.comparison_tab), QCoreApplication.translate("MuMagTool", u"Comparison", None))
    # retranslateUi

