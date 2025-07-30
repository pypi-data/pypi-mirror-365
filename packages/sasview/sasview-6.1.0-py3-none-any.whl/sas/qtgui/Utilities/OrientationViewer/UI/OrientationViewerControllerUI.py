# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'OrientationViewerControllerUI.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QSizePolicy,
    QSlider, QSpacerItem, QWidget)

class Ui_OrientationViewierControllerUI(object):
    def setupUi(self, OrientationViewierControllerUI):
        if not OrientationViewierControllerUI.objectName():
            OrientationViewierControllerUI.setObjectName(u"OrientationViewierControllerUI")
        OrientationViewierControllerUI.resize(664, 250)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(OrientationViewierControllerUI.sizePolicy().hasHeightForWidth())
        OrientationViewierControllerUI.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(OrientationViewierControllerUI)
        self.gridLayout.setObjectName(u"gridLayout")
        self.deltaPhi = QSlider(OrientationViewierControllerUI)
        self.deltaPhi.setObjectName(u"deltaPhi")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.deltaPhi.sizePolicy().hasHeightForWidth())
        self.deltaPhi.setSizePolicy(sizePolicy1)
        self.deltaPhi.setMinimumSize(QSize(50, 0))
        self.deltaPhi.setMaximumSize(QSize(100, 16777215))
        self.deltaPhi.setMaximum(60)
        self.deltaPhi.setOrientation(Qt.Horizontal)
        self.deltaPhi.setTickPosition(QSlider.TicksBothSides)
        self.deltaPhi.setTickInterval(15)

        self.gridLayout.addWidget(self.deltaPhi, 2, 4, 1, 1)

        self.deltaPsi = QSlider(OrientationViewierControllerUI)
        self.deltaPsi.setObjectName(u"deltaPsi")
        sizePolicy1.setHeightForWidth(self.deltaPsi.sizePolicy().hasHeightForWidth())
        self.deltaPsi.setSizePolicy(sizePolicy1)
        self.deltaPsi.setMinimumSize(QSize(50, 0))
        self.deltaPsi.setMaximumSize(QSize(100, 16777215))
        self.deltaPsi.setMaximum(60)
        self.deltaPsi.setOrientation(Qt.Horizontal)
        self.deltaPsi.setTickPosition(QSlider.TicksBothSides)
        self.deltaPsi.setTickInterval(15)

        self.gridLayout.addWidget(self.deltaPsi, 4, 4, 1, 1)

        self.psiNumber = QLabel(OrientationViewierControllerUI)
        self.psiNumber.setObjectName(u"psiNumber")
        font = QFont()
        font.setPointSize(10)
        self.psiNumber.setFont(font)
        self.psiNumber.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.psiNumber, 5, 2, 1, 1)

        self.deltaPhiNumber = QLabel(OrientationViewierControllerUI)
        self.deltaPhiNumber.setObjectName(u"deltaPhiNumber")
        self.deltaPhiNumber.setFont(font)
        self.deltaPhiNumber.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.deltaPhiNumber, 3, 4, 1, 1)

        self.deltaPsiNumber = QLabel(OrientationViewierControllerUI)
        self.deltaPsiNumber.setObjectName(u"deltaPsiNumber")
        self.deltaPsiNumber.setFont(font)
        self.deltaPsiNumber.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.deltaPsiNumber, 5, 4, 1, 1)

        self.phiNumber = QLabel(OrientationViewierControllerUI)
        self.phiNumber.setObjectName(u"phiNumber")
        self.phiNumber.setFont(font)
        self.phiNumber.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.phiNumber, 3, 2, 1, 1)

        self.thetaNumber = QLabel(OrientationViewierControllerUI)
        self.thetaNumber.setObjectName(u"thetaNumber")
        self.thetaNumber.setFont(font)
        self.thetaNumber.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.thetaNumber, 1, 2, 1, 1)

        self.deltaTheta = QSlider(OrientationViewierControllerUI)
        self.deltaTheta.setObjectName(u"deltaTheta")
        sizePolicy1.setHeightForWidth(self.deltaTheta.sizePolicy().hasHeightForWidth())
        self.deltaTheta.setSizePolicy(sizePolicy1)
        self.deltaTheta.setMinimumSize(QSize(50, 0))
        self.deltaTheta.setMaximumSize(QSize(100, 16777215))
        self.deltaTheta.setMaximum(60)
        self.deltaTheta.setOrientation(Qt.Horizontal)
        self.deltaTheta.setTickPosition(QSlider.TicksBothSides)
        self.deltaTheta.setTickInterval(15)

        self.gridLayout.addWidget(self.deltaTheta, 0, 4, 1, 1)

        self.deltaThetaNumber = QLabel(OrientationViewierControllerUI)
        self.deltaThetaNumber.setObjectName(u"deltaThetaNumber")
        self.deltaThetaNumber.setFont(font)
        self.deltaThetaNumber.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.deltaThetaNumber, 1, 4, 1, 1)

        self.deltaThetaLabel = QLabel(OrientationViewierControllerUI)
        self.deltaThetaLabel.setObjectName(u"deltaThetaLabel")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.deltaThetaLabel.sizePolicy().hasHeightForWidth())
        self.deltaThetaLabel.setSizePolicy(sizePolicy2)
        self.deltaThetaLabel.setMinimumSize(QSize(30, 0))
        self.deltaThetaLabel.setMaximumSize(QSize(30, 16777215))
        font1 = QFont()
        font1.setPointSize(11)
        self.deltaThetaLabel.setFont(font1)
        self.deltaThetaLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.deltaThetaLabel, 0, 3, 1, 1)

        self.deltaPhiLabel = QLabel(OrientationViewierControllerUI)
        self.deltaPhiLabel.setObjectName(u"deltaPhiLabel")
        sizePolicy2.setHeightForWidth(self.deltaPhiLabel.sizePolicy().hasHeightForWidth())
        self.deltaPhiLabel.setSizePolicy(sizePolicy2)
        self.deltaPhiLabel.setMinimumSize(QSize(30, 0))
        self.deltaPhiLabel.setMaximumSize(QSize(30, 16777215))
        self.deltaPhiLabel.setFont(font1)
        self.deltaPhiLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.deltaPhiLabel, 2, 3, 1, 1)

        self.psiSlider = QSlider(OrientationViewierControllerUI)
        self.psiSlider.setObjectName(u"psiSlider")
        self.psiSlider.setMinimumSize(QSize(400, 0))
        self.psiSlider.setMaximumSize(QSize(400, 16777215))
        self.psiSlider.setMinimum(-180)
        self.psiSlider.setMaximum(180)
        self.psiSlider.setSingleStep(1)
        self.psiSlider.setPageStep(15)
        self.psiSlider.setOrientation(Qt.Horizontal)
        self.psiSlider.setTickPosition(QSlider.TicksBothSides)
        self.psiSlider.setTickInterval(15)

        self.gridLayout.addWidget(self.psiSlider, 4, 2, 1, 1)

        self.psiLabel = QLabel(OrientationViewierControllerUI)
        self.psiLabel.setObjectName(u"psiLabel")
        sizePolicy2.setHeightForWidth(self.psiLabel.sizePolicy().hasHeightForWidth())
        self.psiLabel.setSizePolicy(sizePolicy2)
        self.psiLabel.setMinimumSize(QSize(20, 0))
        self.psiLabel.setMaximumSize(QSize(20, 16777215))
        self.psiLabel.setFont(font1)

        self.gridLayout.addWidget(self.psiLabel, 4, 1, 1, 1)

        self.phiLabel = QLabel(OrientationViewierControllerUI)
        self.phiLabel.setObjectName(u"phiLabel")
        sizePolicy2.setHeightForWidth(self.phiLabel.sizePolicy().hasHeightForWidth())
        self.phiLabel.setSizePolicy(sizePolicy2)
        self.phiLabel.setMinimumSize(QSize(20, 0))
        self.phiLabel.setMaximumSize(QSize(20, 16777215))
        self.phiLabel.setFont(font1)

        self.gridLayout.addWidget(self.phiLabel, 2, 1, 1, 1)

        self.phiSlider = QSlider(OrientationViewierControllerUI)
        self.phiSlider.setObjectName(u"phiSlider")
        self.phiSlider.setMinimumSize(QSize(400, 0))
        self.phiSlider.setMaximumSize(QSize(400, 16777215))
        self.phiSlider.setMinimum(-180)
        self.phiSlider.setMaximum(180)
        self.phiSlider.setPageStep(15)
        self.phiSlider.setOrientation(Qt.Horizontal)
        self.phiSlider.setTickPosition(QSlider.TicksBothSides)
        self.phiSlider.setTickInterval(15)

        self.gridLayout.addWidget(self.phiSlider, 2, 2, 1, 1)

        self.thetaSlider = QSlider(OrientationViewierControllerUI)
        self.thetaSlider.setObjectName(u"thetaSlider")
        self.thetaSlider.setMinimumSize(QSize(400, 0))
        self.thetaSlider.setMaximumSize(QSize(400, 16777215))
        self.thetaSlider.setMinimum(-90)
        self.thetaSlider.setMaximum(90)
        self.thetaSlider.setPageStep(15)
        self.thetaSlider.setOrientation(Qt.Horizontal)
        self.thetaSlider.setTickPosition(QSlider.TicksBothSides)
        self.thetaSlider.setTickInterval(15)

        self.gridLayout.addWidget(self.thetaSlider, 0, 2, 1, 1)

        self.deltaPsiLabel = QLabel(OrientationViewierControllerUI)
        self.deltaPsiLabel.setObjectName(u"deltaPsiLabel")
        sizePolicy2.setHeightForWidth(self.deltaPsiLabel.sizePolicy().hasHeightForWidth())
        self.deltaPsiLabel.setSizePolicy(sizePolicy2)
        self.deltaPsiLabel.setMinimumSize(QSize(30, 0))
        self.deltaPsiLabel.setMaximumSize(QSize(30, 16777215))
        self.deltaPsiLabel.setFont(font1)
        self.deltaPsiLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.deltaPsiLabel, 4, 3, 1, 1)

        self.thetaLabel = QLabel(OrientationViewierControllerUI)
        self.thetaLabel.setObjectName(u"thetaLabel")
        sizePolicy2.setHeightForWidth(self.thetaLabel.sizePolicy().hasHeightForWidth())
        self.thetaLabel.setSizePolicy(sizePolicy2)
        self.thetaLabel.setMinimumSize(QSize(20, 0))
        self.thetaLabel.setMaximumSize(QSize(20, 16777215))
        self.thetaLabel.setFont(font1)

        self.gridLayout.addWidget(self.thetaLabel, 0, 1, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 2, 0, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 2, 5, 1, 1)


        self.retranslateUi(OrientationViewierControllerUI)

        QMetaObject.connectSlotsByName(OrientationViewierControllerUI)
    # setupUi

    def retranslateUi(self, OrientationViewierControllerUI):
        OrientationViewierControllerUI.setWindowTitle(QCoreApplication.translate("OrientationViewierControllerUI", u"Form", None))
        self.psiNumber.setText(QCoreApplication.translate("OrientationViewierControllerUI", u"TextLabel", None))
        self.deltaPhiNumber.setText(QCoreApplication.translate("OrientationViewierControllerUI", u"TextLabel", None))
        self.deltaPsiNumber.setText(QCoreApplication.translate("OrientationViewierControllerUI", u"TextLabel", None))
        self.phiNumber.setText(QCoreApplication.translate("OrientationViewierControllerUI", u"TextLabel", None))
        self.thetaNumber.setText(QCoreApplication.translate("OrientationViewierControllerUI", u"TextLabel", None))
        self.deltaThetaNumber.setText(QCoreApplication.translate("OrientationViewierControllerUI", u"TextLabel", None))
        self.deltaThetaLabel.setText(QCoreApplication.translate("OrientationViewierControllerUI", u"\u0394\u03b8", None))
        self.deltaPhiLabel.setText(QCoreApplication.translate("OrientationViewierControllerUI", u"\u0394\u03c6", None))
        self.psiLabel.setText(QCoreApplication.translate("OrientationViewierControllerUI", u"\u03c8", None))
        self.phiLabel.setText(QCoreApplication.translate("OrientationViewierControllerUI", u"\u03c6", None))
        self.deltaPsiLabel.setText(QCoreApplication.translate("OrientationViewierControllerUI", u"\u0394\u03c8", None))
        self.thetaLabel.setText(QCoreApplication.translate("OrientationViewierControllerUI", u"\u03b8", None))
    # retranslateUi

