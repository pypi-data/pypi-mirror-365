# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'KiessigPanel.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QWidget)

class Ui_KiessigPanel(object):
    def setupUi(self, KiessigPanel):
        if not KiessigPanel.objectName():
            KiessigPanel.setObjectName(u"KiessigPanel")
        KiessigPanel.resize(392, 209)
        KiessigPanel.setFocusPolicy(Qt.TabFocus)
        icon = QIcon()
        icon.addFile(u":/res/ball.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        KiessigPanel.setWindowIcon(icon)
        self.gridLayout_3 = QGridLayout(KiessigPanel)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.groupBox = QGroupBox(KiessigPanel)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.deltaq_in = QLineEdit(self.groupBox)
        self.deltaq_in.setObjectName(u"deltaq_in")
        self.deltaq_in.setMinimumSize(QSize(77, 21))
        self.deltaq_in.setBaseSize(QSize(77, 21))

        self.horizontalLayout.addWidget(self.deltaq_in)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout.addWidget(self.label_2)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)


        self.gridLayout_3.addWidget(self.groupBox, 0, 0, 1, 3)

        self.groupBox_2 = QGroupBox(KiessigPanel)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_2 = QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_2.addWidget(self.label_3)

        self.lengthscale_out = QLineEdit(self.groupBox_2)
        self.lengthscale_out.setObjectName(u"lengthscale_out")
        self.lengthscale_out.setMinimumSize(QSize(77, 21))
        self.lengthscale_out.setBaseSize(QSize(77, 21))
        self.lengthscale_out.setReadOnly(True)

        self.horizontalLayout_2.addWidget(self.lengthscale_out)

        self.label_4 = QLabel(self.groupBox_2)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_2.addWidget(self.label_4)


        self.gridLayout_2.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)


        self.gridLayout_3.addWidget(self.groupBox_2, 1, 0, 1, 3)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer, 2, 2, 1, 1)

        self.closeButton = QPushButton(KiessigPanel)
        self.closeButton.setObjectName(u"closeButton")

        self.gridLayout_3.addWidget(self.closeButton, 3, 1, 1, 1)

        self.helpButton = QPushButton(KiessigPanel)
        self.helpButton.setObjectName(u"helpButton")

        self.gridLayout_3.addWidget(self.helpButton, 3, 2, 1, 1)

        QWidget.setTabOrder(self.deltaq_in, self.lengthscale_out)
        QWidget.setTabOrder(self.lengthscale_out, self.closeButton)
        QWidget.setTabOrder(self.closeButton, self.helpButton)

        self.retranslateUi(KiessigPanel)

        QMetaObject.connectSlotsByName(KiessigPanel)
    # setupUi

    def retranslateUi(self, KiessigPanel):
        KiessigPanel.setWindowTitle(QCoreApplication.translate("KiessigPanel", u"Dialog", None))
#if QT_CONFIG(tooltip)
        KiessigPanel.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.groupBox.setTitle(QCoreApplication.translate("KiessigPanel", u"Input", None))
        self.label.setText(QCoreApplication.translate("KiessigPanel", u"Kiessig Fringe Width (Delta Q)", None))
        self.label_2.setText(QCoreApplication.translate("KiessigPanel", u"1/\u00c5", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("KiessigPanel", u"Output", None))
        self.label_3.setText(QCoreApplication.translate("KiessigPanel", u"Thickness (or Diameter)               ", None))
        self.label_4.setText(QCoreApplication.translate("KiessigPanel", u"   \u00c5", None))
#if QT_CONFIG(tooltip)
        self.closeButton.setToolTip(QCoreApplication.translate("KiessigPanel", u"<html><head/><body><p>Close this window.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.closeButton.setText(QCoreApplication.translate("KiessigPanel", u"Close", None))
#if QT_CONFIG(tooltip)
        self.helpButton.setToolTip(QCoreApplication.translate("KiessigPanel", u"<html><head/><body><p>Help using the Kiessing fringe calculator.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.helpButton.setText(QCoreApplication.translate("KiessigPanel", u"Help", None))
    # retranslateUi

