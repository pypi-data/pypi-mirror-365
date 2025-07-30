# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PluginManagerUI.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QDialog, QGridLayout,
    QHBoxLayout, QListWidget, QListWidgetItem, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_PluginManagerUI(object):
    def setupUi(self, PluginManagerUI):
        if not PluginManagerUI.objectName():
            PluginManagerUI.setObjectName(u"PluginManagerUI")
        PluginManagerUI.resize(528, 442)
        self.gridLayout = QGridLayout(PluginManagerUI)
        self.gridLayout.setObjectName(u"gridLayout")
        self.lstModels = QListWidget(PluginManagerUI)
        self.lstModels.setObjectName(u"lstModels")
        self.lstModels.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.lstModels.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.lstModels.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.lstModels.setSpacing(2)

        self.gridLayout.addWidget(self.lstModels, 0, 0, 1, 1)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.cmdAdd = QPushButton(PluginManagerUI)
        self.cmdAdd.setObjectName(u"cmdAdd")

        self.verticalLayout.addWidget(self.cmdAdd)

        self.cmdAddFile = QPushButton(PluginManagerUI)
        self.cmdAddFile.setObjectName(u"cmdAddFile")

        self.verticalLayout.addWidget(self.cmdAddFile)

        self.cmdDuplicate = QPushButton(PluginManagerUI)
        self.cmdDuplicate.setObjectName(u"cmdDuplicate")

        self.verticalLayout.addWidget(self.cmdDuplicate)

        self.cmdEdit = QPushButton(PluginManagerUI)
        self.cmdEdit.setObjectName(u"cmdEdit")

        self.verticalLayout.addWidget(self.cmdEdit)

        self.cmdDelete = QPushButton(PluginManagerUI)
        self.cmdDelete.setObjectName(u"cmdDelete")

        self.verticalLayout.addWidget(self.cmdDelete)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.gridLayout.addLayout(self.verticalLayout, 0, 1, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.cmdHelp = QPushButton(PluginManagerUI)
        self.cmdHelp.setObjectName(u"cmdHelp")

        self.horizontalLayout.addWidget(self.cmdHelp)

        self.cmdOK = QPushButton(PluginManagerUI)
        self.cmdOK.setObjectName(u"cmdOK")

        self.horizontalLayout.addWidget(self.cmdOK)


        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)


        self.retranslateUi(PluginManagerUI)

        QMetaObject.connectSlotsByName(PluginManagerUI)
    # setupUi

    def retranslateUi(self, PluginManagerUI):
        PluginManagerUI.setWindowTitle(QCoreApplication.translate("PluginManagerUI", u"Plugin Manager", None))
        self.cmdAdd.setText(QCoreApplication.translate("PluginManagerUI", u"Add...", None))
        self.cmdAddFile.setText(QCoreApplication.translate("PluginManagerUI", u"Add file...", None))
        self.cmdDuplicate.setText(QCoreApplication.translate("PluginManagerUI", u"Duplicate", None))
        self.cmdEdit.setText(QCoreApplication.translate("PluginManagerUI", u"Edit...", None))
        self.cmdDelete.setText(QCoreApplication.translate("PluginManagerUI", u"Delete", None))
        self.cmdHelp.setText(QCoreApplication.translate("PluginManagerUI", u"Help", None))
        self.cmdOK.setText(QCoreApplication.translate("PluginManagerUI", u"Close", None))
    # retranslateUi

