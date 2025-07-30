# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'FittingWidgetUI.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QComboBox,
    QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
    QLabel, QPushButton, QSizePolicy, QSpacerItem,
    QTabWidget, QTreeView, QVBoxLayout, QWidget)

class Ui_FittingWidgetUI(object):
    def setupUi(self, FittingWidgetUI):
        if not FittingWidgetUI.objectName():
            FittingWidgetUI.setObjectName(u"FittingWidgetUI")
        FittingWidgetUI.resize(540, 600)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(FittingWidgetUI.sizePolicy().hasHeightForWidth())
        FittingWidgetUI.setSizePolicy(sizePolicy)
        FittingWidgetUI.setMinimumSize(QSize(445, 540))
        self.gridLayout_5 = QGridLayout(FittingWidgetUI)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer = QSpacerItem(273, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.cmdPlot = QPushButton(FittingWidgetUI)
        self.cmdPlot.setObjectName(u"cmdPlot")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.cmdPlot.sizePolicy().hasHeightForWidth())
        self.cmdPlot.setSizePolicy(sizePolicy1)
        self.cmdPlot.setMinimumSize(QSize(93, 28))

        self.horizontalLayout_3.addWidget(self.cmdPlot)

        self.cmdFit = QPushButton(FittingWidgetUI)
        self.cmdFit.setObjectName(u"cmdFit")
        sizePolicy1.setHeightForWidth(self.cmdFit.sizePolicy().hasHeightForWidth())
        self.cmdFit.setSizePolicy(sizePolicy1)
        self.cmdFit.setMinimumSize(QSize(93, 28))

        self.horizontalLayout_3.addWidget(self.cmdFit)

        self.cmdHelp = QPushButton(FittingWidgetUI)
        self.cmdHelp.setObjectName(u"cmdHelp")
        sizePolicy1.setHeightForWidth(self.cmdHelp.sizePolicy().hasHeightForWidth())
        self.cmdHelp.setSizePolicy(sizePolicy1)
        self.cmdHelp.setMinimumSize(QSize(93, 28))

        self.horizontalLayout_3.addWidget(self.cmdHelp)


        self.gridLayout_5.addLayout(self.horizontalLayout_3, 2, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(FittingWidgetUI)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.cbFileNames = QComboBox(FittingWidgetUI)
        self.cbFileNames.setObjectName(u"cbFileNames")
        self.cbFileNames.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.gridLayout_3.addWidget(self.cbFileNames, 0, 0, 1, 1)

        self.lblFilename = QLabel(FittingWidgetUI)
        self.lblFilename.setObjectName(u"lblFilename")

        self.gridLayout_3.addWidget(self.lblFilename, 0, 1, 1, 1)


        self.horizontalLayout.addLayout(self.gridLayout_3)

        self.horizontalSpacer_4 = QSpacerItem(459, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_4)


        self.gridLayout_5.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.tabFitting = QTabWidget(FittingWidgetUI)
        self.tabFitting.setObjectName(u"tabFitting")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.gridLayout_4 = QGridLayout(self.tab_3)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.groupBox_6 = QGroupBox(self.tab_3)
        self.groupBox_6.setObjectName(u"groupBox_6")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.groupBox_6.sizePolicy().hasHeightForWidth())
        self.groupBox_6.setSizePolicy(sizePolicy2)
        self.gridLayout_2 = QGridLayout(self.groupBox_6)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_2 = QLabel(self.groupBox_6)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)

        self.lblModel = QLabel(self.groupBox_6)
        self.lblModel.setObjectName(u"lblModel")

        self.gridLayout.addWidget(self.lblModel, 0, 1, 1, 1)

        self.lblStructure = QLabel(self.groupBox_6)
        self.lblStructure.setObjectName(u"lblStructure")

        self.gridLayout.addWidget(self.lblStructure, 0, 2, 1, 1)

        self.cbCategory = QComboBox(self.groupBox_6)
        self.cbCategory.setObjectName(u"cbCategory")

        self.gridLayout.addWidget(self.cbCategory, 1, 0, 1, 1)

        self.cbModel = QComboBox(self.groupBox_6)
        self.cbModel.setObjectName(u"cbModel")

        self.gridLayout.addWidget(self.cbModel, 1, 1, 1, 1)

        self.cbStructureFactor = QComboBox(self.groupBox_6)
        self.cbStructureFactor.setObjectName(u"cbStructureFactor")

        self.gridLayout.addWidget(self.cbStructureFactor, 1, 2, 1, 1)


        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.lstParams = QTreeView(self.groupBox_6)
        self.lstParams.setObjectName(u"lstParams")
        self.lstParams.setStyleSheet(u"")
        self.lstParams.setEditTriggers(QAbstractItemView.CurrentChanged|QAbstractItemView.DoubleClicked|QAbstractItemView.EditKeyPressed|QAbstractItemView.SelectedClicked)
        self.lstParams.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.gridLayout_2.addWidget(self.lstParams, 1, 0, 1, 1)


        self.gridLayout_4.addWidget(self.groupBox_6, 0, 0, 1, 4)

        self.groupBox_7 = QGroupBox(self.tab_3)
        self.groupBox_7.setObjectName(u"groupBox_7")
        self.verticalLayout = QVBoxLayout(self.groupBox_7)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.chkPolydispersity = QCheckBox(self.groupBox_7)
        self.chkPolydispersity.setObjectName(u"chkPolydispersity")
        self.chkPolydispersity.setEnabled(True)
        self.chkPolydispersity.setCheckable(True)

        self.verticalLayout.addWidget(self.chkPolydispersity)

        self.chk2DView = QCheckBox(self.groupBox_7)
        self.chk2DView.setObjectName(u"chk2DView")
        self.chk2DView.setEnabled(True)
        self.chk2DView.setCheckable(True)

        self.verticalLayout.addWidget(self.chk2DView)

        self.chkMagnetism = QCheckBox(self.groupBox_7)
        self.chkMagnetism.setObjectName(u"chkMagnetism")
        self.chkMagnetism.setEnabled(True)
        self.chkMagnetism.setCheckable(True)

        self.verticalLayout.addWidget(self.chkMagnetism)

        self.chkChainFit = QCheckBox(self.groupBox_7)
        self.chkChainFit.setObjectName(u"chkChainFit")
        self.chkChainFit.setEnabled(True)
        self.chkChainFit.setCheckable(True)

        self.verticalLayout.addWidget(self.chkChainFit)


        self.gridLayout_4.addWidget(self.groupBox_7, 1, 0, 1, 1)

        self.groupBox_8 = QGroupBox(self.tab_3)
        self.groupBox_8.setObjectName(u"groupBox_8")
        self.gridLayout_17 = QGridLayout(self.groupBox_8)
        self.gridLayout_17.setObjectName(u"gridLayout_17")
        self.gridLayout_8 = QGridLayout()
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.label_16 = QLabel(self.groupBox_8)
        self.label_16.setObjectName(u"label_16")

        self.gridLayout_8.addWidget(self.label_16, 0, 0, 1, 1)

        self.lblMinRangeDef = QLabel(self.groupBox_8)
        self.lblMinRangeDef.setObjectName(u"lblMinRangeDef")

        self.gridLayout_8.addWidget(self.lblMinRangeDef, 0, 1, 1, 1)

        self.label_17 = QLabel(self.groupBox_8)
        self.label_17.setObjectName(u"label_17")

        self.gridLayout_8.addWidget(self.label_17, 0, 2, 1, 1)

        self.label_18 = QLabel(self.groupBox_8)
        self.label_18.setObjectName(u"label_18")

        self.gridLayout_8.addWidget(self.label_18, 1, 0, 1, 1)

        self.lblMaxRangeDef = QLabel(self.groupBox_8)
        self.lblMaxRangeDef.setObjectName(u"lblMaxRangeDef")

        self.gridLayout_8.addWidget(self.lblMaxRangeDef, 1, 1, 1, 1)

        self.label_19 = QLabel(self.groupBox_8)
        self.label_19.setObjectName(u"label_19")

        self.gridLayout_8.addWidget(self.label_19, 1, 2, 1, 1)


        self.gridLayout_17.addLayout(self.gridLayout_8, 0, 0, 1, 2)

        self.label_20 = QLabel(self.groupBox_8)
        self.label_20.setObjectName(u"label_20")

        self.gridLayout_17.addWidget(self.label_20, 1, 0, 1, 1)

        self.lblCurrentSmearing = QLabel(self.groupBox_8)
        self.lblCurrentSmearing.setObjectName(u"lblCurrentSmearing")

        self.gridLayout_17.addWidget(self.lblCurrentSmearing, 1, 1, 1, 1)


        self.gridLayout_4.addWidget(self.groupBox_8, 1, 1, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(207, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_3, 1, 2, 1, 1)

        self.groupBox_9 = QGroupBox(self.tab_3)
        self.groupBox_9.setObjectName(u"groupBox_9")
        self.gridLayout_18 = QGridLayout(self.groupBox_9)
        self.gridLayout_18.setObjectName(u"gridLayout_18")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_23 = QLabel(self.groupBox_9)
        self.label_23.setObjectName(u"label_23")

        self.horizontalLayout_2.addWidget(self.label_23)

        self.lblChi2Value = QLabel(self.groupBox_9)
        self.lblChi2Value.setObjectName(u"lblChi2Value")

        self.horizontalLayout_2.addWidget(self.lblChi2Value)


        self.gridLayout_18.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)


        self.gridLayout_4.addWidget(self.groupBox_9, 1, 3, 1, 1)

        self.tabFitting.addTab(self.tab_3, "")
        self.tabOptions = QWidget()
        self.tabOptions.setObjectName(u"tabOptions")
        self.tabFitting.addTab(self.tabOptions, "")
        self.tabResolution = QWidget()
        self.tabResolution.setObjectName(u"tabResolution")
        self.tabFitting.addTab(self.tabResolution, "")
        self.tabPolydispersity = QWidget()
        self.tabPolydispersity.setObjectName(u"tabPolydispersity")
        self.tabPolydispersity.setEnabled(False)
        self.tabFitting.addTab(self.tabPolydispersity, "")
        self.tabMagnetism = QWidget()
        self.tabMagnetism.setObjectName(u"tabMagnetism")
        self.tabMagnetism.setEnabled(False)
        self.tabFitting.addTab(self.tabMagnetism, "")
        self.tabOrder = QWidget()
        self.tabOrder.setObjectName(u"tabOrder")
        self.tabFitting.addTab(self.tabOrder, "")

        self.gridLayout_5.addWidget(self.tabFitting, 1, 0, 1, 1)

        QWidget.setTabOrder(self.cbFileNames, self.tabFitting)
        QWidget.setTabOrder(self.tabFitting, self.cbCategory)
        QWidget.setTabOrder(self.cbCategory, self.cbModel)
        QWidget.setTabOrder(self.cbModel, self.cbStructureFactor)
        QWidget.setTabOrder(self.cbStructureFactor, self.lstParams)
        QWidget.setTabOrder(self.lstParams, self.chkPolydispersity)
        QWidget.setTabOrder(self.chkPolydispersity, self.chk2DView)
        QWidget.setTabOrder(self.chk2DView, self.chkMagnetism)
        QWidget.setTabOrder(self.chkMagnetism, self.chkChainFit)
        QWidget.setTabOrder(self.chkChainFit, self.cmdPlot)
        QWidget.setTabOrder(self.cmdPlot, self.cmdFit)
        QWidget.setTabOrder(self.cmdFit, self.cmdHelp)

        self.retranslateUi(FittingWidgetUI)

        self.tabFitting.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(FittingWidgetUI)
    # setupUi

    def retranslateUi(self, FittingWidgetUI):
        FittingWidgetUI.setWindowTitle(QCoreApplication.translate("FittingWidgetUI", u"FittingWidget", None))
