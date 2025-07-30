# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MaskEditorUI.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QGridLayout,
    QGroupBox, QPushButton, QRadioButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_MaskEditorUI(object):
    def setupUi(self, MaskEditorUI):
        if not MaskEditorUI.objectName():
            MaskEditorUI.setObjectName(u"MaskEditorUI")
        MaskEditorUI.resize(824, 453)
        icon = QIcon()
        icon.addFile(u":/res/ball.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        MaskEditorUI.setWindowIcon(icon)
        self.gridLayout = QGridLayout(MaskEditorUI)
        self.gridLayout.setObjectName(u"gridLayout")
        self.groupBox = QGroupBox(MaskEditorUI)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.rbWings = QRadioButton(self.groupBox)
        self.rbWings.setObjectName(u"rbWings")

        self.verticalLayout.addWidget(self.rbWings)

        self.rbCircularDisk = QRadioButton(self.groupBox)
        self.rbCircularDisk.setObjectName(u"rbCircularDisk")

        self.verticalLayout.addWidget(self.rbCircularDisk)

        self.rbRectangularDisk = QRadioButton(self.groupBox)
        self.rbRectangularDisk.setObjectName(u"rbRectangularDisk")

        self.verticalLayout.addWidget(self.rbRectangularDisk)

        self.rbDoubleWingWindow = QRadioButton(self.groupBox)
        self.rbDoubleWingWindow.setObjectName(u"rbDoubleWingWindow")

        self.verticalLayout.addWidget(self.rbDoubleWingWindow)

        self.rbCircularWindow = QRadioButton(self.groupBox)
        self.rbCircularWindow.setObjectName(u"rbCircularWindow")

        self.verticalLayout.addWidget(self.rbCircularWindow)

        self.rbRectangularWindow = QRadioButton(self.groupBox)
        self.rbRectangularWindow.setObjectName(u"rbRectangularWindow")

        self.verticalLayout.addWidget(self.rbRectangularWindow)


        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 152, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 1, 0, 1, 1)

        self.cmdAdd = QPushButton(MaskEditorUI)
        self.cmdAdd.setObjectName(u"cmdAdd")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmdAdd.sizePolicy().hasHeightForWidth())
        self.cmdAdd.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.cmdAdd, 2, 0, 1, 1)

        self.cmdReset = QPushButton(MaskEditorUI)
        self.cmdReset.setObjectName(u"cmdReset")
        sizePolicy.setHeightForWidth(self.cmdReset.sizePolicy().hasHeightForWidth())
        self.cmdReset.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.cmdReset, 3, 0, 1, 1)

        self.cmdClear = QPushButton(MaskEditorUI)
        self.cmdClear.setObjectName(u"cmdClear")
        sizePolicy.setHeightForWidth(self.cmdClear.sizePolicy().hasHeightForWidth())
        self.cmdClear.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.cmdClear, 4, 0, 1, 1)

        self.frame = QFrame(MaskEditorUI)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.frame.setLineWidth(2)

        self.gridLayout.addWidget(self.frame, 0, 1, 5, 1)

        QWidget.setTabOrder(self.rbWings, self.rbCircularDisk)
        QWidget.setTabOrder(self.rbCircularDisk, self.rbRectangularDisk)
        QWidget.setTabOrder(self.rbRectangularDisk, self.rbDoubleWingWindow)
        QWidget.setTabOrder(self.rbDoubleWingWindow, self.rbCircularWindow)
        QWidget.setTabOrder(self.rbCircularWindow, self.rbRectangularWindow)
        QWidget.setTabOrder(self.rbRectangularWindow, self.cmdAdd)
        QWidget.setTabOrder(self.cmdAdd, self.cmdReset)
        QWidget.setTabOrder(self.cmdReset, self.cmdClear)

        self.retranslateUi(MaskEditorUI)

        QMetaObject.connectSlotsByName(MaskEditorUI)
    # setupUi

    def retranslateUi(self, MaskEditorUI):
        MaskEditorUI.setWindowTitle(QCoreApplication.translate("MaskEditorUI", u"Dialog", None))
        self.groupBox.setTitle(QCoreApplication.translate("MaskEditorUI", u"Mask shape", None))
        self.rbWings.setText(QCoreApplication.translate("MaskEditorUI", u"Double Wings", None))
        self.rbCircularDisk.setText(QCoreApplication.translate("MaskEditorUI", u"Circular Disk", None))
        self.rbRectangularDisk.setText(QCoreApplication.translate("MaskEditorUI", u"Rectangular Disk", None))
        self.rbDoubleWingWindow.setText(QCoreApplication.translate("MaskEditorUI", u"Double Wing Window", None))
        self.rbCircularWindow.setText(QCoreApplication.translate("MaskEditorUI", u"Circular Window", None))
        self.rbRectangularWindow.setText(QCoreApplication.translate("MaskEditorUI", u"Rectangular Window", None))
        self.cmdAdd.setText(QCoreApplication.translate("MaskEditorUI", u"Add", None))
#if QT_CONFIG(tooltip)
        self.cmdReset.setToolTip(QCoreApplication.translate("MaskEditorUI", u"Clear all the masks", None))
#endif // QT_CONFIG(tooltip)
        self.cmdReset.setText(QCoreApplication.translate("MaskEditorUI", u"Reset", None))
#if QT_CONFIG(tooltip)
        self.cmdClear.setToolTip(QCoreApplication.translate("MaskEditorUI", u"Clear recent masks", None))
#endif // QT_CONFIG(tooltip)
        self.cmdClear.setText(QCoreApplication.translate("MaskEditorUI", u"Clear", None))
    # retranslateUi

