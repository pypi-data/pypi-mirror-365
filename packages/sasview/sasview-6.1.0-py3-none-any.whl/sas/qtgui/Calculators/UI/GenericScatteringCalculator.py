# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'GenericScatteringCalculator.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
    QFrame, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLayout, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QWidget)

class Ui_GenericScatteringCalculator(object):
    def setupUi(self, GenericScatteringCalculator):
        if not GenericScatteringCalculator.objectName():
            GenericScatteringCalculator.setObjectName(u"GenericScatteringCalculator")
        GenericScatteringCalculator.resize(1024, 625)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(GenericScatteringCalculator.sizePolicy().hasHeightForWidth())
        GenericScatteringCalculator.setSizePolicy(sizePolicy)
        GenericScatteringCalculator.setMinimumSize(QSize(660, 550))
        GenericScatteringCalculator.setMaximumSize(QSize(1150, 700))
        icon = QIcon()
        icon.addFile(u":/res/ball.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        GenericScatteringCalculator.setWindowIcon(icon)
        self.gridLayout_12 = QGridLayout(GenericScatteringCalculator)
        self.gridLayout_12.setObjectName(u"gridLayout_12")
        self.groupBox_coordinateInfo = QGroupBox(GenericScatteringCalculator)
        self.groupBox_coordinateInfo.setObjectName(u"groupBox_coordinateInfo")
        font = QFont()
        font.setBold(False)
        self.groupBox_coordinateInfo.setFont(font)
        self.gridLayout_13 = QGridLayout(self.groupBox_coordinateInfo)
        self.gridLayout_13.setObjectName(u"gridLayout_13")
        self.groupBox_7 = QGroupBox(self.groupBox_coordinateInfo)
        self.groupBox_7.setObjectName(u"groupBox_7")
        self.groupBox_7.setFont(font)
        self.gridLayout_14 = QGridLayout(self.groupBox_7)
        self.gridLayout_14.setObjectName(u"gridLayout_14")
        self.lblEnvYaw = QLabel(self.groupBox_7)
        self.lblEnvYaw.setObjectName(u"lblEnvYaw")
        self.lblEnvYaw.setFont(font)

        self.gridLayout_14.addWidget(self.lblEnvYaw, 0, 0, 1, 1)

        self.txtEnvYaw = QLineEdit(self.groupBox_7)
        self.txtEnvYaw.setObjectName(u"txtEnvYaw")
        self.txtEnvYaw.setMinimumSize(QSize(0, 18))
        self.txtEnvYaw.setFont(font)

        self.gridLayout_14.addWidget(self.txtEnvYaw, 0, 1, 1, 1)

        self.lblEnvYawUnit = QLabel(self.groupBox_7)
        self.lblEnvYawUnit.setObjectName(u"lblEnvYawUnit")
        self.lblEnvYawUnit.setFont(font)

        self.gridLayout_14.addWidget(self.lblEnvYawUnit, 0, 2, 1, 1)

        self.lblEnvPitch = QLabel(self.groupBox_7)
        self.lblEnvPitch.setObjectName(u"lblEnvPitch")
        self.lblEnvPitch.setFont(font)

        self.gridLayout_14.addWidget(self.lblEnvPitch, 1, 0, 1, 1)

        self.txtEnvPitch = QLineEdit(self.groupBox_7)
        self.txtEnvPitch.setObjectName(u"txtEnvPitch")
        self.txtEnvPitch.setMinimumSize(QSize(0, 18))
        self.txtEnvPitch.setFont(font)

        self.gridLayout_14.addWidget(self.txtEnvPitch, 1, 1, 1, 1)

        self.lblEnvPitchUnit = QLabel(self.groupBox_7)
        self.lblEnvPitchUnit.setObjectName(u"lblEnvPitchUnit")
        self.lblEnvPitchUnit.setFont(font)

        self.gridLayout_14.addWidget(self.lblEnvPitchUnit, 1, 2, 1, 1)

        self.lblEnvRoll = QLabel(self.groupBox_7)
        self.lblEnvRoll.setObjectName(u"lblEnvRoll")
        self.lblEnvRoll.setFont(font)

        self.gridLayout_14.addWidget(self.lblEnvRoll, 2, 0, 1, 1)

        self.txtEnvRoll = QLineEdit(self.groupBox_7)
        self.txtEnvRoll.setObjectName(u"txtEnvRoll")
        self.txtEnvRoll.setMinimumSize(QSize(0, 18))
        self.txtEnvRoll.setFont(font)

        self.gridLayout_14.addWidget(self.txtEnvRoll, 2, 1, 1, 1)

        self.lblEnvRollUnit = QLabel(self.groupBox_7)
        self.lblEnvRollUnit.setObjectName(u"lblEnvRollUnit")
        self.lblEnvRollUnit.setFont(font)

        self.gridLayout_14.addWidget(self.lblEnvRollUnit, 2, 2, 1, 1)


        self.gridLayout_13.addWidget(self.groupBox_7, 0, 0, 1, 4)

        self.groupBox_8 = QGroupBox(self.groupBox_coordinateInfo)
        self.groupBox_8.setObjectName(u"groupBox_8")
        self.groupBox_8.setFont(font)
        self.gridLayout_15 = QGridLayout(self.groupBox_8)
        self.gridLayout_15.setObjectName(u"gridLayout_15")
        self.lblSampleYaw = QLabel(self.groupBox_8)
        self.lblSampleYaw.setObjectName(u"lblSampleYaw")
        self.lblSampleYaw.setFont(font)

        self.gridLayout_15.addWidget(self.lblSampleYaw, 0, 0, 1, 1)

        self.txtSampleYaw = QLineEdit(self.groupBox_8)
        self.txtSampleYaw.setObjectName(u"txtSampleYaw")
        self.txtSampleYaw.setMinimumSize(QSize(0, 18))
        self.txtSampleYaw.setFont(font)

        self.gridLayout_15.addWidget(self.txtSampleYaw, 0, 1, 1, 1)

        self.lblSampleYawUnit = QLabel(self.groupBox_8)
        self.lblSampleYawUnit.setObjectName(u"lblSampleYawUnit")
        self.lblSampleYawUnit.setFont(font)

        self.gridLayout_15.addWidget(self.lblSampleYawUnit, 0, 2, 1, 1)

        self.lblSamplePitch = QLabel(self.groupBox_8)
        self.lblSamplePitch.setObjectName(u"lblSamplePitch")
        self.lblSamplePitch.setFont(font)

        self.gridLayout_15.addWidget(self.lblSamplePitch, 1, 0, 1, 1)

        self.txtSamplePitch = QLineEdit(self.groupBox_8)
        self.txtSamplePitch.setObjectName(u"txtSamplePitch")
        self.txtSamplePitch.setMinimumSize(QSize(0, 18))
        self.txtSamplePitch.setFont(font)

        self.gridLayout_15.addWidget(self.txtSamplePitch, 1, 1, 1, 1)

        self.lblSamplePitchUnit = QLabel(self.groupBox_8)
        self.lblSamplePitchUnit.setObjectName(u"lblSamplePitchUnit")
        self.lblSamplePitchUnit.setFont(font)

        self.gridLayout_15.addWidget(self.lblSamplePitchUnit, 1, 2, 1, 1)

        self.lblSampleRoll = QLabel(self.groupBox_8)
        self.lblSampleRoll.setObjectName(u"lblSampleRoll")
        self.lblSampleRoll.setFont(font)

        self.gridLayout_15.addWidget(self.lblSampleRoll, 2, 0, 1, 1)

        self.txtSampleRoll = QLineEdit(self.groupBox_8)
        self.txtSampleRoll.setObjectName(u"txtSampleRoll")
        self.txtSampleRoll.setMinimumSize(QSize(0, 18))
        self.txtSampleRoll.setFont(font)

        self.gridLayout_15.addWidget(self.txtSampleRoll, 2, 1, 1, 1)

        self.lblSampleRollUnit = QLabel(self.groupBox_8)
        self.lblSampleRollUnit.setObjectName(u"lblSampleRollUnit")
        self.lblSampleRollUnit.setFont(font)

        self.gridLayout_15.addWidget(self.lblSampleRollUnit, 2, 2, 1, 1)


        self.gridLayout_13.addWidget(self.groupBox_8, 1, 0, 1, 4)


        self.gridLayout_12.addWidget(self.groupBox_coordinateInfo, 0, 13, 2, 2)

        self.groupBox_Datafile = QGroupBox(GenericScatteringCalculator)
        self.groupBox_Datafile.setObjectName(u"groupBox_Datafile")
        self.groupBox_Datafile.setFont(font)
        self.gridLayout_5 = QGridLayout(self.groupBox_Datafile)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.lblNucData = QLabel(self.groupBox_Datafile)
        self.lblNucData.setObjectName(u"lblNucData")
        self.lblNucData.setFont(font)

        self.gridLayout.addWidget(self.lblNucData, 0, 0, 1, 1)

        self.checkboxNucData = QCheckBox(self.groupBox_Datafile)
        self.checkboxNucData.setObjectName(u"checkboxNucData")

        self.gridLayout.addWidget(self.checkboxNucData, 0, 1, 1, 1)

        self.txtNucData = QLineEdit(self.groupBox_Datafile)
        self.txtNucData.setObjectName(u"txtNucData")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.txtNucData.sizePolicy().hasHeightForWidth())
        self.txtNucData.setSizePolicy(sizePolicy1)
        self.txtNucData.setMinimumSize(QSize(151, 0))
        self.txtNucData.setFont(font)

        self.gridLayout.addWidget(self.txtNucData, 0, 2, 1, 1)

        self.cmdNucLoad = QPushButton(self.groupBox_Datafile)
        self.cmdNucLoad.setObjectName(u"cmdNucLoad")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.cmdNucLoad.sizePolicy().hasHeightForWidth())
        self.cmdNucLoad.setSizePolicy(sizePolicy2)
        self.cmdNucLoad.setMinimumSize(QSize(80, 23))
        self.cmdNucLoad.setFont(font)
        self.cmdNucLoad.setAutoDefault(False)

        self.gridLayout.addWidget(self.cmdNucLoad, 0, 3, 1, 1)

        self.lblMagData = QLabel(self.groupBox_Datafile)
        self.lblMagData.setObjectName(u"lblMagData")
        self.lblMagData.setFont(font)

        self.gridLayout.addWidget(self.lblMagData, 1, 0, 1, 1)

        self.checkboxMagData = QCheckBox(self.groupBox_Datafile)
        self.checkboxMagData.setObjectName(u"checkboxMagData")

        self.gridLayout.addWidget(self.checkboxMagData, 1, 1, 1, 1)

        self.txtMagData = QLineEdit(self.groupBox_Datafile)
        self.txtMagData.setObjectName(u"txtMagData")
        sizePolicy1.setHeightForWidth(self.txtMagData.sizePolicy().hasHeightForWidth())
        self.txtMagData.setSizePolicy(sizePolicy1)
        self.txtMagData.setMinimumSize(QSize(151, 0))
        self.txtMagData.setFont(font)

        self.gridLayout.addWidget(self.txtMagData, 1, 2, 1, 1)

        self.cmdMagLoad = QPushButton(self.groupBox_Datafile)
        self.cmdMagLoad.setObjectName(u"cmdMagLoad")
        sizePolicy2.setHeightForWidth(self.cmdMagLoad.sizePolicy().hasHeightForWidth())
        self.cmdMagLoad.setSizePolicy(sizePolicy2)
        self.cmdMagLoad.setMinimumSize(QSize(80, 23))
        self.cmdMagLoad.setFont(font)
        self.cmdMagLoad.setAutoDefault(False)

        self.gridLayout.addWidget(self.cmdMagLoad, 1, 3, 1, 1)

        self.lblShape = QLabel(self.groupBox_Datafile)
        self.lblShape.setObjectName(u"lblShape")
        self.lblShape.setFont(font)

        self.gridLayout.addWidget(self.lblShape, 2, 0, 1, 1)

        self.cbShape = QComboBox(self.groupBox_Datafile)
        self.cbShape.addItem("")
        self.cbShape.setObjectName(u"cbShape")
        sizePolicy1.setHeightForWidth(self.cbShape.sizePolicy().hasHeightForWidth())
        self.cbShape.setSizePolicy(sizePolicy1)
        self.cbShape.setFont(font)

        self.gridLayout.addWidget(self.cbShape, 2, 2, 1, 1)

        self.cmdDraw = QPushButton(self.groupBox_Datafile)
        self.cmdDraw.setObjectName(u"cmdDraw")
        self.cmdDraw.setEnabled(True)
        sizePolicy2.setHeightForWidth(self.cmdDraw.sizePolicy().hasHeightForWidth())
        self.cmdDraw.setSizePolicy(sizePolicy2)
        self.cmdDraw.setMinimumSize(QSize(80, 23))
        self.cmdDraw.setFont(font)
        self.cmdDraw.setAutoDefault(False)

        self.gridLayout.addWidget(self.cmdDraw, 2, 3, 1, 1)


        self.gridLayout_5.addLayout(self.gridLayout, 0, 0, 1, 1)


        self.gridLayout_12.addWidget(self.groupBox_Datafile, 0, 0, 1, 4)

        self.groupBox_InputParam = QGroupBox(GenericScatteringCalculator)
        self.groupBox_InputParam.setObjectName(u"groupBox_InputParam")
        self.groupBox_InputParam.setFont(font)
        self.gridLayout_6 = QGridLayout(self.groupBox_InputParam)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.gridLayout_InputParam = QGridLayout()
        self.gridLayout_InputParam.setObjectName(u"gridLayout_InputParam")
        self.gridLayout_InputParam.setSizeConstraint(QLayout.SetMinimumSize)
        self.label = QLabel(self.groupBox_InputParam)
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignCenter)

        self.gridLayout_InputParam.addWidget(self.label, 0, 1, 1, 1)

        self.txtUpFracIn = QLineEdit(self.groupBox_InputParam)
        self.txtUpFracIn.setObjectName(u"txtUpFracIn")
        self.txtUpFracIn.setMinimumSize(QSize(0, 18))
        self.txtUpFracIn.setFont(font)

        self.gridLayout_InputParam.addWidget(self.txtUpFracIn, 1, 1, 1, 1)

        self.lblUpFracOut = QLabel(self.groupBox_InputParam)
        self.lblUpFracOut.setObjectName(u"lblUpFracOut")
        self.lblUpFracOut.setFont(font)

        self.gridLayout_InputParam.addWidget(self.lblUpFracOut, 2, 0, 1, 1)

        self.lblUpFracIn = QLabel(self.groupBox_InputParam)
        self.lblUpFracIn.setObjectName(u"lblUpFracIn")
        self.lblUpFracIn.setFont(font)

        self.gridLayout_InputParam.addWidget(self.lblUpFracIn, 1, 0, 1, 1)

        self.txtUpTheta = QLineEdit(self.groupBox_InputParam)
        self.txtUpTheta.setObjectName(u"txtUpTheta")
        self.txtUpTheta.setMinimumSize(QSize(0, 18))
        self.txtUpTheta.setFont(font)

        self.gridLayout_InputParam.addWidget(self.txtUpTheta, 3, 1, 1, 1)

        self.lblUpPhi = QLabel(self.groupBox_InputParam)
        self.lblUpPhi.setObjectName(u"lblUpPhi")
        self.lblUpPhi.setFont(font)

        self.gridLayout_InputParam.addWidget(self.lblUpPhi, 4, 0, 1, 1)

        self.txtUpFracOut = QLineEdit(self.groupBox_InputParam)
        self.txtUpFracOut.setObjectName(u"txtUpFracOut")
        self.txtUpFracOut.setMinimumSize(QSize(0, 18))
        self.txtUpFracOut.setFont(font)

        self.gridLayout_InputParam.addWidget(self.txtUpFracOut, 2, 1, 1, 1)

        self.lblUpThetaUnit = QLabel(self.groupBox_InputParam)
        self.lblUpThetaUnit.setObjectName(u"lblUpThetaUnit")
        self.lblUpThetaUnit.setFont(font)

        self.gridLayout_InputParam.addWidget(self.lblUpThetaUnit, 3, 2, 1, 1)

        self.lblUpTheta = QLabel(self.groupBox_InputParam)
        self.lblUpTheta.setObjectName(u"lblUpTheta")
        self.lblUpTheta.setFont(font)

        self.gridLayout_InputParam.addWidget(self.lblUpTheta, 3, 0, 1, 1)

        self.lblUpPhiUnit = QLabel(self.groupBox_InputParam)
        self.lblUpPhiUnit.setObjectName(u"lblUpPhiUnit")
        self.lblUpPhiUnit.setFont(font)

        self.gridLayout_InputParam.addWidget(self.lblUpPhiUnit, 4, 2, 1, 1)

        self.txtUpPhi = QLineEdit(self.groupBox_InputParam)
        self.txtUpPhi.setObjectName(u"txtUpPhi")
        self.txtUpPhi.setMinimumSize(QSize(0, 18))
        self.txtUpPhi.setFont(font)

        self.gridLayout_InputParam.addWidget(self.txtUpPhi, 4, 1, 1, 1)

        self.lbl2 = QLabel(self.groupBox_InputParam)
        self.lbl2.setObjectName(u"lbl2")
        self.lbl2.setFont(font)

        self.gridLayout_InputParam.addWidget(self.lbl2, 6, 2, 1, 1)

        self.txtBackground = QLineEdit(self.groupBox_InputParam)
        self.txtBackground.setObjectName(u"txtBackground")
        self.txtBackground.setMinimumSize(QSize(0, 18))
        self.txtBackground.setFont(font)

        self.gridLayout_InputParam.addWidget(self.txtBackground, 6, 1, 1, 1)

        self.lblScale = QLabel(self.groupBox_InputParam)
        self.lblScale.setObjectName(u"lblScale")
        self.lblScale.setFont(font)

        self.gridLayout_InputParam.addWidget(self.lblScale, 7, 0, 1, 1)

        self.txtScale = QLineEdit(self.groupBox_InputParam)
        self.txtScale.setObjectName(u"txtScale")
        self.txtScale.setMinimumSize(QSize(0, 18))
        self.txtScale.setFont(font)

        self.gridLayout_InputParam.addWidget(self.txtScale, 7, 1, 1, 1)

        self.lblSolventSLD = QLabel(self.groupBox_InputParam)
        self.lblSolventSLD.setObjectName(u"lblSolventSLD")
        self.lblSolventSLD.setFont(font)

        self.gridLayout_InputParam.addWidget(self.lblSolventSLD, 8, 0, 1, 1)

        self.lblTotalVolume = QLabel(self.groupBox_InputParam)
        self.lblTotalVolume.setObjectName(u"lblTotalVolume")
        self.lblTotalVolume.setFont(font)

        self.gridLayout_InputParam.addWidget(self.lblTotalVolume, 9, 0, 1, 1)

        self.txtSolventSLD = QLineEdit(self.groupBox_InputParam)
        self.txtSolventSLD.setObjectName(u"txtSolventSLD")
        self.txtSolventSLD.setMinimumSize(QSize(0, 18))
        self.txtSolventSLD.setFont(font)

        self.gridLayout_InputParam.addWidget(self.txtSolventSLD, 8, 1, 1, 1)

        self.txtTotalVolume = QLineEdit(self.groupBox_InputParam)
        self.txtTotalVolume.setObjectName(u"txtTotalVolume")
        self.txtTotalVolume.setMinimumSize(QSize(0, 18))
        self.txtTotalVolume.setFont(font)

        self.gridLayout_InputParam.addWidget(self.txtTotalVolume, 9, 1, 1, 1)

        self.lblBackgd = QLabel(self.groupBox_InputParam)
        self.lblBackgd.setObjectName(u"lblBackgd")
        self.lblBackgd.setFont(font)

        self.gridLayout_InputParam.addWidget(self.lblBackgd, 6, 0, 1, 1)

        self.lblUnitSolventSLD = QLabel(self.groupBox_InputParam)
        self.lblUnitSolventSLD.setObjectName(u"lblUnitSolventSLD")
        sizePolicy.setHeightForWidth(self.lblUnitSolventSLD.sizePolicy().hasHeightForWidth())
        self.lblUnitSolventSLD.setSizePolicy(sizePolicy)
        self.lblUnitSolventSLD.setMinimumSize(QSize(0, 0))
        self.lblUnitSolventSLD.setBaseSize(QSize(0, 0))
        self.lblUnitSolventSLD.setFont(font)
        self.lblUnitSolventSLD.setScaledContents(False)
        self.lblUnitSolventSLD.setMargin(0)
        self.lblUnitSolventSLD.setIndent(-1)

        self.gridLayout_InputParam.addWidget(self.lblUnitSolventSLD, 8, 2, 1, 1)

        self.lblUnitVolume = QLabel(self.groupBox_InputParam)
        self.lblUnitVolume.setObjectName(u"lblUnitVolume")
        self.lblUnitVolume.setFont(font)

        self.gridLayout_InputParam.addWidget(self.lblUnitVolume, 9, 2, 1, 1)

        self.label_2 = QLabel(self.groupBox_InputParam)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setAlignment(Qt.AlignCenter)

        self.gridLayout_InputParam.addWidget(self.label_2, 5, 1, 1, 1)


        self.gridLayout_6.addLayout(self.gridLayout_InputParam, 0, 0, 1, 1)


        self.gridLayout_12.addWidget(self.groupBox_InputParam, 1, 0, 2, 4)

        self.groupBox_SLDPixelInfo = QGroupBox(GenericScatteringCalculator)
        self.groupBox_SLDPixelInfo.setObjectName(u"groupBox_SLDPixelInfo")
        self.groupBox_SLDPixelInfo.setFont(font)
        self.gridLayout_11 = QGridLayout(self.groupBox_SLDPixelInfo)
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.lblNoPixels = QLabel(self.groupBox_SLDPixelInfo)
        self.lblNoPixels.setObjectName(u"lblNoPixels")
        self.lblNoPixels.setFont(font)

        self.gridLayout_11.addWidget(self.lblNoPixels, 0, 0, 1, 1)

        self.txtNoPixels = QLineEdit(self.groupBox_SLDPixelInfo)
        self.txtNoPixels.setObjectName(u"txtNoPixels")
        self.txtNoPixels.setEnabled(False)
        self.txtNoPixels.setMinimumSize(QSize(110, 27))
        self.txtNoPixels.setFont(font)
        self.txtNoPixels.setReadOnly(True)

        self.gridLayout_11.addWidget(self.txtNoPixels, 0, 1, 1, 3)

        self.groupBox_5 = QGroupBox(self.groupBox_SLDPixelInfo)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.groupBox_5.setFont(font)
        self.gridLayout_8 = QGridLayout(self.groupBox_5)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.lblMx = QLabel(self.groupBox_5)
        self.lblMx.setObjectName(u"lblMx")
        self.lblMx.setFont(font)

        self.gridLayout_4.addWidget(self.lblMx, 0, 0, 1, 1)

        self.txtMx = QLineEdit(self.groupBox_5)
        self.txtMx.setObjectName(u"txtMx")
        self.txtMx.setMinimumSize(QSize(70, 18))
        self.txtMx.setFont(font)

        self.gridLayout_4.addWidget(self.txtMx, 0, 1, 1, 1)

        self.lblUnitMx = QLabel(self.groupBox_5)
        self.lblUnitMx.setObjectName(u"lblUnitMx")
        self.lblUnitMx.setFont(font)

        self.gridLayout_4.addWidget(self.lblUnitMx, 0, 2, 1, 1)

        self.lblMy = QLabel(self.groupBox_5)
        self.lblMy.setObjectName(u"lblMy")
        self.lblMy.setFont(font)

        self.gridLayout_4.addWidget(self.lblMy, 1, 0, 1, 1)

        self.txtMy = QLineEdit(self.groupBox_5)
        self.txtMy.setObjectName(u"txtMy")
        self.txtMy.setMinimumSize(QSize(70, 18))
        self.txtMy.setFont(font)

        self.gridLayout_4.addWidget(self.txtMy, 1, 1, 1, 1)

        self.lblUnitMy = QLabel(self.groupBox_5)
        self.lblUnitMy.setObjectName(u"lblUnitMy")
        self.lblUnitMy.setFont(font)

        self.gridLayout_4.addWidget(self.lblUnitMy, 1, 2, 1, 1)

        self.lblMz = QLabel(self.groupBox_5)
        self.lblMz.setObjectName(u"lblMz")
        self.lblMz.setFont(font)

        self.gridLayout_4.addWidget(self.lblMz, 2, 0, 1, 1)

        self.txtMz = QLineEdit(self.groupBox_5)
        self.txtMz.setObjectName(u"txtMz")
        self.txtMz.setMinimumSize(QSize(70, 18))
        self.txtMz.setFont(font)

        self.gridLayout_4.addWidget(self.txtMz, 2, 1, 1, 1)

        self.lblUnitMz = QLabel(self.groupBox_5)
        self.lblUnitMz.setObjectName(u"lblUnitMz")
        self.lblUnitMz.setFont(font)

        self.gridLayout_4.addWidget(self.lblUnitMz, 2, 2, 1, 1)

        self.lblNucl = QLabel(self.groupBox_5)
        self.lblNucl.setObjectName(u"lblNucl")
        self.lblNucl.setFont(font)

        self.gridLayout_4.addWidget(self.lblNucl, 3, 0, 1, 1)

        self.txtNucl = QLineEdit(self.groupBox_5)
        self.txtNucl.setObjectName(u"txtNucl")
        self.txtNucl.setMinimumSize(QSize(70, 18))
        self.txtNucl.setFont(font)

        self.gridLayout_4.addWidget(self.txtNucl, 3, 1, 1, 1)

        self.lblUnitNucl = QLabel(self.groupBox_5)
        self.lblUnitNucl.setObjectName(u"lblUnitNucl")
        self.lblUnitNucl.setFont(font)

        self.gridLayout_4.addWidget(self.lblUnitNucl, 3, 2, 1, 1)


        self.gridLayout_8.addLayout(self.gridLayout_4, 0, 0, 1, 1)


        self.gridLayout_11.addWidget(self.groupBox_5, 1, 0, 2, 4)

        self.groupBox_6 = QGroupBox(self.groupBox_SLDPixelInfo)
        self.groupBox_6.setObjectName(u"groupBox_6")
        self.groupBox_6.setFont(font)
        self.gridLayout_9 = QGridLayout(self.groupBox_6)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.gridLayout_Nodes = QGridLayout()
        self.gridLayout_Nodes.setObjectName(u"gridLayout_Nodes")
        self.lblXnodes = QLabel(self.groupBox_6)
        self.lblXnodes.setObjectName(u"lblXnodes")
        self.lblXnodes.setFont(font)

        self.gridLayout_Nodes.addWidget(self.lblXnodes, 0, 0, 1, 1)

        self.txtXnodes = QLineEdit(self.groupBox_6)
        self.txtXnodes.setObjectName(u"txtXnodes")
        self.txtXnodes.setMinimumSize(QSize(56, 18))
        self.txtXnodes.setFont(font)

        self.gridLayout_Nodes.addWidget(self.txtXnodes, 0, 1, 1, 1)

        self.label_ynodes = QLabel(self.groupBox_6)
        self.label_ynodes.setObjectName(u"label_ynodes")
        self.label_ynodes.setFont(font)

        self.gridLayout_Nodes.addWidget(self.label_ynodes, 1, 0, 1, 1)

        self.txtYnodes = QLineEdit(self.groupBox_6)
        self.txtYnodes.setObjectName(u"txtYnodes")
        self.txtYnodes.setMinimumSize(QSize(56, 18))
        self.txtYnodes.setFont(font)

        self.gridLayout_Nodes.addWidget(self.txtYnodes, 1, 1, 1, 1)

        self.label_znodes = QLabel(self.groupBox_6)
        self.label_znodes.setObjectName(u"label_znodes")
        self.label_znodes.setFont(font)

        self.gridLayout_Nodes.addWidget(self.label_znodes, 2, 0, 1, 1)

        self.txtZnodes = QLineEdit(self.groupBox_6)
        self.txtZnodes.setObjectName(u"txtZnodes")
        self.txtZnodes.setMinimumSize(QSize(56, 18))
        self.txtZnodes.setFont(font)

        self.gridLayout_Nodes.addWidget(self.txtZnodes, 2, 1, 1, 1)


        self.gridLayout_9.addLayout(self.gridLayout_Nodes, 0, 0, 1, 1)


        self.gridLayout_11.addWidget(self.groupBox_6, 0, 4, 2, 4)

        self.groupBox_Stepsize = QGroupBox(self.groupBox_SLDPixelInfo)
        self.groupBox_Stepsize.setObjectName(u"groupBox_Stepsize")
        self.groupBox_Stepsize.setFont(font)
        self.gridLayout_10 = QGridLayout(self.groupBox_Stepsize)
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.gridLayout_Stepsize = QGridLayout()
        self.gridLayout_Stepsize.setObjectName(u"gridLayout_Stepsize")
        self.lblXstepsize = QLabel(self.groupBox_Stepsize)
        self.lblXstepsize.setObjectName(u"lblXstepsize")
        self.lblXstepsize.setFont(font)

        self.gridLayout_Stepsize.addWidget(self.lblXstepsize, 0, 0, 1, 1)

        self.txtXstepsize = QLineEdit(self.groupBox_Stepsize)
        self.txtXstepsize.setObjectName(u"txtXstepsize")
        self.txtXstepsize.setMinimumSize(QSize(50, 18))
        self.txtXstepsize.setFont(font)

        self.gridLayout_Stepsize.addWidget(self.txtXstepsize, 0, 1, 1, 1)

        self.lblUnitx = QLabel(self.groupBox_Stepsize)
        self.lblUnitx.setObjectName(u"lblUnitx")
        self.lblUnitx.setFont(font)

        self.gridLayout_Stepsize.addWidget(self.lblUnitx, 0, 2, 1, 1)

        self.lblYstepsize = QLabel(self.groupBox_Stepsize)
        self.lblYstepsize.setObjectName(u"lblYstepsize")
        self.lblYstepsize.setFont(font)

        self.gridLayout_Stepsize.addWidget(self.lblYstepsize, 1, 0, 1, 1)

        self.txtYstepsize = QLineEdit(self.groupBox_Stepsize)
        self.txtYstepsize.setObjectName(u"txtYstepsize")
        self.txtYstepsize.setMinimumSize(QSize(50, 18))
        self.txtYstepsize.setFont(font)

        self.gridLayout_Stepsize.addWidget(self.txtYstepsize, 1, 1, 1, 1)

        self.lblUnity = QLabel(self.groupBox_Stepsize)
        self.lblUnity.setObjectName(u"lblUnity")
        self.lblUnity.setFont(font)

        self.gridLayout_Stepsize.addWidget(self.lblUnity, 1, 2, 1, 1)

        self.lblZstepsize = QLabel(self.groupBox_Stepsize)
        self.lblZstepsize.setObjectName(u"lblZstepsize")
        self.lblZstepsize.setFont(font)

        self.gridLayout_Stepsize.addWidget(self.lblZstepsize, 2, 0, 1, 1)

        self.txtZstepsize = QLineEdit(self.groupBox_Stepsize)
        self.txtZstepsize.setObjectName(u"txtZstepsize")
        self.txtZstepsize.setMinimumSize(QSize(50, 18))
        self.txtZstepsize.setFont(font)

        self.gridLayout_Stepsize.addWidget(self.txtZstepsize, 2, 1, 1, 1)

        self.lblUnitz = QLabel(self.groupBox_Stepsize)
        self.lblUnitz.setObjectName(u"lblUnitz")
        self.lblUnitz.setFont(font)

        self.gridLayout_Stepsize.addWidget(self.lblUnitz, 2, 2, 1, 1)


        self.gridLayout_10.addLayout(self.gridLayout_Stepsize, 0, 0, 1, 1)


        self.gridLayout_11.addWidget(self.groupBox_Stepsize, 2, 4, 2, 4)

        self.cmdDrawpoints = QPushButton(self.groupBox_SLDPixelInfo)
        self.cmdDrawpoints.setObjectName(u"cmdDrawpoints")
        self.cmdDrawpoints.setEnabled(True)
        sizePolicy2.setHeightForWidth(self.cmdDrawpoints.sizePolicy().hasHeightForWidth())
        self.cmdDrawpoints.setSizePolicy(sizePolicy2)
        self.cmdDrawpoints.setFont(font)
        self.cmdDrawpoints.setAutoDefault(False)

        self.gridLayout_11.addWidget(self.cmdDrawpoints, 3, 0, 1, 2)

        self.horizontalSpacer = QSpacerItem(7, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_11.addItem(self.horizontalSpacer, 3, 2, 1, 1)

        self.cmdSave = QPushButton(self.groupBox_SLDPixelInfo)
        self.cmdSave.setObjectName(u"cmdSave")
        self.cmdSave.setEnabled(False)
        sizePolicy2.setHeightForWidth(self.cmdSave.sizePolicy().hasHeightForWidth())
        self.cmdSave.setSizePolicy(sizePolicy2)
        self.cmdSave.setFont(font)
        self.cmdSave.setAutoDefault(False)

        self.gridLayout_11.addWidget(self.cmdSave, 3, 3, 1, 1)

        self.cmdDrawpoints.raise_()
        self.cmdSave.raise_()
        self.lblNoPixels.raise_()
        self.txtNoPixels.raise_()
        self.groupBox_5.raise_()
        self.groupBox_6.raise_()
        self.groupBox_Stepsize.raise_()

        self.gridLayout_12.addWidget(self.groupBox_SLDPixelInfo, 0, 7, 2, 4)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_7, 0, 0, 1, 1)

        self.cmdClose = QPushButton(GenericScatteringCalculator)
        self.cmdClose.setObjectName(u"cmdClose")
        sizePolicy2.setHeightForWidth(self.cmdClose.sizePolicy().hasHeightForWidth())
        self.cmdClose.setSizePolicy(sizePolicy2)
        self.cmdClose.setMinimumSize(QSize(75, 23))
        self.cmdClose.setIconSize(QSize(17, 16))
        self.cmdClose.setAutoDefault(False)

        self.gridLayout_2.addWidget(self.cmdClose, 0, 3, 1, 1)

        self.cmdReset = QPushButton(GenericScatteringCalculator)
        self.cmdReset.setObjectName(u"cmdReset")
        sizePolicy2.setHeightForWidth(self.cmdReset.sizePolicy().hasHeightForWidth())
        self.cmdReset.setSizePolicy(sizePolicy2)
        self.cmdReset.setMinimumSize(QSize(75, 23))
        self.cmdReset.setAutoDefault(False)

        self.gridLayout_2.addWidget(self.cmdReset, 0, 2, 1, 1)

        self.cmdHelp = QPushButton(GenericScatteringCalculator)
        self.cmdHelp.setObjectName(u"cmdHelp")
        sizePolicy2.setHeightForWidth(self.cmdHelp.sizePolicy().hasHeightForWidth())
        self.cmdHelp.setSizePolicy(sizePolicy2)
        self.cmdHelp.setMinimumSize(QSize(75, 23))
        self.cmdHelp.setAutoDefault(False)

        self.gridLayout_2.addWidget(self.cmdHelp, 0, 4, 1, 1)

        self.cmdCompute = QPushButton(GenericScatteringCalculator)
        self.cmdCompute.setObjectName(u"cmdCompute")
        sizePolicy2.setHeightForWidth(self.cmdCompute.sizePolicy().hasHeightForWidth())
        self.cmdCompute.setSizePolicy(sizePolicy2)
        self.cmdCompute.setAutoDefault(False)

        self.gridLayout_2.addWidget(self.cmdCompute, 0, 1, 1, 1)


        self.gridLayout_12.addLayout(self.gridLayout_2, 9, 0, 1, 5)

        self.horizontalSpacer_2 = QSpacerItem(3, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_12.addItem(self.horizontalSpacer_2, 1, 4, 1, 1)

        self.coordDisplay = QHBoxLayout()
        self.coordDisplay.setObjectName(u"coordDisplay")

        self.gridLayout_12.addLayout(self.coordDisplay, 2, 7, 6, 8)

        self.gridLayout_17 = QGridLayout()
        self.gridLayout_17.setObjectName(u"gridLayout_17")

        self.gridLayout_12.addLayout(self.gridLayout_17, 4, 0, 1, 1)

        self.line = QFrame(GenericScatteringCalculator)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_12.addWidget(self.line, 0, 5, 8, 2)

        self.lblVerifyError = QLabel(GenericScatteringCalculator)
        self.lblVerifyError.setObjectName(u"lblVerifyError")
        self.lblVerifyError.setMinimumSize(QSize(0, 30))
        self.lblVerifyError.setFont(font)
        self.lblVerifyError.setAlignment(Qt.AlignHCenter)
        self.lblVerifyError.setWordWrap(True)

        self.gridLayout_12.addWidget(self.lblVerifyError, 9, 7, 1, 1)

        self.groupBox_Qrange = QGroupBox(GenericScatteringCalculator)
        self.groupBox_Qrange.setObjectName(u"groupBox_Qrange")
        self.groupBox_Qrange.setFont(font)
        self.gridLayout_7 = QGridLayout(self.groupBox_Qrange)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.txtQxMax = QLineEdit(self.groupBox_Qrange)
        self.txtQxMax.setObjectName(u"txtQxMax")
        self.txtQxMax.setMinimumSize(QSize(0, 18))
        self.txtQxMax.setFont(font)

        self.gridLayout_3.addWidget(self.txtQxMax, 1, 1, 1, 1)

        self.lbl5 = QLabel(self.groupBox_Qrange)
        self.lbl5.setObjectName(u"lbl5")
        self.lbl5.setFont(font)

        self.gridLayout_3.addWidget(self.lbl5, 1, 2, 1, 1)

        self.lblQxQyMax = QLabel(self.groupBox_Qrange)
        self.lblQxQyMax.setObjectName(u"lblQxQyMax")
        self.lblQxQyMax.setFont(font)

        self.gridLayout_3.addWidget(self.lblQxQyMax, 1, 0, 1, 1)

        self.lblNoQBins = QLabel(self.groupBox_Qrange)
        self.lblNoQBins.setObjectName(u"lblNoQBins")
        self.lblNoQBins.setFont(font)

        self.gridLayout_3.addWidget(self.lblNoQBins, 0, 0, 1, 1)

        self.txtNoQBins = QLineEdit(self.groupBox_Qrange)
        self.txtNoQBins.setObjectName(u"txtNoQBins")
        self.txtNoQBins.setMinimumSize(QSize(0, 18))
        self.txtNoQBins.setFont(font)

        self.gridLayout_3.addWidget(self.txtNoQBins, 0, 1, 1, 1)

        self.lblQxQyMin = QLabel(self.groupBox_Qrange)
        self.lblQxQyMin.setObjectName(u"lblQxQyMin")

        self.gridLayout_3.addWidget(self.lblQxQyMin, 2, 0, 1, 1)

        self.txtQxMin = QLineEdit(self.groupBox_Qrange)
        self.txtQxMin.setObjectName(u"txtQxMin")
        self.txtQxMin.setMinimumSize(QSize(0, 18))
        self.txtQxMin.setFont(font)
        self.txtQxMin.setCursorPosition(3)

        self.gridLayout_3.addWidget(self.txtQxMin, 2, 1, 1, 1)

        self.lbl6 = QLabel(self.groupBox_Qrange)
        self.lbl6.setObjectName(u"lbl6")

        self.gridLayout_3.addWidget(self.lbl6, 2, 2, 1, 1)


        self.gridLayout_7.addLayout(self.gridLayout_3, 0, 0, 1, 1)

        self.checkboxLogSpace = QCheckBox(self.groupBox_Qrange)
        self.checkboxLogSpace.setObjectName(u"checkboxLogSpace")

        self.gridLayout_7.addWidget(self.checkboxLogSpace, 1, 0, 1, 1)


        self.gridLayout_12.addWidget(self.groupBox_Qrange, 3, 0, 1, 4)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_12.addItem(self.horizontalSpacer_6, 7, 7, 1, 1)

        self.line1 = QFrame(GenericScatteringCalculator)
        self.line1.setObjectName(u"line1")
        self.line1.setFrameShape(QFrame.Shape.VLine)
        self.line1.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_12.addWidget(self.line1, 0, 11, 2, 2)

        self.horizontalSpacer_3 = QSpacerItem(0, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_12.addItem(self.horizontalSpacer_3, 1, 6, 1, 1)

        self.horizontalSpacer_4 = QSpacerItem(0, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_12.addItem(self.horizontalSpacer_4, 3, 8, 1, 1)

        self.groupbox_RoG = QGroupBox(GenericScatteringCalculator)
        self.groupbox_RoG.setObjectName(u"groupbox_RoG")
        self.groupbox_RoG.setMaximumSize(QSize(180, 16777215))
        self.gridLayout_18 = QGridLayout(self.groupbox_RoG)
        self.gridLayout_18.setObjectName(u"gridLayout_18")
        self.lblRgMass = QLabel(self.groupbox_RoG)
        self.lblRgMass.setObjectName(u"lblRgMass")

        self.gridLayout_18.addWidget(self.lblRgMass, 0, 1, 1, 1)

        self.txtRgMass = QLineEdit(self.groupbox_RoG)
        self.txtRgMass.setObjectName(u"txtRgMass")
        self.txtRgMass.setEnabled(False)

        self.gridLayout_18.addWidget(self.txtRgMass, 0, 2, 1, 1)

        self.gridLayout_16 = QGridLayout()
        self.gridLayout_16.setObjectName(u"gridLayout_16")

        self.gridLayout_18.addLayout(self.gridLayout_16, 2, 0, 1, 1)

        self.txtRG = QLineEdit(self.groupbox_RoG)
        self.txtRG.setObjectName(u"txtRG")
        self.txtRG.setEnabled(False)

        self.gridLayout_18.addWidget(self.txtRG, 1, 2, 1, 1)

        self.lblRG = QLabel(self.groupbox_RoG)
        self.lblRG.setObjectName(u"lblRG")

        self.gridLayout_18.addWidget(self.lblRG, 1, 1, 1, 1)


        self.gridLayout_12.addWidget(self.groupbox_RoG, 5, 0, 1, 1)

        self.gridLayout_19 = QGridLayout()
        self.gridLayout_19.setObjectName(u"gridLayout_19")
        self.gridLayout_19.setSizeConstraint(QLayout.SetMaximumSize)
        self.customFit = QGroupBox(GenericScatteringCalculator)
        self.customFit.setObjectName(u"customFit")
        self.customFit.setMinimumSize(QSize(210, 0))
        self.gridLayout_20 = QGridLayout(self.customFit)
        self.gridLayout_20.setObjectName(u"gridLayout_20")
        self.checkboxPluginModel = QCheckBox(self.customFit)
        self.checkboxPluginModel.setObjectName(u"checkboxPluginModel")

        self.gridLayout_20.addWidget(self.checkboxPluginModel, 0, 0, 1, 1)

        self.txtFileName = QLineEdit(self.customFit)
        self.txtFileName.setObjectName(u"txtFileName")
        self.txtFileName.setEnabled(False)
        self.txtFileName.setMinimumSize(QSize(0, 18))

        self.gridLayout_20.addWidget(self.txtFileName, 1, 0, 1, 1)


        self.gridLayout_19.addWidget(self.customFit, 1, 0, 2, 1)


        self.gridLayout_12.addLayout(self.gridLayout_19, 5, 1, 2, 3)

        self.cbOptionsCalc = QComboBox(GenericScatteringCalculator)
        self.cbOptionsCalc.addItem("")
        self.cbOptionsCalc.addItem("")
        self.cbOptionsCalc.addItem("")
        self.cbOptionsCalc.setObjectName(u"cbOptionsCalc")
        sizePolicy2.setHeightForWidth(self.cbOptionsCalc.sizePolicy().hasHeightForWidth())
        self.cbOptionsCalc.setSizePolicy(sizePolicy2)
        self.cbOptionsCalc.setMinimumSize(QSize(0, 23))
        self.cbOptionsCalc.setMaximumSize(QSize(210, 26))

        self.gridLayout_12.addWidget(self.cbOptionsCalc, 7, 0, 1, 1)

        QWidget.setTabOrder(self.checkboxNucData, self.txtNucData)
        QWidget.setTabOrder(self.txtNucData, self.checkboxMagData)
        QWidget.setTabOrder(self.checkboxMagData, self.txtMagData)
        QWidget.setTabOrder(self.txtMagData, self.cbShape)
        QWidget.setTabOrder(self.cbShape, self.cmdNucLoad)
        QWidget.setTabOrder(self.cmdNucLoad, self.cmdMagLoad)
        QWidget.setTabOrder(self.cmdMagLoad, self.cmdDraw)
        QWidget.setTabOrder(self.cmdDraw, self.txtUpFracIn)
        QWidget.setTabOrder(self.txtUpFracIn, self.txtUpFracOut)
        QWidget.setTabOrder(self.txtUpFracOut, self.txtUpTheta)
        QWidget.setTabOrder(self.txtUpTheta, self.txtUpPhi)
        QWidget.setTabOrder(self.txtUpPhi, self.txtBackground)
        QWidget.setTabOrder(self.txtBackground, self.txtScale)
        QWidget.setTabOrder(self.txtScale, self.txtSolventSLD)
        QWidget.setTabOrder(self.txtSolventSLD, self.txtTotalVolume)
        QWidget.setTabOrder(self.txtTotalVolume, self.txtNoQBins)
        QWidget.setTabOrder(self.txtNoQBins, self.txtQxMax)
        QWidget.setTabOrder(self.txtQxMax, self.txtNoPixels)
        QWidget.setTabOrder(self.txtNoPixels, self.txtMx)
        QWidget.setTabOrder(self.txtMx, self.txtMy)
        QWidget.setTabOrder(self.txtMy, self.txtMz)
        QWidget.setTabOrder(self.txtMz, self.txtNucl)
        QWidget.setTabOrder(self.txtNucl, self.cmdDrawpoints)
        QWidget.setTabOrder(self.cmdDrawpoints, self.cmdSave)
        QWidget.setTabOrder(self.cmdSave, self.txtXnodes)
        QWidget.setTabOrder(self.txtXnodes, self.txtYnodes)
        QWidget.setTabOrder(self.txtYnodes, self.txtZnodes)
        QWidget.setTabOrder(self.txtZnodes, self.txtXstepsize)
        QWidget.setTabOrder(self.txtXstepsize, self.txtYstepsize)
        QWidget.setTabOrder(self.txtYstepsize, self.txtZstepsize)
        QWidget.setTabOrder(self.txtZstepsize, self.txtEnvYaw)
        QWidget.setTabOrder(self.txtEnvYaw, self.txtEnvPitch)
        QWidget.setTabOrder(self.txtEnvPitch, self.txtEnvRoll)
        QWidget.setTabOrder(self.txtEnvRoll, self.txtSampleYaw)
        QWidget.setTabOrder(self.txtSampleYaw, self.txtSamplePitch)
        QWidget.setTabOrder(self.txtSamplePitch, self.txtSampleRoll)
        QWidget.setTabOrder(self.txtSampleRoll, self.cmdCompute)
        QWidget.setTabOrder(self.cmdCompute, self.cmdReset)
        QWidget.setTabOrder(self.cmdReset, self.cmdClose)
        QWidget.setTabOrder(self.cmdClose, self.cmdHelp)

        self.retranslateUi(GenericScatteringCalculator)

        QMetaObject.connectSlotsByName(GenericScatteringCalculator)
    # setupUi

    def retranslateUi(self, GenericScatteringCalculator):
        GenericScatteringCalculator.setWindowTitle(QCoreApplication.translate("GenericScatteringCalculator", u"Generic Scattering Calculator", None))
        self.groupBox_coordinateInfo.setTitle(QCoreApplication.translate("GenericScatteringCalculator", u"Coordinate System Info", None))
        self.groupBox_7.setTitle(QCoreApplication.translate("GenericScatteringCalculator", u"Environment Coordinates (uvw)", None))
#if QT_CONFIG(tooltip)
        self.lblEnvYaw.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>The yaw angle of the environment coordinates from the beamline coordinates.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblEnvYaw.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Yaw", None))
#if QT_CONFIG(tooltip)
        self.txtEnvYaw.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>The yaw angle of the environment coordinates from the beamline coordinates.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.txtEnvYaw.setText(QCoreApplication.translate("GenericScatteringCalculator", u"0.0", None))
        self.lblEnvYawUnit.setText(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p><span style=\" vertical-align:super;\">o</span></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.lblEnvPitch.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>The pitch angle of the environment coordinates from the beamline coordinates.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblEnvPitch.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Pitch", None))
#if QT_CONFIG(tooltip)
        self.txtEnvPitch.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>The pitch angle of the environment coordinates from the beamline coordinates.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.txtEnvPitch.setText(QCoreApplication.translate("GenericScatteringCalculator", u"0.0", None))
        self.lblEnvPitchUnit.setText(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p><span style=\" vertical-align:super;\">o</span></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.lblEnvRoll.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>The roll angle of the environment coordinates from the beamline coordinates.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblEnvRoll.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Roll", None))
#if QT_CONFIG(tooltip)
        self.txtEnvRoll.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>The roll angle of the environment coordinates from the beamline coordinates.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.txtEnvRoll.setText(QCoreApplication.translate("GenericScatteringCalculator", u"0.0", None))
        self.lblEnvRollUnit.setText(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p><span style=\" vertical-align:super;\">o</span></p></body></html>", None))
        self.groupBox_8.setTitle(QCoreApplication.translate("GenericScatteringCalculator", u"Sample Coordinates (xyz)", None))
