# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'GPUTestResultsUI.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QSizePolicy, QSpacerItem, QTextEdit, QWidget)

class Ui_GPUTestResults(object):
    def setupUi(self, GPUTestResults):
        if not GPUTestResults.objectName():
            GPUTestResults.setObjectName(u"GPUTestResults")
        GPUTestResults.resize(487, 532)
        icon = QIcon()
        icon.addFile(u"../../../UI/res/ball.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        GPUTestResults.setWindowIcon(icon)
        self.gridLayout_3 = QGridLayout(GPUTestResults)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.TestResultsBox = QGroupBox(GPUTestResults)
        self.TestResultsBox.setObjectName(u"TestResultsBox")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.TestResultsBox.sizePolicy().hasHeightForWidth())
        self.TestResultsBox.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(self.TestResultsBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.resultsText = QTextEdit(self.TestResultsBox)
        self.resultsText.setObjectName(u"resultsText")
        sizePolicy.setHeightForWidth(self.resultsText.sizePolicy().hasHeightForWidth())
        self.resultsText.setSizePolicy(sizePolicy)
        self.resultsText.setMinimumSize(QSize(300, 300))
        self.resultsText.setReadOnly(True)

        self.gridLayout.addWidget(self.resultsText, 0, 0, 1, 1)


        self.gridLayout_2.addWidget(self.TestResultsBox, 0, 0, 1, 1)

        self.falingTestsNoOpenCL = QLabel(GPUTestResults)
        self.falingTestsNoOpenCL.setObjectName(u"falingTestsNoOpenCL")
        self.falingTestsNoOpenCL.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.falingTestsNoOpenCL, 1, 0, 1, 1)

        self.howToReportIssues = QLabel(GPUTestResults)
        self.howToReportIssues.setObjectName(u"howToReportIssues")
        self.howToReportIssues.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.howToReportIssues.setWordWrap(True)

        self.gridLayout_2.addWidget(self.howToReportIssues, 2, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(218, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.okButton = QDialogButtonBox(GPUTestResults)
        self.okButton.setObjectName(u"okButton")
        self.okButton.setOrientation(Qt.Horizontal)
        self.okButton.setStandardButtons(QDialogButtonBox.Ok)
        self.okButton.setCenterButtons(False)

        self.horizontalLayout.addWidget(self.okButton)


        self.gridLayout_2.addLayout(self.horizontalLayout, 3, 0, 1, 1)


        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 0, 1, 1)


        self.retranslateUi(GPUTestResults)
        self.okButton.accepted.connect(GPUTestResults.accept)
        self.okButton.rejected.connect(GPUTestResults.reject)

        QMetaObject.connectSlotsByName(GPUTestResults)
    # setupUi

    def retranslateUi(self, GPUTestResults):
        GPUTestResults.setWindowTitle(QCoreApplication.translate("GPUTestResults", u"OpenCL Test Results", None))
        self.TestResultsBox.setTitle(QCoreApplication.translate("GPUTestResults", u"OpenCL test results", None))
        self.falingTestsNoOpenCL.setText(QCoreApplication.translate("GPUTestResults", u"If tests fail on OpenCL devices, please select the No OpenCL option.", None))
        self.howToReportIssues.setText(QCoreApplication.translate("GPUTestResults", u"In the case where many tests are failing, please consider sending the above report to help@sasview.org.", None))
    # retranslateUi

