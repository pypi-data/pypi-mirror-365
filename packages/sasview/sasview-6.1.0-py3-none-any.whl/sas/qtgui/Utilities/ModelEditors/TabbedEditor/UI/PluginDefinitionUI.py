# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PluginDefinitionUI.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QFrame,
    QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QSizePolicy, QTableWidget,
    QTableWidgetItem, QTextBrowser, QWidget)

class Ui_PluginDefinition(object):
    def setupUi(self, PluginDefinition):
        if not PluginDefinition.objectName():
            PluginDefinition.setObjectName(u"PluginDefinition")
        PluginDefinition.resize(723, 784)
        self.gridLayout_7 = QGridLayout(PluginDefinition)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.groupBox = QGroupBox(PluginDefinition)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_3 = QGridLayout(self.groupBox)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.groupBox_3 = QGroupBox(self.groupBox)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.gridLayout = QGridLayout(self.groupBox_3)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tblParams = QTableWidget(self.groupBox_3)
        if (self.tblParams.columnCount() < 2):
            self.tblParams.setColumnCount(2)
        __qtablewidgetitem = QTableWidgetItem()
        self.tblParams.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tblParams.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        if (self.tblParams.rowCount() < 1):
            self.tblParams.setRowCount(1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tblParams.setVerticalHeaderItem(0, __qtablewidgetitem2)
        self.tblParams.setObjectName(u"tblParams")
        self.tblParams.setFrameShadow(QFrame.Sunken)
        self.tblParams.setDragEnabled(False)
        self.tblParams.setDragDropOverwriteMode(False)
        self.tblParams.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.tblParams.setDefaultDropAction(Qt.IgnoreAction)
        self.tblParams.setTextElideMode(Qt.ElideRight)
        self.tblParams.setWordWrap(True)
        self.tblParams.horizontalHeader().setCascadingSectionResizes(False)
        self.tblParams.horizontalHeader().setDefaultSectionSize(100)
        self.tblParams.horizontalHeader().setProperty(u"showSortIndicator", False)
        self.tblParams.horizontalHeader().setStretchLastSection(True)

        self.gridLayout.addWidget(self.tblParams, 0, 0, 1, 1)


        self.gridLayout_3.addWidget(self.groupBox_3, 0, 0, 1, 1)

        self.groupBox_4 = QGroupBox(self.groupBox)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.gridLayout_2 = QGridLayout(self.groupBox_4)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.tblParamsPD = QTableWidget(self.groupBox_4)
        if (self.tblParamsPD.columnCount() < 2):
            self.tblParamsPD.setColumnCount(2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tblParamsPD.setHorizontalHeaderItem(0, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tblParamsPD.setHorizontalHeaderItem(1, __qtablewidgetitem4)
        if (self.tblParamsPD.rowCount() < 1):
            self.tblParamsPD.setRowCount(1)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tblParamsPD.setVerticalHeaderItem(0, __qtablewidgetitem5)
        self.tblParamsPD.setObjectName(u"tblParamsPD")
        self.tblParamsPD.horizontalHeader().setStretchLastSection(True)

        self.gridLayout_2.addWidget(self.tblParamsPD, 0, 0, 1, 1)


        self.gridLayout_3.addWidget(self.groupBox_4, 0, 1, 1, 1)


        self.gridLayout_7.addWidget(self.groupBox, 3, 0, 1, 1)

        self.groupBox_6 = QGroupBox(PluginDefinition)
        self.groupBox_6.setObjectName(u"groupBox_6")
        self.gridLayout_5 = QGridLayout(self.groupBox_6)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.txtName = QLineEdit(self.groupBox_6)
        self.txtName.setObjectName(u"txtName")

        self.gridLayout_5.addWidget(self.txtName, 0, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.chkGenPython = QCheckBox(self.groupBox_6)
        self.chkGenPython.setObjectName(u"chkGenPython")
        self.chkGenPython.setAutoFillBackground(False)
        self.chkGenPython.setChecked(True)

        self.horizontalLayout.addWidget(self.chkGenPython)

        self.chkGenC = QCheckBox(self.groupBox_6)
        self.chkGenC.setObjectName(u"chkGenC")

        self.horizontalLayout.addWidget(self.chkGenC)


        self.gridLayout_5.addLayout(self.horizontalLayout, 4, 0, 1, 1)

        self.chkOverwrite = QCheckBox(self.groupBox_6)
        self.chkOverwrite.setObjectName(u"chkOverwrite")

        self.gridLayout_5.addWidget(self.chkOverwrite, 0, 1, 1, 1)

        self.infoLabel = QLabel(self.groupBox_6)
        self.infoLabel.setObjectName(u"infoLabel")
        self.infoLabel.setStyleSheet(u"font-size: 8pt")

        self.gridLayout_5.addWidget(self.infoLabel, 1, 0, 1, 1)


        self.gridLayout_7.addWidget(self.groupBox_6, 0, 0, 1, 1)

        self.groupBox_5 = QGroupBox(PluginDefinition)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.gridLayout_4 = QGridLayout(self.groupBox_5)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.txtDescription = QLineEdit(self.groupBox_5)
        self.txtDescription.setObjectName(u"txtDescription")

        self.gridLayout_4.addWidget(self.txtDescription, 0, 0, 1, 1)


        self.gridLayout_7.addWidget(self.groupBox_5, 2, 0, 1, 1)

        self.formFunctionBox = QGroupBox(PluginDefinition)
        self.formFunctionBox.setObjectName(u"formFunctionBox")
        self.gridLayout_9 = QGridLayout(self.formFunctionBox)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.txtFormVolumeFunction = QTextBrowser(self.formFunctionBox)
        self.txtFormVolumeFunction.setObjectName(u"txtFormVolumeFunction")
        self.txtFormVolumeFunction.viewport().setProperty(u"cursor", QCursor(Qt.CursorShape.IBeamCursor))
        self.txtFormVolumeFunction.setReadOnly(False)

        self.gridLayout_9.addWidget(self.txtFormVolumeFunction, 0, 0, 1, 1)


        self.gridLayout_7.addWidget(self.formFunctionBox, 5, 0, 1, 1)

        self.groupBox_2 = QGroupBox(PluginDefinition)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_6 = QGridLayout(self.groupBox_2)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.txtFunction = QTextBrowser(self.groupBox_2)
        self.txtFunction.setObjectName(u"txtFunction")
        self.txtFunction.viewport().setProperty(u"cursor", QCursor(Qt.CursorShape.IBeamCursor))
        self.txtFunction.setReadOnly(False)

        self.gridLayout_6.addWidget(self.txtFunction, 0, 0, 1, 1)


        self.gridLayout_7.addWidget(self.groupBox_2, 4, 0, 1, 1)

        self.boolGroupBox = QGroupBox(PluginDefinition)
        self.boolGroupBox.setObjectName(u"boolGroupBox")
        self.gridLayout_8 = QGridLayout(self.boolGroupBox)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.chkOpenCL = QCheckBox(self.boolGroupBox)
        self.chkOpenCL.setObjectName(u"chkOpenCL")

        self.gridLayout_8.addWidget(self.chkOpenCL, 1, 0, 1, 1)

        self.chkSingle = QCheckBox(self.boolGroupBox)
        self.chkSingle.setObjectName(u"chkSingle")
        self.chkSingle.setChecked(True)

        self.gridLayout_8.addWidget(self.chkSingle, 0, 0, 1, 1)

        self.chkFQ = QCheckBox(self.boolGroupBox)
        self.chkFQ.setObjectName(u"chkFQ")

        self.gridLayout_8.addWidget(self.chkFQ, 1, 1, 1, 1)

        self.chkStructure = QCheckBox(self.boolGroupBox)
        self.chkStructure.setObjectName(u"chkStructure")

        self.gridLayout_8.addWidget(self.chkStructure, 0, 1, 1, 1)


        self.gridLayout_7.addWidget(self.boolGroupBox, 1, 0, 1, 1)

        QWidget.setTabOrder(self.txtName, self.chkOverwrite)
        QWidget.setTabOrder(self.chkOverwrite, self.txtDescription)
        QWidget.setTabOrder(self.txtDescription, self.tblParamsPD)
        QWidget.setTabOrder(self.tblParamsPD, self.txtFunction)

        self.retranslateUi(PluginDefinition)

        QMetaObject.connectSlotsByName(PluginDefinition)
    # setupUi

    def retranslateUi(self, PluginDefinition):
        PluginDefinition.setWindowTitle(QCoreApplication.translate("PluginDefinition", u"Plugin Definition", None))
        self.groupBox.setTitle(QCoreApplication.translate("PluginDefinition", u"Fit parameters", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("PluginDefinition", u"Non-polydisperse", None))
        ___qtablewidgetitem = self.tblParams.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("PluginDefinition", u"Parameters", None));
        ___qtablewidgetitem1 = self.tblParams.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("PluginDefinition", u"Initial value", None));
        self.groupBox_4.setTitle(QCoreApplication.translate("PluginDefinition", u"Polydisperse", None))
        ___qtablewidgetitem2 = self.tblParamsPD.horizontalHeaderItem(0)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("PluginDefinition", u"Parameters", None));
        ___qtablewidgetitem3 = self.tblParamsPD.horizontalHeaderItem(1)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("PluginDefinition", u"Initial value", None));
        self.groupBox_6.setTitle(QCoreApplication.translate("PluginDefinition", u"Plugin name", None))
        self.txtName.setPlaceholderText(QCoreApplication.translate("PluginDefinition", u"Enter a plugin name", None))
        self.chkGenPython.setText(QCoreApplication.translate("PluginDefinition", u"Generate Python model", None))
        self.chkGenC.setText(QCoreApplication.translate("PluginDefinition", u"Generate C model template", None))
        self.chkOverwrite.setText(QCoreApplication.translate("PluginDefinition", u"Overwrite existing plugin model of this name", None))
        self.infoLabel.setText("")
        self.groupBox_5.setTitle(QCoreApplication.translate("PluginDefinition", u"Description", None))
        self.txtDescription.setPlaceholderText(QCoreApplication.translate("PluginDefinition", u"Enter a description of the model", None))
        self.formFunctionBox.setTitle(QCoreApplication.translate("PluginDefinition", u"Enter function for calculating volume of the particle:", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("PluginDefinition", u"Enter function for calculating scattering intensity I(Q):", None))
        self.txtFunction.setHtml(QCoreApplication.translate("PluginDefinition", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'MS Shell Dlg 2'; font-size:7.8pt;\"><br /></p></body></html>", None))
        self.boolGroupBox.setTitle(QCoreApplication.translate("PluginDefinition", u"Model Options", None))
        self.chkOpenCL.setText(QCoreApplication.translate("PluginDefinition", u"Can use OpenCL", None))
        self.chkSingle.setText(QCoreApplication.translate("PluginDefinition", u"Can use single precision floating point values", None))
        self.chkFQ.setText(QCoreApplication.translate("PluginDefinition", u"Has F(Q) calculations", None))
        self.chkStructure.setText(QCoreApplication.translate("PluginDefinition", u"Can be used as structure factor", None))
    # retranslateUi

