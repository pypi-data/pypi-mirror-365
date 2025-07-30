# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'TabbedModelEditor.ui'
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
    QHBoxLayout, QPushButton, QSizePolicy, QSpacerItem,
    QTabWidget, QVBoxLayout, QWidget)

class Ui_TabbedModelEditor(object):
    def setupUi(self, TabbedModelEditor):
        if not TabbedModelEditor.objectName():
            TabbedModelEditor.setObjectName(u"TabbedModelEditor")
        TabbedModelEditor.resize(688, 697)
        icon = QIcon()
        icon.addFile(u":/res/ball.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        TabbedModelEditor.setWindowIcon(icon)
        self.verticalLayout = QVBoxLayout(TabbedModelEditor)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(TabbedModelEditor)
        self.tabWidget.setObjectName(u"tabWidget")

        self.verticalLayout.addWidget(self.tabWidget)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.cmdLoad = QPushButton(TabbedModelEditor)
        self.cmdLoad.setObjectName(u"cmdLoad")

        self.horizontalLayout.addWidget(self.cmdLoad)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.buttonBox = QDialogButtonBox(TabbedModelEditor)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Apply|QDialogButtonBox.Cancel|QDialogButtonBox.Help)

        self.horizontalLayout.addWidget(self.buttonBox)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(TabbedModelEditor)

        self.tabWidget.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(TabbedModelEditor)
    # setupUi

    def retranslateUi(self, TabbedModelEditor):
        TabbedModelEditor.setWindowTitle(QCoreApplication.translate("TabbedModelEditor", u"Model Editor", None))
        self.cmdLoad.setText(QCoreApplication.translate("TabbedModelEditor", u"Load plugin...", None))
    # retranslateUi

