# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MultiConstraintUI.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QWidget)

class Ui_MultiConstraintUI(object):
    def setupUi(self, MultiConstraintUI):
        if not MultiConstraintUI.objectName():
            MultiConstraintUI.setObjectName(u"MultiConstraintUI")
        MultiConstraintUI.setWindowModality(Qt.ApplicationModal)
        MultiConstraintUI.resize(435, 233)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MultiConstraintUI.sizePolicy().hasHeightForWidth())
        MultiConstraintUI.setSizePolicy(sizePolicy)
        MultiConstraintUI.setModal(True)
        self.gridLayout = QGridLayout(MultiConstraintUI)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.txtParam1 = QLabel(MultiConstraintUI)
        self.txtParam1.setObjectName(u"txtParam1")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.txtParam1.sizePolicy().hasHeightForWidth())
        self.txtParam1.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.txtParam1)

        self.label = QLabel(MultiConstraintUI)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.txtParam2 = QLabel(MultiConstraintUI)
        self.txtParam2.setObjectName(u"txtParam2")
        sizePolicy1.setHeightForWidth(self.txtParam2.sizePolicy().hasHeightForWidth())
        self.txtParam2.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.txtParam2)

        self.label_3 = QLabel(MultiConstraintUI)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout.addWidget(self.label_3)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.cmdRevert = QPushButton(MultiConstraintUI)
        self.cmdRevert.setObjectName(u"cmdRevert")

        self.horizontalLayout.addWidget(self.cmdRevert)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.txtParam1_2 = QLabel(MultiConstraintUI)
        self.txtParam1_2.setObjectName(u"txtParam1_2")
        sizePolicy1.setHeightForWidth(self.txtParam1_2.sizePolicy().hasHeightForWidth())
        self.txtParam1_2.setSizePolicy(sizePolicy1)

        self.horizontalLayout_3.addWidget(self.txtParam1_2)

        self.label_2 = QLabel(MultiConstraintUI)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_3.addWidget(self.label_2)

        self.txtConstraint = QLineEdit(MultiConstraintUI)
        self.txtConstraint.setObjectName(u"txtConstraint")

        self.horizontalLayout_3.addWidget(self.txtConstraint)


        self.gridLayout.addLayout(self.horizontalLayout_3, 1, 0, 1, 1)

        self.lblWarning = QLabel(MultiConstraintUI)
        self.lblWarning.setObjectName(u"lblWarning")

        self.gridLayout.addWidget(self.lblWarning, 2, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 35, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 3, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.cmdOK = QPushButton(MultiConstraintUI)
        self.cmdOK.setObjectName(u"cmdOK")

        self.horizontalLayout_2.addWidget(self.cmdOK)

        self.cmdCancel = QPushButton(MultiConstraintUI)
        self.cmdCancel.setObjectName(u"cmdCancel")

        self.horizontalLayout_2.addWidget(self.cmdCancel)

        self.cmdHelp = QPushButton(MultiConstraintUI)
        self.cmdHelp.setObjectName(u"cmdHelp")

        self.horizontalLayout_2.addWidget(self.cmdHelp)


        self.gridLayout.addLayout(self.horizontalLayout_2, 4, 0, 1, 1)


        self.retranslateUi(MultiConstraintUI)
        self.cmdCancel.clicked.connect(MultiConstraintUI.reject)
        self.cmdOK.clicked.connect(MultiConstraintUI.accept)

        self.cmdOK.setDefault(False)


        QMetaObject.connectSlotsByName(MultiConstraintUI)
    # setupUi

    def retranslateUi(self, MultiConstraintUI):
        MultiConstraintUI.setWindowTitle(QCoreApplication.translate("MultiConstraintUI", u"2 parameter constraint", None))
        self.txtParam1.setText(QCoreApplication.translate("MultiConstraintUI", u"<html><head/><body><p><span style=\" font-weight:600;\">parameter1</span></p></body></html>", None))
        self.label.setText(QCoreApplication.translate("MultiConstraintUI", u"<html><head/><body><p><span style=\" font-weight:600;\">= function(</span></p></body></html>", None))
        self.txtParam2.setText(QCoreApplication.translate("MultiConstraintUI", u"<html><head/><body><p><span style=\" font-weight:600;\">parameter2</span></p></body></html>", None))
        self.label_3.setText(QCoreApplication.translate("MultiConstraintUI", u"<html><head/><body><p><span style=\" font-weight:600;\">)</span></p></body></html>", None))
        self.cmdRevert.setText(QCoreApplication.translate("MultiConstraintUI", u"Swap", None))
        self.txtParam1_2.setText(QCoreApplication.translate("MultiConstraintUI", u"parameter1", None))
        self.label_2.setText(QCoreApplication.translate("MultiConstraintUI", u"=", None))
        self.lblWarning.setText(QCoreApplication.translate("MultiConstraintUI", u"<html><head/><body><p><span style=\" color:#ff0000;\">Warning! Polydisperse parameter selected.<br/></span>Constraints involving polydisperse parameters only apply to<br/>starting values and are not re-applied during size or angle polydispersity<br/>integrations. To do so requires creating a custom model.</p></body></html>", None))
        self.cmdOK.setText(QCoreApplication.translate("MultiConstraintUI", u"OK", None))
        self.cmdCancel.setText(QCoreApplication.translate("MultiConstraintUI", u"Cancel", None))
        self.cmdHelp.setText(QCoreApplication.translate("MultiConstraintUI", u"Help", None))
    # retranslateUi

