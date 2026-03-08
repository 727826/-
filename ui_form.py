# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
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
from PySide6.QtWidgets import (QApplication, QGraphicsView, QLabel, QPushButton,
    QSizePolicy, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(247, 327)
        self.open = QPushButton(Form)
        self.open.setObjectName(u"open")
        self.open.setGeometry(QRect(180, 160, 51, 31))
        self.open.setStyleSheet(u"border-image: url(:/image/open.png);")
        self.open.setCheckable(False)
        self.open.setFlat(False)
        self.mode = QPushButton(Form)
        self.mode.setObjectName(u"mode")
        self.mode.setGeometry(QRect(100, 200, 51, 21))
        self.mode.setStyleSheet(u"border-image: url(:/image/mode.png);")
        self.start = QPushButton(Form)
        self.start.setObjectName(u"start")
        self.start.setGeometry(QRect(100, 230, 51, 31))
        self.start.setStyleSheet(u"border-image: url(:/image/start.png);")
        self.clear = QPushButton(Form)
        self.clear.setObjectName(u"clear")
        self.clear.setGeometry(QRect(100, 270, 51, 21))
        self.clear.setStyleSheet(u"border-image: url(:/image/clear.png);")
        self.plus = QPushButton(Form)
        self.plus.setObjectName(u"plus")
        self.plus.setGeometry(QRect(30, 200, 41, 21))
        self.plus.setStyleSheet(u"border-image: url(:/image/subtract.png);")
        self.Benchmark = QPushButton(Form)
        self.Benchmark.setObjectName(u"Benchmark")
        self.Benchmark.setGeometry(QRect(30, 230, 41, 31))
        self.Benchmark.setStyleSheet(u"border-image: url(:/image/Benchmark.png);")
        self.subtract = QPushButton(Form)
        self.subtract.setObjectName(u"subtract")
        self.subtract.setGeometry(QRect(180, 200, 41, 21))
        self.subtract.setStyleSheet(u"border-image: url(:/image/plus.png);")
        self.listen = QPushButton(Form)
        self.listen.setObjectName(u"listen")
        self.listen.setGeometry(QRect(180, 230, 41, 31))
        self.listen.setStyleSheet(u"border-image: url(:/image/listen.png);")
        self.graphicsView_mode = QGraphicsView(Form)
        self.graphicsView_mode.setObjectName(u"graphicsView_mode")
        self.graphicsView_mode.setGeometry(QRect(70, 10, 31, 31))
        self.graphicsView_benchmark = QGraphicsView(Form)
        self.graphicsView_benchmark.setObjectName(u"graphicsView_benchmark")
        self.graphicsView_benchmark.setGeometry(QRect(20, 10, 41, 41))
        self.graphicsView_benchmark.setStyleSheet(u"")
        self.graphicsView_battery = QGraphicsView(Form)
        self.graphicsView_battery.setObjectName(u"graphicsView_battery")
        self.graphicsView_battery.setGeometry(QRect(190, 10, 41, 21))
        self.graphicsView_listen = QGraphicsView(Form)
        self.graphicsView_listen.setObjectName(u"graphicsView_listen")
        self.graphicsView_listen.setGeometry(QRect(140, 10, 41, 21))
        self.data = QLabel(Form)
        self.data.setObjectName(u"data")
        self.data.setGeometry(QRect(30, 60, 191, 71))
        self.data.setStyleSheet(u"font: 16pt \"Microsoft YaHei UI\";\n"
"")
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 1, 231, 151))
        self.label.setStyleSheet(u"\n"
"style = \"background: yellow;\";\n"
"")
        self.graphicsView_warning = QGraphicsView(Form)
        self.graphicsView_warning.setObjectName(u"graphicsView_warning")
        self.graphicsView_warning.setGeometry(QRect(200, 30, 31, 31))
        self.graphicsView_warning.setStyleSheet(u"")
        self.label.raise_()
        self.open.raise_()
        self.mode.raise_()
        self.start.raise_()
        self.clear.raise_()
        self.plus.raise_()
        self.Benchmark.raise_()
        self.subtract.raise_()
        self.listen.raise_()
        self.graphicsView_mode.raise_()
        self.graphicsView_benchmark.raise_()
        self.graphicsView_battery.raise_()
        self.graphicsView_listen.raise_()
        self.data.raise_()
        self.graphicsView_warning.raise_()

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.open.setText("")
        self.mode.setText("")
        self.start.setText("")
        self.clear.setText("")
        self.plus.setText("")
        self.Benchmark.setText("")
        self.subtract.setText("")
        self.listen.setText("")
        self.data.setText("")
        self.label.setText("")
    # retranslateUi

