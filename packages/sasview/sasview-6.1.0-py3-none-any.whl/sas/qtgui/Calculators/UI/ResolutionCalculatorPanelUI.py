# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ResolutionCalculatorPanelUI.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QFrame,
    QGraphicsView, QGridLayout, QGroupBox, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QSpacerItem,
    QWidget)

class Ui_ResolutionCalculatorPanel(object):
    def setupUi(self, ResolutionCalculatorPanel):
        if not ResolutionCalculatorPanel.objectName():
            ResolutionCalculatorPanel.setObjectName(u"ResolutionCalculatorPanel")
        ResolutionCalculatorPanel.setEnabled(True)
        ResolutionCalculatorPanel.resize(876, 540)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ResolutionCalculatorPanel.sizePolicy().hasHeightForWidth())
        ResolutionCalculatorPanel.setSizePolicy(sizePolicy)
        ResolutionCalculatorPanel.setMinimumSize(QSize(800, 540))
        ResolutionCalculatorPanel.setMaximumSize(QSize(1310, 667))
        icon = QIcon()
        icon.addFile(u":/res/ball.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        ResolutionCalculatorPanel.setWindowIcon(icon)
        self.gridLayout_7 = QGridLayout(ResolutionCalculatorPanel)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.groupBox = QGroupBox(ResolutionCalculatorPanel)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setMinimumSize(QSize(400, 0))
        self.groupBox.setMaximumSize(QSize(16777215, 350))
        self.gridLayout_6 = QGridLayout(self.groupBox)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.gridLayout_6.setContentsMargins(6, 6, 6, 6)
        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.label_26 = QLabel(self.groupBox)
        self.label_26.setObjectName(u"label_26")
        self.label_26.setMinimumSize(QSize(26, 17))

        self.gridLayout_5.addWidget(self.label_26, 0, 0, 1, 1)

        self.cbSource = QComboBox(self.groupBox)
        self.cbSource.addItem("")
        self.cbSource.addItem("")
        self.cbSource.addItem("")
        self.cbSource.addItem("")
        self.cbSource.addItem("")
        self.cbSource.addItem("")
        self.cbSource.setObjectName(u"cbSource")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.cbSource.sizePolicy().hasHeightForWidth())
        self.cbSource.setSizePolicy(sizePolicy1)
        self.cbSource.setMinimumSize(QSize(85, 26))

        self.gridLayout_5.addWidget(self.cbSource, 0, 1, 1, 1)

        self.cbWaveColor = QComboBox(self.groupBox)
        self.cbWaveColor.addItem("")
        self.cbWaveColor.addItem("")
        self.cbWaveColor.setObjectName(u"cbWaveColor")
        sizePolicy1.setHeightForWidth(self.cbWaveColor.sizePolicy().hasHeightForWidth())
        self.cbWaveColor.setSizePolicy(sizePolicy1)
        self.cbWaveColor.setMinimumSize(QSize(100, 26))
        self.cbWaveColor.setMaximumSize(QSize(150, 26))

        self.gridLayout_5.addWidget(self.cbWaveColor, 0, 2, 1, 2)

        self.lblSpectrum = QLabel(self.groupBox)
        self.lblSpectrum.setObjectName(u"lblSpectrum")
        self.lblSpectrum.setMinimumSize(QSize(70, 20))
        self.lblSpectrum.setBaseSize(QSize(80, 20))

        self.gridLayout_5.addWidget(self.lblSpectrum, 1, 1, 1, 1)

        self.cbCustomSpectrum = QComboBox(self.groupBox)
        self.cbCustomSpectrum.addItem("")
        self.cbCustomSpectrum.addItem("")
        self.cbCustomSpectrum.setObjectName(u"cbCustomSpectrum")
        sizePolicy1.setHeightForWidth(self.cbCustomSpectrum.sizePolicy().hasHeightForWidth())
        self.cbCustomSpectrum.setSizePolicy(sizePolicy1)
        self.cbCustomSpectrum.setMinimumSize(QSize(90, 26))
        self.cbCustomSpectrum.setMaximumSize(QSize(150, 26))

        self.gridLayout_5.addWidget(self.cbCustomSpectrum, 1, 2, 1, 2)

        self.label_27 = QLabel(self.groupBox)
        self.label_27.setObjectName(u"label_27")
        self.label_27.setMinimumSize(QSize(84, 20))

        self.gridLayout_5.addWidget(self.label_27, 2, 0, 1, 2)

        self.txtWavelength = QLineEdit(self.groupBox)
        self.txtWavelength.setObjectName(u"txtWavelength")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.txtWavelength.sizePolicy().hasHeightForWidth())
        self.txtWavelength.setSizePolicy(sizePolicy2)
        self.txtWavelength.setMinimumSize(QSize(100, 23))
        self.txtWavelength.setBaseSize(QSize(100, 20))
        self.txtWavelength.setFocusPolicy(Qt.StrongFocus)
        self.txtWavelength.setEchoMode(QLineEdit.Normal)

        self.gridLayout_5.addWidget(self.txtWavelength, 2, 3, 1, 1)

        self.lblUnitWavelength = QLabel(self.groupBox)
        self.lblUnitWavelength.setObjectName(u"lblUnitWavelength")
        self.lblUnitWavelength.setMinimumSize(QSize(22, 21))
        self.lblUnitWavelength.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout_5.addWidget(self.lblUnitWavelength, 2, 4, 1, 1)

        self.label_28 = QLabel(self.groupBox)
        self.label_28.setObjectName(u"label_28")
        self.label_28.setMinimumSize(QSize(134, 20))

        self.gridLayout_5.addWidget(self.label_28, 3, 0, 1, 2)

        self.txtWavelengthSpread = QLineEdit(self.groupBox)
        self.txtWavelengthSpread.setObjectName(u"txtWavelengthSpread")
        self.txtWavelengthSpread.setMinimumSize(QSize(100, 23))
        self.txtWavelengthSpread.setBaseSize(QSize(100, 20))
        self.txtWavelengthSpread.setFocusPolicy(Qt.StrongFocus)

        self.gridLayout_5.addWidget(self.txtWavelengthSpread, 3, 3, 1, 1)

        self.label_29 = QLabel(self.groupBox)
        self.label_29.setObjectName(u"label_29")
        self.label_29.setMinimumSize(QSize(143, 20))

        self.gridLayout_5.addWidget(self.label_29, 4, 0, 1, 2)

        self.txtSourceApertureSize = QLineEdit(self.groupBox)
        self.txtSourceApertureSize.setObjectName(u"txtSourceApertureSize")
        sizePolicy2.setHeightForWidth(self.txtSourceApertureSize.sizePolicy().hasHeightForWidth())
        self.txtSourceApertureSize.setSizePolicy(sizePolicy2)
        self.txtSourceApertureSize.setMinimumSize(QSize(100, 23))
        self.txtSourceApertureSize.setBaseSize(QSize(100, 20))
        self.txtSourceApertureSize.setFocusPolicy(Qt.StrongFocus)

        self.gridLayout_5.addWidget(self.txtSourceApertureSize, 4, 3, 1, 1)

        self.label_39 = QLabel(self.groupBox)
        self.label_39.setObjectName(u"label_39")
        self.label_39.setMinimumSize(QSize(22, 21))
        self.label_39.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout_5.addWidget(self.label_39, 4, 4, 1, 1)

        self.label_30 = QLabel(self.groupBox)
        self.label_30.setObjectName(u"label_30")
        self.label_30.setMinimumSize(QSize(147, 20))

        self.gridLayout_5.addWidget(self.label_30, 5, 0, 1, 2)

        self.txtSampleApertureSize = QLineEdit(self.groupBox)
        self.txtSampleApertureSize.setObjectName(u"txtSampleApertureSize")
        sizePolicy2.setHeightForWidth(self.txtSampleApertureSize.sizePolicy().hasHeightForWidth())
        self.txtSampleApertureSize.setSizePolicy(sizePolicy2)
        self.txtSampleApertureSize.setMinimumSize(QSize(100, 23))
        self.txtSampleApertureSize.setBaseSize(QSize(100, 20))
        self.txtSampleApertureSize.setFocusPolicy(Qt.StrongFocus)

        self.gridLayout_5.addWidget(self.txtSampleApertureSize, 5, 3, 1, 1)

        self.label_40 = QLabel(self.groupBox)
        self.label_40.setObjectName(u"label_40")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_40.sizePolicy().hasHeightForWidth())
        self.label_40.setSizePolicy(sizePolicy3)
        self.label_40.setMinimumSize(QSize(22, 21))

        self.gridLayout_5.addWidget(self.label_40, 5, 4, 1, 1)

        self.label_31 = QLabel(self.groupBox)
        self.label_31.setObjectName(u"label_31")
        self.label_31.setMinimumSize(QSize(220, 20))

        self.gridLayout_5.addWidget(self.label_31, 6, 0, 1, 3)

        self.txtSource2SampleDistance = QLineEdit(self.groupBox)
        self.txtSource2SampleDistance.setObjectName(u"txtSource2SampleDistance")
        sizePolicy2.setHeightForWidth(self.txtSource2SampleDistance.sizePolicy().hasHeightForWidth())
        self.txtSource2SampleDistance.setSizePolicy(sizePolicy2)
        self.txtSource2SampleDistance.setMinimumSize(QSize(100, 23))
        self.txtSource2SampleDistance.setBaseSize(QSize(100, 20))
        self.txtSource2SampleDistance.setFocusPolicy(Qt.StrongFocus)

        self.gridLayout_5.addWidget(self.txtSource2SampleDistance, 6, 3, 1, 1)

        self.label_41 = QLabel(self.groupBox)
        self.label_41.setObjectName(u"label_41")
        self.label_41.setMinimumSize(QSize(22, 21))

        self.gridLayout_5.addWidget(self.label_41, 6, 4, 1, 1)

        self.label_32 = QLabel(self.groupBox)
        self.label_32.setObjectName(u"label_32")
        self.label_32.setMinimumSize(QSize(225, 20))

        self.gridLayout_5.addWidget(self.label_32, 7, 0, 1, 3)

        self.txtSample2DetectorDistance = QLineEdit(self.groupBox)
        self.txtSample2DetectorDistance.setObjectName(u"txtSample2DetectorDistance")
        self.txtSample2DetectorDistance.setMinimumSize(QSize(100, 23))
        self.txtSample2DetectorDistance.setBaseSize(QSize(100, 20))

        self.gridLayout_5.addWidget(self.txtSample2DetectorDistance, 7, 3, 1, 1)

        self.label_42 = QLabel(self.groupBox)
        self.label_42.setObjectName(u"label_42")
        self.label_42.setMinimumSize(QSize(22, 21))

        self.gridLayout_5.addWidget(self.label_42, 7, 4, 1, 1)

        self.label_33 = QLabel(self.groupBox)
        self.label_33.setObjectName(u"label_33")
        self.label_33.setMinimumSize(QSize(100, 20))

        self.gridLayout_5.addWidget(self.label_33, 8, 0, 1, 2)

        self.txtSampleOffset = QLineEdit(self.groupBox)
        self.txtSampleOffset.setObjectName(u"txtSampleOffset")
        self.txtSampleOffset.setMinimumSize(QSize(100, 23))
        self.txtSampleOffset.setBaseSize(QSize(100, 20))

        self.gridLayout_5.addWidget(self.txtSampleOffset, 8, 3, 1, 1)

        self.label_43 = QLabel(self.groupBox)
        self.label_43.setObjectName(u"label_43")
        self.label_43.setMinimumSize(QSize(22, 21))

        self.gridLayout_5.addWidget(self.label_43, 8, 4, 1, 1)

        self.label_34 = QLabel(self.groupBox)
        self.label_34.setObjectName(u"label_34")
        self.label_34.setMinimumSize(QSize(175, 20))

        self.gridLayout_5.addWidget(self.label_34, 9, 0, 1, 3)

        self.txtDetectorSize = QLineEdit(self.groupBox)
        self.txtDetectorSize.setObjectName(u"txtDetectorSize")
        self.txtDetectorSize.setMinimumSize(QSize(100, 23))
        self.txtDetectorSize.setBaseSize(QSize(100, 20))

        self.gridLayout_5.addWidget(self.txtDetectorSize, 9, 3, 1, 1)

        self.label_35 = QLabel(self.groupBox)
        self.label_35.setObjectName(u"label_35")
        self.label_35.setMinimumSize(QSize(129, 20))

        self.gridLayout_5.addWidget(self.label_35, 10, 0, 1, 2)

        self.txtDetectorPixSize = QLineEdit(self.groupBox)
        self.txtDetectorPixSize.setObjectName(u"txtDetectorPixSize")
        self.txtDetectorPixSize.setMinimumSize(QSize(100, 23))
        self.txtDetectorPixSize.setBaseSize(QSize(100, 20))

        self.gridLayout_5.addWidget(self.txtDetectorPixSize, 10, 3, 1, 1)

        self.label_45 = QLabel(self.groupBox)
        self.label_45.setObjectName(u"label_45")
        self.label_45.setMinimumSize(QSize(22, 21))

        self.gridLayout_5.addWidget(self.label_45, 10, 4, 1, 1)


        self.gridLayout_6.addLayout(self.gridLayout_5, 0, 0, 1, 1)


        self.gridLayout_7.addWidget(self.groupBox, 0, 0, 1, 1)

        self.line_4 = QFrame(ResolutionCalculatorPanel)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.Shape.VLine)
        self.line_4.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_7.addWidget(self.line_4, 0, 1, 7, 1)

        self.graphicsView = QGraphicsView(ResolutionCalculatorPanel)
        self.graphicsView.setObjectName(u"graphicsView")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.graphicsView.sizePolicy().hasHeightForWidth())
        self.graphicsView.setSizePolicy(sizePolicy4)
        self.graphicsView.setMinimumSize(QSize(415, 415))
        self.graphicsView.setFocusPolicy(Qt.NoFocus)

        self.gridLayout_7.addWidget(self.graphicsView, 0, 2, 3, 1)

        self.line = QFrame(ResolutionCalculatorPanel)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_7.addWidget(self.line, 1, 0, 1, 1)

        self.groupBox_2 = QGroupBox(ResolutionCalculatorPanel)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setMinimumSize(QSize(400, 95))
        self.groupBox_2.setMaximumSize(QSize(450, 110))
        self.gridLayout_9 = QGridLayout(self.groupBox_2)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.gridLayout_9.setContentsMargins(6, 6, 6, 6)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_21 = QLabel(self.groupBox_2)
        self.label_21.setObjectName(u"label_21")
        self.label_21.setMinimumSize(QSize(21, 21))

        self.gridLayout.addWidget(self.label_21, 0, 0, 1, 1)

        self.txtQx = QLineEdit(self.groupBox_2)
        self.txtQx.setObjectName(u"txtQx")
        self.txtQx.setMinimumSize(QSize(100, 21))
        self.txtQx.setBaseSize(QSize(100, 21))

        self.gridLayout.addWidget(self.txtQx, 0, 1, 1, 1)

        self.lblUnitQx = QLabel(self.groupBox_2)
        self.lblUnitQx.setObjectName(u"lblUnitQx")
        self.lblUnitQx.setMinimumSize(QSize(18, 21))

        self.gridLayout.addWidget(self.lblUnitQx, 0, 2, 1, 1)

        self.label_22 = QLabel(self.groupBox_2)
        self.label_22.setObjectName(u"label_22")
        self.label_22.setMinimumSize(QSize(21, 21))

        self.gridLayout.addWidget(self.label_22, 1, 0, 1, 1)

        self.txtQy = QLineEdit(self.groupBox_2)
        self.txtQy.setObjectName(u"txtQy")
        self.txtQy.setMinimumSize(QSize(100, 21))
        self.txtQy.setBaseSize(QSize(100, 21))

        self.gridLayout.addWidget(self.txtQy, 1, 1, 1, 1)

        self.lblUnitQy = QLabel(self.groupBox_2)
        self.lblUnitQy.setObjectName(u"lblUnitQy")
        self.lblUnitQy.setMinimumSize(QSize(18, 21))

        self.gridLayout.addWidget(self.lblUnitQy, 1, 2, 1, 1)


        self.gridLayout_9.addLayout(self.gridLayout, 0, 0, 1, 1)


        self.gridLayout_7.addWidget(self.groupBox_2, 2, 0, 3, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_7.addItem(self.verticalSpacer_2, 3, 2, 1, 1)

        self.groupBox_3 = QGroupBox(ResolutionCalculatorPanel)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.gridLayout_4 = QGridLayout(self.groupBox_3)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(6, 6, 6, 6)
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.txtSigma_x = QLineEdit(self.groupBox_3)
        self.txtSigma_x.setObjectName(u"txtSigma_x")
        self.txtSigma_x.setEnabled(True)
        self.txtSigma_x.setMinimumSize(QSize(80, 23))
        self.txtSigma_x.setBaseSize(QSize(100, 21))
        self.txtSigma_x.setReadOnly(True)

        self.gridLayout_2.addWidget(self.txtSigma_x, 0, 1, 1, 1)

        self.txtSigma_y = QLineEdit(self.groupBox_3)
        self.txtSigma_y.setObjectName(u"txtSigma_y")
        self.txtSigma_y.setEnabled(True)
        self.txtSigma_y.setMinimumSize(QSize(80, 23))
        self.txtSigma_y.setBaseSize(QSize(100, 21))
        self.txtSigma_y.setReadOnly(True)

        self.gridLayout_2.addWidget(self.txtSigma_y, 0, 5, 1, 1)

        self.label_2 = QLabel(self.groupBox_3)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(87, 20))
        self.label_2.setBaseSize(QSize(87, 20))

        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)

        self.txtSigma_lamd = QLineEdit(self.groupBox_3)
        self.txtSigma_lamd.setObjectName(u"txtSigma_lamd")
        self.txtSigma_lamd.setEnabled(True)
        self.txtSigma_lamd.setMinimumSize(QSize(80, 23))
        self.txtSigma_lamd.setBaseSize(QSize(100, 21))
        self.txtSigma_lamd.setReadOnly(True)

        self.gridLayout_2.addWidget(self.txtSigma_lamd, 1, 1, 1, 1)

        self.txt1DSigma = QLineEdit(self.groupBox_3)
        self.txt1DSigma.setObjectName(u"txt1DSigma")
        self.txt1DSigma.setEnabled(True)
        self.txt1DSigma.setMinimumSize(QSize(80, 23))
        self.txt1DSigma.setBaseSize(QSize(100, 21))
        self.txt1DSigma.setReadOnly(True)

        self.gridLayout_2.addWidget(self.txt1DSigma, 1, 5, 1, 1)

        self.lblUnit1DSigma = QLabel(self.groupBox_3)
        self.lblUnit1DSigma.setObjectName(u"lblUnit1DSigma")
        self.lblUnit1DSigma.setMinimumSize(QSize(20, 21))

        self.gridLayout_2.addWidget(self.lblUnit1DSigma, 1, 6, 1, 1)

        self.lblUnitSigmalamd = QLabel(self.groupBox_3)
        self.lblUnitSigmalamd.setObjectName(u"lblUnitSigmalamd")
        self.lblUnitSigmalamd.setMinimumSize(QSize(20, 21))

        self.gridLayout_2.addWidget(self.lblUnitSigmalamd, 1, 2, 1, 1)

        self.label_6 = QLabel(self.groupBox_3)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setMinimumSize(QSize(87, 20))
        self.label_6.setBaseSize(QSize(87, 20))

        self.gridLayout_2.addWidget(self.label_6, 1, 4, 1, 1)

        self.label_5 = QLabel(self.groupBox_3)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMinimumSize(QSize(87, 20))
        self.label_5.setBaseSize(QSize(87, 20))

        self.gridLayout_2.addWidget(self.label_5, 0, 4, 1, 1)

        self.lblUnitSigmay = QLabel(self.groupBox_3)
        self.lblUnitSigmay.setObjectName(u"lblUnitSigmay")
        self.lblUnitSigmay.setMinimumSize(QSize(20, 21))

        self.gridLayout_2.addWidget(self.lblUnitSigmay, 0, 6, 1, 1)

        self.lblUnitSigmax = QLabel(self.groupBox_3)
        self.lblUnitSigmax.setObjectName(u"lblUnitSigmax")
        self.lblUnitSigmax.setMinimumSize(QSize(20, 21))

        self.gridLayout_2.addWidget(self.lblUnitSigmax, 0, 2, 1, 1)

        self.label = QLabel(self.groupBox_3)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(87, 20))
        self.label.setBaseSize(QSize(87, 20))

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer, 0, 3, 1, 1)


        self.gridLayout_4.addLayout(self.gridLayout_2, 0, 0, 1, 1)


        self.gridLayout_7.addWidget(self.groupBox_3, 4, 2, 3, 1)

        self.line_2 = QFrame(ResolutionCalculatorPanel)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_7.addWidget(self.line_2, 5, 0, 1, 1)

        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.cmdReset = QPushButton(ResolutionCalculatorPanel)
        self.cmdReset.setObjectName(u"cmdReset")
        self.cmdReset.setMinimumSize(QSize(75, 25))
        self.cmdReset.setAutoDefault(False)

        self.gridLayout_3.addWidget(self.cmdReset, 0, 1, 1, 1)

        self.cmdCompute = QPushButton(ResolutionCalculatorPanel)
        self.cmdCompute.setObjectName(u"cmdCompute")
        self.cmdCompute.setAutoDefault(False)

        self.gridLayout_3.addWidget(self.cmdCompute, 0, 2, 1, 1)

        self.cmdClose = QPushButton(ResolutionCalculatorPanel)
        self.cmdClose.setObjectName(u"cmdClose")
        self.cmdClose.setMinimumSize(QSize(75, 23))
        self.cmdClose.setAutoDefault(False)

        self.gridLayout_3.addWidget(self.cmdClose, 0, 3, 1, 1)

        self.cmdHelp = QPushButton(ResolutionCalculatorPanel)
        self.cmdHelp.setObjectName(u"cmdHelp")
        self.cmdHelp.setMinimumSize(QSize(75, 23))
        self.cmdHelp.setAutoDefault(False)

        self.gridLayout_3.addWidget(self.cmdHelp, 0, 4, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer_3, 0, 0, 1, 1)


        self.gridLayout_7.addLayout(self.gridLayout_3, 6, 0, 1, 1)

        self.groupBox.raise_()
        self.groupBox_2.raise_()
        self.groupBox_3.raise_()
        self.graphicsView.raise_()
        self.line_4.raise_()
        self.line.raise_()
        self.line_2.raise_()
        QWidget.setTabOrder(self.cbSource, self.cbWaveColor)
        QWidget.setTabOrder(self.cbWaveColor, self.cbCustomSpectrum)
        QWidget.setTabOrder(self.cbCustomSpectrum, self.txtWavelength)
        QWidget.setTabOrder(self.txtWavelength, self.txtWavelengthSpread)
        QWidget.setTabOrder(self.txtWavelengthSpread, self.txtSourceApertureSize)
        QWidget.setTabOrder(self.txtSourceApertureSize, self.txtSampleApertureSize)
        QWidget.setTabOrder(self.txtSampleApertureSize, self.txtSource2SampleDistance)
        QWidget.setTabOrder(self.txtSource2SampleDistance, self.txtSample2DetectorDistance)
        QWidget.setTabOrder(self.txtSample2DetectorDistance, self.txtSampleOffset)
        QWidget.setTabOrder(self.txtSampleOffset, self.txtDetectorSize)
        QWidget.setTabOrder(self.txtDetectorSize, self.txtDetectorPixSize)
        QWidget.setTabOrder(self.txtDetectorPixSize, self.graphicsView)
        QWidget.setTabOrder(self.graphicsView, self.txtQx)
        QWidget.setTabOrder(self.txtQx, self.txtQy)
        QWidget.setTabOrder(self.txtQy, self.txtSigma_x)
        QWidget.setTabOrder(self.txtSigma_x, self.txtSigma_y)
        QWidget.setTabOrder(self.txtSigma_y, self.txtSigma_lamd)
        QWidget.setTabOrder(self.txtSigma_lamd, self.txt1DSigma)
        QWidget.setTabOrder(self.txt1DSigma, self.cmdReset)
        QWidget.setTabOrder(self.cmdReset, self.cmdCompute)
        QWidget.setTabOrder(self.cmdCompute, self.cmdClose)
        QWidget.setTabOrder(self.cmdClose, self.cmdHelp)

        self.retranslateUi(ResolutionCalculatorPanel)

        self.cbSource.setCurrentIndex(2)


        QMetaObject.connectSlotsByName(ResolutionCalculatorPanel)
    # setupUi

    def retranslateUi(self, ResolutionCalculatorPanel):
        ResolutionCalculatorPanel.setWindowTitle(QCoreApplication.translate("ResolutionCalculatorPanel", u"Q Resolution Estimator", None))
        self.groupBox.setTitle(QCoreApplication.translate("ResolutionCalculatorPanel", u"Instrumental Parameters", None))
        self.label_26.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"Source:", None))
        self.cbSource.setItemText(0, QCoreApplication.translate("ResolutionCalculatorPanel", u"Alpha", None))
        self.cbSource.setItemText(1, QCoreApplication.translate("ResolutionCalculatorPanel", u"Deutron", None))
        self.cbSource.setItemText(2, QCoreApplication.translate("ResolutionCalculatorPanel", u"Neutron", None))
        self.cbSource.setItemText(3, QCoreApplication.translate("ResolutionCalculatorPanel", u"Photon", None))
        self.cbSource.setItemText(4, QCoreApplication.translate("ResolutionCalculatorPanel", u"Proton", None))
        self.cbSource.setItemText(5, QCoreApplication.translate("ResolutionCalculatorPanel", u"Triton", None))

