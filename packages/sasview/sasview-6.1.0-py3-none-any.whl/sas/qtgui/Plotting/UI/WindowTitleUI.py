# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'WindowTitleUI.ui'
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
    QGridLayout, QLabel, QLineEdit, QSizePolicy,
    QWidget)

class Ui_WindowTitle(object):
    def setupUi(self, WindowTitle):
        if not WindowTitle.objectName():
            WindowTitle.setObjectName(u"WindowTitle")
        WindowTitle.setWindowModality(Qt.ApplicationModal)
        WindowTitle.resize(287, 137)
        self.gridLayout = QGridLayout(WindowTitle)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(WindowTitle)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.txtTitle = QLineEdit(WindowTitle)
        self.txtTitle.setObjectName(u"txtTitle")

        self.gridLayout.addWidget(self.txtTitle, 0, 1, 1, 1)

        self.buttonBox = QDialogButtonBox(WindowTitle)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 2)


        self.retranslateUi(WindowTitle)
        self.buttonBox.accepted.connect(WindowTitle.accept)
        self.buttonBox.rejected.connect(WindowTitle.reject)

        QMetaObject.connectSlotsByName(WindowTitle)
    # setupUi

    def retranslateUi(self, WindowTitle):
        WindowTitle.setWindowTitle(QCoreApplication.translate("WindowTitle", u"Modify Window Title", None))
        self.label.setText(QCoreApplication.translate("WindowTitle", u"New title", None))
    # retranslateUi

