# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'FittingOptionsUI.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QSpacerItem, QStackedWidget,
    QWidget)

class Ui_FittingOptions(object):
    def setupUi(self, FittingOptions):
        if not FittingOptions.objectName():
            FittingOptions.setObjectName(u"FittingOptions")
        FittingOptions.resize(421, 459)
        FittingOptions.setMinimumSize(QSize(421, 459))
        FittingOptions.setBaseSize(QSize(421, 439))
        self.groupBox = QGroupBox(FittingOptions)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(0, 80, 421, 381))
        self.groupBox.setMinimumSize(QSize(421, 381))
        self.gridLayout_9 = QGridLayout(self.groupBox)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.cbAlgorithm = QComboBox(self.groupBox)
        self.cbAlgorithm.setObjectName(u"cbAlgorithm")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbAlgorithm.sizePolicy().hasHeightForWidth())
        self.cbAlgorithm.setSizePolicy(sizePolicy)
        self.cbAlgorithm.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.gridLayout_9.addWidget(self.cbAlgorithm, 0, 0, 1, 1)

        self.stackedWidget = QStackedWidget(self.groupBox)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setFrameShape(QFrame.NoFrame)
        self.page_dream = QWidget()
        self.page_dream.setObjectName(u"page_dream")
        self.gridLayout_2 = QGridLayout(self.page_dream)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.groupBox_2 = QGroupBox(self.page_dream)
        self.groupBox_2.setObjectName(u"groupBox_2")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy1)
        self.gridLayout = QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(self.groupBox_2)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)

        self.init_dream = QComboBox(self.groupBox_2)
        self.init_dream.addItem("")
        self.init_dream.addItem("")
        self.init_dream.addItem("")
        self.init_dream.addItem("")
        self.init_dream.setObjectName(u"init_dream")

        self.gridLayout.addWidget(self.init_dream, 3, 1, 1, 1)

        self.thin_dream = QLineEdit(self.groupBox_2)
        self.thin_dream.setObjectName(u"thin_dream")

        self.gridLayout.addWidget(self.thin_dream, 4, 1, 1, 1)

        self.label_5 = QLabel(self.groupBox_2)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)

        self.label_4 = QLabel(self.groupBox_2)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)

        self.burn_dream = QLineEdit(self.groupBox_2)
        self.burn_dream.setObjectName(u"burn_dream")

        self.gridLayout.addWidget(self.burn_dream, 1, 1, 1, 1)

        self.label_6 = QLabel(self.groupBox_2)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout.addWidget(self.label_6, 5, 0, 1, 1)

        self.label_2 = QLabel(self.groupBox_2)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.pop_dream = QLineEdit(self.groupBox_2)
        self.pop_dream.setObjectName(u"pop_dream")

        self.gridLayout.addWidget(self.pop_dream, 2, 1, 1, 1)

        self.steps_dream = QLineEdit(self.groupBox_2)
        self.steps_dream.setObjectName(u"steps_dream")

        self.gridLayout.addWidget(self.steps_dream, 5, 1, 1, 1)

        self.samples_dream = QLineEdit(self.groupBox_2)
        self.samples_dream.setObjectName(u"samples_dream")

        self.gridLayout.addWidget(self.samples_dream, 0, 1, 1, 1)


        self.gridLayout_2.addWidget(self.groupBox_2, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.page_dream)
        self.page_lm = QWidget()
        self.page_lm.setObjectName(u"page_lm")
        self.gridLayout_4 = QGridLayout(self.page_lm)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.groupBox_3 = QGroupBox(self.page_lm)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.gridLayout_3 = QGridLayout(self.groupBox_3)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label_7 = QLabel(self.groupBox_3)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_3.addWidget(self.label_7, 0, 0, 1, 1)

        self.steps_lm = QLineEdit(self.groupBox_3)
        self.steps_lm.setObjectName(u"steps_lm")

        self.gridLayout_3.addWidget(self.steps_lm, 0, 1, 1, 1)

        self.label_8 = QLabel(self.groupBox_3)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_3.addWidget(self.label_8, 1, 0, 1, 1)

        self.ftol_lm = QLineEdit(self.groupBox_3)
        self.ftol_lm.setObjectName(u"ftol_lm")

        self.gridLayout_3.addWidget(self.ftol_lm, 1, 1, 1, 1)

        self.label_9 = QLabel(self.groupBox_3)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_3.addWidget(self.label_9, 2, 0, 1, 1)

        self.xtol_lm = QLineEdit(self.groupBox_3)
        self.xtol_lm.setObjectName(u"xtol_lm")

        self.gridLayout_3.addWidget(self.xtol_lm, 2, 1, 1, 1)


        self.gridLayout_4.addWidget(self.groupBox_3, 0, 0, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 434, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_4.addItem(self.verticalSpacer_2, 1, 0, 1, 1)

        self.stackedWidget.addWidget(self.page_lm)
        self.page_newton = QWidget()
        self.page_newton.setObjectName(u"page_newton")
        self.gridLayout_7 = QGridLayout(self.page_newton)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.groupBox_5 = QGroupBox(self.page_newton)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.gridLayout_5 = QGridLayout(self.groupBox_5)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.label_10 = QLabel(self.groupBox_5)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout_5.addWidget(self.label_10, 0, 0, 1, 1)

        self.steps_newton = QLineEdit(self.groupBox_5)
        self.steps_newton.setObjectName(u"steps_newton")

        self.gridLayout_5.addWidget(self.steps_newton, 0, 1, 1, 1)

        self.label_13 = QLabel(self.groupBox_5)
        self.label_13.setObjectName(u"label_13")

        self.gridLayout_5.addWidget(self.label_13, 1, 0, 1, 1)

        self.starts_newton = QLineEdit(self.groupBox_5)
        self.starts_newton.setObjectName(u"starts_newton")

        self.gridLayout_5.addWidget(self.starts_newton, 1, 1, 1, 1)

        self.label_11 = QLabel(self.groupBox_5)
        self.label_11.setObjectName(u"label_11")

        self.gridLayout_5.addWidget(self.label_11, 2, 0, 1, 1)

        self.ftol_newton = QLineEdit(self.groupBox_5)
        self.ftol_newton.setObjectName(u"ftol_newton")

        self.gridLayout_5.addWidget(self.ftol_newton, 2, 1, 1, 1)

        self.label_12 = QLabel(self.groupBox_5)
        self.label_12.setObjectName(u"label_12")

        self.gridLayout_5.addWidget(self.label_12, 3, 0, 1, 1)

        self.xtol_newton = QLineEdit(self.groupBox_5)
        self.xtol_newton.setObjectName(u"xtol_newton")

        self.gridLayout_5.addWidget(self.xtol_newton, 3, 1, 1, 1)


        self.gridLayout_7.addWidget(self.groupBox_5, 0, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 68, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_7.addItem(self.verticalSpacer, 1, 0, 1, 1)

        self.stackedWidget.addWidget(self.page_newton)
        self.page_de = QWidget()
        self.page_de.setObjectName(u"page_de")
        self.gridLayout_8 = QGridLayout(self.page_de)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.groupBox_6 = QGroupBox(self.page_de)
        self.groupBox_6.setObjectName(u"groupBox_6")
        self.gridLayout_6 = QGridLayout(self.groupBox_6)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.label_14 = QLabel(self.groupBox_6)
        self.label_14.setObjectName(u"label_14")

        self.gridLayout_6.addWidget(self.label_14, 0, 0, 1, 1)

        self.steps_de = QLineEdit(self.groupBox_6)
        self.steps_de.setObjectName(u"steps_de")

        self.gridLayout_6.addWidget(self.steps_de, 0, 1, 1, 1)

        self.label_15 = QLabel(self.groupBox_6)
        self.label_15.setObjectName(u"label_15")

        self.gridLayout_6.addWidget(self.label_15, 1, 0, 1, 1)

        self.pop_de = QLineEdit(self.groupBox_6)
        self.pop_de.setObjectName(u"pop_de")

        self.gridLayout_6.addWidget(self.pop_de, 1, 1, 1, 1)

        self.label_18 = QLabel(self.groupBox_6)
        self.label_18.setObjectName(u"label_18")

        self.gridLayout_6.addWidget(self.label_18, 2, 0, 1, 1)

        self.CR_de = QLineEdit(self.groupBox_6)
        self.CR_de.setObjectName(u"CR_de")

        self.gridLayout_6.addWidget(self.CR_de, 2, 1, 1, 1)

        self.label_19 = QLabel(self.groupBox_6)
        self.label_19.setObjectName(u"label_19")

        self.gridLayout_6.addWidget(self.label_19, 3, 0, 1, 1)

        self.F_de = QLineEdit(self.groupBox_6)
        self.F_de.setObjectName(u"F_de")

        self.gridLayout_6.addWidget(self.F_de, 3, 1, 1, 1)

        self.label_16 = QLabel(self.groupBox_6)
        self.label_16.setObjectName(u"label_16")

        self.gridLayout_6.addWidget(self.label_16, 4, 0, 1, 1)

        self.ftol_de = QLineEdit(self.groupBox_6)
        self.ftol_de.setObjectName(u"ftol_de")

        self.gridLayout_6.addWidget(self.ftol_de, 4, 1, 1, 1)

        self.label_17 = QLabel(self.groupBox_6)
        self.label_17.setObjectName(u"label_17")

        self.gridLayout_6.addWidget(self.label_17, 5, 0, 1, 1)

        self.xtol_de = QLineEdit(self.groupBox_6)
        self.xtol_de.setObjectName(u"xtol_de")

        self.gridLayout_6.addWidget(self.xtol_de, 5, 1, 1, 1)


        self.gridLayout_8.addWidget(self.groupBox_6, 0, 0, 1, 1)

        self.verticalSpacer_3 = QSpacerItem(20, 356, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_8.addItem(self.verticalSpacer_3, 1, 0, 1, 1)

        self.stackedWidget.addWidget(self.page_de)
        self.page_amoeba = QWidget()
        self.page_amoeba.setObjectName(u"page_amoeba")
        self.gridLayout_10 = QGridLayout(self.page_amoeba)
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.verticalSpacer_4 = QSpacerItem(20, 382, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_10.addItem(self.verticalSpacer_4, 2, 0, 1, 1)

        self.groupBox_7 = QGroupBox(self.page_amoeba)
        self.groupBox_7.setObjectName(u"groupBox_7")
        self.gridLayout_11 = QGridLayout(self.groupBox_7)
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.label_22 = QLabel(self.groupBox_7)
        self.label_22.setObjectName(u"label_22")

        self.gridLayout_11.addWidget(self.label_22, 2, 0, 1, 1)

        self.label_25 = QLabel(self.groupBox_7)
        self.label_25.setObjectName(u"label_25")

        self.gridLayout_11.addWidget(self.label_25, 4, 0, 1, 1)

        self.steps_amoeba = QLineEdit(self.groupBox_7)
        self.steps_amoeba.setObjectName(u"steps_amoeba")

        self.gridLayout_11.addWidget(self.steps_amoeba, 0, 1, 1, 1)

        self.ftol_amoeba = QLineEdit(self.groupBox_7)
        self.ftol_amoeba.setObjectName(u"ftol_amoeba")

        self.gridLayout_11.addWidget(self.ftol_amoeba, 3, 1, 1, 1)

        self.radius_amoeba = QLineEdit(self.groupBox_7)
        self.radius_amoeba.setObjectName(u"radius_amoeba")

        self.gridLayout_11.addWidget(self.radius_amoeba, 2, 1, 1, 1)

        self.label_21 = QLabel(self.groupBox_7)
        self.label_21.setObjectName(u"label_21")

        self.gridLayout_11.addWidget(self.label_21, 1, 0, 1, 1)

        self.label_20 = QLabel(self.groupBox_7)
        self.label_20.setObjectName(u"label_20")

        self.gridLayout_11.addWidget(self.label_20, 0, 0, 1, 1)

        self.label_24 = QLabel(self.groupBox_7)
        self.label_24.setObjectName(u"label_24")

        self.gridLayout_11.addWidget(self.label_24, 3, 0, 1, 1)

        self.xtol_amoeba = QLineEdit(self.groupBox_7)
        self.xtol_amoeba.setObjectName(u"xtol_amoeba")

        self.gridLayout_11.addWidget(self.xtol_amoeba, 4, 1, 1, 1)

        self.starts_amoeba = QLineEdit(self.groupBox_7)
        self.starts_amoeba.setObjectName(u"starts_amoeba")

        self.gridLayout_11.addWidget(self.starts_amoeba, 1, 1, 1, 1)


        self.gridLayout_10.addWidget(self.groupBox_7, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.page_amoeba)

        self.gridLayout_9.addWidget(self.stackedWidget, 1, 0, 1, 1)

        self.horizontal_layout = QHBoxLayout()
        self.horizontal_layout.setObjectName(u"horizontal_layout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontal_layout.addItem(self.horizontalSpacer)

        self.cmdHelp = QPushButton(self.groupBox)
        self.cmdHelp.setObjectName(u"cmdHelp")

        self.horizontal_layout.addWidget(self.cmdHelp)


        self.gridLayout_9.addLayout(self.horizontal_layout, 2, 0, 1, 1)

        self.groupBox_4 = QGroupBox(FittingOptions)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.groupBox_4.setGeometry(QRect(0, 0, 421, 71))
        self.groupBox_4.setMinimumSize(QSize(421, 51))
        self.gridLayout_12 = QGridLayout(self.groupBox_4)
        self.gridLayout_12.setObjectName(u"gridLayout_12")
        self.cbAlgorithmDefault = QComboBox(self.groupBox_4)
        self.cbAlgorithmDefault.setObjectName(u"cbAlgorithmDefault")
        sizePolicy.setHeightForWidth(self.cbAlgorithmDefault.sizePolicy().hasHeightForWidth())
        self.cbAlgorithmDefault.setSizePolicy(sizePolicy)
        self.cbAlgorithmDefault.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.gridLayout_12.addWidget(self.cbAlgorithmDefault, 0, 0, 1, 1)


        self.retranslateUi(FittingOptions)

        self.stackedWidget.setCurrentIndex(4)


        QMetaObject.connectSlotsByName(FittingOptions)
    # setupUi

    def retranslateUi(self, FittingOptions):
        FittingOptions.setWindowTitle(QCoreApplication.translate("FittingOptions", u"Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("FittingOptions", u"Fit Algorithms ", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("FittingOptions", u"DREAM", None))
        self.label.setText(QCoreApplication.translate("FittingOptions", u"Samples:", None))
        self.label_3.setText(QCoreApplication.translate("FittingOptions", u"Population:", None))
        self.init_dream.setItemText(0, QCoreApplication.translate("FittingOptions", u"eps", None))
        self.init_dream.setItemText(1, QCoreApplication.translate("FittingOptions", u"lhs", None))
        self.init_dream.setItemText(2, QCoreApplication.translate("FittingOptions", u"cov", None))
        self.init_dream.setItemText(3, QCoreApplication.translate("FittingOptions", u"random", None))

#if QT_CONFIG(tooltip)
        self.init_dream.setToolTip(QCoreApplication.translate("FittingOptions", u"<html><head/><body><p><span style=\" font-style:italic;\">Initializer</span> determines how the population will be initialized. The options are as follows:</p><p><span style=\" font-style:italic;\">eps</span> (epsilon ball), in which the entire initial population is chosen at random from within a tiny hypersphere centered about the initial point</p><p><span style=\" font-style:italic;\">lhs</span> (latin hypersquare), which chops the bounds within each dimension in <span style=\" font-weight:600;\">k</span> equal sized chunks where <span style=\" font-weight:600;\">k</span> is the size of the population and makes sure that each parameter has at least one value within each chunk across the population.</p><p><span style=\" font-style:italic;\">cov</span> (covariance matrix), in which the uncertainty is estimated using the covariance matrix at the initial point, and points are selected at random from the corresponding gaussian ellipsoid</p><p><span style=\" font-style:italic;\">random</span> (uniform random), in "
                        "which the points are selected at random within the bounds of the parameters</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.thin_dream.setToolTip(QCoreApplication.translate("FittingOptions", u"<html><head/><body><p>The amount of thinning to use when collecting the population.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_5.setText(QCoreApplication.translate("FittingOptions", u"Thinning:", None))
        self.label_4.setText(QCoreApplication.translate("FittingOptions", u"Initializer:", None))
#if QT_CONFIG(tooltip)
        self.burn_dream.setToolTip(QCoreApplication.translate("FittingOptions", u"<html><head/><body><p>The number of iterations to required for the Markov chain to converge to the equilibrium distribution.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_6.setText(QCoreApplication.translate("FittingOptions", u"Steps:", None))
        self.label_2.setText(QCoreApplication.translate("FittingOptions", u"Burn-in Steps:", None))
#if QT_CONFIG(tooltip)
        self.pop_dream.setToolTip(QCoreApplication.translate("FittingOptions", u"<html><head/><body><p>The size of the population.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.steps_dream.setToolTip(QCoreApplication.translate("FittingOptions", u"<html><head/><body><p>Determines the number of iterations to use for drawing samples after burn in.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.samples_dream.setToolTip(QCoreApplication.translate("FittingOptions", u"<html><head/><body><p>Number of points to be drawn from the Markov chain.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.groupBox_3.setTitle(QCoreApplication.translate("FittingOptions", u"Levenberg", None))
        self.label_7.setText(QCoreApplication.translate("FittingOptions", u"Steps:", None))
#if QT_CONFIG(tooltip)
        self.steps_lm.setToolTip(QCoreApplication.translate("FittingOptions", u"<html><head/><body><p>The number of gradient steps to take.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_8.setText(QCoreApplication.translate("FittingOptions", u"f(x) tolerance:", None))
#if QT_CONFIG(tooltip)
        self.ftol_lm.setToolTip(QCoreApplication.translate("FittingOptions", u"<html><head/><body><p>Used to determine when the fit has reached the point where no significant improvement is expected.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_9.setText(QCoreApplication.translate("FittingOptions", u"x tolerance:", None))
#if QT_CONFIG(tooltip)
        self.xtol_lm.setToolTip(QCoreApplication.translate("FittingOptions", u"<html><head/><body><p>Used to determine when the fit has reached the point where no significant improvement is expected.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.groupBox_5.setTitle(QCoreApplication.translate("FittingOptions", u"Quasi-Newton BFGS ", None))
        self.label_10.setText(QCoreApplication.translate("FittingOptions", u"Steps:", None))
#if QT_CONFIG(tooltip)
        self.steps_newton.setToolTip(QCoreApplication.translate("FittingOptions", u"<html><head/><body><p>The number of gradient steps to take.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_13.setText(QCoreApplication.translate("FittingOptions", u"Starts:", None))
#if QT_CONFIG(tooltip)
        self.starts_newton.setToolTip(QCoreApplication.translate("FittingOptions", u"<html><head/><body><p>Value thattells the optimizer to restart a given number of times. Each time it restarts it uses a random starting point.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_11.setText(QCoreApplication.translate("FittingOptions", u"f(x) tolerance:", None))
#if QT_CONFIG(tooltip)
        self.ftol_newton.setToolTip(QCoreApplication.translate("FittingOptions", u"<html><head/><body><p>Used to determine when the fit has reached the point where no significant improvement is expected.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_12.setText(QCoreApplication.translate("FittingOptions", u"x tolerance:", None))
#if QT_CONFIG(tooltip)
        self.xtol_newton.setToolTip(QCoreApplication.translate("FittingOptions", u"<html><head/><body><p>Used to determine when the fit has reached the point where no significant improvement is expected.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.groupBox_6.setTitle(QCoreApplication.translate("FittingOptions", u"Differential Evolution", None))
        self.label_14.setText(QCoreApplication.translate("FittingOptions", u"Steps:", None))
#if QT_CONFIG(tooltip)
        self.steps_de.setToolTip(QCoreApplication.translate("FittingOptions", u"<html><head/><body><p>The number of iterations.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_15.setText(QCoreApplication.translate("FittingOptions", u"Population:", None))
        self.label_18.setText(QCoreApplication.translate("FittingOptions", u"Crossover ratio:", None))
#if QT_CONFIG(tooltip)
        self.CR_de.setToolTip(QCoreApplication.translate("FittingOptions", u"<html><head/><body><p>The size of the population.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_19.setText(QCoreApplication.translate("FittingOptions", u"Scale:", None))
#if QT_CONFIG(tooltip)
        self.F_de.setToolTip(QCoreApplication.translate("FittingOptions", u"<html><head/><body><p>Determines how much to scale each difference vector before adding it to the candidate point.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_16.setText(QCoreApplication.translate("FittingOptions", u"f(x) tolerance:", None))
#if QT_CONFIG(tooltip)
        self.ftol_de.setToolTip(QCoreApplication.translate("FittingOptions", u"<html><head/><body><p>Used to determine when the fit has reached the point where no significant improvement is expected.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_17.setText(QCoreApplication.translate("FittingOptions", u"x tolerance:", None))
#if QT_CONFIG(tooltip)
        self.xtol_de.setToolTip(QCoreApplication.translate("FittingOptions", u"<html><head/><body><p>Used to determine when the fit has reached the point where no significant improvement is expected.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.groupBox_7.setTitle(QCoreApplication.translate("FittingOptions", u"Nelder-Mead Simplex", None))
        self.label_22.setText(QCoreApplication.translate("FittingOptions", u"Simplex radius:", None))
        self.label_25.setText(QCoreApplication.translate("FittingOptions", u"x tolerance:", None))
#if QT_CONFIG(tooltip)
        self.steps_amoeba.setToolTip(QCoreApplication.translate("FittingOptions", u"<html><head/><body><p>The number of simplex update iterations to perform.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.ftol_amoeba.setToolTip(QCoreApplication.translate("FittingOptions", u"<html><head/><body><p>Used to determine when the fit has reached the point where no significant improvement is expected. </p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.radius_amoeba.setToolTip(QCoreApplication.translate("FittingOptions", u"<html><head/><body><p>The initial size of the simplex, as a portion of the bounds defining the parameter space.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_21.setText(QCoreApplication.translate("FittingOptions", u"Starts:", None))
        self.label_20.setText(QCoreApplication.translate("FittingOptions", u"Steps:", None))
        self.label_24.setText(QCoreApplication.translate("FittingOptions", u"f(x) tolerance:", None))
#if QT_CONFIG(tooltip)
        self.xtol_amoeba.setToolTip(QCoreApplication.translate("FittingOptions", u"<html><head/><body><p>Used to determine when the fit has reached the point where no significant improvement is expected. </p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.starts_amoeba.setToolTip(QCoreApplication.translate("FittingOptions", u"<html><head/><body><p>Tells the optimizer to restart a given number of times. Each time it restarts it uses a random starting point.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cmdHelp.setText(QCoreApplication.translate("FittingOptions", u"Help", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("FittingOptions", u"Default Fit Algorithm", None))
    # retranslateUi