#if QT_CONFIG(tooltip)
        self.cbSource.setToolTip(QCoreApplication.translate("ResolutionCalculatorPanel", u"Source Selection: Affect on the gravitational contribution.", None))
#endif // QT_CONFIG(tooltip)
        self.cbWaveColor.setItemText(0, QCoreApplication.translate("ResolutionCalculatorPanel", u"Monochromatic", None))
        self.cbWaveColor.setItemText(1, QCoreApplication.translate("ResolutionCalculatorPanel", u"TOF", None))

        self.lblSpectrum.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"Spectrum:", None))
        self.cbCustomSpectrum.setItemText(0, QCoreApplication.translate("ResolutionCalculatorPanel", u"Flat", None))
        self.cbCustomSpectrum.setItemText(1, QCoreApplication.translate("ResolutionCalculatorPanel", u"Add New", None))

#if QT_CONFIG(tooltip)
        self.cbCustomSpectrum.setToolTip(QCoreApplication.translate("ResolutionCalculatorPanel", u"Wavelength Spectrum: Intensity vs. wavelength.", None))
#endif // QT_CONFIG(tooltip)
        self.label_27.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"Wavelength:", None))
#if QT_CONFIG(tooltip)
        self.txtWavelength.setToolTip(QCoreApplication.translate("ResolutionCalculatorPanel", u"Wavelength of the Neutrons.", None))
