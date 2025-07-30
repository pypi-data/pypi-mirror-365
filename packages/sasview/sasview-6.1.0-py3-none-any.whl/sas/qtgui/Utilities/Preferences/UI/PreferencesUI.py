# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PreferencesUI.ui'
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
    QFrame, QGridLayout, QHBoxLayout, QLayout,
    QListWidget, QListWidgetItem, QSizePolicy, QStackedWidget,
    QVBoxLayout, QWidget)

class Ui_preferencesUI(object):
    def setupUi(self, preferencesUI):
        if not preferencesUI.objectName():
            preferencesUI.setObjectName(u"preferencesUI")
        preferencesUI.resize(731, 463)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(preferencesUI.sizePolicy().hasHeightForWidth())
        preferencesUI.setSizePolicy(sizePolicy)
        icon = QIcon()
        icon.addFile(u":/res/ball.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        preferencesUI.setWindowIcon(icon)
        self.gridLayout_2 = QGridLayout(preferencesUI)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setSizeConstraint(QLayout.SetNoConstraint)
        self.listWidget = QListWidget(preferencesUI)
        self.listWidget.setObjectName(u"listWidget")
        self.listWidget.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.listWidget.sizePolicy().hasHeightForWidth())
        self.listWidget.setSizePolicy(sizePolicy1)
        self.listWidget.setMaximumSize(QSize(256, 16777215))

        self.horizontalLayout_2.addWidget(self.listWidget)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.stackedWidget = QStackedWidget(preferencesUI)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setEnabled(True)
        self.stackedWidget.setLayoutDirection(Qt.LeftToRight)
        self.stackedWidget.setFrameShape(QFrame.StyledPanel)
        self.stackedWidget.setFrameShadow(QFrame.Sunken)
        self.stackedWidget.setLineWidth(2)
        self.stackedWidget.setMidLineWidth(1)

        self.verticalLayout.addWidget(self.stackedWidget)


        self.horizontalLayout_2.addLayout(self.verticalLayout)


        self.gridLayout_2.addLayout(self.horizontalLayout_2, 18, 0, 2, 1)

        self.buttonBox = QDialogButtonBox(preferencesUI)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Apply|QDialogButtonBox.Cancel|QDialogButtonBox.Help|QDialogButtonBox.Ok|QDialogButtonBox.RestoreDefaults)

        self.gridLayout_2.addWidget(self.buttonBox, 22, 0, 1, 1)


        self.retranslateUi(preferencesUI)
        self.buttonBox.accepted.connect(preferencesUI.accept)
        self.buttonBox.rejected.connect(preferencesUI.reject)

        self.listWidget.setCurrentRow(-1)
        self.stackedWidget.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(preferencesUI)
    # setupUi

    def retranslateUi(self, preferencesUI):
        preferencesUI.setWindowTitle(QCoreApplication.translate("preferencesUI", u"Preferences", None))
    # retranslateUi

