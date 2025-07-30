# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SlicerParametersUI.ui'
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
    QDialog, QGridLayout, QGroupBox, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QPushButton, QSizePolicy, QSpacerItem,
    QTabWidget, QTableView, QWidget)

class Ui_SlicerParametersUI(object):
    def setupUi(self, SlicerParametersUI):
        if not SlicerParametersUI.objectName():
            SlicerParametersUI.setObjectName(u"SlicerParametersUI")
        SlicerParametersUI.resize(395, 468)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SlicerParametersUI.sizePolicy().hasHeightForWidth())
        SlicerParametersUI.setSizePolicy(sizePolicy)
        icon = QIcon()
        icon.addFile(u":/res/ball.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        SlicerParametersUI.setWindowIcon(icon)
        self.gridLayout_5 = QGridLayout(SlicerParametersUI)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.cmdApply = QPushButton(SlicerParametersUI)
        self.cmdApply.setObjectName(u"cmdApply")

        self.horizontalLayout.addWidget(self.cmdApply)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.cmdClose = QPushButton(SlicerParametersUI)
        self.cmdClose.setObjectName(u"cmdClose")

        self.horizontalLayout.addWidget(self.cmdClose)

        self.cmdHelp = QPushButton(SlicerParametersUI)
        self.cmdHelp.setObjectName(u"cmdHelp")

        self.horizontalLayout.addWidget(self.cmdHelp)


        self.gridLayout_5.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.tabWidget = QTabWidget(SlicerParametersUI)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.gridLayout_2 = QGridLayout(self.tab)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.groupBox = QGroupBox(self.tab)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy1)
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.cbSlicer = QComboBox(self.groupBox)
        self.cbSlicer.addItem("")
        self.cbSlicer.addItem("")
        self.cbSlicer.addItem("")
        self.cbSlicer.addItem("")
        self.cbSlicer.addItem("")
        self.cbSlicer.addItem("")
        self.cbSlicer.addItem("")
        self.cbSlicer.setObjectName(u"cbSlicer")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.cbSlicer.sizePolicy().hasHeightForWidth())
        self.cbSlicer.setSizePolicy(sizePolicy2)

        self.horizontalLayout_2.addWidget(self.cbSlicer)


        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)

        self.lstParams = QTableView(self.groupBox)
        self.lstParams.setObjectName(u"lstParams")
        sizePolicy.setHeightForWidth(self.lstParams.sizePolicy().hasHeightForWidth())
        self.lstParams.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.lstParams, 0, 0, 1, 1)


        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.gridLayout_4 = QGridLayout(self.tab_2)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.groupBox_2 = QGroupBox(self.tab_2)
        self.groupBox_2.setObjectName(u"groupBox_2")
        sizePolicy1.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy1)
        self.gridLayout_6 = QGridLayout(self.groupBox_2)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.lstPlots = QListWidget(self.groupBox_2)
        self.lstPlots.setObjectName(u"lstPlots")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.lstPlots.sizePolicy().hasHeightForWidth())
        self.lstPlots.setSizePolicy(sizePolicy3)
        self.lstPlots.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.lstPlots.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.lstPlots.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.gridLayout_6.addWidget(self.lstPlots, 0, 0, 1, 1)

        self.cbSave1DPlots = QCheckBox(self.groupBox_2)
        self.cbSave1DPlots.setObjectName(u"cbSave1DPlots")

        self.gridLayout_6.addWidget(self.cbSave1DPlots, 1, 0, 1, 1)

        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_2 = QLabel(self.groupBox_2)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_3.addWidget(self.label_2)

        self.txtLocation = QLineEdit(self.groupBox_2)
        self.txtLocation.setObjectName(u"txtLocation")

        self.horizontalLayout_3.addWidget(self.txtLocation)

        self.cmdFiles = QPushButton(self.groupBox_2)
        self.cmdFiles.setObjectName(u"cmdFiles")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.cmdFiles.sizePolicy().hasHeightForWidth())
        self.cmdFiles.setSizePolicy(sizePolicy4)
        self.cmdFiles.setMaximumSize(QSize(20, 21))

        self.horizontalLayout_3.addWidget(self.cmdFiles)

        self.label_4 = QLabel(self.groupBox_2)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_3.addWidget(self.label_4)

        self.cbSaveExt = QComboBox(self.groupBox_2)
        self.cbSaveExt.addItem("")
        self.cbSaveExt.addItem("")
        self.cbSaveExt.addItem("")
        self.cbSaveExt.setObjectName(u"cbSaveExt")

        self.horizontalLayout_3.addWidget(self.cbSaveExt)


        self.gridLayout_3.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.lblExtension = QLabel(self.groupBox_2)
        self.lblExtension.setObjectName(u"lblExtension")

        self.horizontalLayout_5.addWidget(self.lblExtension)

        self.txtExtension = QLineEdit(self.groupBox_2)
        self.txtExtension.setObjectName(u"txtExtension")

        self.horizontalLayout_5.addWidget(self.txtExtension)


        self.gridLayout_3.addLayout(self.horizontalLayout_5, 1, 0, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_4.addWidget(self.label_3)

        self.cbFitOptions = QComboBox(self.groupBox_2)
        self.cbFitOptions.addItem("")
        self.cbFitOptions.addItem("")
        self.cbFitOptions.addItem("")
        self.cbFitOptions.setObjectName(u"cbFitOptions")

        self.horizontalLayout_4.addWidget(self.cbFitOptions)


        self.gridLayout_3.addLayout(self.horizontalLayout_4, 2, 0, 1, 1)


        self.gridLayout_6.addLayout(self.gridLayout_3, 2, 0, 1, 1)


        self.gridLayout_4.addWidget(self.groupBox_2, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_2, "")

        self.gridLayout_5.addWidget(self.tabWidget, 0, 0, 1, 1)

        QWidget.setTabOrder(self.tabWidget, self.lstParams)
        QWidget.setTabOrder(self.lstParams, self.cbSlicer)
        QWidget.setTabOrder(self.cbSlicer, self.cmdApply)
        QWidget.setTabOrder(self.cmdApply, self.cmdClose)
        QWidget.setTabOrder(self.cmdClose, self.cmdHelp)
        QWidget.setTabOrder(self.cmdHelp, self.lstPlots)
        QWidget.setTabOrder(self.lstPlots, self.cbSave1DPlots)
        QWidget.setTabOrder(self.cbSave1DPlots, self.txtLocation)
        QWidget.setTabOrder(self.txtLocation, self.cmdFiles)
        QWidget.setTabOrder(self.cmdFiles, self.cbSaveExt)
        QWidget.setTabOrder(self.cbSaveExt, self.txtExtension)
        QWidget.setTabOrder(self.txtExtension, self.cbFitOptions)

        self.retranslateUi(SlicerParametersUI)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(SlicerParametersUI)
    # setupUi

    def retranslateUi(self, SlicerParametersUI):
        SlicerParametersUI.setWindowTitle(QCoreApplication.translate("SlicerParametersUI", u"Slicer Parameters", None))
#if QT_CONFIG(tooltip)
        self.cmdApply.setToolTip(QCoreApplication.translate("SlicerParametersUI", u"Apply Slicer to Selected Plots", None))
#endif // QT_CONFIG(tooltip)
        self.cmdApply.setText(QCoreApplication.translate("SlicerParametersUI", u"Apply", None))
#if QT_CONFIG(tooltip)
        self.cmdClose.setToolTip(QCoreApplication.translate("SlicerParametersUI", u"Close the dialog", None))
#endif // QT_CONFIG(tooltip)
        self.cmdClose.setText(QCoreApplication.translate("SlicerParametersUI", u"Close", None))
        self.cmdHelp.setText(QCoreApplication.translate("SlicerParametersUI", u"Help", None))
        self.groupBox.setTitle(QCoreApplication.translate("SlicerParametersUI", u"Slicer Parameters ", None))
        self.label.setText(QCoreApplication.translate("SlicerParametersUI", u"Slicer type:", None))
        self.cbSlicer.setItemText(0, QCoreApplication.translate("SlicerParametersUI", u"None", None))
        self.cbSlicer.setItemText(1, QCoreApplication.translate("SlicerParametersUI", u"Sector Interactor", None))
        self.cbSlicer.setItemText(2, QCoreApplication.translate("SlicerParametersUI", u"Annulus Interactor", None))
        self.cbSlicer.setItemText(3, QCoreApplication.translate("SlicerParametersUI", u"Box Interactor X", None))
        self.cbSlicer.setItemText(4, QCoreApplication.translate("SlicerParametersUI", u"Box Interactor Y", None))
        self.cbSlicer.setItemText(5, QCoreApplication.translate("SlicerParametersUI", u"Wedge Interactor Q", None))
        self.cbSlicer.setItemText(6, QCoreApplication.translate("SlicerParametersUI", u"Wedge Interactor Phi", None))

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("SlicerParametersUI", u"Slicer", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("SlicerParametersUI", u"Batch Slicing Options ", None))
        self.cbSave1DPlots.setText(QCoreApplication.translate("SlicerParametersUI", u"Auto save generated 1D plots", None))
        self.label_2.setText(QCoreApplication.translate("SlicerParametersUI", u"Files saved in:", None))
#if QT_CONFIG(tooltip)
        self.txtLocation.setToolTip(QCoreApplication.translate("SlicerParametersUI", u"<html><head/><body><p><br/></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cmdFiles.setText(QCoreApplication.translate("SlicerParametersUI", u"...", None))
        self.label_4.setText(QCoreApplication.translate("SlicerParametersUI", u"as ", None))
        self.cbSaveExt.setItemText(0, QCoreApplication.translate("SlicerParametersUI", u".txt", None))
        self.cbSaveExt.setItemText(1, QCoreApplication.translate("SlicerParametersUI", u".xml", None))
        self.cbSaveExt.setItemText(2, QCoreApplication.translate("SlicerParametersUI", u".h5", None))

        self.lblExtension.setText(QCoreApplication.translate("SlicerParametersUI", u"Append text:", None))
#if QT_CONFIG(tooltip)
        self.txtExtension.setToolTip(QCoreApplication.translate("SlicerParametersUI", u"<html><head/><body><p>Files will be saved as &lt;SlicerType&gt;&lt;FileName&gt;&lt;AppendText&gt;.txt</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_3.setText(QCoreApplication.translate("SlicerParametersUI", u"Fitting Options:", None))
        self.cbFitOptions.setItemText(0, QCoreApplication.translate("SlicerParametersUI", u"No fitting", None))
        self.cbFitOptions.setItemText(1, QCoreApplication.translate("SlicerParametersUI", u"Fitting", None))
        self.cbFitOptions.setItemText(2, QCoreApplication.translate("SlicerParametersUI", u"Batch fitting", None))

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("SlicerParametersUI", u"Batch Slicing", None))
    # retranslateUi

