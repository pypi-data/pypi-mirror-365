# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'GPUOptionsUI.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QGridLayout, QGroupBox,
    QHBoxLayout, QLayout, QProgressBar, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_GPUOptions(object):
    def setupUi(self, GPUOptions):
        if not GPUOptions.objectName():
            GPUOptions.setObjectName(u"GPUOptions")
        GPUOptions.resize(505, 268)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(GPUOptions.sizePolicy().hasHeightForWidth())
        GPUOptions.setSizePolicy(sizePolicy)
        icon = QIcon()
        icon.addFile(u"../../../../../../../../../../../Users/UI/res/ball.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        GPUOptions.setWindowIcon(icon)
        self.gridLayout = QGridLayout(GPUOptions)
        self.gridLayout.setObjectName(u"gridLayout")
        self.openCLCheckBoxGroup = QGroupBox(GPUOptions)
        self.openCLCheckBoxGroup.setObjectName(u"openCLCheckBoxGroup")
        sizePolicy.setHeightForWidth(self.openCLCheckBoxGroup.sizePolicy().hasHeightForWidth())
        self.openCLCheckBoxGroup.setSizePolicy(sizePolicy)
        self.openCLCheckBoxGroup.setMinimumSize(QSize(300, 150))
        self.verticalLayoutWidget = QWidget(self.openCLCheckBoxGroup)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(10, 20, 391, 141))
        self.optionsLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.optionsLayout.setObjectName(u"optionsLayout")
        self.optionsLayout.setSizeConstraint(QLayout.SetMinimumSize)
        self.optionsLayout.setContentsMargins(0, 0, 0, 0)

        self.gridLayout.addWidget(self.openCLCheckBoxGroup, 0, 0, 1, 2)

        self.progressBar = QProgressBar(GPUOptions)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(24)

        self.gridLayout.addWidget(self.progressBar, 1, 0, 1, 2)

        self.horizontalSpacer = QSpacerItem(78, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 2, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetMinimumSize)
        self.testButton = QPushButton(GPUOptions)
        self.testButton.setObjectName(u"testButton")

        self.horizontalLayout.addWidget(self.testButton)

        self.helpButton = QPushButton(GPUOptions)
        self.helpButton.setObjectName(u"helpButton")
        self.helpButton.setAutoDefault(True)

        self.horizontalLayout.addWidget(self.helpButton)


        self.gridLayout.addLayout(self.horizontalLayout, 2, 1, 1, 1)


        self.retranslateUi(GPUOptions)

        QMetaObject.connectSlotsByName(GPUOptions)
    # setupUi

    def retranslateUi(self, GPUOptions):
        GPUOptions.setWindowTitle(QCoreApplication.translate("GPUOptions", u"OpenCL Options", None))
        self.openCLCheckBoxGroup.setTitle(QCoreApplication.translate("GPUOptions", u"Available OpenCL Options", None))
        self.testButton.setText(QCoreApplication.translate("GPUOptions", u"Test", None))
        self.helpButton.setText(QCoreApplication.translate("GPUOptions", u"Help", None))
    # retranslateUi

