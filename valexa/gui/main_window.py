# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/kdesrosiers/Documents/valexa/scripts/../valexa/gui/main_window.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(717, 595)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setEnabled(True)
        self.centralwidget.setAutoFillBackground(False)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.stackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName("stackedWidget")
        self.main = QtWidgets.QWidget()
        self.main.setObjectName("main")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.main)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(-1, -1, -1, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(self.main)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.label_2 = QtWidgets.QLabel(self.main)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btn_response = QtWidgets.QPushButton(self.main)
        self.btn_response.setDefault(False)
        self.btn_response.setFlat(False)
        self.btn_response.setObjectName("btn_response")
        self.horizontalLayout.addWidget(self.btn_response)
        self.btn_result = QtWidgets.QPushButton(self.main)
        self.btn_result.setObjectName("btn_result")
        self.horizontalLayout.addWidget(self.btn_result)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout_4.addLayout(self.verticalLayout_2)
        self.stackedWidget.addWidget(self.main)
        self.data = QtWidgets.QWidget()
        self.data.setObjectName("data")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.data)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout()
        self.verticalLayout_8.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.xlsxUploadLabel = QtWidgets.QLabel(self.data)
        self.xlsxUploadLabel.setObjectName("xlsxUploadLabel")
        self.horizontalLayout_2.addWidget(self.xlsxUploadLabel)
        self.xlsx_choose_button = QtWidgets.QPushButton(self.data)
        self.xlsx_choose_button.setObjectName("xlsx_choose_button")
        self.horizontalLayout_2.addWidget(self.xlsx_choose_button)
        self.horizontalLayout_2.setStretch(1, 5)
        self.verticalLayout_8.addLayout(self.horizontalLayout_2)
        self.verticalLayout_5.addLayout(self.verticalLayout_8)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.file_name_label = QtWidgets.QLabel(self.data)
        self.file_name_label.setObjectName("file_name_label")
        self.horizontalLayout_5.addWidget(self.file_name_label)
        self.file_name_input = QtWidgets.QLineEdit(self.data)
        self.file_name_input.setEnabled(False)
        self.file_name_input.setAutoFillBackground(False)
        self.file_name_input.setObjectName("file_name_input")
        self.horizontalLayout_5.addWidget(self.file_name_input)
        self.verticalLayout_5.addLayout(self.horizontalLayout_5)
        self.label_3 = QtWidgets.QLabel(self.data)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_5.addWidget(self.label_3)
        self.listWidget = QtWidgets.QListWidget(self.data)
        self.listWidget.setAlternatingRowColors(False)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout_5.addWidget(self.listWidget)
        self.label_4 = QtWidgets.QLabel(self.data)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_5.addWidget(self.label_4)
        self.listWidget_2 = QtWidgets.QListWidget(self.data)
        self.listWidget_2.setObjectName("listWidget_2")
        self.verticalLayout_5.addWidget(self.listWidget_2)
        self.stackedWidget.addWidget(self.data)
        self.verticalLayout.addWidget(self.stackedWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 717, 20))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionQuit = QtWidgets.QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")
        self.menuFile.addAction(self.actionQuit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        self.stackedWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:16pt;\">Welcome to Valexa</span></p></body></html>"))
        self.label_2.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">To begin choose between the following validation options</span></p></body></html>"))
        self.btn_response.setText(_translate("MainWindow", "Response"))
        self.btn_result.setText(_translate("MainWindow", "Result"))
        self.xlsxUploadLabel.setText(_translate("MainWindow", "Xlsx"))
        self.xlsx_choose_button.setText(_translate("MainWindow", "Choose file"))
        self.file_name_label.setText(_translate("MainWindow", "File name"))
        self.label_3.setText(_translate("MainWindow", "Calibration data"))
        self.label_4.setText(_translate("MainWindow", "Validation data"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionQuit.setText(_translate("MainWindow", "Quit"))

