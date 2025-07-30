# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'DMaxExplorer.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QGridLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_DmaxExplorer(object):
    def setupUi(self, DmaxExplorer):
        if not DmaxExplorer.objectName():
            DmaxExplorer.setObjectName(u"DmaxExplorer")
        DmaxExplorer.resize(586, 538)
        self.gridLayout_3 = QGridLayout(DmaxExplorer)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label = QLabel(DmaxExplorer)
        self.label.setObjectName(u"label")

        self.horizontalLayout_3.addWidget(self.label)

        self.dependentVariable = QComboBox(DmaxExplorer)
        self.dependentVariable.addItem("")
        self.dependentVariable.addItem("")
        self.dependentVariable.addItem("")
        self.dependentVariable.addItem("")
        self.dependentVariable.addItem("")
        self.dependentVariable.addItem("")
        self.dependentVariable.addItem("")
        self.dependentVariable.setObjectName(u"dependentVariable")

        self.horizontalLayout_3.addWidget(self.dependentVariable)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)


        self.gridLayout.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_2 = QLabel(DmaxExplorer)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_2.addWidget(self.label_2)

        self.Npts = QLineEdit(DmaxExplorer)
        self.Npts.setObjectName(u"Npts")

        self.horizontalLayout_2.addWidget(self.Npts)

        self.label_3 = QLabel(DmaxExplorer)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_2.addWidget(self.label_3)

        self.minDist = QLineEdit(DmaxExplorer)
        self.minDist.setObjectName(u"minDist")

        self.horizontalLayout_2.addWidget(self.minDist)

        self.label_4 = QLabel(DmaxExplorer)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_2.addWidget(self.label_4)

        self.maxDist = QLineEdit(DmaxExplorer)
        self.maxDist.setObjectName(u"maxDist")

        self.horizontalLayout_2.addWidget(self.maxDist)


        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.closeButton = QPushButton(DmaxExplorer)
        self.closeButton.setObjectName(u"closeButton")
        self.closeButton.setAutoDefault(False)

        self.horizontalLayout.addWidget(self.closeButton)


        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)


        self.gridLayout_3.addLayout(self.verticalLayout, 0, 0, 1, 1)


        self.retranslateUi(DmaxExplorer)

        QMetaObject.connectSlotsByName(DmaxExplorer)
    # setupUi

    def retranslateUi(self, DmaxExplorer):
        DmaxExplorer.setWindowTitle(QCoreApplication.translate("DmaxExplorer", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("DmaxExplorer", u"Dependent Variable:", None))
        self.dependentVariable.setItemText(0, QCoreApplication.translate("DmaxExplorer", u"1-\u03c3 positive fraction", None))
        self.dependentVariable.setItemText(1, QCoreApplication.translate("DmaxExplorer", u"\u03c7\u00b2/dof", None))
        self.dependentVariable.setItemText(2, QCoreApplication.translate("DmaxExplorer", u"I(Q=0)", None))
        self.dependentVariable.setItemText(3, QCoreApplication.translate("DmaxExplorer", u"Rg", None))
        self.dependentVariable.setItemText(4, QCoreApplication.translate("DmaxExplorer", u"Oscillation parameter", None))
        self.dependentVariable.setItemText(5, QCoreApplication.translate("DmaxExplorer", u"Background", None))
        self.dependentVariable.setItemText(6, QCoreApplication.translate("DmaxExplorer", u"Positive Fraction", None))

        self.label_2.setText(QCoreApplication.translate("DmaxExplorer", u"Npts", None))
        self.label_3.setText(QCoreApplication.translate("DmaxExplorer", u"Min Distance [\u212b]", None))
        self.label_4.setText(QCoreApplication.translate("DmaxExplorer", u"Max Distance [\u212b]", None))
        self.closeButton.setText(QCoreApplication.translate("DmaxExplorer", u"Close", None))
    # retranslateUi