#if QT_CONFIG(tooltip)
        self.lblSampleYaw.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>The yaw angle of the sample coordinates from the environment coordinates.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblSampleYaw.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Yaw", None))
#if QT_CONFIG(tooltip)
        self.txtSampleYaw.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>The yaw angle of the sample coordinates from the environment coordinates.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.txtSampleYaw.setText(QCoreApplication.translate("GenericScatteringCalculator", u"0.0", None))
        self.lblSampleYawUnit.setText(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p><span style=\" vertical-align:super;\">o</span></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.lblSamplePitch.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>The pitch angle of the sample coordinates from the environment coordinates.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblSamplePitch.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Pitch", None))
#if QT_CONFIG(tooltip)
        self.txtSamplePitch.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>The pitch angle of the sample coordinates from the environment coordinates.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.txtSamplePitch.setText(QCoreApplication.translate("GenericScatteringCalculator", u"0.0", None))
        self.lblSamplePitchUnit.setText(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p><span style=\" vertical-align:super;\">o</span></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.lblSampleRoll.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>The roll angle of the sample coordinates from the environment coordinates.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblSampleRoll.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Roll", None))
#if QT_CONFIG(tooltip)
        self.txtSampleRoll.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>The roll angle of the sample coordinates from the enivronment coordinates.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.txtSampleRoll.setText(QCoreApplication.translate("GenericScatteringCalculator", u"0.0", None))
        self.lblSampleRollUnit.setText(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p><span style=\" vertical-align:super;\">o</span></p></body></html>", None))
        self.groupBox_Datafile.setTitle(QCoreApplication.translate("GenericScatteringCalculator", u"SLD Data File", None))
