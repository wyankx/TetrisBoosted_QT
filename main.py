#!/usr/bin/env python
# -*- coding: utf-8 -*-
# !/usr/bin/env python
import sqlite3
import sys
import os
from PyQt5.QtCore import pyqtSignal, QUrl, Qt
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtMultimedia import QMediaPlaylist, QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import QApplication, QWidget
import interfaces.window_interface as window_interface
from game import Board, ExtraBoard, Piece, Tetrominoe


class MainWindow(window_interface.Window):  # Main window
    change_window = pyqtSignal(int)
    exit = pyqtSignal()
    finish_game = pyqtSignal(int)

    def __init__(self):
        self.db_connect = sqlite3.connect('interfaces/resources/app_data.db')
        self.db_cursor = self.db_connect.cursor()
        super().__init__()
        self.setup_ui()
        self.init_ui()

    def init_ui(self):
        self.change_window[int].connect(self.setCurrentIndex)
        self.exit.connect(self.close)

        full_file_path = os.path.join(os.getcwd(), 'interfaces/resources/music.mp3')
        self.playlist = QMediaPlaylist()
        url = QUrl.fromLocalFile(full_file_path)
        self.playlist.addMedia(QMediaContent(url))
        self.playlist.setPlaybackMode(QMediaPlaylist.Loop)

        self.player = QMediaPlayer()
        self.player.setPlaylist(self.playlist)
        self.player.play()

    def keyPressEvent(self, event):
        self.currentWidget().keyPressEvent(event)

    def paintEvent(self, event):
        color = QColor(50, 50, 210)
        painter = QPainter(self)
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, self.width(), self.height())

    def start_game(self, extra_mode):
        if extra_mode:
            self.board = ExtraBoard(self.db_cursor, self.widget(2))
        else:
            self.board = Board(self.db_cursor, self.widget(2))
        self.change_window.emit(2)
        self.currentWidget().layout().insertWidget(0, self.board)
        self.currentWidget().back_button.setFocusPolicy(Qt.NoFocus)
        self.board.start_game()


if __name__ == '__main__':  # Start of programm
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
