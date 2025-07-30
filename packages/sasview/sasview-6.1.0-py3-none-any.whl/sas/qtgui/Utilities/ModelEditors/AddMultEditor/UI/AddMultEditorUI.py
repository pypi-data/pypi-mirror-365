# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'AddMultEditorUI.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QComboBox,
    QDialog, QDialogButtonBox, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QSizePolicy,
    QSpacerItem, QWidget)

class Ui_AddMultEditorUI(object):
    def setupUi(self, AddMultEditorUI):
        if not AddMultEditorUI.objectName():
            AddMultEditorUI.setObjectName(u"AddMultEditorUI")
        AddMultEditorUI.resize(527, 331)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AddMultEditorUI.sizePolicy().hasHeightForWidth())
        AddMultEditorUI.setSizePolicy(sizePolicy)
        AddMultEditorUI.setMinimumSize(QSize(527, 331))
        self.gridLayout_3 = QGridLayout(AddMultEditorUI)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.groupBox_5 = QGroupBox(AddMultEditorUI)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.gridLayout_4 = QGridLayout(self.groupBox_5)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.txtDescription = QLineEdit(self.groupBox_5)
        self.txtDescription.setObjectName(u"txtDescription")

        self.gridLayout_4.addWidget(self.txtDescription, 0, 0, 1, 1)


        self.gridLayout_3.addWidget(self.groupBox_5, 1, 0, 1, 1)

        self.groupBox_6 = QGroupBox(AddMultEditorUI)
        self.groupBox_6.setObjectName(u"groupBox_6")
        self.gridLayout_5 = QGridLayout(self.groupBox_6)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.txtName = QLineEdit(self.groupBox_6)
        self.txtName.setObjectName(u"txtName")

        self.gridLayout_5.addWidget(self.txtName, 0, 0, 1, 1)

        self.chkOverwrite = QCheckBox(self.groupBox_6)
        self.chkOverwrite.setObjectName(u"chkOverwrite")

        self.gridLayout_5.addWidget(self.chkOverwrite, 0, 1, 1, 1)


        self.gridLayout_3.addWidget(self.groupBox_6, 0, 0, 1, 1)

        self.groupBox = QGroupBox(AddMultEditorUI)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 0, 2, 1, 1)

        self.cbModel1 = QComboBox(self.groupBox)
        self.cbModel1.setObjectName(u"cbModel1")
        self.cbModel1.setEditable(True)

        self.gridLayout.addWidget(self.cbModel1, 1, 0, 1, 1)

        self.cbOperator = QComboBox(self.groupBox)
        self.cbOperator.addItem("")
        self.cbOperator.addItem("")
        self.cbOperator.addItem("")
        self.cbOperator.setObjectName(u"cbOperator")
        sizePolicy.setHeightForWidth(self.cbOperator.sizePolicy().hasHeightForWidth())
        self.cbOperator.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.cbOperator, 1, 1, 1, 1)

        self.cbModel2 = QComboBox(self.groupBox)
        self.cbModel2.setObjectName(u"cbModel2")
        self.cbModel2.setEditable(True)

        self.gridLayout.addWidget(self.cbModel2, 1, 2, 1, 1)


        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)


        self.gridLayout_3.addWidget(self.groupBox, 3, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.buttonBox = QDialogButtonBox(AddMultEditorUI)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Apply|QDialogButtonBox.Close|QDialogButtonBox.Help)

        self.horizontalLayout_3.addWidget(self.buttonBox)


        self.gridLayout_3.addLayout(self.horizontalLayout_3, 4, 0, 1, 1)

        self.lblEquation = QLabel(AddMultEditorUI)
        self.lblEquation.setObjectName(u"lblEquation")

        self.gridLayout_3.addWidget(self.lblEquation, 2, 0, 1, 1)

        QWidget.setTabOrder(self.txtName, self.chkOverwrite)
        QWidget.setTabOrder(self.chkOverwrite, self.txtDescription)
        QWidget.setTabOrder(self.txtDescription, self.cbModel1)
        QWidget.setTabOrder(self.cbModel1, self.cbOperator)
        QWidget.setTabOrder(self.cbOperator, self.cbModel2)

        self.retranslateUi(AddMultEditorUI)

        QMetaObject.connectSlotsByName(AddMultEditorUI)
    # setupUi

    def retranslateUi(self, AddMultEditorUI):
        AddMultEditorUI.setWindowTitle(QCoreApplication.translate("AddMultEditorUI", u"Easy Add/Multiply Editor", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("AddMultEditorUI", u"Description", None))
        self.txtDescription.setPlaceholderText(QCoreApplication.translate("AddMultEditorUI", u"Enter a description of the model (optional)", None))
        self.groupBox_6.setTitle(QCoreApplication.translate("AddMultEditorUI", u"Plugin model", None))
#if QT_CONFIG(tooltip)
        self.txtName.setToolTip(QCoreApplication.translate("AddMultEditorUI", u"Sum / Multiply model function name.", None))
#endif // QT_CONFIG(tooltip)
        self.txtName.setPlaceholderText(QCoreApplication.translate("AddMultEditorUI", u"Enter a plugin name", None))
#if QT_CONFIG(tooltip)
        self.chkOverwrite.setToolTip(QCoreApplication.translate("AddMultEditorUI", u"Check to overwrite the existing model with the same name.", None))
#endif // QT_CONFIG(tooltip)
        self.chkOverwrite.setText(QCoreApplication.translate("AddMultEditorUI", u"Overwrite existing model", None))
        self.groupBox.setTitle(QCoreApplication.translate("AddMultEditorUI", u"Model selection", None))
        self.label.setText(QCoreApplication.translate("AddMultEditorUI", u"model_1", None))
        self.label_2.setText(QCoreApplication.translate("AddMultEditorUI", u"model_2", None))
        self.cbOperator.setItemText(0, QCoreApplication.translate("AddMultEditorUI", u"+", None))
        self.cbOperator.setItemText(1, QCoreApplication.translate("AddMultEditorUI", u"*", None))
        self.cbOperator.setItemText(2, QCoreApplication.translate("AddMultEditorUI", u"@", None))

#if QT_CONFIG(tooltip)
        self.cbOperator.setToolTip(QCoreApplication.translate("AddMultEditorUI", u"Add: +\n"
"Multiply: *", None))
#endif // QT_CONFIG(tooltip)
        self.lblEquation.setText(QCoreApplication.translate("AddMultEditorUI", u"<html><head/><body><p><span style=\" font-weight:600;\">Plugin_model = scale_factor * (model_1 + model_2) + background</span></p><p>To add/multiply plugin models, or combine more than two models, please click Help below.<br/></p></body></html>", None))
    # retranslateUi

