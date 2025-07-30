# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'DesignWindowUI.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QSizePolicy, QSpacerItem, QStackedWidget, QTabWidget,
    QWidget)

class Ui_Shape2SAS(object):
    def setupUi(self, Shape2SAS):
        if not Shape2SAS.objectName():
            Shape2SAS.setObjectName(u"Shape2SAS")
        Shape2SAS.resize(1306, 823)
        self.gridLayout = QGridLayout(Shape2SAS)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tabWidget = QTabWidget(Shape2SAS)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setMinimumSize(QSize(783, 600))
        self.model = QWidget()
        self.model.setObjectName(u"model")
        self.tabWidget.addTab(self.model, "")
        self.SAXSExperiment = QWidget()
        self.SAXSExperiment.setObjectName(u"SAXSExperiment")
        self.gridLayout_2 = QGridLayout(self.SAXSExperiment)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.group3 = QGroupBox(self.SAXSExperiment)
        self.group3.setObjectName(u"group3")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.group3.sizePolicy().hasHeightForWidth())
        self.group3.setSizePolicy(sizePolicy)
        self.gridLayout_5 = QGridLayout(self.group3)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout_6 = QGridLayout()
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.verticalSpacer_9 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_6.addItem(self.verticalSpacer_9, 0, 1, 1, 1)

        self.verticalSpacer_8 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_6.addItem(self.verticalSpacer_8, 4, 1, 1, 1)

        self.verticalSpacer_7 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_6.addItem(self.verticalSpacer_7, 2, 1, 1, 1)

        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.horizontalLayout_15.setContentsMargins(-1, 0, -1, 10)
        self.label_38 = QLabel(self.group3)
        self.label_38.setObjectName(u"label_38")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_38.sizePolicy().hasHeightForWidth())
        self.label_38.setSizePolicy(sizePolicy1)

        self.horizontalLayout_15.addWidget(self.label_38)

        self.modelName = QLineEdit(self.group3)
        self.modelName.setObjectName(u"modelName")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.modelName.sizePolicy().hasHeightForWidth())
        self.modelName.setSizePolicy(sizePolicy2)
        self.modelName.setMinimumSize(QSize(139, 22))
        self.modelName.setMaximumSize(QSize(139, 22))

        self.horizontalLayout_15.addWidget(self.modelName)

        self.horizontalLayout_15.setStretch(1, 1)

        self.gridLayout_6.addLayout(self.horizontalLayout_15, 5, 3, 1, 1)

        self.horizontalLayout_18 = QHBoxLayout()
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.horizontalLayout_18.setContentsMargins(-1, 0, -1, 10)
        self.label_33 = QLabel(self.group3)
        self.label_33.setObjectName(u"label_33")
        sizePolicy1.setHeightForWidth(self.label_33.sizePolicy().hasHeightForWidth())
        self.label_33.setSizePolicy(sizePolicy1)

        self.horizontalLayout_18.addWidget(self.label_33)

        self.qMax = QLineEdit(self.group3)
        self.qMax.setObjectName(u"qMax")
        sizePolicy2.setHeightForWidth(self.qMax.sizePolicy().hasHeightForWidth())
        self.qMax.setSizePolicy(sizePolicy2)
        self.qMax.setMinimumSize(QSize(139, 22))
        self.qMax.setMaximumSize(QSize(139, 22))

        self.horizontalLayout_18.addWidget(self.qMax)


        self.gridLayout_6.addLayout(self.horizontalLayout_18, 3, 1, 1, 1)

        self.horizontalLayout_17 = QHBoxLayout()
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.horizontalLayout_17.setContentsMargins(-1, 0, -1, 10)
        self.label_32 = QLabel(self.group3)
        self.label_32.setObjectName(u"label_32")
        sizePolicy1.setHeightForWidth(self.label_32.sizePolicy().hasHeightForWidth())
        self.label_32.setSizePolicy(sizePolicy1)

        self.horizontalLayout_17.addWidget(self.label_32)

        self.qMin = QLineEdit(self.group3)
        self.qMin.setObjectName(u"qMin")
        sizePolicy2.setHeightForWidth(self.qMin.sizePolicy().hasHeightForWidth())
        self.qMin.setSizePolicy(sizePolicy2)
        self.qMin.setMinimumSize(QSize(139, 22))
        self.qMin.setMaximumSize(QSize(139, 22))

        self.horizontalLayout_17.addWidget(self.qMin)


        self.gridLayout_6.addLayout(self.horizontalLayout_17, 1, 1, 1, 1)

        self.horizontalLayout_19 = QHBoxLayout()
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.horizontalLayout_19.setContentsMargins(-1, 0, -1, 10)
        self.label_34 = QLabel(self.group3)
        self.label_34.setObjectName(u"label_34")
        sizePolicy1.setHeightForWidth(self.label_34.sizePolicy().hasHeightForWidth())
        self.label_34.setSizePolicy(sizePolicy1)

        self.horizontalLayout_19.addWidget(self.label_34)

        self.Nq = QLineEdit(self.group3)
        self.Nq.setObjectName(u"Nq")
        sizePolicy2.setHeightForWidth(self.Nq.sizePolicy().hasHeightForWidth())
        self.Nq.setSizePolicy(sizePolicy2)
        self.Nq.setMinimumSize(QSize(139, 22))
        self.Nq.setMaximumSize(QSize(139, 22))

        self.horizontalLayout_19.addWidget(self.Nq)

        self.horizontalLayout_19.setStretch(1, 1)

        self.gridLayout_6.addLayout(self.horizontalLayout_19, 5, 1, 1, 1)

        self.horizontalLayout_16 = QHBoxLayout()
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.horizontalLayout_16.setContentsMargins(-1, 0, -1, 10)
        self.label_35 = QLabel(self.group3)
        self.label_35.setObjectName(u"label_35")
        sizePolicy1.setHeightForWidth(self.label_35.sizePolicy().hasHeightForWidth())
        self.label_35.setSizePolicy(sizePolicy1)

        self.horizontalLayout_16.addWidget(self.label_35)

        self.Npr = QLineEdit(self.group3)
        self.Npr.setObjectName(u"Npr")
        sizePolicy2.setHeightForWidth(self.Npr.sizePolicy().hasHeightForWidth())
        self.Npr.setSizePolicy(sizePolicy2)
        self.Npr.setMinimumSize(QSize(139, 22))
        self.Npr.setMaximumSize(QSize(139, 22))

        self.horizontalLayout_16.addWidget(self.Npr)

        self.horizontalLayout_16.setStretch(1, 1)

        self.gridLayout_6.addLayout(self.horizontalLayout_16, 1, 3, 1, 1)

        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.horizontalLayout_13.setContentsMargins(-1, 0, -1, 10)
        self.label_36 = QLabel(self.group3)
        self.label_36.setObjectName(u"label_36")
        sizePolicy1.setHeightForWidth(self.label_36.sizePolicy().hasHeightForWidth())
        self.label_36.setSizePolicy(sizePolicy1)

        self.horizontalLayout_13.addWidget(self.label_36)

        self.NSimPoints = QLineEdit(self.group3)
        self.NSimPoints.setObjectName(u"NSimPoints")
        sizePolicy2.setHeightForWidth(self.NSimPoints.sizePolicy().hasHeightForWidth())
        self.NSimPoints.setSizePolicy(sizePolicy2)
        self.NSimPoints.setMinimumSize(QSize(139, 22))
        self.NSimPoints.setMaximumSize(QSize(139, 22))

        self.horizontalLayout_13.addWidget(self.NSimPoints)

        self.horizontalLayout_13.setStretch(0, 2)
        self.horizontalLayout_13.setStretch(1, 1)

        self.gridLayout_6.addLayout(self.horizontalLayout_13, 3, 3, 1, 1)

        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_6.addItem(self.horizontalSpacer_7, 1, 4, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_6.addItem(self.horizontalSpacer, 1, 0, 1, 1)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_6.addItem(self.horizontalSpacer_5, 1, 2, 1, 1)

        self.verticalSpacer_10 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_6.addItem(self.verticalSpacer_10, 6, 1, 1, 1)


        self.gridLayout_5.addLayout(self.gridLayout_6, 0, 0, 1, 1)


        self.gridLayout_2.addWidget(self.group3, 1, 0, 1, 2)

        self.group1 = QGroupBox(self.SAXSExperiment)
        self.group1.setObjectName(u"group1")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy3.setHorizontalStretch(5)
        sizePolicy3.setVerticalStretch(5)
        sizePolicy3.setHeightForWidth(self.group1.sizePolicy().hasHeightForWidth())
        self.group1.setSizePolicy(sizePolicy3)
        self.gridLayout_3 = QGridLayout(self.group1)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.verticalSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_4.addItem(self.verticalSpacer, 11, 1, 1, 1)

        self.horizontalSpacer_11 = QSpacerItem(13, 17, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_4.addItem(self.horizontalSpacer_11, 0, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, 0, -1, 0)
        self.label_7 = QLabel(self.group1)
        self.label_7.setObjectName(u"label_7")
        sizePolicy1.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.label_7)

        self.structureFactor = QComboBox(self.group1)
        self.structureFactor.addItem("")
        self.structureFactor.addItem("")
        self.structureFactor.addItem("")
        self.structureFactor.setObjectName(u"structureFactor")
        sizePolicy2.setHeightForWidth(self.structureFactor.sizePolicy().hasHeightForWidth())
        self.structureFactor.setSizePolicy(sizePolicy2)
        self.structureFactor.setMinimumSize(QSize(139, 22))
        self.structureFactor.setMaximumSize(QSize(139, 22))

        self.horizontalLayout.addWidget(self.structureFactor)

        self.horizontalLayout.setStretch(0, 2)
        self.horizontalLayout.setStretch(1, 1)

        self.gridLayout_4.addLayout(self.horizontalLayout, 1, 1, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_4.addItem(self.verticalSpacer_2, 0, 1, 1, 1)

        self.verticalSpacer_5 = QSpacerItem(266, 13, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_4.addItem(self.verticalSpacer_5, 7, 1, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(-1, 10, -1, 10)
        self.label_10 = QLabel(self.group1)
        self.label_10.setObjectName(u"label_10")

        self.horizontalLayout_4.addWidget(self.label_10)

        self.volumeFraction = QLineEdit(self.group1)
        self.volumeFraction.setObjectName(u"volumeFraction")
        sizePolicy2.setHeightForWidth(self.volumeFraction.sizePolicy().hasHeightForWidth())
        self.volumeFraction.setSizePolicy(sizePolicy2)
        self.volumeFraction.setMinimumSize(QSize(139, 22))
        self.volumeFraction.setMaximumSize(QSize(139, 22))

        self.horizontalLayout_4.addWidget(self.volumeFraction)

        self.horizontalSpacer_8 = QSpacerItem(0, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_8)

        self.horizontalLayout_4.setStretch(0, 2)
        self.horizontalLayout_4.setStretch(1, 1)

        self.gridLayout_4.addLayout(self.horizontalLayout_4, 8, 1, 1, 1)

        self.horizontalSpacer_12 = QSpacerItem(13, 17, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_4.addItem(self.horizontalSpacer_12, 0, 2, 1, 1)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(-1, 10, -1, 10)
        self.label_9 = QLabel(self.group1)
        self.label_9.setObjectName(u"label_9")

        self.horizontalLayout_5.addWidget(self.label_9)

        self.exposureTime = QLineEdit(self.group1)
        self.exposureTime.setObjectName(u"exposureTime")
        sizePolicy2.setHeightForWidth(self.exposureTime.sizePolicy().hasHeightForWidth())
        self.exposureTime.setSizePolicy(sizePolicy2)
        self.exposureTime.setMinimumSize(QSize(139, 22))
        self.exposureTime.setMaximumSize(QSize(139, 22))

        self.horizontalLayout_5.addWidget(self.exposureTime)

        self.horizontalSpacer_10 = QSpacerItem(0, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_10)

        self.horizontalLayout_5.setStretch(0, 2)
        self.horizontalLayout_5.setStretch(1, 1)

        self.gridLayout_4.addLayout(self.horizontalLayout_5, 10, 1, 1, 1)

        self.verticalSpacer_3 = QSpacerItem(266, 13, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_4.addItem(self.verticalSpacer_3, 3, 1, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 10, -1, 10)
        self.label_12 = QLabel(self.group1)
        self.label_12.setObjectName(u"label_12")
        sizePolicy1.setHeightForWidth(self.label_12.sizePolicy().hasHeightForWidth())
        self.label_12.setSizePolicy(sizePolicy1)

        self.horizontalLayout_2.addWidget(self.label_12)

        self.interfaceRoughness = QLineEdit(self.group1)
        self.interfaceRoughness.setObjectName(u"interfaceRoughness")
        sizePolicy2.setHeightForWidth(self.interfaceRoughness.sizePolicy().hasHeightForWidth())
        self.interfaceRoughness.setSizePolicy(sizePolicy2)
        self.interfaceRoughness.setMinimumSize(QSize(139, 22))
        self.interfaceRoughness.setMaximumSize(QSize(139, 22))

        self.horizontalLayout_2.addWidget(self.interfaceRoughness)

        self.horizontalSpacer_4 = QSpacerItem(0, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_4)

        self.horizontalLayout_2.setStretch(0, 2)
        self.horizontalLayout_2.setStretch(1, 1)

        self.gridLayout_4.addLayout(self.horizontalLayout_2, 4, 1, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(-1, 10, -1, 10)
        self.label_14 = QLabel(self.group1)
        self.label_14.setObjectName(u"label_14")
        sizePolicy1.setHeightForWidth(self.label_14.sizePolicy().hasHeightForWidth())
        self.label_14.setSizePolicy(sizePolicy1)

        self.horizontalLayout_3.addWidget(self.label_14)

        self.polydispersity = QLineEdit(self.group1)
        self.polydispersity.setObjectName(u"polydispersity")
        sizePolicy2.setHeightForWidth(self.polydispersity.sizePolicy().hasHeightForWidth())
        self.polydispersity.setSizePolicy(sizePolicy2)
        self.polydispersity.setMinimumSize(QSize(139, 22))
        self.polydispersity.setMaximumSize(QSize(139, 22))

        self.horizontalLayout_3.addWidget(self.polydispersity)

        self.horizontalSpacer_6 = QSpacerItem(0, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_6)

        self.horizontalLayout_3.setStretch(0, 2)
        self.horizontalLayout_3.setStretch(1, 1)

        self.gridLayout_4.addLayout(self.horizontalLayout_3, 6, 1, 1, 1)

        self.stackedWidget = QStackedWidget(self.group1)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setMinimumSize(QSize(0, 100))
        self.stackedWidget.setMaximumSize(QSize(160000, 100))
        self.stackedWidget.setFrameShape(QFrame.NoFrame)
        self.stackedWidget.setLineWidth(1)
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.stackedWidget.addWidget(self.page)
        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")
        self.horizontalLayoutWidget_6 = QWidget(self.page_3)
        self.horizontalLayoutWidget_6.setObjectName(u"horizontalLayoutWidget_6")
        self.horizontalLayoutWidget_6.setGeometry(QRect(0, 10, 269, 33))
        self.horizontalLayout_6 = QHBoxLayout(self.horizontalLayoutWidget_6)
        self.horizontalLayout_6.setSpacing(0)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.label_1 = QLabel(self.horizontalLayoutWidget_6)
        self.label_1.setObjectName(u"label_1")
        sizePolicy1.setHeightForWidth(self.label_1.sizePolicy().hasHeightForWidth())
        self.label_1.setSizePolicy(sizePolicy1)

        self.horizontalLayout_6.addWidget(self.label_1)

        self.hardSphereRadius = QLineEdit(self.horizontalLayoutWidget_6)
        self.hardSphereRadius.setObjectName(u"hardSphereRadius")
        sizePolicy2.setHeightForWidth(self.hardSphereRadius.sizePolicy().hasHeightForWidth())
        self.hardSphereRadius.setSizePolicy(sizePolicy2)
        self.hardSphereRadius.setMinimumSize(QSize(139, 22))
        self.hardSphereRadius.setMaximumSize(QSize(139, 22))

        self.horizontalLayout_6.addWidget(self.hardSphereRadius)

        self.horizontalSpacer_3 = QSpacerItem(0, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_3)

        self.horizontalLayout_6.setStretch(0, 2)
        self.stackedWidget.addWidget(self.page_3)
        self.page_4 = QWidget()
        self.page_4.setObjectName(u"page_4")
        self.horizontalLayoutWidget_9 = QWidget(self.page_4)
        self.horizontalLayoutWidget_9.setObjectName(u"horizontalLayoutWidget_9")
        self.horizontalLayoutWidget_9.setGeometry(QRect(0, 0, 269, 33))
        self.horizontalLayout_10 = QHBoxLayout(self.horizontalLayoutWidget_9)
        self.horizontalLayout_10.setSpacing(0)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.label_5 = QLabel(self.horizontalLayoutWidget_9)
        self.label_5.setObjectName(u"label_5")
        sizePolicy1.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy1)

        self.horizontalLayout_10.addWidget(self.label_5)

        self.EffctiveRadius = QLineEdit(self.horizontalLayoutWidget_9)
        self.EffctiveRadius.setObjectName(u"EffctiveRadius")
        sizePolicy2.setHeightForWidth(self.EffctiveRadius.sizePolicy().hasHeightForWidth())
        self.EffctiveRadius.setSizePolicy(sizePolicy2)
        self.EffctiveRadius.setMinimumSize(QSize(139, 22))
        self.EffctiveRadius.setMaximumSize(QSize(139, 22))

        self.horizontalLayout_10.addWidget(self.EffctiveRadius)

        self.horizontalLayoutWidget_10 = QWidget(self.page_4)
        self.horizontalLayoutWidget_10.setObjectName(u"horizontalLayoutWidget_10")
        self.horizontalLayoutWidget_10.setGeometry(QRect(0, 30, 274, 33))
        self.horizontalLayout_11 = QHBoxLayout(self.horizontalLayoutWidget_10)
        self.horizontalLayout_11.setSpacing(0)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.label_8 = QLabel(self.horizontalLayoutWidget_10)
        self.label_8.setObjectName(u"label_8")
        sizePolicy1.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy1)

        self.horizontalLayout_11.addWidget(self.label_8)

        self.particlePerAggregate = QLineEdit(self.horizontalLayoutWidget_10)
        self.particlePerAggregate.setObjectName(u"particlePerAggregate")
        sizePolicy2.setHeightForWidth(self.particlePerAggregate.sizePolicy().hasHeightForWidth())
        self.particlePerAggregate.setSizePolicy(sizePolicy2)
        self.particlePerAggregate.setMinimumSize(QSize(139, 22))
        self.particlePerAggregate.setMaximumSize(QSize(139, 22))

        self.horizontalLayout_11.addWidget(self.particlePerAggregate)

        self.horizontalLayoutWidget_8 = QWidget(self.page_4)
        self.horizontalLayoutWidget_8.setObjectName(u"horizontalLayoutWidget_8")
        self.horizontalLayoutWidget_8.setGeometry(QRect(0, 60, 269, 33))
        self.horizontalLayout_8 = QHBoxLayout(self.horizontalLayoutWidget_8)
        self.horizontalLayout_8.setSpacing(0)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.label_3 = QLabel(self.horizontalLayoutWidget_8)
        self.label_3.setObjectName(u"label_3")
        sizePolicy1.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy1)

        self.horizontalLayout_8.addWidget(self.label_3)

        self.aggregateFrac = QLineEdit(self.horizontalLayoutWidget_8)
        self.aggregateFrac.setObjectName(u"aggregateFrac")
        sizePolicy2.setHeightForWidth(self.aggregateFrac.sizePolicy().hasHeightForWidth())
        self.aggregateFrac.setSizePolicy(sizePolicy2)
        self.aggregateFrac.setMinimumSize(QSize(139, 22))
        self.aggregateFrac.setMaximumSize(QSize(139, 22))

        self.horizontalLayout_8.addWidget(self.aggregateFrac)

        self.stackedWidget.addWidget(self.page_4)

        self.gridLayout_4.addWidget(self.stackedWidget, 2, 1, 1, 1)

        self.verticalSpacer_6 = QSpacerItem(266, 13, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_4.addItem(self.verticalSpacer_6, 9, 1, 1, 1)

        self.verticalSpacer_4 = QSpacerItem(266, 13, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_4.addItem(self.verticalSpacer_4, 5, 1, 1, 1)


        self.gridLayout_3.addLayout(self.gridLayout_4, 0, 0, 1, 1)


        self.gridLayout_2.addWidget(self.group1, 0, 0, 1, 1)

        self.group2 = QGroupBox(self.SAXSExperiment)
        self.group2.setObjectName(u"group2")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy4.setHorizontalStretch(7)
        sizePolicy4.setVerticalStretch(5)
        sizePolicy4.setHeightForWidth(self.group2.sizePolicy().hasHeightForWidth())
        self.group2.setSizePolicy(sizePolicy4)

        self.gridLayout_2.addWidget(self.group2, 0, 1, 1, 1)

        self.tabWidget.addTab(self.SAXSExperiment, "")

        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)


        self.retranslateUi(Shape2SAS)

        self.tabWidget.setCurrentIndex(0)
        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Shape2SAS)
    # setupUi

    def retranslateUi(self, Shape2SAS):
        Shape2SAS.setWindowTitle(QCoreApplication.translate("Shape2SAS", u"Shape2SAS", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.model), QCoreApplication.translate("Shape2SAS", u"Build Model", None))
        self.group3.setTitle(QCoreApplication.translate("Shape2SAS", u"Simulation parameters", None))
        self.label_38.setText(QCoreApplication.translate("Shape2SAS", u"Model Name", None))
#if QT_CONFIG(tooltip)
        self.modelName.setToolTip(QCoreApplication.translate("Shape2SAS", u"<html><head/><body><p>File name to the simulated data send to Data Explorer.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.modelName.setText(QCoreApplication.translate("Shape2SAS", u"Model_1", None))
        self.label_33.setText(QCoreApplication.translate("Shape2SAS", u"q max", None))
#if QT_CONFIG(tooltip)
        self.qMax.setToolTip(QCoreApplication.translate("Shape2SAS", u"<html><head/><body><p>Last q-value over the simulated q-range</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.qMax.setText(QCoreApplication.translate("Shape2SAS", u"0.5", None))
        self.label_32.setText(QCoreApplication.translate("Shape2SAS", u"q min", None))
#if QT_CONFIG(tooltip)
        self.qMin.setToolTip(QCoreApplication.translate("Shape2SAS", u"<html><head/><body><p>Start q-value over the simulated q-range</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.qMin.setText(QCoreApplication.translate("Shape2SAS", u"0.001", None))
        self.label_34.setText(QCoreApplication.translate("Shape2SAS", u"Number of points in q", None))
#if QT_CONFIG(tooltip)
        self.Nq.setToolTip(QCoreApplication.translate("Shape2SAS", u"<html><head/><body><p>Number of q-values over the q-range from q min to q max</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Nq.setText(QCoreApplication.translate("Shape2SAS", u"400", None))
        self.label_35.setText(QCoreApplication.translate("Shape2SAS", u"Number of points in p(r)", None))
#if QT_CONFIG(tooltip)
        self.Npr.setToolTip(QCoreApplication.translate("Shape2SAS", u"<html><head/><body><p>Number of points in the pair distance distribution.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Npr.setText(QCoreApplication.translate("Shape2SAS", u"100", None))
        self.label_36.setText(QCoreApplication.translate("Shape2SAS", u"Number of simulated points", None))
#if QT_CONFIG(tooltip)
        self.NSimPoints.setToolTip(QCoreApplication.translate("Shape2SAS", u"<html><head/><body><p>Number of points in the model used to calculate the scattering profile.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.NSimPoints.setText(QCoreApplication.translate("Shape2SAS", u"3000", None))
        self.group1.setTitle(QCoreApplication.translate("Shape2SAS", u"Scattering parameters", None))
        self.label_7.setText(QCoreApplication.translate("Shape2SAS", u"Structure factor", None))
        self.structureFactor.setItemText(0, QCoreApplication.translate("Shape2SAS", u"None", None))
        self.structureFactor.setItemText(1, QCoreApplication.translate("Shape2SAS", u"Hard Sphere", None))
        self.structureFactor.setItemText(2, QCoreApplication.translate("Shape2SAS", u"Aggregation", None))

#if QT_CONFIG(tooltip)
        self.structureFactor.setToolTip(QCoreApplication.translate("Shape2SAS", u"<html><head/><body><p>Select a structure factor (default: None).</p><p>Hard sphere: hard sphere structure factor, repulsion in concentrated sample<br/></p><p>Aggregate: aggregate structure factor, 2-dimensional fractal aggregate.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_10.setText(QCoreApplication.translate("Shape2SAS", u"Volume fraction", None))
#if QT_CONFIG(tooltip)
        self.volumeFraction.setToolTip(QCoreApplication.translate("Shape2SAS", u"Volume fraction (concentration)", None))
#endif // QT_CONFIG(tooltip)
        self.volumeFraction.setText(QCoreApplication.translate("Shape2SAS", u"0.02", None))
        self.label_9.setText(QCoreApplication.translate("Shape2SAS", u"Relative exposure time", None))
#if QT_CONFIG(tooltip)
        self.exposureTime.setToolTip(QCoreApplication.translate("Shape2SAS", u"<html><head/><body><p>The exposure time is normalised out in the simulated intensity, but it will affect the noise level of data.</p><p>Typical values when using default model parameters: synchrotron SAXS: 100-500, home-source SAXS: 10-50.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.exposureTime.setText(QCoreApplication.translate("Shape2SAS", u"500", None))
        self.label_12.setText(QCoreApplication.translate("Shape2SAS", u"Interface roughness", None))
#if QT_CONFIG(tooltip)
        self.interfaceRoughness.setToolTip(QCoreApplication.translate("Shape2SAS", u"Interface roughness for non-sharp edges between subunits. Min: 0.0 (no roughness), max: 15.0", None))
#endif // QT_CONFIG(tooltip)
        self.interfaceRoughness.setText(QCoreApplication.translate("Shape2SAS", u"0.0", None))
        self.label_14.setText(QCoreApplication.translate("Shape2SAS", u"Relative polydispersity", None))
#if QT_CONFIG(tooltip)
        self.polydispersity.setToolTip(QCoreApplication.translate("Shape2SAS", u"Relative polydispersity. Min: 0.0 (monodisperse), max: 0.3", None))
#endif // QT_CONFIG(tooltip)
        self.polydispersity.setText(QCoreApplication.translate("Shape2SAS", u"0.0", None))
        self.label_1.setText(QCoreApplication.translate("Shape2SAS", u"Hard sphere radius", None))
#if QT_CONFIG(tooltip)
        self.hardSphereRadius.setToolTip(QCoreApplication.translate("Shape2SAS", u"<html><head/><body><p>Hard sphere interaction radius</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.hardSphereRadius.setText(QCoreApplication.translate("Shape2SAS", u"50.0", None))
        self.label_5.setText(QCoreApplication.translate("Shape2SAS", u"Effective radius", None))
#if QT_CONFIG(tooltip)
        self.EffctiveRadius.setToolTip(QCoreApplication.translate("Shape2SAS", u"<html><head/><body><p>Effective radius of each particle in aggregate.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.EffctiveRadius.setText(QCoreApplication.translate("Shape2SAS", u"50.0", None))
        self.label_8.setText(QCoreApplication.translate("Shape2SAS", u"Particles per aggregate", None))
#if QT_CONFIG(tooltip)
        self.particlePerAggregate.setToolTip(QCoreApplication.translate("Shape2SAS", u"<html><head/><body><p>Number of particles per aggregate.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.particlePerAggregate.setText(QCoreApplication.translate("Shape2SAS", u"80.0", None))
        self.label_3.setText(QCoreApplication.translate("Shape2SAS", u"Fraction of aggregate", None))
#if QT_CONFIG(tooltip)
        self.aggregateFrac.setToolTip(QCoreApplication.translate("Shape2SAS", u"<html><head/><body><p>Fraction of particles that are in aggregated form.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.aggregateFrac.setText(QCoreApplication.translate("Shape2SAS", u"0.1", None))
        self.group2.setTitle(QCoreApplication.translate("Shape2SAS", u"Scattering plot", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.SAXSExperiment), QCoreApplication.translate("Shape2SAS", u"Virtual SAXS Experiment", None))
    # retranslateUi