#if QT_CONFIG(tooltip)
        self.lblNucData.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>Nuclear data used to simulate SANS.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblNucData.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Nuclear Data", None))
        self.checkboxNucData.setText("")
#if QT_CONFIG(tooltip)
        self.txtNucData.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"Display name of loaded datafile.", None))
#endif // QT_CONFIG(tooltip)
        self.txtNucData.setText(QCoreApplication.translate("GenericScatteringCalculator", u"No File Loaded", None))
#if QT_CONFIG(tooltip)
        self.cmdNucLoad.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>Only .txt, .sld, .vtk and .pdb datafile formats are supported. </p><p>Load Nuclear sld data.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cmdNucLoad.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Load", None))
#if QT_CONFIG(tooltip)
        self.lblMagData.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>Magnetic data used to simulate SANS.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblMagData.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Magnetic Data", None))
        self.checkboxMagData.setText("")
#if QT_CONFIG(tooltip)
        self.txtMagData.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"Display name of loaded datafile.", None))
#endif // QT_CONFIG(tooltip)
        self.txtMagData.setText(QCoreApplication.translate("GenericScatteringCalculator", u"No File Loaded", None))
#if QT_CONFIG(tooltip)
        self.cmdMagLoad.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>Only .txt, .omf, .vtk and .sld datafile formats are supported. </p><p>Load Magnetic sld data.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cmdMagLoad.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Load", None))
