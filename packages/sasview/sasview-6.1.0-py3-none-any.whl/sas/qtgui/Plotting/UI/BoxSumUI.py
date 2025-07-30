# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'BoxSumUI.ui'
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
    QFormLayout, QGridLayout, QGroupBox, QLabel,
    QLineEdit, QSizePolicy, QSpacerItem, QWidget)

class Ui_BoxSumUI(object):
    def setupUi(self, BoxSumUI):
        if not BoxSumUI.objectName():
            BoxSumUI.setObjectName(u"BoxSumUI")
        BoxSumUI.resize(322, 313)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(BoxSumUI.sizePolicy().hasHeightForWidth())
        BoxSumUI.setSizePolicy(sizePolicy)
        icon = QIcon()
        icon.addFile(u":/res/ball.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        BoxSumUI.setWindowIcon(icon)
        self.gridLayout_4 = QGridLayout(BoxSumUI)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.groupBox = QGroupBox(BoxSumUI)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.gridLayout_3 = QGridLayout(self.groupBox)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.groupBox_4 = QGroupBox(self.groupBox)
        self.groupBox_4.setObjectName(u"groupBox_4")
        sizePolicy.setHeightForWidth(self.groupBox_4.sizePolicy().hasHeightForWidth())
        self.groupBox_4.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(self.groupBox_4)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(self.groupBox_4)
        self.label.setObjectName(u"label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.txtBoxHeight = QLineEdit(self.groupBox_4)
        self.txtBoxHeight.setObjectName(u"txtBoxHeight")
        sizePolicy1.setHeightForWidth(self.txtBoxHeight.sizePolicy().hasHeightForWidth())
        self.txtBoxHeight.setSizePolicy(sizePolicy1)
        self.txtBoxHeight.setMinimumSize(QSize(70, 0))
        self.txtBoxHeight.setMaximumSize(QSize(70, 16777215))

        self.gridLayout.addWidget(self.txtBoxHeight, 0, 1, 1, 1)

        self.label_10 = QLabel(self.groupBox_4)
        self.label_10.setObjectName(u"label_10")
        sizePolicy1.setHeightForWidth(self.label_10.sizePolicy().hasHeightForWidth())
        self.label_10.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.label_10, 0, 2, 1, 1)

        self.label_2 = QLabel(self.groupBox_4)
        self.label_2.setObjectName(u"label_2")
        sizePolicy1.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.txtBoxWidth = QLineEdit(self.groupBox_4)
        self.txtBoxWidth.setObjectName(u"txtBoxWidth")
        sizePolicy1.setHeightForWidth(self.txtBoxWidth.sizePolicy().hasHeightForWidth())
        self.txtBoxWidth.setSizePolicy(sizePolicy1)
        self.txtBoxWidth.setMinimumSize(QSize(70, 0))
        self.txtBoxWidth.setMaximumSize(QSize(70, 16777215))

        self.gridLayout.addWidget(self.txtBoxWidth, 1, 1, 1, 1)

        self.label_11 = QLabel(self.groupBox_4)
        self.label_11.setObjectName(u"label_11")
        sizePolicy1.setHeightForWidth(self.label_11.sizePolicy().hasHeightForWidth())
        self.label_11.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.label_11, 1, 2, 1, 1)


        self.gridLayout_3.addWidget(self.groupBox_4, 0, 0, 1, 1)

        self.groupBox_2 = QGroupBox(self.groupBox)
        self.groupBox_2.setObjectName(u"groupBox_2")
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.gridLayout_2 = QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 0, 0, 1, 1)

        self.txtCenterX = QLineEdit(self.groupBox_2)
        self.txtCenterX.setObjectName(u"txtCenterX")
        sizePolicy1.setHeightForWidth(self.txtCenterX.sizePolicy().hasHeightForWidth())
        self.txtCenterX.setSizePolicy(sizePolicy1)
        self.txtCenterX.setMinimumSize(QSize(70, 0))
        self.txtCenterX.setMaximumSize(QSize(70, 16777215))

        self.gridLayout_2.addWidget(self.txtCenterX, 0, 1, 1, 1)

        self.label_13 = QLabel(self.groupBox_2)
        self.label_13.setObjectName(u"label_13")

        self.gridLayout_2.addWidget(self.label_13, 0, 2, 1, 1)

        self.label_4 = QLabel(self.groupBox_2)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_2.addWidget(self.label_4, 1, 0, 1, 1)

        self.txtCenterY = QLineEdit(self.groupBox_2)
        self.txtCenterY.setObjectName(u"txtCenterY")
        sizePolicy1.setHeightForWidth(self.txtCenterY.sizePolicy().hasHeightForWidth())
        self.txtCenterY.setSizePolicy(sizePolicy1)
        self.txtCenterY.setMinimumSize(QSize(70, 0))
        self.txtCenterY.setMaximumSize(QSize(70, 16777215))

        self.gridLayout_2.addWidget(self.txtCenterY, 1, 1, 1, 1)

        self.label_12 = QLabel(self.groupBox_2)
        self.label_12.setObjectName(u"label_12")

        self.gridLayout_2.addWidget(self.label_12, 1, 2, 1, 1)


        self.gridLayout_3.addWidget(self.groupBox_2, 0, 1, 1, 1)


        self.gridLayout_4.addWidget(self.groupBox, 0, 0, 1, 2)

        self.groupBox_3 = QGroupBox(BoxSumUI)
        self.groupBox_3.setObjectName(u"groupBox_3")
        sizePolicy.setHeightForWidth(self.groupBox_3.sizePolicy().hasHeightForWidth())
        self.groupBox_3.setSizePolicy(sizePolicy)
        self.gridLayout_5 = QGridLayout(self.groupBox_3)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label_5 = QLabel(self.groupBox_3)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_5)

        self.lblAvg = QLabel(self.groupBox_3)
        self.lblAvg.setObjectName(u"lblAvg")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lblAvg)

        self.label_6 = QLabel(self.groupBox_3)
        self.label_6.setObjectName(u"label_6")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_6)

        self.lblAvgErr = QLabel(self.groupBox_3)
        self.lblAvgErr.setObjectName(u"lblAvgErr")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lblAvgErr)

        self.label_7 = QLabel(self.groupBox_3)
        self.label_7.setObjectName(u"label_7")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_7)

        self.lblNumPoints = QLabel(self.groupBox_3)
        self.lblNumPoints.setObjectName(u"lblNumPoints")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.lblNumPoints)

        self.label_8 = QLabel(self.groupBox_3)
        self.label_8.setObjectName(u"label_8")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_8)

        self.lblSum = QLabel(self.groupBox_3)
        self.lblSum.setObjectName(u"lblSum")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.lblSum)

        self.label_9 = QLabel(self.groupBox_3)
        self.label_9.setObjectName(u"label_9")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.label_9)

        self.lblSumErr = QLabel(self.groupBox_3)
        self.lblSumErr.setObjectName(u"lblSumErr")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.lblSumErr)


        self.gridLayout_5.addLayout(self.formLayout, 0, 0, 1, 1)


        self.gridLayout_4.addWidget(self.groupBox_3, 1, 0, 1, 2)

        self.verticalSpacer = QSpacerItem(20, 18, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_4.addItem(self.verticalSpacer, 2, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(BoxSumUI)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close)

        self.gridLayout_4.addWidget(self.buttonBox, 3, 1, 1, 1)


        self.retranslateUi(BoxSumUI)
        self.buttonBox.accepted.connect(BoxSumUI.accept)
        self.buttonBox.rejected.connect(BoxSumUI.reject)

        QMetaObject.connectSlotsByName(BoxSumUI)
    # setupUi

    def retranslateUi(self, BoxSumUI):
        BoxSumUI.setWindowTitle(QCoreApplication.translate("BoxSumUI", u"Box Sum", None))
        self.groupBox.setTitle(QCoreApplication.translate("BoxSumUI", u"Box dimensions", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("BoxSumUI", u"Box size", None))
#if QT_CONFIG(tooltip)
        self.label.setToolTip(QCoreApplication.translate("BoxSumUI", u"<html><head/><body><p>Height of the box.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label.setText(QCoreApplication.translate("BoxSumUI", u"Height", None))
#if QT_CONFIG(tooltip)
        self.txtBoxHeight.setToolTip(QCoreApplication.translate("BoxSumUI", u"<html><head/><body><p>Height of the box.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_10.setText(QCoreApplication.translate("BoxSumUI", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.label_2.setToolTip(QCoreApplication.translate("BoxSumUI", u"<html><head/><body><p>Width of the box.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_2.setText(QCoreApplication.translate("BoxSumUI", u"Width", None))
#if QT_CONFIG(tooltip)
        self.txtBoxWidth.setToolTip(QCoreApplication.translate("BoxSumUI", u"<html><head/><body><p>Width of the box.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_11.setText(QCoreApplication.translate("BoxSumUI", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("BoxSumUI", u"Box center", None))
#if QT_CONFIG(tooltip)
        self.label_3.setToolTip(QCoreApplication.translate("BoxSumUI", u"<html><head/><body><p>X coordinate of the center of the box.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_3.setText(QCoreApplication.translate("BoxSumUI", u"<html><head/><body><p>Q<span style=\" vertical-align:sub;\">X</span></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.txtCenterX.setToolTip(QCoreApplication.translate("BoxSumUI", u"<html><head/><body><p>X coordinate of the center of the box.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_13.setText(QCoreApplication.translate("BoxSumUI", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.label_4.setToolTip(QCoreApplication.translate("BoxSumUI", u"<html><head/><body><p>Y coordinate of the center of the box.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_4.setText(QCoreApplication.translate("BoxSumUI", u"<html><head/><body><p>Q<span style=\" vertical-align:sub;\">Y</span></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.txtCenterY.setToolTip(QCoreApplication.translate("BoxSumUI", u"<html><head/><body><p>Y coordinate of the center of the box.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.txtCenterY.setText("")
        self.label_12.setText(QCoreApplication.translate("BoxSumUI", u"<html><head/><body><p>\u00c5<span style=\" vertical-align:super;\">-1</span></p></body></html>", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("BoxSumUI", u"Box parameters", None))
#if QT_CONFIG(tooltip)
        self.label_5.setToolTip(QCoreApplication.translate("BoxSumUI", u"<html><head/><body><p>Average point count in selected region.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_5.setText(QCoreApplication.translate("BoxSumUI", u"Avg:", None))
#if QT_CONFIG(tooltip)
        self.lblAvg.setToolTip(QCoreApplication.translate("BoxSumUI", u"<html><head/><body><p>Average point count in selected region.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblAvg.setText(QCoreApplication.translate("BoxSumUI", u"TextLabel", None))
#if QT_CONFIG(tooltip)
        self.label_6.setToolTip(QCoreApplication.translate("BoxSumUI", u"<html><head/><body><p>Error of average point count in selected region.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_6.setText(QCoreApplication.translate("BoxSumUI", u"Avg error:", None))
#if QT_CONFIG(tooltip)
        self.lblAvgErr.setToolTip(QCoreApplication.translate("BoxSumUI", u"<html><head/><body><p>Error of average point count in selected region.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblAvgErr.setText(QCoreApplication.translate("BoxSumUI", u"TextLabel", None))
#if QT_CONFIG(tooltip)
        self.label_7.setToolTip(QCoreApplication.translate("BoxSumUI", u"<html><head/><body><p>Total number of points in the selected region.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_7.setText(QCoreApplication.translate("BoxSumUI", u"Num. of points:", None))
#if QT_CONFIG(tooltip)
        self.lblNumPoints.setToolTip(QCoreApplication.translate("BoxSumUI", u"<html><head/><body><p>Total number of points in the selected region.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblNumPoints.setText(QCoreApplication.translate("BoxSumUI", u"TextLabel", None))
#if QT_CONFIG(tooltip)
        self.label_8.setToolTip(QCoreApplication.translate("BoxSumUI", u"<html><head/><body><p>Sum of point intensities for all points in the selected region.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_8.setText(QCoreApplication.translate("BoxSumUI", u"Sum:", None))
#if QT_CONFIG(tooltip)
        self.lblSum.setToolTip(QCoreApplication.translate("BoxSumUI", u"<html><head/><body><p>Sum of point intensities for all points in the selected region.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblSum.setText(QCoreApplication.translate("BoxSumUI", u"TextLabel", None))
#if QT_CONFIG(tooltip)
        self.label_9.setToolTip(QCoreApplication.translate("BoxSumUI", u"<html><head/><body><p>Error of point intensity sum for all points in the selected region.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_9.setText(QCoreApplication.translate("BoxSumUI", u"Sum error:", None))
#if QT_CONFIG(tooltip)
        self.lblSumErr.setToolTip(QCoreApplication.translate("BoxSumUI", u"<html><head/><body><p>Error of point intensity sum for all points in the selected region.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblSumErr.setText(QCoreApplication.translate("BoxSumUI", u"TextLabel", None))
    # retranslateUi