#endif // QT_CONFIG(tooltip)
        self.txtWavelength.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"6.0", None))
        self.lblUnitWavelength.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"\u00c5", None))
        self.label_28.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"Wavelength Spread:", None))
#if QT_CONFIG(tooltip)
        self.txtWavelengthSpread.setToolTip(QCoreApplication.translate("ResolutionCalculatorPanel", u"Wavelength Spread of Neutrons.", None))
#endif // QT_CONFIG(tooltip)
        self.txtWavelengthSpread.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"0.125", None))
        self.label_29.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"Source Aperture Size:", None))
#if QT_CONFIG(tooltip)
        self.txtSourceApertureSize.setToolTip(QCoreApplication.translate("ResolutionCalculatorPanel", u"Source Aperture Size.", None))
#endif // QT_CONFIG(tooltip)
        self.txtSourceApertureSize.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"3.81", None))
        self.label_39.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"cm", None))
        self.label_30.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"Sample Aperture Size:", None))
#if QT_CONFIG(tooltip)
        self.txtSampleApertureSize.setToolTip(QCoreApplication.translate("ResolutionCalculatorPanel", u"Sample Aperture Size.", None))
#endif // QT_CONFIG(tooltip)
        self.txtSampleApertureSize.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"1.27", None))
        self.label_40.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"cm", None))
        self.label_31.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"Source to Sample Aperture Distance:", None))