#if QT_CONFIG(tooltip)
        self.lblShape.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>Default shape of the sample.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblShape.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Shape", None))
        self.cbShape.setItemText(0, QCoreApplication.translate("GenericScatteringCalculator", u"Rectangular", None))

#if QT_CONFIG(tooltip)
        self.cbShape.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>Select the default shape of the sample.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.cmdDraw.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>Generate a 3D plot with arrows for the magnetic vectors.</p><p>It is not recommanded for a large number of pixels.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cmdDraw.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Draw", None))
        self.groupBox_InputParam.setTitle(QCoreApplication.translate("GenericScatteringCalculator", u"Input Parameters", None))
        self.label.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Polarisation Settings", None))
#if QT_CONFIG(tooltip)
        self.txtUpFracIn.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>Ratio of spin up/(spin up + spin down) neutrons after the analyzer.</p><p>It must be between 0 and 1.</p><p>It is equal to 0.5 for unpolarized neutrons.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.txtUpFracIn.setText(QCoreApplication.translate("GenericScatteringCalculator", u"1.0", None))
#if QT_CONFIG(tooltip)
        self.lblUpFracOut.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>Ratio of spin up/(spin up + spin down) neutrons before the sample.</p><p>It must be between 0 and 1.</p><p>It is equal to 0.5 for unpolarized neutrons.</p><p>The editing is disabled if data are from .omf, .sld, .pdb files.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblUpFracOut.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Out Polarisation (fraction up)", None))
