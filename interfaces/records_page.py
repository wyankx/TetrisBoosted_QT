# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'records_page.ui'
#
# Created by: PyQt5 UI code generator 5.15.5
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_form(object):
    def setupUi(self, form):
        form.setObjectName("form")
        form.resize(600, 600)
        self.gridLayout = QtWidgets.QGridLayout(form)
        self.gridLayout.setObjectName("gridLayout")
        self.back_button = QtWidgets.QPushButton(form)
        self.back_button.setObjectName("back_button")
        self.gridLayout.addWidget(self.back_button, 0, 0, 1, 1, QtCore.Qt.AlignLeft)
        self.scroll_area = QtWidgets.QScrollArea(form)
        self.scroll_area.setStyleSheet("")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scroll_area")
        self.records_widget = QtWidgets.QWidget()
        self.records_widget.setGeometry(QtCore.QRect(0, 0, 574, 540))
        self.records_widget.setObjectName("records_widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.records_widget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scroll_area.setWidget(self.records_widget)
        self.gridLayout.addWidget(self.scroll_area, 1, 0, 1, 1)

        self.retranslateUi(form)
        QtCore.QMetaObject.connectSlotsByName(form)

    def retranslateUi(self, form):
        _translate = QtCore.QCoreApplication.translate
        form.setWindowTitle(_translate("form", "Form"))
        self.back_button.setText(_translate("form", "Back"))
