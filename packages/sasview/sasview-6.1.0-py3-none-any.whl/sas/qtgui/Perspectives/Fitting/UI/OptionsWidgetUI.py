# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'OptionsWidgetUI.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QRadioButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_tabOptions(object):
    def setupUi(self, tabOptions):
        if not tabOptions.objectName():
            tabOptions.setObjectName(u"tabOptions")
        tabOptions.resize(522, 455)
        self.gridLayout_23 = QGridLayout(tabOptions)
        self.gridLayout_23.setObjectName(u"gridLayout_23")
        self.groupBox_4 = QGroupBox(tabOptions)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.gridLayout_11 = QGridLayout(self.groupBox_4)
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.gridLayout_13 = QGridLayout()
        self.gridLayout_13.setObjectName(u"gridLayout_13")
        self.label_9 = QLabel(self.groupBox_4)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_13.addWidget(self.label_9, 0, 0, 1, 1)

        self.txtMinRange = QLineEdit(self.groupBox_4)
        self.txtMinRange.setObjectName(u"txtMinRange")
        self.txtMinRange.setMinimumSize(QSize(80, 0))

        self.gridLayout_13.addWidget(self.txtMinRange, 0, 1, 1, 1)

        self.label_13 = QLabel(self.groupBox_4)
        self.label_13.setObjectName(u"label_13")

        self.gridLayout_13.addWidget(self.label_13, 0, 2, 1, 1)

        self.label_14 = QLabel(self.groupBox_4)
        self.label_14.setObjectName(u"label_14")

        self.gridLayout_13.addWidget(self.label_14, 1, 0, 1, 1)

        self.txtMaxRange = QLineEdit(self.groupBox_4)
        self.txtMaxRange.setObjectName(u"txtMaxRange")
        self.txtMaxRange.setMinimumSize(QSize(80, 0))

        self.gridLayout_13.addWidget(self.txtMaxRange, 1, 1, 1, 1)

        self.label_15 = QLabel(self.groupBox_4)
        self.label_15.setObjectName(u"label_15")

        self.gridLayout_13.addWidget(self.label_15, 1, 2, 1, 1)


        self.gridLayout_11.addLayout(self.gridLayout_13, 0, 0, 2, 1)

        self.horizontalSpacer_8 = QSpacerItem(217, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_11.addItem(self.horizontalSpacer_8, 0, 1, 2, 1)

        self.cmdReset = QPushButton(self.groupBox_4)
        self.cmdReset.setObjectName(u"cmdReset")

        self.gridLayout_11.addWidget(self.cmdReset, 0, 2, 1, 1)

        self.cmdMaskEdit = QPushButton(self.groupBox_4)
        self.cmdMaskEdit.setObjectName(u"cmdMaskEdit")

        self.gridLayout_11.addWidget(self.cmdMaskEdit, 1, 2, 1, 1)


        self.gridLayout_23.addWidget(self.groupBox_4, 0, 0, 1, 1)

        self.groupBox_5 = QGroupBox(tabOptions)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.gridLayout_14 = QGridLayout(self.groupBox_5)
        self.gridLayout_14.setObjectName(u"gridLayout_14")
        self.gridLayout_15 = QGridLayout()
        self.gridLayout_15.setObjectName(u"gridLayout_15")
        self.horizontalSpacer_9 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_15.addItem(self.horizontalSpacer_9, 1, 2, 1, 1)

        self.txtNpts = QLineEdit(self.groupBox_5)
        self.txtNpts.setObjectName(u"txtNpts")

        self.gridLayout_15.addWidget(self.txtNpts, 0, 1, 1, 1)

        self.label_22 = QLabel(self.groupBox_5)
        self.label_22.setObjectName(u"label_22")

        self.gridLayout_15.addWidget(self.label_22, 1, 0, 1, 1)

        self.txtNptsFit = QLineEdit(self.groupBox_5)
        self.txtNptsFit.setObjectName(u"txtNptsFit")
        self.txtNptsFit.setReadOnly(True)

        self.gridLayout_15.addWidget(self.txtNptsFit, 1, 1, 1, 1)

        self.chkLogData = QCheckBox(self.groupBox_5)
        self.chkLogData.setObjectName(u"chkLogData")
        self.chkLogData.setChecked(True)

        self.gridLayout_15.addWidget(self.chkLogData, 0, 2, 1, 1)

        self.label_21 = QLabel(self.groupBox_5)
        self.label_21.setObjectName(u"label_21")

        self.gridLayout_15.addWidget(self.label_21, 0, 0, 1, 1)


        self.gridLayout_14.addLayout(self.gridLayout_15, 0, 0, 1, 1)


        self.gridLayout_23.addWidget(self.groupBox_5, 1, 0, 1, 1)

        self.boxWeighting = QGroupBox(tabOptions)
        self.boxWeighting.setObjectName(u"boxWeighting")
        self.gridLayout_20 = QGridLayout(self.boxWeighting)
        self.gridLayout_20.setObjectName(u"gridLayout_20")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.rbWeighting1 = QRadioButton(self.boxWeighting)
        self.rbWeighting1.setObjectName(u"rbWeighting1")
        self.rbWeighting1.setChecked(True)

        self.verticalLayout.addWidget(self.rbWeighting1)

        self.rbWeighting2 = QRadioButton(self.boxWeighting)
        self.rbWeighting2.setObjectName(u"rbWeighting2")

        self.verticalLayout.addWidget(self.rbWeighting2)

        self.rbWeighting3 = QRadioButton(self.boxWeighting)
        self.rbWeighting3.setObjectName(u"rbWeighting3")

        self.verticalLayout.addWidget(self.rbWeighting3)

        self.rbWeighting4 = QRadioButton(self.boxWeighting)
        self.rbWeighting4.setObjectName(u"rbWeighting4")

        self.verticalLayout.addWidget(self.rbWeighting4)


        self.gridLayout_20.addLayout(self.verticalLayout, 0, 0, 1, 1)


        self.gridLayout_23.addWidget(self.boxWeighting, 2, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 312, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_23.addItem(self.verticalSpacer, 3, 0, 1, 1)

        QWidget.setTabOrder(self.txtMinRange, self.txtMaxRange)
        QWidget.setTabOrder(self.txtMaxRange, self.txtNpts)
        QWidget.setTabOrder(self.txtNpts, self.chkLogData)
        QWidget.setTabOrder(self.chkLogData, self.txtNptsFit)
        QWidget.setTabOrder(self.txtNptsFit, self.rbWeighting1)
        QWidget.setTabOrder(self.rbWeighting1, self.rbWeighting2)
        QWidget.setTabOrder(self.rbWeighting2, self.rbWeighting3)
        QWidget.setTabOrder(self.rbWeighting3, self.rbWeighting4)
        QWidget.setTabOrder(self.rbWeighting4, self.cmdReset)
        QWidget.setTabOrder(self.cmdReset, self.cmdMaskEdit)

        self.retranslateUi(tabOptions)

        QMetaObject.connectSlotsByName(tabOptions)
    # setupUi

    def retranslateUi(self, tabOptions):
        tabOptions.setWindowTitle(QCoreApplication.translate("tabOptions", u"Fit Options", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("tabOptions", u"Fitting range", None))
        self.label_9.setText(QCoreApplication.translate("tabOptions", u"Min range", None))
#if QT_CONFIG(tooltip)
        self.txtMinRange.setToolTip(QCoreApplication.translate("tabOptions", u"<html><head/><body><p>Minimum value of Q.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_13.setText(QCoreApplication.translate("tabOptions", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.label_14.setText(QCoreApplication.translate("tabOptions", u"Max range", None))
#if QT_CONFIG(tooltip)
        self.txtMaxRange.setToolTip(QCoreApplication.translate("tabOptions", u"<html><head/><body><p>Maximum value of Q.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_15.setText(QCoreApplication.translate("tabOptions", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.cmdReset.setToolTip(QCoreApplication.translate("tabOptions", u"<html><head/><body><p>Reset the Q range to the default.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cmdReset.setText(QCoreApplication.translate("tabOptions", u"Reset", None))
        self.cmdMaskEdit.setText(QCoreApplication.translate("tabOptions", u"Mask Editor", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("tabOptions", u"Data points", None))
#if QT_CONFIG(tooltip)
        self.txtNpts.setToolTip(QCoreApplication.translate("tabOptions", u"<html><head/><body><p>Total number of data points.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_22.setText(QCoreApplication.translate("tabOptions", u"Npts(Fit)", None))
#if QT_CONFIG(tooltip)
        self.txtNptsFit.setToolTip(QCoreApplication.translate("tabOptions", u"<html><head/><body><p>Number of points selected for fitting.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.chkLogData.setToolTip(QCoreApplication.translate("tabOptions", u"<html><head/><body><p>Check to use log spaced points.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.chkLogData.setText(QCoreApplication.translate("tabOptions", u"Log spaced points", None))
        self.label_21.setText(QCoreApplication.translate("tabOptions", u"Npts", None))
        self.boxWeighting.setTitle(QCoreApplication.translate("tabOptions", u"Weighting", None))
        self.rbWeighting1.setText(QCoreApplication.translate("tabOptions", u"None", None))
        self.rbWeighting2.setText(QCoreApplication.translate("tabOptions", u"Use dI Data", None))
        self.rbWeighting3.setText(QCoreApplication.translate("tabOptions", u"Use |sqrt(I Data)|", None))
        self.rbWeighting4.setText(QCoreApplication.translate("tabOptions", u"Use |I Data|", None))
    # retranslateUi