#if QT_CONFIG(tooltip)
        self.lblUpFracIn.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>Ratio of spin up/(spin up + spin down) neutrons after the analyzer.</p><p>It must be between 0 and 1.</p><p>It is equal to 0.5 for unpolarized neutrons.</p><p>The editing is disabled if data are from .omf, .sld, .pdb files.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblUpFracIn.setText(QCoreApplication.translate("GenericScatteringCalculator", u"In Polarisation (fraction up)", None))
#if QT_CONFIG(tooltip)
        self.txtUpTheta.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>Polarization angle.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.txtUpTheta.setText(QCoreApplication.translate("GenericScatteringCalculator", u"0.0", None))
#if QT_CONFIG(tooltip)
        self.lblUpPhi.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>Polarization angle.</p><p>The editing is disabled if data are from .omf, .sld, .pdb files.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblUpPhi.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Up Polarisation Direction, \u03d5", None))
#if QT_CONFIG(tooltip)
        self.txtUpFracOut.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>Ratio of spin up/(spin up + spin down) neutrons before the sample.</p><p>It must be between 0 and 1.</p><p>It is equal to 0.5 for unpolarized neutrons.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.txtUpFracOut.setText(QCoreApplication.translate("GenericScatteringCalculator", u"1.0", None))
        self.lblUpThetaUnit.setText(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p><span style=\" vertical-align:super;\">o</span></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.lblUpTheta.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>Polarization angle.</p><p>The editing is disabled if data are from .omf, .sld, .pdb files.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblUpTheta.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Up Polarisation Direction, \u03b8", None))
        self.lblUpPhiUnit.setText(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p><span style=\" vertical-align:super;\">o</span></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.txtUpPhi.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>Polarization angle.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.txtUpPhi.setText(QCoreApplication.translate("GenericScatteringCalculator", u"0.0", None))
        self.lbl2.setText(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>cm<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.txtBackground.setText(QCoreApplication.translate("GenericScatteringCalculator", u"0.0", None))
        self.lblScale.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Scale", None))
        self.txtScale.setText(QCoreApplication.translate("GenericScatteringCalculator", u"1.0", None))
        self.lblSolventSLD.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Solvent SLD", None))
#if QT_CONFIG(tooltip)
        self.lblTotalVolume.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"Default total volume calculated from the pixel information (or natural density for pdb file).", None))
