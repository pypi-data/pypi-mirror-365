# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'FrameSelectUI.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog, QGridLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QWidget)

class Ui_FrameSelect(object):
    def setupUi(self, FrameSelect):
        if not FrameSelect.objectName():
            FrameSelect.setObjectName(u"FrameSelect")
        FrameSelect.setWindowModality(Qt.WindowModal)
        FrameSelect.resize(278, 173)
        self.gridLayout_3 = QGridLayout(FrameSelect)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.lblDescription = QLabel(FrameSelect)
        self.lblDescription.setObjectName(u"lblDescription")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblDescription.sizePolicy().hasHeightForWidth())
        self.lblDescription.setSizePolicy(sizePolicy)

        self.gridLayout_2.addWidget(self.lblDescription, 0, 0, 1, 1)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_2 = QLabel(FrameSelect)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)

        self.txtFirstFrame = QLineEdit(FrameSelect)
        self.txtFirstFrame.setObjectName(u"txtFirstFrame")

        self.gridLayout.addWidget(self.txtFirstFrame, 0, 1, 1, 1)

        self.label_3 = QLabel(FrameSelect)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)

        self.txtLastFrame = QLineEdit(FrameSelect)
        self.txtLastFrame.setObjectName(u"txtLastFrame")

        self.gridLayout.addWidget(self.txtLastFrame, 1, 1, 1, 1)

        self.label_4 = QLabel(FrameSelect)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)

        self.txtIncrement = QLineEdit(FrameSelect)
        self.txtIncrement.setObjectName(u"txtIncrement")

        self.gridLayout.addWidget(self.txtIncrement, 2, 1, 1, 1)


        self.gridLayout_2.addLayout(self.gridLayout, 1, 0, 1, 1)

        self.chkSeparateFiles = QCheckBox(FrameSelect)
        self.chkSeparateFiles.setObjectName(u"chkSeparateFiles")

        self.gridLayout_2.addWidget(self.chkSeparateFiles, 2, 0, 1, 1)


        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer, 1, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.cmdOK = QPushButton(FrameSelect)
        self.cmdOK.setObjectName(u"cmdOK")

        self.horizontalLayout.addWidget(self.cmdOK)

        self.cmdCancel = QPushButton(FrameSelect)
        self.cmdCancel.setObjectName(u"cmdCancel")

        self.horizontalLayout.addWidget(self.cmdCancel)


        self.gridLayout_3.addLayout(self.horizontalLayout, 2, 0, 1, 1)


        self.retranslateUi(FrameSelect)

        QMetaObject.connectSlotsByName(FrameSelect)
    # setupUi

    def retranslateUi(self, FrameSelect):
        FrameSelect.setWindowTitle(QCoreApplication.translate("FrameSelect", u"Frame Select", None))
        self.lblDescription.setText(QCoreApplication.translate("FrameSelect", u"text", None))
        self.label_2.setText(QCoreApplication.translate("FrameSelect", u"First frame:", None))
        self.label_3.setText(QCoreApplication.translate("FrameSelect", u"Last frame:", None))
        self.label_4.setText(QCoreApplication.translate("FrameSelect", u"Increment:", None))
        self.chkSeparateFiles.setText(QCoreApplication.translate("FrameSelect", u"Export each frame to separate file", None))
        self.cmdOK.setText(QCoreApplication.translate("FrameSelect", u"OK", None))
        self.cmdCancel.setText(QCoreApplication.translate("FrameSelect", u"Cancel", None))
    # retranslateUi

