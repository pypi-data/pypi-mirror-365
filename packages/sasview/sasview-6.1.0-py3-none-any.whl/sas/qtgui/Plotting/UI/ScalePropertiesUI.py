# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ScalePropertiesUI.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialog,
    QDialogButtonBox, QGridLayout, QLabel, QSizePolicy,
    QSpacerItem, QWidget)

class Ui_scalePropertiesUI(object):
    def setupUi(self, scalePropertiesUI):
        if not scalePropertiesUI.objectName():
            scalePropertiesUI.setObjectName(u"scalePropertiesUI")
        scalePropertiesUI.resize(400, 137)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(scalePropertiesUI.sizePolicy().hasHeightForWidth())
        scalePropertiesUI.setSizePolicy(sizePolicy)
        icon = QIcon()
        icon.addFile(u":/res/ball.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        scalePropertiesUI.setWindowIcon(icon)
        self.gridLayout_2 = QGridLayout(scalePropertiesUI)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(scalePropertiesUI)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.label_2 = QLabel(scalePropertiesUI)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)

        self.label_3 = QLabel(scalePropertiesUI)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 0, 2, 1, 1)

        self.cbX = QComboBox(scalePropertiesUI)
        self.cbX.setObjectName(u"cbX")

        self.gridLayout.addWidget(self.cbX, 1, 0, 1, 1)

        self.cbY = QComboBox(scalePropertiesUI)
        self.cbY.setObjectName(u"cbY")

        self.gridLayout.addWidget(self.cbY, 1, 1, 1, 1)

        self.cbView = QComboBox(scalePropertiesUI)
        self.cbView.setObjectName(u"cbView")

        self.gridLayout.addWidget(self.cbView, 1, 2, 1, 1)


        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer, 1, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(scalePropertiesUI)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.gridLayout_2.addWidget(self.buttonBox, 2, 0, 1, 1)


        self.retranslateUi(scalePropertiesUI)
        self.buttonBox.accepted.connect(scalePropertiesUI.accept)
        self.buttonBox.rejected.connect(scalePropertiesUI.reject)

        QMetaObject.connectSlotsByName(scalePropertiesUI)
    # setupUi

    def retranslateUi(self, scalePropertiesUI):
        scalePropertiesUI.setWindowTitle(QCoreApplication.translate("scalePropertiesUI", u"Scale Properties", None))
        self.label.setText(QCoreApplication.translate("scalePropertiesUI", u"X", None))
        self.label_2.setText(QCoreApplication.translate("scalePropertiesUI", u"Y", None))
        self.label_3.setText(QCoreApplication.translate("scalePropertiesUI", u"View", None))
    # retranslateUi