#endif // QT_CONFIG(tooltip)
        self.lblTotalVolume.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Total volume", None))
        self.txtSolventSLD.setText(QCoreApplication.translate("GenericScatteringCalculator", u"0.0", None))
#if QT_CONFIG(tooltip)
        self.txtTotalVolume.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>Default total volume calculated from the pixel information (or natural density for pdb file)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.txtTotalVolume.setText(QCoreApplication.translate("GenericScatteringCalculator", u"216000.0", None))
        self.lblBackgd.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Background", None))
        self.lblUnitSolventSLD.setText(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-2</span></p></body></html>", None))
        self.lblUnitVolume.setText(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">3</span></p></body></html>", None))
        self.label_2.setText(QCoreApplication.translate("GenericScatteringCalculator", u"SLD/Geometry Settings", None))
        self.groupBox_SLDPixelInfo.setTitle(QCoreApplication.translate("GenericScatteringCalculator", u"SLD Pixel Info", None))
#if QT_CONFIG(tooltip)
        self.lblNoPixels.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"Number of pixels.\n"
"Not editable.", None))
#endif // QT_CONFIG(tooltip)
        self.lblNoPixels.setText(QCoreApplication.translate("GenericScatteringCalculator", u"No. of Pixels", None))
        self.txtNoPixels.setText(QCoreApplication.translate("GenericScatteringCalculator", u"1000", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("GenericScatteringCalculator", u"Mean SLD", None))
#if QT_CONFIG(tooltip)
        self.lblMx.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>Mean value of M<span style=\" vertical-align:sub;\">x</span> (x-component of the magnetisation vector).</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblMx.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Mx", None))
