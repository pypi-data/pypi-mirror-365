# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ColorMapUI.ui'
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
    QHBoxLayout, QLabel, QLineEdit, QSizePolicy,
    QSpacerItem, QWidget)

class Ui_ColorMapUI(object):
    def setupUi(self, ColorMapUI):
        if not ColorMapUI.objectName():
            ColorMapUI.setObjectName(u"ColorMapUI")
        ColorMapUI.resize(450, 329)
        icon = QIcon()
        icon.addFile(u":/res/ball.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        ColorMapUI.setWindowIcon(icon)
        ColorMapUI.setModal(True)
        self.gridLayout_5 = QGridLayout(ColorMapUI)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.verticalSpacer = QSpacerItem(20, 62, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_5.addItem(self.verticalSpacer, 1, 1, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.buttonBox = QDialogButtonBox(ColorMapUI)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Apply|QDialogButtonBox.Cancel|QDialogButtonBox.Ok|QDialogButtonBox.Reset)

        self.horizontalLayout_2.addWidget(self.buttonBox)


        self.gridLayout_5.addLayout(self.horizontalLayout_2, 3, 0, 1, 3)

        self.groupBox = QGroupBox(ColorMapUI)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.cbColorMap = QComboBox(self.groupBox)
        self.cbColorMap.setObjectName(u"cbColorMap")

        self.horizontalLayout.addWidget(self.cbColorMap)


        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)

        self.txtMinAmplitude = QLineEdit(self.groupBox)
        self.txtMinAmplitude.setObjectName(u"txtMinAmplitude")

        self.gridLayout.addWidget(self.txtMinAmplitude, 0, 1, 1, 1)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)

        self.txtMaxAmplitude = QLineEdit(self.groupBox)
        self.txtMaxAmplitude.setObjectName(u"txtMaxAmplitude")

        self.gridLayout.addWidget(self.txtMaxAmplitude, 1, 1, 1, 1)


        self.gridLayout_2.addLayout(self.gridLayout, 1, 0, 1, 1)

        self.chkReverse = QCheckBox(self.groupBox)
        self.chkReverse.setObjectName(u"chkReverse")

        self.gridLayout_2.addWidget(self.chkReverse, 2, 0, 1, 1)


        self.gridLayout_5.addWidget(self.groupBox, 0, 0, 1, 2)

        self.groupBox_2 = QGroupBox(ColorMapUI)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_4 = QGridLayout(self.groupBox_2)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label_4 = QLabel(self.groupBox_2)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_3.addWidget(self.label_4, 0, 0, 1, 1)

        self.lblWidth = QLabel(self.groupBox_2)
        self.lblWidth.setObjectName(u"lblWidth")

        self.gridLayout_3.addWidget(self.lblWidth, 0, 1, 1, 1)

        self.label_5 = QLabel(self.groupBox_2)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_3.addWidget(self.label_5, 1, 0, 1, 1)

        self.lblHeight = QLabel(self.groupBox_2)
        self.lblHeight.setObjectName(u"lblHeight")

        self.gridLayout_3.addWidget(self.lblHeight, 1, 1, 1, 1)

        self.label_6 = QLabel(self.groupBox_2)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_3.addWidget(self.label_6, 2, 0, 1, 1)

        self.lblQmax = QLabel(self.groupBox_2)
        self.lblQmax.setObjectName(u"lblQmax")

        self.gridLayout_3.addWidget(self.lblQmax, 2, 1, 1, 1)

        self.label_7 = QLabel(self.groupBox_2)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_3.addWidget(self.label_7, 3, 0, 1, 1)

        self.lblStopRadius = QLabel(self.groupBox_2)
        self.lblStopRadius.setObjectName(u"lblStopRadius")

        self.gridLayout_3.addWidget(self.lblStopRadius, 3, 1, 1, 1)


        self.gridLayout_4.addLayout(self.gridLayout_3, 0, 0, 1, 1)


        self.gridLayout_5.addWidget(self.groupBox_2, 0, 2, 1, 1)

        self.widget = QWidget(ColorMapUI)
        self.widget.setObjectName(u"widget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)

        self.gridLayout_5.addWidget(self.widget, 2, 0, 1, 3)

        self.groupBox.raise_()
        self.widget.raise_()
        self.groupBox_2.raise_()
        QWidget.setTabOrder(self.cbColorMap, self.txtMinAmplitude)
        QWidget.setTabOrder(self.txtMinAmplitude, self.txtMaxAmplitude)
        QWidget.setTabOrder(self.txtMaxAmplitude, self.chkReverse)

        self.retranslateUi(ColorMapUI)
        self.buttonBox.accepted.connect(ColorMapUI.accept)
        self.buttonBox.rejected.connect(ColorMapUI.reject)

        QMetaObject.connectSlotsByName(ColorMapUI)
    # setupUi

    def retranslateUi(self, ColorMapUI):
        ColorMapUI.setWindowTitle(QCoreApplication.translate("ColorMapUI", u"Color Map", None))
        self.groupBox.setTitle(QCoreApplication.translate("ColorMapUI", u"Color map", None))
        self.label.setText(QCoreApplication.translate("ColorMapUI", u"Select color map", None))
#if QT_CONFIG(tooltip)
        self.cbColorMap.setToolTip(QCoreApplication.translate("ColorMapUI", u"<html><head/><body><p>Select color map from the list.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.label_2.setToolTip(QCoreApplication.translate("ColorMapUI", u"<html><head/><body><p>Enter value for minimum color map amplitude.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_2.setText(QCoreApplication.translate("ColorMapUI", u"Min amplitude for color map", None))
#if QT_CONFIG(tooltip)
        self.txtMinAmplitude.setToolTip(QCoreApplication.translate("ColorMapUI", u"<html><head/><body><p>Enter value for minimum color map amplitude.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.label_3.setToolTip(QCoreApplication.translate("ColorMapUI", u"<html><head/><body><p>Enter value for maximum color map amplitude.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_3.setText(QCoreApplication.translate("ColorMapUI", u"Max amplitude for color map", None))
#if QT_CONFIG(tooltip)
        self.txtMaxAmplitude.setToolTip(QCoreApplication.translate("ColorMapUI", u"<html><head/><body><p>Enter value for maximum color map amplitude.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.chkReverse.setToolTip(QCoreApplication.translate("ColorMapUI", u"<html><head/><body><p>Use the color-reversed map.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.chkReverse.setText(QCoreApplication.translate("ColorMapUI", u"Reverse map", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("ColorMapUI", u"Detector", None))
#if QT_CONFIG(tooltip)
        self.label_4.setToolTip(QCoreApplication.translate("ColorMapUI", u"<html><head/><body><p>Detector width.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_4.setText(QCoreApplication.translate("ColorMapUI", u"Width in pixels", None))
        self.lblWidth.setText(QCoreApplication.translate("ColorMapUI", u"0", None))
#if QT_CONFIG(tooltip)
        self.label_5.setToolTip(QCoreApplication.translate("ColorMapUI", u"<html><head/><body><p>Detector height.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_5.setText(QCoreApplication.translate("ColorMapUI", u"Height in pixels", None))
        self.lblHeight.setText(QCoreApplication.translate("ColorMapUI", u"0", None))
#if QT_CONFIG(tooltip)
        self.label_6.setToolTip(QCoreApplication.translate("ColorMapUI", u"<html><head/><body><p>Maximum absolute Q<span style=\" vertical-align:sub;\">x,y</span> value.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_6.setText(QCoreApplication.translate("ColorMapUI", u"<html><head/><body><p>Q<span style=\" vertical-align:sub;\">max</span></p></body></html>", None))
        self.lblQmax.setText(QCoreApplication.translate("ColorMapUI", u"0", None))
#if QT_CONFIG(tooltip)
        self.label_7.setToolTip(QCoreApplication.translate("ColorMapUI", u"<html><head/><body><p>Minimum value of Q<span style=\" vertical-align:sub;\">x</span> in units of Q.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_7.setText(QCoreApplication.translate("ColorMapUI", u"Beam stop radius", None))
        self.lblStopRadius.setText(QCoreApplication.translate("ColorMapUI", u"TextLabel", None))
    # retranslateUi

