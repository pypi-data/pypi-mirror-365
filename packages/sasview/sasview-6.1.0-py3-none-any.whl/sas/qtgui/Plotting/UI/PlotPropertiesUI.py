# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PlotPropertiesUI.ui'
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
    QDialogButtonBox, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QSpinBox, QWidget)

class Ui_PlotPropertiesUI(object):
    def setupUi(self, PlotPropertiesUI):
        if not PlotPropertiesUI.objectName():
            PlotPropertiesUI.setObjectName(u"PlotPropertiesUI")
        PlotPropertiesUI.resize(319, 285)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(PlotPropertiesUI.sizePolicy().hasHeightForWidth())
        PlotPropertiesUI.setSizePolicy(sizePolicy)
        icon = QIcon()
        icon.addFile(u":/res/ball.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        PlotPropertiesUI.setWindowIcon(icon)
        self.gridLayout_3 = QGridLayout(PlotPropertiesUI)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.groupBox = QGroupBox(PlotPropertiesUI)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)

        self.cbShape = QComboBox(self.groupBox)
        self.cbShape.setObjectName(u"cbShape")

        self.gridLayout.addWidget(self.cbShape, 0, 1, 1, 2)

        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 0, 3, 1, 1, Qt.AlignRight)

        self.sbSize = QSpinBox(self.groupBox)
        self.sbSize.setObjectName(u"sbSize")
        self.sbSize.setMinimum(1)
        self.sbSize.setMaximum(72)

        self.gridLayout.addWidget(self.sbSize, 0, 4, 1, 1)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)

        self.cbColor = QComboBox(self.groupBox)
        self.cbColor.setObjectName(u"cbColor")

        self.gridLayout.addWidget(self.cbColor, 1, 1, 1, 1)

        self.cmdCustom = QPushButton(self.groupBox)
        self.cmdCustom.setObjectName(u"cmdCustom")

        self.gridLayout.addWidget(self.cmdCustom, 1, 2, 1, 1)


        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)


        self.gridLayout_3.addWidget(self.groupBox, 0, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(PlotPropertiesUI)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.txtLegend = QLineEdit(PlotPropertiesUI)
        self.txtLegend.setObjectName(u"txtLegend")

        self.horizontalLayout.addWidget(self.txtLegend)


        self.gridLayout_3.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 120, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer, 2, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(PlotPropertiesUI)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.gridLayout_3.addWidget(self.buttonBox, 3, 0, 1, 1)


        self.retranslateUi(PlotPropertiesUI)
        self.buttonBox.accepted.connect(PlotPropertiesUI.accept)
        self.buttonBox.rejected.connect(PlotPropertiesUI.reject)

        QMetaObject.connectSlotsByName(PlotPropertiesUI)
    # setupUi

    def retranslateUi(self, PlotPropertiesUI):
        PlotPropertiesUI.setWindowTitle(QCoreApplication.translate("PlotPropertiesUI", u"Modify Plot Properties", None))
        self.groupBox.setTitle(QCoreApplication.translate("PlotPropertiesUI", u"Symbol", None))
        self.label_2.setText(QCoreApplication.translate("PlotPropertiesUI", u"Shape", None))
        self.label_4.setText(QCoreApplication.translate("PlotPropertiesUI", u"Size", None))
        self.label_3.setText(QCoreApplication.translate("PlotPropertiesUI", u"Color", None))
        self.cmdCustom.setText(QCoreApplication.translate("PlotPropertiesUI", u"Custom..", None))
        self.label.setText(QCoreApplication.translate("PlotPropertiesUI", u"Legend Label", None))
    # retranslateUi

