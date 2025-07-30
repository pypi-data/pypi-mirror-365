# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'CategoryManagerUI.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QDialog,
    QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QTableView, QWidget)

class Ui_CategoryManagerUI(object):
    def setupUi(self, CategoryManagerUI):
        if not CategoryManagerUI.objectName():
            CategoryManagerUI.setObjectName(u"CategoryManagerUI")
        CategoryManagerUI.resize(548, 717)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(CategoryManagerUI.sizePolicy().hasHeightForWidth())
        CategoryManagerUI.setSizePolicy(sizePolicy)
        self.gridLayout_2 = QGridLayout(CategoryManagerUI)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.CategoryManagerGroup = QGroupBox(CategoryManagerUI)
        self.CategoryManagerGroup.setObjectName(u"CategoryManagerGroup")
        sizePolicy.setHeightForWidth(self.CategoryManagerGroup.sizePolicy().hasHeightForWidth())
        self.CategoryManagerGroup.setSizePolicy(sizePolicy)
        self.CategoryManagerGroup.setMinimumSize(QSize(300, 150))
        self.CategoryManagerGroup.setCheckable(False)
        self.gridLayout = QGridLayout(self.CategoryManagerGroup)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.chkEnable = QCheckBox(self.CategoryManagerGroup)
        self.chkEnable.setObjectName(u"chkEnable")

        self.horizontalLayout_3.addWidget(self.chkEnable)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(self.CategoryManagerGroup)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label)

        self.txtSearch = QLineEdit(self.CategoryManagerGroup)
        self.txtSearch.setObjectName(u"txtSearch")

        self.horizontalLayout_2.addWidget(self.txtSearch)


        self.horizontalLayout_3.addLayout(self.horizontalLayout_2)


        self.gridLayout.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)

        self.lstCategory = QTableView(self.CategoryManagerGroup)
        self.lstCategory.setObjectName(u"lstCategory")
        self.lstCategory.setEnabled(True)
        self.lstCategory.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.lstCategory.setAlternatingRowColors(True)
        self.lstCategory.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.lstCategory.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.gridLayout.addWidget(self.lstCategory, 1, 0, 1, 1)


        self.gridLayout_2.addWidget(self.CategoryManagerGroup, 0, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(78, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.cmdModify = QPushButton(CategoryManagerUI)
        self.cmdModify.setObjectName(u"cmdModify")

        self.horizontalLayout.addWidget(self.cmdModify)

        self.cmdReset = QPushButton(CategoryManagerUI)
        self.cmdReset.setObjectName(u"cmdReset")

        self.horizontalLayout.addWidget(self.cmdReset)

        self.cmdOK = QPushButton(CategoryManagerUI)
        self.cmdOK.setObjectName(u"cmdOK")
        self.cmdOK.setAutoDefault(True)

        self.horizontalLayout.addWidget(self.cmdOK)

        self.cmdHelp = QPushButton(CategoryManagerUI)
        self.cmdHelp.setObjectName(u"cmdHelp")
        self.cmdHelp.setAutoDefault(True)

        self.horizontalLayout.addWidget(self.cmdHelp)


        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        QWidget.setTabOrder(self.chkEnable, self.txtSearch)
        QWidget.setTabOrder(self.txtSearch, self.lstCategory)
        QWidget.setTabOrder(self.lstCategory, self.cmdModify)
        QWidget.setTabOrder(self.cmdModify, self.cmdReset)
        QWidget.setTabOrder(self.cmdReset, self.cmdOK)
        QWidget.setTabOrder(self.cmdOK, self.cmdHelp)

        self.retranslateUi(CategoryManagerUI)

        QMetaObject.connectSlotsByName(CategoryManagerUI)
    # setupUi

    def retranslateUi(self, CategoryManagerUI):
        CategoryManagerUI.setWindowTitle(QCoreApplication.translate("CategoryManagerUI", u"Category Manager", None))
        self.CategoryManagerGroup.setTitle(QCoreApplication.translate("CategoryManagerUI", u"Category Manager", None))
        self.chkEnable.setText(QCoreApplication.translate("CategoryManagerUI", u"Enable/Disable all", None))
        self.label.setText(QCoreApplication.translate("CategoryManagerUI", u"Search", None))
        self.txtSearch.setText("")
#if QT_CONFIG(tooltip)
        self.cmdModify.setToolTip(QCoreApplication.translate("CategoryManagerUI", u"Add/Remove categories for the selected model.", None))
#endif // QT_CONFIG(tooltip)
        self.cmdModify.setText(QCoreApplication.translate("CategoryManagerUI", u"Modify", None))
#if QT_CONFIG(tooltip)
        self.cmdReset.setToolTip(QCoreApplication.translate("CategoryManagerUI", u"Reset categories for selected models.", None))
#endif // QT_CONFIG(tooltip)
        self.cmdReset.setText(QCoreApplication.translate("CategoryManagerUI", u"Reset", None))
        self.cmdOK.setText(QCoreApplication.translate("CategoryManagerUI", u"OK", None))
        self.cmdHelp.setText(QCoreApplication.translate("CategoryManagerUI", u"Help", None))
    # retranslateUi

