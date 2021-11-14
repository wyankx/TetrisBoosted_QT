# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'game_page.ui'
#
# Created by: PyQt5 UI code generator 5.15.5
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_game_layout(object):
    def setupUi(self, game_layout):
        game_layout.setObjectName("game_layout")
        game_layout.resize(580, 624)
        self.horizontalLayout = QtWidgets.QHBoxLayout(game_layout)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.line = QtWidgets.QFrame(game_layout)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout.addWidget(self.line)
        self.grid_layout = QtWidgets.QGridLayout()
        self.grid_layout.setObjectName("grid_layout")
        self.back_button = QtWidgets.QPushButton(game_layout)
        self.back_button.setObjectName("back_button")
        self.grid_layout.addWidget(self.back_button, 0, 0, 1, 1, QtCore.Qt.AlignLeft)
        self.score = QtWidgets.QLabel(game_layout)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.score.setFont(font)
        self.score.setObjectName("score")
        self.grid_layout.addWidget(self.score, 1, 0, 1, 1)
        self.time = QtWidgets.QLabel(game_layout)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.time.setFont(font)
        self.time.setObjectName("time")
        self.grid_layout.addWidget(self.time, 2, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.grid_layout.addItem(spacerItem, 4, 0, 1, 1)
        self.score_LCD_number = QtWidgets.QLCDNumber(game_layout)
        self.score_LCD_number.setObjectName("score_LCD_number")
        self.grid_layout.addWidget(self.score_LCD_number, 1, 1, 1, 1)
        self.time_LCD_number = QtWidgets.QLCDNumber(game_layout)
        self.time_LCD_number.setObjectName("time_LCD_number")
        self.grid_layout.addWidget(self.time_LCD_number, 2, 1, 1, 1)
        self.state_label = QtWidgets.QLabel(game_layout)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.state_label.setFont(font)
        self.state_label.setText("")
        self.state_label.setObjectName("state_label")
        self.grid_layout.addWidget(self.state_label, 3, 0, 1, 1)
        self.horizontalLayout.addLayout(self.grid_layout)

        self.retranslateUi(game_layout)
        QtCore.QMetaObject.connectSlotsByName(game_layout)

    def retranslateUi(self, game_layout):
        _translate = QtCore.QCoreApplication.translate
        game_layout.setWindowTitle(_translate("game_layout", "Form"))
        self.back_button.setText(_translate("game_layout", "Back"))
        self.score.setText(_translate("game_layout", "Score: "))
        self.time.setText(_translate("game_layout", "Time: "))
