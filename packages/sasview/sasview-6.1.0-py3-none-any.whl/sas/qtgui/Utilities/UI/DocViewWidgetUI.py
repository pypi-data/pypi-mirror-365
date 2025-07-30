# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'DocViewWidgetUI.ui'
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
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QPushButton,
    QSizePolicy, QSpacerItem, QWidget)

class Ui_DocViewerWindow(object):
    def setupUi(self, DocViewerWindow):
        if not DocViewerWindow.objectName():
            DocViewerWindow.setObjectName(u"DocViewerWindow")
        DocViewerWindow.setWindowModality(Qt.NonModal)
        DocViewerWindow.resize(983, 832)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DocViewerWindow.sizePolicy().hasHeightForWidth())
        DocViewerWindow.setSizePolicy(sizePolicy)
        DocViewerWindow.setMinimumSize(QSize(30, 30))
        self.gridLayout = QGridLayout(DocViewerWindow)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.editButton = QPushButton(DocViewerWindow)
        self.editButton.setObjectName(u"editButton")
        self.editButton.setMinimumSize(QSize(100, 0))

        self.horizontalLayout.addWidget(self.editButton)

        self.closeButton = QPushButton(DocViewerWindow)
        self.closeButton.setObjectName(u"closeButton")
        self.closeButton.setMinimumSize(QSize(100, 0))

        self.horizontalLayout.addWidget(self.closeButton)


        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 1)

        self.webEngineViewer = QWebEngineView(DocViewerWindow)
        self.webEngineViewer.setObjectName(u"webEngineViewer")
        sizePolicy.setHeightForWidth(self.webEngineViewer.sizePolicy().hasHeightForWidth())
        self.webEngineViewer.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.webEngineViewer, 1, 0, 1, 1)


        self.retranslateUi(DocViewerWindow)

        QMetaObject.connectSlotsByName(DocViewerWindow)
    # setupUi

    def retranslateUi(self, DocViewerWindow):
        DocViewerWindow.setWindowTitle(QCoreApplication.translate("DocViewerWindow", u"docViewerWindow", None))
        self.editButton.setText(QCoreApplication.translate("DocViewerWindow", u"Edit", None))
        self.closeButton.setText(QCoreApplication.translate("DocViewerWindow", u"Close", None))
    # retranslateUi