#if QT_CONFIG(tooltip)
        self.txtSource2SampleDistance.setToolTip(QCoreApplication.translate("ResolutionCalculatorPanel", u"Source to Sample Aperture Distance.", None))
#endif // QT_CONFIG(tooltip)
        self.txtSource2SampleDistance.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"1627", None))
        self.label_41.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"cm", None))
        self.label_32.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"Sample Aperture to Detector Distance:", None))
#if QT_CONFIG(tooltip)
        self.txtSample2DetectorDistance.setToolTip(QCoreApplication.translate("ResolutionCalculatorPanel", u"Sample Aperture to Detector Distance.", None))
#endif // QT_CONFIG(tooltip)
        self.txtSample2DetectorDistance.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"1000", None))
        self.label_42.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"cm", None))
        self.label_33.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"Sample Offset:", None))
#if QT_CONFIG(tooltip)
        self.txtSampleOffset.setToolTip(QCoreApplication.translate("ResolutionCalculatorPanel", u"Sample Offset.", None))
#endif // QT_CONFIG(tooltip)
        self.txtSampleOffset.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"0", None))
        self.label_43.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"cm", None))
        self.label_34.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"Number of Pixels on Detector:", None))
#if QT_CONFIG(tooltip)
        self.txtDetectorSize.setToolTip(QCoreApplication.translate("ResolutionCalculatorPanel", u"Number of Pixels on Detector.", None))
