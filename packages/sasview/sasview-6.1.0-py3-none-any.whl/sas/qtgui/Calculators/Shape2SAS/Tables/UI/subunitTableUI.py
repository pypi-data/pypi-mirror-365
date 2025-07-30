# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'subunitTableUI.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QGridLayout, QHBoxLayout, QHeaderView, QPushButton,
    QSizePolicy, QSpacerItem, QSpinBox, QTableView,
    QWidget)

class Ui_SubunitTableController(object):
    def setupUi(self, SubunitTableController):
        if not SubunitTableController.objectName():
            SubunitTableController.setObjectName(u"SubunitTableController")
        SubunitTableController.resize(516, 240)
        self.gridLayout_2 = QGridLayout(SubunitTableController)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.add = QPushButton(SubunitTableController)
        self.add.setObjectName(u"add")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.add.sizePolicy().hasHeightForWidth())
        self.add.setSizePolicy(sizePolicy)
        self.add.setMinimumSize(QSize(60, 24))

        self.horizontalLayout.addWidget(self.add)

        self.subunit = QComboBox(SubunitTableController)
        self.subunit.setObjectName(u"subunit")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.subunit.sizePolicy().hasHeightForWidth())
        self.subunit.setSizePolicy(sizePolicy1)
        self.subunit.setMinimumSize(QSize(120, 24))

        self.horizontalLayout.addWidget(self.subunit)

        self.line = QFrame(SubunitTableController)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Raised)

        self.horizontalLayout.addWidget(self.line)

        self.deleteButton = QPushButton(SubunitTableController)
        self.deleteButton.setObjectName(u"deleteButton")
        sizePolicy.setHeightForWidth(self.deleteButton.sizePolicy().hasHeightForWidth())
        self.deleteButton.setSizePolicy(sizePolicy)
        self.deleteButton.setMinimumSize(QSize(100, 24))

        self.horizontalLayout.addWidget(self.deleteButton)

        self.selected = QSpinBox(SubunitTableController)
        self.selected.setObjectName(u"selected")
        sizePolicy.setHeightForWidth(self.selected.sizePolicy().hasHeightForWidth())
        self.selected.setSizePolicy(sizePolicy)
        self.selected.setMinimumSize(QSize(40, 24))
        self.selected.setMinimum(1)

        self.horizontalLayout.addWidget(self.selected)

        self.line2 = QFrame(SubunitTableController)
        self.line2.setObjectName(u"line2")
        self.line2.setFrameShape(QFrame.Shape.VLine)
        self.line2.setFrameShadow(QFrame.Shadow.Raised)

        self.horizontalLayout.addWidget(self.line2)

        self.overlap = QCheckBox(SubunitTableController)
        self.overlap.setObjectName(u"overlap")
        sizePolicy.setHeightForWidth(self.overlap.sizePolicy().hasHeightForWidth())
        self.overlap.setSizePolicy(sizePolicy)
        self.overlap.setMinimumSize(QSize(110, 24))
        self.overlap.setChecked(True)

        self.horizontalLayout.addWidget(self.overlap)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.table = QTableView(SubunitTableController)
        self.table.setObjectName(u"table")

        self.gridLayout.addWidget(self.table, 1, 0, 1, 1)


        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)


        self.retranslateUi(SubunitTableController)

        QMetaObject.connectSlotsByName(SubunitTableController)
    # setupUi

    def retranslateUi(self, SubunitTableController):
        SubunitTableController.setWindowTitle(QCoreApplication.translate("SubunitTableController", u"SubunitInitialiser", None))
#if QT_CONFIG(tooltip)
        self.add.setToolTip(QCoreApplication.translate("SubunitTableController", u"Add subunit to table.", None))
#endif // QT_CONFIG(tooltip)
        self.add.setText(QCoreApplication.translate("SubunitTableController", u"Add", None))
#if QT_CONFIG(tooltip)
        self.subunit.setToolTip(QCoreApplication.translate("SubunitTableController", u"Available subunits.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.deleteButton.setToolTip(QCoreApplication.translate("SubunitTableController", u"Delete selected subunit.", None))
#endif // QT_CONFIG(tooltip)
        self.deleteButton.setText(QCoreApplication.translate("SubunitTableController", u"Delete column", None))
#if QT_CONFIG(tooltip)
        self.selected.setToolTip(QCoreApplication.translate("SubunitTableController", u"Selected column to delete.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.overlap.setToolTip(QCoreApplication.translate("SubunitTableController", u"Exclude point overlap among subunits", None))
#endif // QT_CONFIG(tooltip)
        self.overlap.setText(QCoreApplication.translate("SubunitTableController", u"Exclude overlap", None))
    # retranslateUi