#if QT_CONFIG(tooltip)
        self.txtMx.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"x component of the magnetization vector in the laboratory xyz frame", None))
#endif // QT_CONFIG(tooltip)
        self.txtMx.setText(QCoreApplication.translate("GenericScatteringCalculator", u"0.0", None))
        self.lblUnitMx.setText(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-2</span></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.lblMy.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>Mean value of My (y-component of the magnetisation vector).</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblMy.setText(QCoreApplication.translate("GenericScatteringCalculator", u"My", None))
#if QT_CONFIG(tooltip)
        self.txtMy.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"y component of the magnetization vector in the laboratory xyz frame", None))
#endif // QT_CONFIG(tooltip)
        self.txtMy.setText(QCoreApplication.translate("GenericScatteringCalculator", u"0.0", None))
        self.lblUnitMy.setText(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-2</span></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.lblMz.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>Mean value of M<span style=\" vertical-align:sub;\">z</span> (z-component of the magnetisation vector).</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblMz.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Mz", None))
#if QT_CONFIG(tooltip)
        self.txtMz.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"z component of the magnetization vector in the laboratory xyz frame", None))
#endif // QT_CONFIG(tooltip)
        self.txtMz.setText(QCoreApplication.translate("GenericScatteringCalculator", u"0.0", None))
        self.lblUnitMz.setText(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-2</span></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.lblNucl.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>Average of the nuclear scattering density.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblNucl.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Nucl.", None))
        self.txtNucl.setText(QCoreApplication.translate("GenericScatteringCalculator", u"6.97e-06", None))
        self.lblUnitNucl.setText(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-2</span></p></body></html>", None))
        self.groupBox_6.setTitle(QCoreApplication.translate("GenericScatteringCalculator", u"Nodes", None))
        self.lblXnodes.setText(QCoreApplication.translate("GenericScatteringCalculator", u"x", None))
        self.txtXnodes.setText(QCoreApplication.translate("GenericScatteringCalculator", u"10", None))
        self.label_ynodes.setText(QCoreApplication.translate("GenericScatteringCalculator", u"y", None))
        self.txtYnodes.setText(QCoreApplication.translate("GenericScatteringCalculator", u"10", None))
        self.label_znodes.setText(QCoreApplication.translate("GenericScatteringCalculator", u"z", None))
        self.txtZnodes.setText(QCoreApplication.translate("GenericScatteringCalculator", u"10", None))
        self.groupBox_Stepsize.setTitle(QCoreApplication.translate("GenericScatteringCalculator", u"Step Size", None))
        self.lblXstepsize.setText(QCoreApplication.translate("GenericScatteringCalculator", u"x", None))
        self.txtXstepsize.setText(QCoreApplication.translate("GenericScatteringCalculator", u"6", None))
        self.lblUnitx.setText(QCoreApplication.translate("GenericScatteringCalculator", u"\u00c5", None))
        self.lblYstepsize.setText(QCoreApplication.translate("GenericScatteringCalculator", u"y", None))
        self.txtYstepsize.setText(QCoreApplication.translate("GenericScatteringCalculator", u"6", None))
        self.lblUnity.setText(QCoreApplication.translate("GenericScatteringCalculator", u"\u00c5", None))
        self.lblZstepsize.setText(QCoreApplication.translate("GenericScatteringCalculator", u"z", None))
        self.txtZstepsize.setText(QCoreApplication.translate("GenericScatteringCalculator", u"6", None))
        self.lblUnitz.setText(QCoreApplication.translate("GenericScatteringCalculator", u"\u00c5", None))
#if QT_CONFIG(tooltip)
        self.cmdDrawpoints.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>Draw a scatter plot for sld profile (without arrows)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cmdDrawpoints.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Draw Points", None))
#if QT_CONFIG(tooltip)
        self.cmdSave.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>Save the sld data as sld format.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cmdSave.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Save SLD Data", None))
#if QT_CONFIG(tooltip)
        self.cmdClose.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"Close the calculator.", None))
