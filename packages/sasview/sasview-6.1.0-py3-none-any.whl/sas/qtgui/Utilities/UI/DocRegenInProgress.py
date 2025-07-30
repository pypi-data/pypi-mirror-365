# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'DocRegenInProgress.ui'
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
    QTextBrowser, QWidget)

class Ui_DocRegenProgress(object):
    def setupUi(self, DocRegenProgress):
        if not DocRegenProgress.objectName():
            DocRegenProgress.setObjectName(u"DocRegenProgress")
        DocRegenProgress.resize(378, 400)
        self.gridLayout_3 = QGridLayout(DocRegenProgress)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label = QLabel(DocRegenProgress)
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignCenter)

        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)

        self.label1 = QLabel(DocRegenProgress)
        self.label1.setObjectName(u"label1")

        self.gridLayout_3.addWidget(self.label1, 1, 0, 1, 1)

        self.textBrowser = QTextBrowser(DocRegenProgress)
        self.textBrowser.setObjectName(u"textBrowser")

        self.gridLayout_3.addWidget(self.textBrowser, 2, 0, 1, 1)


        self.retranslateUi(DocRegenProgress)

        QMetaObject.connectSlotsByName(DocRegenProgress)
    # setupUi

    def retranslateUi(self, DocRegenProgress):
        DocRegenProgress.setWindowTitle(QCoreApplication.translate("DocRegenProgress", u"Documentation Generation Progress Window", None))
        self.label.setText(QCoreApplication.translate("DocRegenProgress", u"::Documentation Generation In Progress::", None))
        self.label1.setText(QCoreApplication.translate("DocRegenProgress", u"This process may take a few minutes.", None))
    # retranslateUi

