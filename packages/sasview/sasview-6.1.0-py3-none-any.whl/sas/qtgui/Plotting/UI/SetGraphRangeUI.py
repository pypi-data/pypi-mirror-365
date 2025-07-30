# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SetGraphRangeUI.ui'
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
    QGridLayout, QLabel, QLineEdit, QSizePolicy,
    QSpacerItem, QWidget)

class Ui_setGraphRangeUI(object):
    def setupUi(self, setGraphRangeUI):
        if not setGraphRangeUI.objectName():
            setGraphRangeUI.setObjectName(u"setGraphRangeUI")
        setGraphRangeUI.resize(358, 144)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(setGraphRangeUI.sizePolicy().hasHeightForWidth())
        setGraphRangeUI.setSizePolicy(sizePolicy)
        icon = QIcon()
        icon.addFile(u":/res/ball.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        setGraphRangeUI.setWindowIcon(icon)
        setGraphRangeUI.setModal(True)
        self.gridLayout_2 = QGridLayout(setGraphRangeUI)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(setGraphRangeUI)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.txtXmin = QLineEdit(setGraphRangeUI)
        self.txtXmin.setObjectName(u"txtXmin")

        self.gridLayout.addWidget(self.txtXmin, 0, 1, 1, 1)

        self.label_2 = QLabel(setGraphRangeUI)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 0, 2, 1, 1)

        self.txtXmax = QLineEdit(setGraphRangeUI)
        self.txtXmax.setObjectName(u"txtXmax")

        self.gridLayout.addWidget(self.txtXmax, 0, 3, 1, 1)

        self.label_3 = QLabel(setGraphRangeUI)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)

        self.txtYmin = QLineEdit(setGraphRangeUI)
        self.txtYmin.setObjectName(u"txtYmin")

        self.gridLayout.addWidget(self.txtYmin, 1, 1, 1, 1)

        self.label_4 = QLabel(setGraphRangeUI)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 1, 2, 1, 1)

        self.txtYmax = QLineEdit(setGraphRangeUI)
        self.txtYmax.setObjectName(u"txtYmax")

        self.gridLayout.addWidget(self.txtYmax, 1, 3, 1, 1)


        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer, 1, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(setGraphRangeUI)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.gridLayout_2.addWidget(self.buttonBox, 2, 0, 1, 1)


        self.retranslateUi(setGraphRangeUI)
        self.buttonBox.accepted.connect(setGraphRangeUI.accept)
        self.buttonBox.rejected.connect(setGraphRangeUI.reject)

        QMetaObject.connectSlotsByName(setGraphRangeUI)
    # setupUi

    def retranslateUi(self, setGraphRangeUI):
        setGraphRangeUI.setWindowTitle(QCoreApplication.translate("setGraphRangeUI", u"Set Graph Range", None))
        self.label.setText(QCoreApplication.translate("setGraphRangeUI", u"X min", None))
        self.label_2.setText(QCoreApplication.translate("setGraphRangeUI", u"X max", None))
        self.label_3.setText(QCoreApplication.translate("setGraphRangeUI", u"Y min", None))
        self.label_4.setText(QCoreApplication.translate("setGraphRangeUI", u"Y max", None))
    # retranslateUi