#if QT_CONFIG(tooltip)
        self.cmdPlot.setToolTip(QCoreApplication.translate("FittingWidgetUI", u"<html><head/><body><p>Perform a single computation of the model using the parameters as-entered and subsequently plot the result.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cmdPlot.setText(QCoreApplication.translate("FittingWidgetUI", u"Compute/Plot", None))
        self.cmdFit.setText(QCoreApplication.translate("FittingWidgetUI", u"Fit", None))
        self.cmdHelp.setText(QCoreApplication.translate("FittingWidgetUI", u"Help", None))
        self.label.setText(QCoreApplication.translate("FittingWidgetUI", u"File name:", None))
#if QT_CONFIG(tooltip)
        self.cbFileNames.setToolTip(QCoreApplication.translate("FittingWidgetUI", u"<html><head/><body><p>Choose a file to set initial fit parameters.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblFilename.setText(QCoreApplication.translate("FittingWidgetUI", u"None", None))
        self.groupBox_6.setTitle(QCoreApplication.translate("FittingWidgetUI", u"Model ", None))
        self.label_2.setText(QCoreApplication.translate("FittingWidgetUI", u"Category", None))
        self.lblModel.setText(QCoreApplication.translate("FittingWidgetUI", u"Model name", None))
        self.lblStructure.setText(QCoreApplication.translate("FittingWidgetUI", u"Structure factor", None))
#if QT_CONFIG(tooltip)
        self.cbCategory.setToolTip(QCoreApplication.translate("FittingWidgetUI", u"Select a category", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.cbModel.setToolTip(QCoreApplication.translate("FittingWidgetUI", u"Select a model", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.cbStructureFactor.setToolTip(QCoreApplication.translate("FittingWidgetUI", u"Select a structure factor", None))
#endif // QT_CONFIG(tooltip)
        self.groupBox_7.setTitle(QCoreApplication.translate("FittingWidgetUI", u"Options ", None))
#if QT_CONFIG(tooltip)
        self.chkPolydispersity.setToolTip(QCoreApplication.translate("FittingWidgetUI", u"<html><head/><body><p>Switch on orientational polydispersity.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.chkPolydispersity.setText(QCoreApplication.translate("FittingWidgetUI", u"Polydispersity", None))
#if QT_CONFIG(tooltip)
        self.chk2DView.setToolTip(QCoreApplication.translate("FittingWidgetUI", u"<html><head/><body><p>Switch on 2D view of the model.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.chk2DView.setText(QCoreApplication.translate("FittingWidgetUI", u"2D view", None))
#if QT_CONFIG(tooltip)
        self.chkMagnetism.setToolTip(QCoreApplication.translate("FittingWidgetUI", u"<html><head/><body><p>Switch on magnetic scattering parameters.</p><p>This option is available only for 2D models.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.chkMagnetism.setText(QCoreApplication.translate("FittingWidgetUI", u"Magnetism", None))
#if QT_CONFIG(tooltip)
        self.chkChainFit.setToolTip(QCoreApplication.translate("FittingWidgetUI", u"<html><head/><body><p>Switch on Chain Fitting (parameter reuse) for batch datasets.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.chkChainFit.setText(QCoreApplication.translate("FittingWidgetUI", u"Chain fit", None))
        self.groupBox_8.setTitle(QCoreApplication.translate("FittingWidgetUI", u"Fitting details ", None))
        self.label_16.setText(QCoreApplication.translate("FittingWidgetUI", u"Min range", None))
        self.lblMinRangeDef.setText(QCoreApplication.translate("FittingWidgetUI", u"0.005", None))
        self.label_17.setText(QCoreApplication.translate("FittingWidgetUI", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.label_18.setText(QCoreApplication.translate("FittingWidgetUI", u"Max range", None))
        self.lblMaxRangeDef.setText(QCoreApplication.translate("FittingWidgetUI", u"0.1", None))
        self.label_19.setText(QCoreApplication.translate("FittingWidgetUI", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.label_20.setText(QCoreApplication.translate("FittingWidgetUI", u"Smearing:", None))
        self.lblCurrentSmearing.setText(QCoreApplication.translate("FittingWidgetUI", u"None", None))
#if QT_CONFIG(tooltip)
        self.groupBox_9.setToolTip(QCoreApplication.translate("FittingWidgetUI", u"<html><head/><body><p>\u03c7<span style=\" vertical-align:super;\">2</span>/DOF (DOF=N<span style=\" vertical-align:sub;\">pts</span>-N<span style=\" vertical-align:sub;\">par</span> fitted)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.groupBox_9.setTitle(QCoreApplication.translate("FittingWidgetUI", u"Fitting error", None))
        self.label_23.setText(QCoreApplication.translate("FittingWidgetUI", u"<html><head/><body><p><span style=\" font-weight:600;\">\u03c7</span><span style=\" font-weight:600; vertical-align:super;\">2</span></p></body></html>", None))
        self.lblChi2Value.setText(QCoreApplication.translate("FittingWidgetUI", u"<html><head/><body><p><span style=\" font-weight:600;\">0.01625</span></p></body></html>", None))
        self.tabFitting.setTabText(self.tabFitting.indexOf(self.tab_3), QCoreApplication.translate("FittingWidgetUI", u"Model", None))
        self.tabFitting.setTabText(self.tabFitting.indexOf(self.tabOptions), QCoreApplication.translate("FittingWidgetUI", u"Fit Options", None))
        self.tabFitting.setTabText(self.tabFitting.indexOf(self.tabResolution), QCoreApplication.translate("FittingWidgetUI", u"Resolution", None))
        self.tabFitting.setTabText(self.tabFitting.indexOf(self.tabPolydispersity), QCoreApplication.translate("FittingWidgetUI", u"Polydispersity", None))
        self.tabFitting.setTabText(self.tabFitting.indexOf(self.tabMagnetism), QCoreApplication.translate("FittingWidgetUI", u"Magnetism", None))
        self.tabFitting.setTabText(self.tabFitting.indexOf(self.tabOrder), QCoreApplication.translate("FittingWidgetUI", u"Order", None))
    # retranslateUi

