# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ReparameterizationEditorUI.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QTextBrowser, QWidget)

from sas.qtgui.Utilities.CustomGUI.ParameterTree import QParameterTreeWidget

class Ui_ReparameterizationEditor(object):
    def setupUi(self, ReparameterizationEditor):
        if not ReparameterizationEditor.objectName():
            ReparameterizationEditor.setObjectName(u"ReparameterizationEditor")
        ReparameterizationEditor.setWindowModality(Qt.NonModal)
        ReparameterizationEditor.resize(723, 580)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ReparameterizationEditor.sizePolicy().hasHeightForWidth())
        ReparameterizationEditor.setSizePolicy(sizePolicy)
        self.gridLayout_4 = QGridLayout(ReparameterizationEditor)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.groupBox_3 = QGroupBox(ReparameterizationEditor)
        self.groupBox_3.setObjectName(u"groupBox_3")
        font = QFont()
        font.setStrikeOut(False)
        self.groupBox_3.setFont(font)
        self.gridLayout_3 = QGridLayout(self.groupBox_3)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.txtFunction = QTextBrowser(self.groupBox_3)
        self.txtFunction.setObjectName(u"txtFunction")
        self.txtFunction.setReadOnly(False)

        self.gridLayout_3.addWidget(self.txtFunction, 1, 0, 1, 1)


        self.gridLayout_4.addWidget(self.groupBox_3, 2, 0, 1, 2)

        self.groupBox_2 = QGroupBox(ReparameterizationEditor)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout = QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.cmdEditSelected = QPushButton(self.groupBox_2)
        self.cmdEditSelected.setObjectName(u"cmdEditSelected")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.cmdEditSelected.sizePolicy().hasHeightForWidth())
        self.cmdEditSelected.setSizePolicy(sizePolicy1)
        self.cmdEditSelected.setMinimumSize(QSize(95, 0))
        self.cmdEditSelected.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_2.addWidget(self.cmdEditSelected)

        self.cmdDeleteParam = QPushButton(self.groupBox_2)
        self.cmdDeleteParam.setObjectName(u"cmdDeleteParam")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.cmdDeleteParam.sizePolicy().hasHeightForWidth())
        self.cmdDeleteParam.setSizePolicy(sizePolicy2)
        self.cmdDeleteParam.setMaximumSize(QSize(25, 25))
        font1 = QFont()
        font1.setPointSize(20)
        font1.setBold(True)
        font1.setStrikeOut(False)
        font1.setKerning(True)
        self.cmdDeleteParam.setFont(font1)
        self.cmdDeleteParam.setStyleSheet(u"")

        self.horizontalLayout_2.addWidget(self.cmdDeleteParam)

        self.cmdAddParam = QPushButton(self.groupBox_2)
        self.cmdAddParam.setObjectName(u"cmdAddParam")
        sizePolicy2.setHeightForWidth(self.cmdAddParam.sizePolicy().hasHeightForWidth())
        self.cmdAddParam.setSizePolicy(sizePolicy2)
        self.cmdAddParam.setMaximumSize(QSize(25, 25))
        font2 = QFont()
        font2.setPointSize(20)
        font2.setBold(True)
        self.cmdAddParam.setFont(font2)

        self.horizontalLayout_2.addWidget(self.cmdAddParam)


        self.gridLayout.addLayout(self.horizontalLayout_2, 4, 0, 1, 1)

        self.newParamTree = QParameterTreeWidget(self.groupBox_2)
        self.newParamTree.setObjectName(u"newParamTree")
        self.newParamTree.setEnabled(True)
        self.newParamTree.setProperty(u"alternatingRowColors", True)
        self.newParamTree.setProperty(u"headerHidden", True)
        self.newParamTree.setProperty(u"columnCount", 2)

        self.gridLayout.addWidget(self.newParamTree, 3, 0, 1, 1)


        self.gridLayout_4.addWidget(self.groupBox_2, 1, 1, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.cmdHelp = QPushButton(ReparameterizationEditor)
        self.cmdHelp.setObjectName(u"cmdHelp")
        sizePolicy1.setHeightForWidth(self.cmdHelp.sizePolicy().hasHeightForWidth())
        self.cmdHelp.setSizePolicy(sizePolicy1)
        self.cmdHelp.setMinimumSize(QSize(50, 0))
        self.cmdHelp.setAutoDefault(False)
        self.cmdHelp.setFlat(False)

        self.horizontalLayout.addWidget(self.cmdHelp)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.cmdCancel = QPushButton(ReparameterizationEditor)
        self.cmdCancel.setObjectName(u"cmdCancel")

        self.horizontalLayout.addWidget(self.cmdCancel)

        self.cmdApply = QPushButton(ReparameterizationEditor)
        self.cmdApply.setObjectName(u"cmdApply")

        self.horizontalLayout.addWidget(self.cmdApply)


        self.gridLayout_4.addLayout(self.horizontalLayout, 3, 0, 1, 2)

        self.groupBox_4 = QGroupBox(ReparameterizationEditor)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.gridLayout_5 = QGridLayout(self.groupBox_4)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.txtNewModelName = QLineEdit(self.groupBox_4)
        self.txtNewModelName.setObjectName(u"txtNewModelName")

        self.gridLayout_5.addWidget(self.txtNewModelName, 0, 1, 1, 1)

        self.label = QLabel(self.groupBox_4)
        self.label.setObjectName(u"label")

        self.gridLayout_5.addWidget(self.label, 0, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.chkOverwrite = QCheckBox(self.groupBox_4)
        self.chkOverwrite.setObjectName(u"chkOverwrite")

        self.horizontalLayout_3.addWidget(self.chkOverwrite)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.lblSelectModelInfo = QLabel(self.groupBox_4)
        self.lblSelectModelInfo.setObjectName(u"lblSelectModelInfo")

        self.horizontalLayout_3.addWidget(self.lblSelectModelInfo)

        self.selectModelButton = QPushButton(self.groupBox_4)
        self.selectModelButton.setObjectName(u"selectModelButton")
        sizePolicy1.setHeightForWidth(self.selectModelButton.sizePolicy().hasHeightForWidth())
        self.selectModelButton.setSizePolicy(sizePolicy1)
        self.selectModelButton.setMinimumSize(QSize(100, 0))
        self.selectModelButton.setAutoDefault(False)
        self.selectModelButton.setFlat(False)

        self.horizontalLayout_3.addWidget(self.selectModelButton)


        self.gridLayout_5.addLayout(self.horizontalLayout_3, 1, 0, 1, 2)


        self.gridLayout_4.addWidget(self.groupBox_4, 0, 0, 1, 2)

        self.groupBox = QGroupBox(ReparameterizationEditor)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.oldParamTree = QParameterTreeWidget(self.groupBox)
        self.oldParamTree.setObjectName(u"oldParamTree")
        self.oldParamTree.setEnabled(True)
        self.oldParamTree.setAutoFillBackground(False)
        self.oldParamTree.setProperty(u"alternatingRowColors", True)
        self.oldParamTree.setProperty(u"headerHidden", True)
        self.oldParamTree.setProperty(u"columnCount", 2)

        self.gridLayout_2.addWidget(self.oldParamTree, 1, 0, 1, 1)

        self.cmdModelHelp = QPushButton(self.groupBox)
        self.cmdModelHelp.setObjectName(u"cmdModelHelp")

        self.gridLayout_2.addWidget(self.cmdModelHelp, 2, 0, 1, 1)


        self.gridLayout_4.addWidget(self.groupBox, 1, 0, 1, 1)


        self.retranslateUi(ReparameterizationEditor)

        self.cmdHelp.setDefault(False)
        self.selectModelButton.setDefault(False)


        QMetaObject.connectSlotsByName(ReparameterizationEditor)
    # setupUi

    def retranslateUi(self, ReparameterizationEditor):
        ReparameterizationEditor.setWindowTitle(QCoreApplication.translate("ReparameterizationEditor", u"Reparameterization Editor", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("ReparameterizationEditor", u"Parameter Redefinition", None))
        self.txtFunction.setHtml(QCoreApplication.translate("ReparameterizationEditor", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'Consolas'; font-size:11pt;\"><br /></p></body></html>", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("ReparameterizationEditor", u"New Parameters", None))
        self.cmdEditSelected.setText(QCoreApplication.translate("ReparameterizationEditor", u"Edit Selected", None))
        self.cmdDeleteParam.setText(QCoreApplication.translate("ReparameterizationEditor", u"-", None))
        self.cmdAddParam.setText(QCoreApplication.translate("ReparameterizationEditor", u"+", None))
        self.cmdHelp.setText(QCoreApplication.translate("ReparameterizationEditor", u"Help", None))
        self.cmdCancel.setText(QCoreApplication.translate("ReparameterizationEditor", u"Cancel", None))
        self.cmdApply.setText(QCoreApplication.translate("ReparameterizationEditor", u"Apply", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("ReparameterizationEditor", u"Model Definition", None))
        self.txtNewModelName.setPlaceholderText(QCoreApplication.translate("ReparameterizationEditor", u"Enter plugin name", None))
        self.label.setText(QCoreApplication.translate("ReparameterizationEditor", u"Model Name", None))
        self.chkOverwrite.setText(QCoreApplication.translate("ReparameterizationEditor", u"Overwrite existing plugin model", None))
        self.lblSelectModelInfo.setText(QCoreApplication.translate("ReparameterizationEditor", u"Select model to be reparameterized", None))
        self.selectModelButton.setText(QCoreApplication.translate("ReparameterizationEditor", u"Select Model", None))
        self.groupBox.setTitle(QCoreApplication.translate("ReparameterizationEditor", u"Old Parameters", None))
        self.cmdModelHelp.setText(QCoreApplication.translate("ReparameterizationEditor", u"Model Help", None))
    # retranslateUi

