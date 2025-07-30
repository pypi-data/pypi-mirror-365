# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ComplexConstraintUI.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QSpacerItem, QToolButton,
    QWidget)

class Ui_ComplexConstraintUI(object):
    def setupUi(self, ComplexConstraintUI):
        if not ComplexConstraintUI.objectName():
            ComplexConstraintUI.setObjectName(u"ComplexConstraintUI")
        ComplexConstraintUI.resize(449, 260)
        self.gridLayout_2 = QGridLayout(ComplexConstraintUI)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.groupBox = QGroupBox(ComplexConstraintUI)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.cbModel1 = QComboBox(self.groupBox)
        self.cbModel1.setObjectName(u"cbModel1")

        self.horizontalLayout.addWidget(self.cbModel1)

        self.cbParam1 = QComboBox(self.groupBox)
        self.cbParam1.addItem("")
        self.cbParam1.setObjectName(u"cbParam1")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbParam1.sizePolicy().hasHeightForWidth())
        self.cbParam1.setSizePolicy(sizePolicy)
        self.cbParam1.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.horizontalLayout.addWidget(self.cbParam1)

        self.cbOperator = QComboBox(self.groupBox)
        self.cbOperator.addItem("")
        self.cbOperator.setObjectName(u"cbOperator")

        self.horizontalLayout.addWidget(self.cbOperator)

        self.cbModel2 = QComboBox(self.groupBox)
        self.cbModel2.setObjectName(u"cbModel2")

        self.horizontalLayout.addWidget(self.cbModel2)

        self.cbParam2 = QComboBox(self.groupBox)
        self.cbParam2.addItem("")
        self.cbParam2.setObjectName(u"cbParam2")
        sizePolicy.setHeightForWidth(self.cbParam2.sizePolicy().hasHeightForWidth())
        self.cbParam2.setSizePolicy(sizePolicy)
        self.cbParam2.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.horizontalLayout.addWidget(self.cbParam2)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.txtParam = QLabel(self.groupBox)
        self.txtParam.setObjectName(u"txtParam")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.txtParam.sizePolicy().hasHeightForWidth())
        self.txtParam.setSizePolicy(sizePolicy1)

        self.horizontalLayout_2.addWidget(self.txtParam)

        self.txtOperator = QLabel(self.groupBox)
        self.txtOperator.setObjectName(u"txtOperator")

        self.horizontalLayout_2.addWidget(self.txtOperator)

        self.txtConstraint = QLineEdit(self.groupBox)
        self.txtConstraint.setObjectName(u"txtConstraint")

        self.horizontalLayout_2.addWidget(self.txtConstraint)


        self.gridLayout.addLayout(self.horizontalLayout_2, 2, 0, 1, 1)


        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)

        self.lblWarning = QLabel(ComplexConstraintUI)
        self.lblWarning.setObjectName(u"lblWarning")

        self.gridLayout_2.addWidget(self.lblWarning, 1, 0, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 9, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer_2, 2, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_2 = QSpacerItem(58, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.cmdAddAll = QToolButton(ComplexConstraintUI)
        self.cmdAddAll.setObjectName(u"cmdAddAll")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.cmdAddAll.sizePolicy().hasHeightForWidth())
        self.cmdAddAll.setSizePolicy(sizePolicy2)
        self.cmdAddAll.setMinimumSize(QSize(93, 28))
        self.cmdAddAll.setPopupMode(QToolButton.InstantPopup)
        self.cmdAddAll.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.cmdAddAll.setAutoRaise(False)
        self.cmdAddAll.setArrowType(Qt.DownArrow)

        self.horizontalLayout_3.addWidget(self.cmdAddAll)

        self.cmdOK = QToolButton(ComplexConstraintUI)
        self.cmdOK.setObjectName(u"cmdOK")
        sizePolicy2.setHeightForWidth(self.cmdOK.sizePolicy().hasHeightForWidth())
        self.cmdOK.setSizePolicy(sizePolicy2)
        self.cmdOK.setMinimumSize(QSize(93, 28))
        self.cmdOK.setPopupMode(QToolButton.InstantPopup)
        self.cmdOK.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.cmdOK.setAutoRaise(False)
        self.cmdOK.setArrowType(Qt.DownArrow)

        self.horizontalLayout_3.addWidget(self.cmdOK)

        self.cmdHelp = QPushButton(ComplexConstraintUI)
        self.cmdHelp.setObjectName(u"cmdHelp")

        self.horizontalLayout_3.addWidget(self.cmdHelp)


        self.gridLayout_2.addLayout(self.horizontalLayout_3, 3, 0, 1, 1)


        self.retranslateUi(ComplexConstraintUI)

        QMetaObject.connectSlotsByName(ComplexConstraintUI)
    # setupUi

    def retranslateUi(self, ComplexConstraintUI):
        ComplexConstraintUI.setWindowTitle(QCoreApplication.translate("ComplexConstraintUI", u"Complex Constraint", None))
        self.groupBox.setTitle(QCoreApplication.translate("ComplexConstraintUI", u"2 parameter constraint", None))
        self.cbParam1.setItemText(0, QCoreApplication.translate("ComplexConstraintUI", u"sld", None))

        self.cbOperator.setItemText(0, QCoreApplication.translate("ComplexConstraintUI", u">", None))

        self.cbParam2.setItemText(0, QCoreApplication.translate("ComplexConstraintUI", u"sld_a", None))

        self.label.setText(QCoreApplication.translate("ComplexConstraintUI", u"Edit complex constraint:", None))
        self.txtParam.setText(QCoreApplication.translate("ComplexConstraintUI", u"param1", None))
        self.txtOperator.setText(QCoreApplication.translate("ComplexConstraintUI", u"=", None))
        self.txtConstraint.setText("")
        self.lblWarning.setText(QCoreApplication.translate("ComplexConstraintUI", u"<html><head/><body><p><span style=\" color:#ff0000;\">Warning! Polydisperse parameter selected.<br/></span>Constraints involving polydisperse parameters only apply to<br/>starting values and are not re-applied during size or angle polydispersity<br/>integrations. To do so requires creating a custom model.</p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.cmdAddAll.setToolTip(QCoreApplication.translate("ComplexConstraintUI", u"<html><head/><body><p>Add constraints between all identically named parameters in both fitpages</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cmdAddAll.setText(QCoreApplication.translate("ComplexConstraintUI", u"Add All", None))
#if QT_CONFIG(tooltip)
        self.cmdOK.setToolTip(QCoreApplication.translate("ComplexConstraintUI", u"<html><head/><body><p>Add the constraint as defined by the above expression.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cmdOK.setText(QCoreApplication.translate("ComplexConstraintUI", u"Add", None))
        self.cmdHelp.setText(QCoreApplication.translate("ComplexConstraintUI", u"Help", None))
    # retranslateUi

