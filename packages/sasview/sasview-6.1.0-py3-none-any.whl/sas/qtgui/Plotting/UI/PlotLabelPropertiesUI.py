# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PlotLabelPropertiesUI.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QComboBox,
    QDialog, QDialogButtonBox, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QSpinBox, QWidget)

class Ui_PlotLabelPropertiesUI(object):
    def setupUi(self, PlotLabelPropertiesUI):
        if not PlotLabelPropertiesUI.objectName():
            PlotLabelPropertiesUI.setObjectName(u"PlotLabelPropertiesUI")
        PlotLabelPropertiesUI.resize(341, 505)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(PlotLabelPropertiesUI.sizePolicy().hasHeightForWidth())
        PlotLabelPropertiesUI.setSizePolicy(sizePolicy)
        icon = QIcon()
        icon.addFile(u":/res/ball.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        PlotLabelPropertiesUI.setWindowIcon(icon)
        self.gridLayout_3 = QGridLayout(PlotLabelPropertiesUI)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.groupBox = QGroupBox(PlotLabelPropertiesUI)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)

        self.cbFont = QComboBox(self.groupBox)
        self.cbFont.setObjectName(u"cbFont")

        self.gridLayout.addWidget(self.cbFont, 0, 1, 1, 2)

        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 0, 3, 1, 1)

        self.cbWeight = QComboBox(self.groupBox)
        self.cbWeight.setObjectName(u"cbWeight")

        self.gridLayout.addWidget(self.cbWeight, 0, 4, 1, 3)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)

        self.cbColor = QComboBox(self.groupBox)
        self.cbColor.setObjectName(u"cbColor")

        self.gridLayout.addWidget(self.cbColor, 1, 1, 1, 1)

        self.cmdCustom = QPushButton(self.groupBox)
        self.cmdCustom.setObjectName(u"cmdCustom")

        self.gridLayout.addWidget(self.cmdCustom, 1, 2, 1, 3)

        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 1, 5, 1, 1)

        self.cbSize = QSpinBox(self.groupBox)
        self.cbSize.setObjectName(u"cbSize")
        self.cbSize.setMinimum(1)
        self.cbSize.setMaximum(72)

        self.gridLayout.addWidget(self.cbSize, 1, 6, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.txtLegend = QLineEdit(self.groupBox)
        self.txtLegend.setObjectName(u"txtLegend")

        self.horizontalLayout.addWidget(self.txtLegend)


        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 7)

        self.chkTicks = QCheckBox(self.groupBox)
        self.chkTicks.setObjectName(u"chkTicks")

        self.gridLayout.addWidget(self.chkTicks, 3, 0, 1, 4)


        self.gridLayout_3.addWidget(self.groupBox, 0, 0, 1, 1)

        self.groupBox_2 = QGroupBox(PlotLabelPropertiesUI)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_2 = QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_6 = QLabel(self.groupBox_2)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_2.addWidget(self.label_6, 0, 0, 1, 1)

        self.cbFont_y = QComboBox(self.groupBox_2)
        self.cbFont_y.setObjectName(u"cbFont_y")

        self.gridLayout_2.addWidget(self.cbFont_y, 0, 1, 1, 2)

        self.label_7 = QLabel(self.groupBox_2)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_2.addWidget(self.label_7, 0, 3, 1, 1)

        self.cbWeight_y = QComboBox(self.groupBox_2)
        self.cbWeight_y.setObjectName(u"cbWeight_y")

        self.gridLayout_2.addWidget(self.cbWeight_y, 0, 4, 1, 3)

        self.label_8 = QLabel(self.groupBox_2)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_2.addWidget(self.label_8, 1, 0, 1, 1)

        self.cbColor_y = QComboBox(self.groupBox_2)
        self.cbColor_y.setObjectName(u"cbColor_y")

        self.gridLayout_2.addWidget(self.cbColor_y, 1, 1, 1, 1)

        self.cmdCustom_y = QPushButton(self.groupBox_2)
        self.cmdCustom_y.setObjectName(u"cmdCustom_y")

        self.gridLayout_2.addWidget(self.cmdCustom_y, 1, 2, 1, 3)

        self.label_9 = QLabel(self.groupBox_2)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_2.addWidget(self.label_9, 1, 5, 1, 1)

        self.cbSize_y = QSpinBox(self.groupBox_2)
        self.cbSize_y.setObjectName(u"cbSize_y")
        self.cbSize_y.setMinimum(1)
        self.cbSize_y.setMaximum(72)

        self.gridLayout_2.addWidget(self.cbSize_y, 1, 6, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_10 = QLabel(self.groupBox_2)
        self.label_10.setObjectName(u"label_10")

        self.horizontalLayout_2.addWidget(self.label_10)

        self.txtLegend_y = QLineEdit(self.groupBox_2)
        self.txtLegend_y.setObjectName(u"txtLegend_y")

        self.horizontalLayout_2.addWidget(self.txtLegend_y)


        self.gridLayout_2.addLayout(self.horizontalLayout_2, 2, 0, 1, 7)

        self.chkTicks_y = QCheckBox(self.groupBox_2)
        self.chkTicks_y.setObjectName(u"chkTicks_y")

        self.gridLayout_2.addWidget(self.chkTicks_y, 3, 0, 1, 4)


        self.gridLayout_3.addWidget(self.groupBox_2, 1, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 120, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer, 2, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(PlotLabelPropertiesUI)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.gridLayout_3.addWidget(self.buttonBox, 3, 0, 1, 1)

        QWidget.setTabOrder(self.cbFont, self.cbWeight)
        QWidget.setTabOrder(self.cbWeight, self.cbColor)
        QWidget.setTabOrder(self.cbColor, self.cmdCustom)
        QWidget.setTabOrder(self.cmdCustom, self.cbSize)
        QWidget.setTabOrder(self.cbSize, self.txtLegend)
        QWidget.setTabOrder(self.txtLegend, self.chkTicks)
        QWidget.setTabOrder(self.chkTicks, self.cbFont_y)
        QWidget.setTabOrder(self.cbFont_y, self.cbWeight_y)
        QWidget.setTabOrder(self.cbWeight_y, self.cbColor_y)
        QWidget.setTabOrder(self.cbColor_y, self.cmdCustom_y)
        QWidget.setTabOrder(self.cmdCustom_y, self.cbSize_y)
        QWidget.setTabOrder(self.cbSize_y, self.txtLegend_y)
        QWidget.setTabOrder(self.txtLegend_y, self.chkTicks_y)

        self.retranslateUi(PlotLabelPropertiesUI)
        self.buttonBox.accepted.connect(PlotLabelPropertiesUI.accept)
        self.buttonBox.rejected.connect(PlotLabelPropertiesUI.reject)

        QMetaObject.connectSlotsByName(PlotLabelPropertiesUI)
    # setupUi

    def retranslateUi(self, PlotLabelPropertiesUI):
        PlotLabelPropertiesUI.setWindowTitle(QCoreApplication.translate("PlotLabelPropertiesUI", u"Modify Label Properties", None))
        self.groupBox.setTitle(QCoreApplication.translate("PlotLabelPropertiesUI", u"X Label", None))
        self.label_2.setText(QCoreApplication.translate("PlotLabelPropertiesUI", u"Family", None))
        self.label_5.setText(QCoreApplication.translate("PlotLabelPropertiesUI", u"Weight", None))
        self.label_3.setText(QCoreApplication.translate("PlotLabelPropertiesUI", u"Color", None))
        self.cmdCustom.setText(QCoreApplication.translate("PlotLabelPropertiesUI", u"Custom..", None))
        self.label_4.setText(QCoreApplication.translate("PlotLabelPropertiesUI", u"Size", None))
        self.label.setText(QCoreApplication.translate("PlotLabelPropertiesUI", u"Legend Label", None))
        self.chkTicks.setText(QCoreApplication.translate("PlotLabelPropertiesUI", u"Apply style to X tick labels", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("PlotLabelPropertiesUI", u"Y Label", None))
        self.label_6.setText(QCoreApplication.translate("PlotLabelPropertiesUI", u"Family", None))
        self.label_7.setText(QCoreApplication.translate("PlotLabelPropertiesUI", u"Weight", None))
        self.label_8.setText(QCoreApplication.translate("PlotLabelPropertiesUI", u"Color", None))
        self.cmdCustom_y.setText(QCoreApplication.translate("PlotLabelPropertiesUI", u"Custom..", None))
        self.label_9.setText(QCoreApplication.translate("PlotLabelPropertiesUI", u"Size", None))
        self.label_10.setText(QCoreApplication.translate("PlotLabelPropertiesUI", u"Legend Label", None))
        self.chkTicks_y.setText(QCoreApplication.translate("PlotLabelPropertiesUI", u"Apply style to Y tick labels", None))
    # retranslateUi