#endif // QT_CONFIG(tooltip)
        self.txtDetectorSize.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"128, 128", None))
        self.label_35.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"Detector Pixel Size:", None))
#if QT_CONFIG(tooltip)
        self.txtDetectorPixSize.setToolTip(QCoreApplication.translate("ResolutionCalculatorPanel", u"Detector Pixel Size.", None))
#endif // QT_CONFIG(tooltip)
        self.txtDetectorPixSize.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"0.5, 0.5", None))
        self.label_45.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"cm", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("ResolutionCalculatorPanel", u"Q Location of the Estimation", None))
        self.label_21.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"Qx:", None))
#if QT_CONFIG(tooltip)
        self.txtQx.setToolTip(QCoreApplication.translate("ResolutionCalculatorPanel", u"Type the Qx value.", None))
#endif // QT_CONFIG(tooltip)
        self.txtQx.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"0.0", None))
        self.lblUnitQx.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.label_22.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"Qy:", None))
#if QT_CONFIG(tooltip)
        self.txtQy.setToolTip(QCoreApplication.translate("ResolutionCalculatorPanel", u"Type the Qy value.", None))
#endif // QT_CONFIG(tooltip)
        self.txtQy.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"0.0", None))
        self.lblUnitQy.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("ResolutionCalculatorPanel", u"Standard Deviation of the Resolution Distribution", None))
