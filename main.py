#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import sys
import random
from PyQt5.QtCore import pyqtSignal, QBasicTimer, QPropertyAnimation, QRect, QEasingCurve,\
    QAbstractAnimation, QPoint
from PyQt5.QtWidgets import QApplication, QWidget
import interfaces.window_interface as window_interface


class MainWindow(window_interface.Window):  # Main window
    change_window = pyqtSignal(int)
    exit = pyqtSignal()
    finish_game = pyqtSignal(int)

    def __init__(self):
        self.db_connect = sqlite3.connect('app_data.db')
        self.db_cursor = self.db_connect.cursor()
        super().__init__()
        self.setup_ui()
        self.init_ui()

    def init_ui(self):
        self.change_window[int].connect(self.setCurrentIndex)
        self.exit.connect(self.close)

    def start_game(self, extra_mode):
        if extra_mode:
            self.board = ExtraBoard(self.db_cursor, self.widget(2))
        else:
            self.board = Board(self.db_cursor, self.widget(2))
        self.change_window.emit(2)
        self.currentWidget().layout().insertWidget(0, self.board)
        self.board.start_game()


class Board(QWidget):  # Game board
    def __init__(self, db_cursor: sqlite3.Cursor, main_window: QWidget):
        super().__init__()
        self.main_window = main_window
        self.show()
        self.PIXEL_SIZE = 30
        self.SPEED = 500
        self.X_WIDTH, self.Y_HEIGHT = db_cursor.execute('''SELECT X_WIDTH, Y_HEIGHT FROM settings
        WHERE TYPE == \'Using\'''').fetchone()
        self.setMinimumSize(self.PIXEL_SIZE * self.X_WIDTH, self.PIXEL_SIZE * self.Y_HEIGHT)
        self.setMaximumSize(self.PIXEL_SIZE * self.X_WIDTH, self.PIXEL_SIZE * self.Y_HEIGHT)

        self.timer = QBasicTimer()
        self.board = []
        self.is_started = False
        self.next_piece = False

    def start_game(self):
        self.set_clear_board()
        self.is_started = True
        self.waiting_next_piece = False
        self.score = 0
        self.new_piece()
        self.timer.start(self.SPEED, self)

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            if self.waiting_next_piece:
                self.waiting_next_piece = False
                self.new_piece()
            else:
                self.one_line_down()

    def one_line_down(self):
        if not self.try_move(self.current_piece, self.current_piece.board_coords[0],
                             self.current_piece.board_coords[1] + 1):
            self.piece_dropped()

    def piece_dropped(self):
        pass

    def try_move(self, piece, new_x, new_y):
        piece.animate_self(new_x, new_y)

    def new_piece(self):
        shape = random.randint(1, 7)
        self.current_piece = Piece(self, self.X_WIDTH // 2 + 1,
                                   -1 + Tetrominoe().min_y(shape))
        self.current_piece.set_shape(shape)

    def set_clear_board(self):
        self.board = [[Tetrominoe.no_shape for _ in range(self.X_WIDTH)]
                      for _ in range(self.Y_HEIGHT)]

    def finish_game(self):
        self.main_window.finish_game.emit(self.score)


class ExtraBoard(Board):  # TODO: Game board for extra mode
    pass


class Piece(QWidget):  # TODO: Piece for game
    def __init__(self, board: Board, cur_x, cur_y):
        self.board = board
        self.board_coords = [cur_x, cur_y]
        self.coords = [[0, 0] for _ in range(4)]
        self.squares = [None, None, None, None]
        self.set_shape(Tetrominoe.no_shape)

    def set_shape(self, shape):
        colors = ['0x000000', '0xCC6666', '0x66CC66', '0x6666CC',
                  '0xCCCC66', '0xCC66CC', '0x66CCCC', '0xDAAA00']
        table = Tetrominoe.pieces[shape]
        for i in range(4):
            for j in range(2):
                self.coords[i][j] = table[i][j]
            if type(self.squares[i]) == QWidget:
                self.squares[i].setParent(None)
                self.squares[i] = None
            self.squares[i] = QWidget(self.board)
            self.squares[i].setGeometry(self.board.PIXEL_SIZE *
                                        (self.coords[i][0] + self.board_coords[0]),
                                        self.board.PIXEL_SIZE *
                                        (self.coords[i][1] + self.board_coords[1]),
                                        self.board.PIXEL_SIZE, self.board.PIXEL_SIZE)
            self.squares[i].setStyleSheet(f'background-color:rgb(255, 0, 0);border-radius:2px;')
            self.squares[i].show()

        self.shape = shape

    def animate_self(self, new_x, new_y):
        self.board_coords = [new_x, new_y]
        self.animations = []  # Damn Python garbage collector
        if self.shape != Tetrominoe.no_shape:
            for i in range(4):
                elem = self.squares[i]
                self.animation = QPropertyAnimation(elem, b'pos')
                self.animation.setDuration(100)
                self.animation.setEndValue(QPoint(self.board.PIXEL_SIZE *
                                                  (self.coords[i][0] + new_x),
                                                  self.board.PIXEL_SIZE *
                                                  (self.coords[i][1] + new_y)))
                self.animation.start()
                self.animations.append(self.animation)


class Tetrominoe:  # Data of pieces
    pieces = (((0, 0), (0, 0), (0, 0), (0, 0)),
              ((0, -1), (0, 0), (-1, 0), (-1, 1)),
              ((0, -1), (0, 0), (1, 0), (1, 1)),
              ((0, -1), (0, 0), (0, 1), (0, 2)),
              ((-1, 0), (0, 0), (1, 0), (0, 1)),
              ((0, 0), (1, 0), (0, 1), (1, 1)),
              ((-1, -1), (0, -1), (0, 0), (0, 1)),
              ((1, -1), (0, -1), (0, 0), (0, 1)))
    no_shape = 0
    z_shape = 1
    s_shape = 2
    line_shape = 3
    t_shape = 4
    square_shape = 5
    l_shape = 6
    mirrored_l_shape = 7

    def min_y(self, shape):
        min_y = self.pieces[shape][0][1]
        for i in range(4):
            min_y = min(min_y, self.pieces[shape][i][1])
        return min_y


if __name__ == '__main__':  # Start of programm
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
