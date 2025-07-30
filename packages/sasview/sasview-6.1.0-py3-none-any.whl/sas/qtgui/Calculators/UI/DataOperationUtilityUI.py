# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'DataOperationUtilityUI.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QGraphicsView,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QSpacerItem,
    QWidget)

class Ui_DataOperationUtility(object):
    def setupUi(self, DataOperationUtility):
        if not DataOperationUtility.objectName():
            DataOperationUtility.setObjectName(u"DataOperationUtility")
        DataOperationUtility.resize(951, 425)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DataOperationUtility.sizePolicy().hasHeightForWidth())
        DataOperationUtility.setSizePolicy(sizePolicy)
        DataOperationUtility.setMinimumSize(QSize(951, 425))
        DataOperationUtility.setMaximumSize(QSize(951, 425))
        icon = QIcon()
        icon.addFile(u":/res/ball.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        DataOperationUtility.setWindowIcon(icon)
        self.gridLayout_3 = QGridLayout(DataOperationUtility)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.groupBox = QGroupBox(DataOperationUtility)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy1)
        self.groupBox.setMinimumSize(QSize(870, 361))
        self.groupBox.setMaximumSize(QSize(950, 400))
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.lblOutputDataName = QLabel(self.groupBox)
        self.lblOutputDataName.setObjectName(u"lblOutputDataName")

        self.gridLayout.addWidget(self.lblOutputDataName, 0, 0, 1, 1)

        self.lblData2OrNumber = QLabel(self.groupBox)
        self.lblData2OrNumber.setObjectName(u"lblData2OrNumber")

        self.gridLayout.addWidget(self.lblData2OrNumber, 0, 8, 1, 1)

        self.lblBigEqual = QLabel(self.groupBox)
        self.lblBigEqual.setObjectName(u"lblBigEqual")
        self.lblBigEqual.setMinimumSize(QSize(21, 21))
        self.lblBigEqual.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lblBigEqual, 3, 2, 1, 1)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_5, 3, 7, 1, 1)

        self.graphOutput = QGraphicsView(self.groupBox)
        self.graphOutput.setObjectName(u"graphOutput")
        self.graphOutput.setMinimumSize(QSize(260, 260))
        self.graphOutput.setMaximumSize(QSize(300, 300))
        self.graphOutput.setFocusPolicy(Qt.NoFocus)

        self.gridLayout.addWidget(self.graphOutput, 3, 0, 1, 1)

        self.cbData1 = QComboBox(self.groupBox)
        self.cbData1.addItem("")
        self.cbData1.setObjectName(u"cbData1")
        self.cbData1.setMinimumSize(QSize(170, 26))
        self.cbData1.setMaximumSize(QSize(200, 30))
        self.cbData1.setBaseSize(QSize(0, 26))
        self.cbData1.setEditable(False)

        self.gridLayout.addWidget(self.cbData1, 1, 4, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_3, 3, 5, 1, 1)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_4, 3, 3, 1, 1)

        self.lblData1 = QLabel(self.groupBox)
        self.lblData1.setObjectName(u"lblData1")

        self.gridLayout.addWidget(self.lblData1, 0, 4, 1, 1)

        self.txtOutputData = QLineEdit(self.groupBox)
        self.txtOutputData.setObjectName(u"txtOutputData")
        self.txtOutputData.setMinimumSize(QSize(260, 21))
        self.txtOutputData.setMaximumSize(QSize(300, 30))

        self.gridLayout.addWidget(self.txtOutputData, 1, 0, 1, 1)

        self.graphData1 = QGraphicsView(self.groupBox)
        self.graphData1.setObjectName(u"graphData1")
        self.graphData1.setMinimumSize(QSize(260, 260))
        self.graphData1.setMaximumSize(QSize(300, 300))
        self.graphData1.setFocusPolicy(Qt.NoFocus)

        self.gridLayout.addWidget(self.graphData1, 3, 4, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 3, 1, 1, 1)

        self.lblEqual = QLabel(self.groupBox)
        self.lblEqual.setObjectName(u"lblEqual")
        self.lblEqual.setMinimumSize(QSize(21, 21))
        self.lblEqual.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lblEqual, 1, 2, 1, 1)

        self.txtNumber = QLineEdit(self.groupBox)
        self.txtNumber.setObjectName(u"txtNumber")
        self.txtNumber.setEnabled(False)
        self.txtNumber.setMinimumSize(QSize(50, 21))
        self.txtNumber.setMaximumSize(QSize(150, 30))

        self.gridLayout.addWidget(self.txtNumber, 1, 9, 1, 1)

        self.lblOperatorApplied = QLabel(self.groupBox)
        self.lblOperatorApplied.setObjectName(u"lblOperatorApplied")
        self.lblOperatorApplied.setMinimumSize(QSize(21, 21))
        self.lblOperatorApplied.setAlignment(Qt.AlignCenter)
        self.lblOperatorApplied.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextEditable)

        self.gridLayout.addWidget(self.lblOperatorApplied, 3, 6, 1, 1)

        self.cbData2 = QComboBox(self.groupBox)
        self.cbData2.addItem("")
        self.cbData2.setObjectName(u"cbData2")
        self.cbData2.setMinimumSize(QSize(170, 26))
        self.cbData2.setMaximumSize(QSize(200, 30))
        self.cbData2.setEditable(False)

        self.gridLayout.addWidget(self.cbData2, 1, 8, 1, 1)

        self.cbOperator = QComboBox(self.groupBox)
        self.cbOperator.addItem("")
        self.cbOperator.addItem("")
        self.cbOperator.addItem("")
        self.cbOperator.addItem("")
        self.cbOperator.addItem("")
        self.cbOperator.setObjectName(u"cbOperator")
        self.cbOperator.setMinimumSize(QSize(51, 26))
        self.cbOperator.setMaximumSize(QSize(60, 30))

        self.gridLayout.addWidget(self.cbOperator, 1, 6, 1, 1)

        self.graphData2 = QGraphicsView(self.groupBox)
        self.graphData2.setObjectName(u"graphData2")
        self.graphData2.setMinimumSize(QSize(260, 260))
        self.graphData2.setMaximumSize(QSize(300, 300))
        self.graphData2.setFocusPolicy(Qt.NoFocus)

        self.gridLayout.addWidget(self.graphData2, 3, 8, 1, 2)


        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)


        self.gridLayout_3.addWidget(self.groupBox, 0, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.cmdReset = QPushButton(DataOperationUtility)
        self.cmdReset.setObjectName(u"cmdReset")
        self.cmdReset.setMinimumSize(QSize(75, 25))
        self.cmdReset.setAutoDefault(False)

        self.horizontalLayout.addWidget(self.cmdReset)

        self.cmdCompute = QPushButton(DataOperationUtility)
        self.cmdCompute.setObjectName(u"cmdCompute")
        self.cmdCompute.setMinimumSize(QSize(75, 25))
        self.cmdCompute.setAutoDefault(False)

        self.horizontalLayout.addWidget(self.cmdCompute)

        self.cmdClose = QPushButton(DataOperationUtility)
        self.cmdClose.setObjectName(u"cmdClose")
        self.cmdClose.setMinimumSize(QSize(75, 25))
        self.cmdClose.setAutoDefault(False)

        self.horizontalLayout.addWidget(self.cmdClose)

        self.cmdHelp = QPushButton(DataOperationUtility)
        self.cmdHelp.setObjectName(u"cmdHelp")
        self.cmdHelp.setMinimumSize(QSize(75, 25))
        self.cmdHelp.setAutoDefault(False)

        self.horizontalLayout.addWidget(self.cmdHelp)


        self.gridLayout_3.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        QWidget.setTabOrder(self.txtOutputData, self.cbData1)
        QWidget.setTabOrder(self.cbData1, self.cbOperator)
        QWidget.setTabOrder(self.cbOperator, self.cbData2)
        QWidget.setTabOrder(self.cbData2, self.txtNumber)
        QWidget.setTabOrder(self.txtNumber, self.graphOutput)
        QWidget.setTabOrder(self.graphOutput, self.graphData1)
        QWidget.setTabOrder(self.graphData1, self.graphData2)
        QWidget.setTabOrder(self.graphData2, self.cmdReset)
        QWidget.setTabOrder(self.cmdReset, self.cmdCompute)
        QWidget.setTabOrder(self.cmdCompute, self.cmdClose)
        QWidget.setTabOrder(self.cmdClose, self.cmdHelp)

        self.retranslateUi(DataOperationUtility)

        QMetaObject.connectSlotsByName(DataOperationUtility)
    # setupUi

    def retranslateUi(self, DataOperationUtility):
        DataOperationUtility.setWindowTitle(QCoreApplication.translate("DataOperationUtility", u"Data Operation", None))
        self.groupBox.setTitle(QCoreApplication.translate("DataOperationUtility", u"Data Operation [ + (add); - (subtract); * (multiply); / (divide); | (append)]", None))
        self.lblOutputDataName.setText(QCoreApplication.translate("DataOperationUtility", u"Output Data Name", None))
        self.lblData2OrNumber.setText(QCoreApplication.translate("DataOperationUtility", u"Data2 (or Number)", None))
        self.lblBigEqual.setText(QCoreApplication.translate("DataOperationUtility", u"=", None))
        self.cbData1.setItemText(0, QCoreApplication.translate("DataOperationUtility", u"No Data Available", None))

        self.lblData1.setText(QCoreApplication.translate("DataOperationUtility", u"Data1", None))
        self.txtOutputData.setText(QCoreApplication.translate("DataOperationUtility", u"MyNewDataName", None))
        self.lblEqual.setText(QCoreApplication.translate("DataOperationUtility", u"=", None))
#if QT_CONFIG(tooltip)
        self.txtNumber.setToolTip(QCoreApplication.translate("DataOperationUtility", u"If no Data2 loaded, enter a number to be applied to Data1 using the operator", None))
#endif // QT_CONFIG(tooltip)
        self.txtNumber.setText(QCoreApplication.translate("DataOperationUtility", u"1.0", None))
        self.lblOperatorApplied.setText(QCoreApplication.translate("DataOperationUtility", u"+", None))
        self.cbData2.setItemText(0, QCoreApplication.translate("DataOperationUtility", u"No Data Available", None))

        self.cbOperator.setItemText(0, QCoreApplication.translate("DataOperationUtility", u"+", None))
        self.cbOperator.setItemText(1, QCoreApplication.translate("DataOperationUtility", u"-", None))
        self.cbOperator.setItemText(2, QCoreApplication.translate("DataOperationUtility", u"*", None))
        self.cbOperator.setItemText(3, QCoreApplication.translate("DataOperationUtility", u"/", None))
        self.cbOperator.setItemText(4, QCoreApplication.translate("DataOperationUtility", u"|", None))

#if QT_CONFIG(tooltip)
        self.cbOperator.setToolTip(QCoreApplication.translate("DataOperationUtility", u"Add: +\n"
"Subtract: - \n"
"Multiply: *\n"
"Divide: /\n"
"Append(Combine): |", None))
#endif // QT_CONFIG(tooltip)
        self.cmdReset.setText(QCoreApplication.translate("DataOperationUtility", u"Reset", None))
#if QT_CONFIG(tooltip)
        self.cmdCompute.setToolTip(QCoreApplication.translate("DataOperationUtility", u"Generate the Data and send to Data Explorer.", None))
#endif // QT_CONFIG(tooltip)
        self.cmdCompute.setText(QCoreApplication.translate("DataOperationUtility", u"Compute", None))
#if QT_CONFIG(tooltip)
        self.cmdClose.setToolTip(QCoreApplication.translate("DataOperationUtility", u"Close this panel.", None))
#endif // QT_CONFIG(tooltip)
        self.cmdClose.setText(QCoreApplication.translate("DataOperationUtility", u"Close", None))
#if QT_CONFIG(tooltip)
        self.cmdHelp.setToolTip(QCoreApplication.translate("DataOperationUtility", u"Get help on Data Operations.", None))
#endif // QT_CONFIG(tooltip)
        self.cmdHelp.setText(QCoreApplication.translate("DataOperationUtility", u"Help", None))
    # retranslateUi

