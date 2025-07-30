# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SlitSizeCalculator.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QWidget)

class Ui_SlitSizeCalculator(object):
    def setupUi(self, SlitSizeCalculator):
        if not SlitSizeCalculator.objectName():
            SlitSizeCalculator.setObjectName(u"SlitSizeCalculator")
        SlitSizeCalculator.resize(496, 253)
        icon = QIcon()
        icon.addFile(u":/res/ball.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        SlitSizeCalculator.setWindowIcon(icon)
        self.gridLayout_3 = QGridLayout(SlitSizeCalculator)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.groupBox = QGroupBox(SlitSizeCalculator)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.data_file = QLineEdit(self.groupBox)
        self.data_file.setObjectName(u"data_file")
        self.data_file.setMinimumSize(QSize(200, 21))
        self.data_file.setReadOnly(True)

        self.horizontalLayout.addWidget(self.data_file)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)


        self.gridLayout_3.addWidget(self.groupBox, 0, 0, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer_2, 2, 0, 1, 1)

        self.groupBox_2 = QGroupBox(SlitSizeCalculator)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_2 = QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_2.addWidget(self.label_3)

        self.slit_length_out = QLineEdit(self.groupBox_2)
        self.slit_length_out.setObjectName(u"slit_length_out")
        self.slit_length_out.setMinimumSize(QSize(110, 21))
        self.slit_length_out.setReadOnly(True)

        self.horizontalLayout_2.addWidget(self.slit_length_out)


        self.gridLayout_2.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_2 = QLabel(self.groupBox_2)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_3.addWidget(self.label_2)

        self.unit_out = QLineEdit(self.groupBox_2)
        self.unit_out.setObjectName(u"unit_out")
        self.unit_out.setMinimumSize(QSize(100, 21))
        self.unit_out.setReadOnly(True)

        self.horizontalLayout_3.addWidget(self.unit_out)


        self.gridLayout_2.addLayout(self.horizontalLayout_3, 0, 1, 1, 1)


        self.gridLayout_3.addWidget(self.groupBox_2, 1, 0, 1, 3)

        self.browseButton = QPushButton(SlitSizeCalculator)
        self.browseButton.setObjectName(u"browseButton")

        self.gridLayout_3.addWidget(self.browseButton, 0, 2, 1, 1)

        self.helpButton = QPushButton(SlitSizeCalculator)
        self.helpButton.setObjectName(u"helpButton")

        self.gridLayout_3.addWidget(self.helpButton, 4, 2, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer, 4, 0, 1, 1)

        self.closeButton = QPushButton(SlitSizeCalculator)
        self.closeButton.setObjectName(u"closeButton")

        self.gridLayout_3.addWidget(self.closeButton, 4, 1, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer_2, 0, 1, 1, 1)

        QWidget.setTabOrder(self.data_file, self.browseButton)
        QWidget.setTabOrder(self.browseButton, self.slit_length_out)
        QWidget.setTabOrder(self.slit_length_out, self.unit_out)
        QWidget.setTabOrder(self.unit_out, self.closeButton)
        QWidget.setTabOrder(self.closeButton, self.helpButton)

        self.retranslateUi(SlitSizeCalculator)

        QMetaObject.connectSlotsByName(SlitSizeCalculator)
    # setupUi

    def retranslateUi(self, SlitSizeCalculator):
        SlitSizeCalculator.setWindowTitle(QCoreApplication.translate("SlitSizeCalculator", u"Dialog", None))
#if QT_CONFIG(tooltip)
        SlitSizeCalculator.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.groupBox.setTitle(QCoreApplication.translate("SlitSizeCalculator", u"Input", None))
        self.label.setText(QCoreApplication.translate("SlitSizeCalculator", u"Data", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("SlitSizeCalculator", u"Output", None))
        self.label_3.setText(QCoreApplication.translate("SlitSizeCalculator", u"Slit Size (FWHM/2):", None))
        self.label_2.setText(QCoreApplication.translate("SlitSizeCalculator", u"Unit:", None))
#if QT_CONFIG(tooltip)
        self.browseButton.setToolTip(QCoreApplication.translate("SlitSizeCalculator", u"<html><head/><body><p>Compute the thickness or diameter.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.browseButton.setText(QCoreApplication.translate("SlitSizeCalculator", u"Browse", None))
#if QT_CONFIG(tooltip)
        self.helpButton.setToolTip(QCoreApplication.translate("SlitSizeCalculator", u"<html><head/><body><p>Help using the Kiessing fringe calculator.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.helpButton.setText(QCoreApplication.translate("SlitSizeCalculator", u"Help", None))
#if QT_CONFIG(tooltip)
        self.closeButton.setToolTip(QCoreApplication.translate("SlitSizeCalculator", u"<html><head/><body><p>Close this window.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.closeButton.setText(QCoreApplication.translate("SlitSizeCalculator", u"Close", None))
    # retranslateUi