#endif // QT_CONFIG(tooltip)
        self.cmdClose.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Close", None))
#if QT_CONFIG(tooltip)
        self.cmdReset.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"Reset the interface to its default values", None))
#endif // QT_CONFIG(tooltip)
        self.cmdReset.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Reset", None))
#if QT_CONFIG(tooltip)
        self.cmdHelp.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"Display 'Help' information about the calculator", None))
#endif // QT_CONFIG(tooltip)
        self.cmdHelp.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Help", None))
#if QT_CONFIG(tooltip)
        self.cmdCompute.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>Compute the scattering pattern and display 1D or 2D plot depending on the settings.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cmdCompute.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Compute", None))
#if QT_CONFIG(tooltip)
        self.lblVerifyError.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"Verification Error", None))
#endif // QT_CONFIG(tooltip)
        self.lblVerifyError.setText("")
        self.groupBox_Qrange.setTitle(QCoreApplication.translate("GenericScatteringCalculator", u"Q Range", None))
        self.txtQxMax.setText(QCoreApplication.translate("GenericScatteringCalculator", u"0.3", None))
        self.lbl5.setText(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.lblQxQyMax.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>Maximum value of Q<span style=\" vertical-align:sub;\">x,y</span>.</p><p>Q<span style=\" vertical-align:sub;\">x,ymax </span>&isin; ]0, 1000].</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblQxQyMax.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Qx (Qy) Max", None))
#if QT_CONFIG(tooltip)
        self.lblNoQBins.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"Number of bins in reciprocal space for the 1D or 2D plot generated by 'Compute'.\n"
"Number of Qbins &isin; [2, 1000].", None))
#endif // QT_CONFIG(tooltip)
        self.lblNoQBins.setText(QCoreApplication.translate("GenericScatteringCalculator", u"No. of Qx (Qy) bins", None))
        self.txtNoQBins.setText(QCoreApplication.translate("GenericScatteringCalculator", u"30", None))
#if QT_CONFIG(tooltip)
        self.lblQxQyMin.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>Minimum value of Q<span style=\" vertical-align:sub;\">x,y </span></p><p>Default Values- 2D: [-1 * QMax]; 1D: [.001 * QMax]; </p><p>Q<span style=\" vertical-align:sub;\">x,ymin </span>\u2208 ]0, 1000].</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblQxQyMin.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Qx (Qy) Min", None))
        self.txtQxMin.setText(QCoreApplication.translate("GenericScatteringCalculator", u"-0.3", None))
        self.lbl6.setText(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.checkboxLogSpace.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>Checking this box will use Log Spacing between the Qx Values rather than Linear Spacing.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.checkboxLogSpace.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Log Spacing", None))
        self.groupbox_RoG.setTitle(QCoreApplication.translate("GenericScatteringCalculator", u"Radius of Gyration", None))
#if QT_CONFIG(tooltip)
        self.lblRgMass.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"Radius of Gyration, calculated with the mass of each atom.", None))
#endif // QT_CONFIG(tooltip)
        self.lblRgMass.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Rg - Mass", None))
        self.txtRgMass.setText(QCoreApplication.translate("GenericScatteringCalculator", u"0", None))
        self.txtRG.setText(QCoreApplication.translate("GenericScatteringCalculator", u"0", None))
#if QT_CONFIG(tooltip)
        self.lblRG.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"Guinier Radius - Radius of Gyration based on Scattering Length Density\n"
"NOTE: Currently not impacted by Solvent SLD ", None))
#endif // QT_CONFIG(tooltip)
        self.lblRG.setText(QCoreApplication.translate("GenericScatteringCalculator", u"RG - SLD", None))
        self.customFit.setTitle(QCoreApplication.translate("GenericScatteringCalculator", u"Plugin Models", None))
        self.checkboxPluginModel.setText(QCoreApplication.translate("GenericScatteringCalculator", u"Export Model", None))
        self.cbOptionsCalc.setItemText(0, QCoreApplication.translate("GenericScatteringCalculator", u"Fixed orientation", None))
        self.cbOptionsCalc.setItemText(1, QCoreApplication.translate("GenericScatteringCalculator", u"Debye full avg.", None))
        self.cbOptionsCalc.setItemText(2, QCoreApplication.translate("GenericScatteringCalculator", u"Debye full avg. w/ \u03b2(Q)", None))

#if QT_CONFIG(tooltip)
        self.cbOptionsCalc.setToolTip(QCoreApplication.translate("GenericScatteringCalculator", u"<html><head/><body><p>Option of orientation to perform calculations:</p><p>- Scattering calculated for fixed orientation &#8594; 2D output</p><p>- Scattering orientation averaged over all orientations &#8594; 1D output</p><p>This choice is only available for pdb files.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