#if QT_CONFIG(tooltip)
        self.txtSigma_x.setToolTip(QCoreApplication.translate("ResolutionCalculatorPanel", u"The x component of the geometric resolution, excluding sigma_lamda.", None))
#endif // QT_CONFIG(tooltip)
        self.txtSigma_x.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"0.0008288", None))
#if QT_CONFIG(tooltip)
        self.txtSigma_y.setToolTip(QCoreApplication.translate("ResolutionCalculatorPanel", u"The y component of the geometric resolution, excluding sigma_lamda.", None))
#endif // QT_CONFIG(tooltip)
        self.txtSigma_y.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"0.0008288", None))
        self.label_2.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"Sigma_lamd:", None))
#if QT_CONFIG(tooltip)
        self.txtSigma_lamd.setToolTip(QCoreApplication.translate("ResolutionCalculatorPanel", u"The wavelength contribution in the radial direction. Note: The phi component is always zero.", None))
#endif // QT_CONFIG(tooltip)
        self.txtSigma_lamd.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"3.168e-05", None))
#if QT_CONFIG(tooltip)
        self.txt1DSigma.setToolTip(QCoreApplication.translate("ResolutionCalculatorPanel", u"Resolution in 1-dimension (for 1D data).", None))
#endif // QT_CONFIG(tooltip)
        self.txt1DSigma.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"0.0008289", None))
        self.lblUnit1DSigma.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.lblUnitSigmalamd.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.label_6.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"(1D) Sigma:", None))
        self.label_5.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"Sigma_y:", None))
        self.lblUnitSigmay.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.lblUnitSigmax.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.label.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"Sigma_x:", None))
#if QT_CONFIG(tooltip)
        self.cmdReset.setToolTip(QCoreApplication.translate("ResolutionCalculatorPanel", u"Reset to default SAS instrumental parameter", None))
#endif // QT_CONFIG(tooltip)
        self.cmdReset.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"Reset", None))
#if QT_CONFIG(tooltip)
        self.cmdCompute.setToolTip(QCoreApplication.translate("ResolutionCalculatorPanel", u"Compute the resolution of Q from SAS instrumental parameter", None))
#endif // QT_CONFIG(tooltip)
        self.cmdCompute.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"Compute", None))
#if QT_CONFIG(tooltip)
        self.cmdClose.setToolTip(QCoreApplication.translate("ResolutionCalculatorPanel", u"Close this window", None))
#endif // QT_CONFIG(tooltip)
        self.cmdClose.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"Close", None))
#if QT_CONFIG(tooltip)
        self.cmdHelp.setToolTip(QCoreApplication.translate("ResolutionCalculatorPanel", u"Help on using the Resolution Calculator", None))
#endif // QT_CONFIG(tooltip)
        self.cmdHelp.setText(QCoreApplication.translate("ResolutionCalculatorPanel", u"Help", None))
    # retranslateUi

