# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'variableTableUI.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QHeaderView,
    QLabel, QLayout, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QTableView, QVBoxLayout,
    QWidget)

class Ui_VariableTable(object):
    def setupUi(self, VariableTable):
        if not VariableTable.objectName():
            VariableTable.setObjectName(u"VariableTable")
        VariableTable.resize(232, 600)
        VariableTable.setMinimumSize(QSize(232, 0))
        VariableTable.setMaximumSize(QSize(232, 16777215))
        self.gridLayout = QGridLayout(VariableTable)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tableView = QTableView(VariableTable)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setMinimumSize(QSize(230, 300))
        self.tableView.setMaximumSize(QSize(230, 16777215))

        self.verticalLayout.addWidget(self.tableView)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_5)

        self.setConstraints = QPushButton(VariableTable)
        self.setConstraints.setObjectName(u"setConstraints")
        self.setConstraints.setMinimumSize(QSize(150, 30))
        self.setConstraints.setMaximumSize(QSize(150, 30))

        self.horizontalLayout_5.addWidget(self.setConstraints)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_6)


        self.verticalLayout_5.addLayout(self.horizontalLayout_5)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_5.addItem(self.verticalSpacer)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setSpacing(0)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalSpacer_7 = QSpacerItem(20, 24, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_7)

        self.label_3 = QLabel(VariableTable)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMinimumSize(QSize(75, 24))
        self.label_3.setMaximumSize(QSize(75, 24))

        self.horizontalLayout_6.addWidget(self.label_3)

        self.pluginModelName = QLineEdit(VariableTable)
        self.pluginModelName.setObjectName(u"pluginModelName")
        self.pluginModelName.setMinimumSize(QSize(130, 24))
        self.pluginModelName.setMaximumSize(QSize(130, 24))

        self.horizontalLayout_6.addWidget(self.pluginModelName)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_8)


        self.verticalLayout_5.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer = QSpacerItem(20, 24, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.label = QLabel(VariableTable)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(75, 24))
        self.label.setMaximumSize(QSize(75, 24))

        self.horizontalLayout_4.addWidget(self.label)

        self.Npoints = QLineEdit(VariableTable)
        self.Npoints.setObjectName(u"Npoints")
        self.Npoints.setMinimumSize(QSize(130, 24))
        self.Npoints.setMaximumSize(QSize(130, 24))

        self.horizontalLayout_4.addWidget(self.Npoints)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_2)


        self.verticalLayout_5.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_3 = QSpacerItem(20, 24, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.label_2 = QLabel(VariableTable)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(75, 24))
        self.label_2.setMaximumSize(QSize(75, 24))

        self.horizontalLayout_3.addWidget(self.label_2)

        self.prPoints = QLineEdit(VariableTable)
        self.prPoints.setObjectName(u"prPoints")
        self.prPoints.setMinimumSize(QSize(130, 24))
        self.prPoints.setMaximumSize(QSize(130, 24))

        self.horizontalLayout_3.addWidget(self.prPoints)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_4)


        self.verticalLayout_5.addLayout(self.horizontalLayout_3)


        self.verticalLayout.addLayout(self.verticalLayout_5)

        self.verticalSpacer_2 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(u"gridLayout_2")

        self.verticalLayout.addLayout(self.gridLayout_2)


        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)


        self.retranslateUi(VariableTable)

        QMetaObject.connectSlotsByName(VariableTable)
    # setupUi

    def retranslateUi(self, VariableTable):
        VariableTable.setWindowTitle(QCoreApplication.translate("VariableTable", u"Widget", None))
#if QT_CONFIG(tooltip)
        self.tableView.setToolTip(QCoreApplication.translate("VariableTable", u"Check a parameter to include as a fit parameter in the plugin model.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.setConstraints.setToolTip(QCoreApplication.translate("VariableTable", u"Set underlying constraints to the subunits", None))
#endif // QT_CONFIG(tooltip)
        self.setConstraints.setText(QCoreApplication.translate("VariableTable", u"Set Constraints", None))
        self.label_3.setText(QCoreApplication.translate("VariableTable", u"Model Name", None))
#if QT_CONFIG(tooltip)
        self.pluginModelName.setToolTip(QCoreApplication.translate("VariableTable", u"Name to plugin model", None))
#endif // QT_CONFIG(tooltip)
        self.pluginModelName.setText(QCoreApplication.translate("VariableTable", u"Model_1", None))
        self.label.setText(QCoreApplication.translate("VariableTable", u"N points", None))
#if QT_CONFIG(tooltip)
        self.Npoints.setToolTip(QCoreApplication.translate("VariableTable", u"Number of points in the model used to calculate a scattering profile.", None))
#endif // QT_CONFIG(tooltip)
        self.Npoints.setText(QCoreApplication.translate("VariableTable", u"3000", None))
        self.label_2.setText(QCoreApplication.translate("VariableTable", u"P(r) points", None))
#if QT_CONFIG(tooltip)
        self.prPoints.setToolTip(QCoreApplication.translate("VariableTable", u"Number of points in the pair distance distribution.", None))
#endif // QT_CONFIG(tooltip)
        self.prPoints.setText(QCoreApplication.translate("VariableTable", u"100", None))
    # retranslateUi

