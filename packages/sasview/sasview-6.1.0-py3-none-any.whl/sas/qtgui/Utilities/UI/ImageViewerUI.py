# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ImageViewerUI.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QMainWindow,
    QMenu, QMenuBar, QSizePolicy, QStatusBar,
    QWidget)

class Ui_ImageViewerUI(object):
    def setupUi(self, ImageViewerUI):
        if not ImageViewerUI.objectName():
            ImageViewerUI.setObjectName(u"ImageViewerUI")
        ImageViewerUI.resize(492, 418)
        self.actionLoad_Image = QAction(ImageViewerUI)
        self.actionLoad_Image.setObjectName(u"actionLoad_Image")
        self.actionSave_Image = QAction(ImageViewerUI)
        self.actionSave_Image.setObjectName(u"actionSave_Image")
        self.actionPrint_Image = QAction(ImageViewerUI)
        self.actionPrint_Image.setObjectName(u"actionPrint_Image")
        self.actionCopy_Image = QAction(ImageViewerUI)
        self.actionCopy_Image.setObjectName(u"actionCopy_Image")
        self.actionConvert_to_Data = QAction(ImageViewerUI)
        self.actionConvert_to_Data.setObjectName(u"actionConvert_to_Data")
        self.actionHow_To = QAction(ImageViewerUI)
        self.actionHow_To.setObjectName(u"actionHow_To")
        self.centralwidget = QWidget(ImageViewerUI)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.imgFrame = QFrame(self.centralwidget)
        self.imgFrame.setObjectName(u"imgFrame")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.imgFrame.sizePolicy().hasHeightForWidth())
        self.imgFrame.setSizePolicy(sizePolicy)
        self.imgFrame.setFrameShape(QFrame.StyledPanel)
        self.imgFrame.setFrameShadow(QFrame.Raised)

        self.gridLayout.addWidget(self.imgFrame, 0, 0, 1, 1)

        ImageViewerUI.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(ImageViewerUI)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 492, 26))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName(u"menuEdit")
        self.menuImage = QMenu(self.menubar)
        self.menuImage.setObjectName(u"menuImage")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        self.menuHelp.setLayoutDirection(Qt.RightToLeft)
        ImageViewerUI.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(ImageViewerUI)
        self.statusbar.setObjectName(u"statusbar")
        ImageViewerUI.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuImage.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionLoad_Image)
        self.menuFile.addAction(self.actionSave_Image)
        self.menuFile.addAction(self.actionPrint_Image)
        self.menuEdit.addAction(self.actionCopy_Image)
        self.menuImage.addAction(self.actionConvert_to_Data)
        self.menuHelp.addAction(self.actionHow_To)

        self.retranslateUi(ImageViewerUI)

        QMetaObject.connectSlotsByName(ImageViewerUI)
    # setupUi

    def retranslateUi(self, ImageViewerUI):
        ImageViewerUI.setWindowTitle(QCoreApplication.translate("ImageViewerUI", u"Image Viewer", None))
        self.actionLoad_Image.setText(QCoreApplication.translate("ImageViewerUI", u"Load Image", None))
        self.actionSave_Image.setText(QCoreApplication.translate("ImageViewerUI", u"Save Image", None))
        self.actionPrint_Image.setText(QCoreApplication.translate("ImageViewerUI", u"Print Image", None))
        self.actionCopy_Image.setText(QCoreApplication.translate("ImageViewerUI", u"Copy", None))
        self.actionConvert_to_Data.setText(QCoreApplication.translate("ImageViewerUI", u"Convert to Data", None))
        self.actionHow_To.setText(QCoreApplication.translate("ImageViewerUI", u"How To", None))
        self.menuFile.setTitle(QCoreApplication.translate("ImageViewerUI", u"File", None))
        self.menuEdit.setTitle(QCoreApplication.translate("ImageViewerUI", u"Edit", None))
        self.menuImage.setTitle(QCoreApplication.translate("ImageViewerUI", u"Image", None))
        self.menuHelp.setTitle(QCoreApplication.translate("ImageViewerUI", u"Help", None))
    # retranslateUi

