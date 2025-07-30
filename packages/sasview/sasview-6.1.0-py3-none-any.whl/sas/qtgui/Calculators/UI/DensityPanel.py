# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'DensityPanel.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QFrame, QGridLayout, QLabel, QLineEdit,
    QSizePolicy, QSpacerItem, QWidget)

class Ui_DensityPanel(object):
    def setupUi(self, DensityPanel):
        if not DensityPanel.objectName():
            DensityPanel.setObjectName(u"DensityPanel")
        DensityPanel.resize(345, 236)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DensityPanel.sizePolicy().hasHeightForWidth())
        DensityPanel.setSizePolicy(sizePolicy)
        icon = QIcon()
        icon.addFile(u":/res/ball.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        DensityPanel.setWindowIcon(icon)
        self.gridLayout_2 = QGridLayout(DensityPanel)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_1 = QLabel(DensityPanel)
        self.label_1.setObjectName(u"label_1")

        self.gridLayout.addWidget(self.label_1, 0, 0, 1, 1)

        self.editMolecularFormula = QLineEdit(DensityPanel)
        self.editMolecularFormula.setObjectName(u"editMolecularFormula")
        self.editMolecularFormula.setMinimumSize(QSize(61, 21))
        self.editMolecularFormula.setBaseSize(QSize(61, 21))
        self.editMolecularFormula.setFocusPolicy(Qt.StrongFocus)

        self.gridLayout.addWidget(self.editMolecularFormula, 0, 1, 1, 1)

        self.label_3 = QLabel(DensityPanel)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 0, 2, 1, 1)

        self.label_2 = QLabel(DensityPanel)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.editMolarMass = QLineEdit(DensityPanel)
        self.editMolarMass.setObjectName(u"editMolarMass")
        self.editMolarMass.setMinimumSize(QSize(61, 21))
        self.editMolarMass.setBaseSize(QSize(61, 21))
        self.editMolarMass.setFocusPolicy(Qt.StrongFocus)
        self.editMolarMass.setStyleSheet(u"")
        self.editMolarMass.setReadOnly(True)

        self.gridLayout.addWidget(self.editMolarMass, 1, 1, 1, 1)

        self.label_4 = QLabel(DensityPanel)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 1, 2, 1, 1)

        self.frame = QFrame(DensityPanel)
        self.frame.setObjectName(u"frame")
        self.frame.setMinimumSize(QSize(0, 5))
        self.frame.setFrameShape(QFrame.HLine)
        self.frame.setFrameShadow(QFrame.Raised)
        self.frame.setLineWidth(1)
        self.frame.setMidLineWidth(0)

        self.gridLayout.addWidget(self.frame, 2, 0, 1, 3)

        self.label_5 = QLabel(DensityPanel)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 3, 0, 1, 1)

        self.editMolarVolume = QLineEdit(DensityPanel)
        self.editMolarVolume.setObjectName(u"editMolarVolume")
        self.editMolarVolume.setMinimumSize(QSize(61, 21))
        self.editMolarVolume.setBaseSize(QSize(61, 21))
        self.editMolarVolume.setFocusPolicy(Qt.StrongFocus)

        self.gridLayout.addWidget(self.editMolarVolume, 3, 1, 1, 1)

        self.label_6 = QLabel(DensityPanel)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout.addWidget(self.label_6, 3, 2, 1, 1)

        self.label_7 = QLabel(DensityPanel)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout.addWidget(self.label_7, 4, 0, 1, 1)

        self.editMassDensity = QLineEdit(DensityPanel)
        self.editMassDensity.setObjectName(u"editMassDensity")
        self.editMassDensity.setMinimumSize(QSize(61, 21))
        self.editMassDensity.setBaseSize(QSize(61, 21))
        self.editMassDensity.setFocusPolicy(Qt.StrongFocus)

        self.gridLayout.addWidget(self.editMassDensity, 4, 1, 1, 1)

        self.label_8 = QLabel(DensityPanel)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout.addWidget(self.label_8, 4, 2, 1, 1)


        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer, 1, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(DensityPanel)
        self.buttonBox.setObjectName(u"buttonBox")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy1)
        self.buttonBox.setFocusPolicy(Qt.StrongFocus)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close|QDialogButtonBox.Help|QDialogButtonBox.Reset)
        self.buttonBox.setCenterButtons(True)

        self.gridLayout_2.addWidget(self.buttonBox, 2, 0, 1, 1)

        QWidget.setTabOrder(self.editMolecularFormula, self.editMolarMass)
        QWidget.setTabOrder(self.editMolarMass, self.editMolarVolume)
        QWidget.setTabOrder(self.editMolarVolume, self.editMassDensity)
        QWidget.setTabOrder(self.editMassDensity, self.buttonBox)

        self.retranslateUi(DensityPanel)
        self.buttonBox.accepted.connect(DensityPanel.accept)
        self.buttonBox.rejected.connect(DensityPanel.reject)

        QMetaObject.connectSlotsByName(DensityPanel)
    # setupUi

    def retranslateUi(self, DensityPanel):
        DensityPanel.setWindowTitle(QCoreApplication.translate("DensityPanel", u"Density/Volume Calculator", None))
        self.label_1.setText(QCoreApplication.translate("DensityPanel", u"Molecular Formula", None))
        self.label_3.setText(QCoreApplication.translate("DensityPanel", u"e.g. H2O", None))
        self.label_2.setText(QCoreApplication.translate("DensityPanel", u"Molar Mass", None))
        self.label_4.setText(QCoreApplication.translate("DensityPanel", u"g/mol", None))
        self.label_5.setText(QCoreApplication.translate("DensityPanel", u"Molar Volume", None))
        self.label_6.setText(QCoreApplication.translate("DensityPanel", u"cm\u00b3/mol", None))
        self.label_7.setText(QCoreApplication.translate("DensityPanel", u"Mass Density", None))
        self.label_8.setText(QCoreApplication.translate("DensityPanel", u"g/cm\u00b3", None))
    # retranslateUi

