#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import sys
import os
import random
from PyQt5.QtCore import pyqtSignal, QBasicTimer, QPropertyAnimation, QRect, QEasingCurve, \
    QAbstractAnimation, QPoint, QRectF, Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlaylist, QMediaContent, QMediaPlayer
from PyQt5.QtGui import QKeySequence, QPainterPath, QPainter, QColor, QPen
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

        full_file_path = os.path.join(os.getcwd(), 'music.mp3')
        self.playlist = QMediaPlaylist()
        url = QUrl.fromLocalFile(full_file_path)
        self.playlist.addMedia(QMediaContent(url))
        self.playlist.setPlaybackMode(QMediaPlaylist.Loop)

        self.player = QMediaPlayer()
        self.player.setPlaylist(self.playlist)
        self.player.play()

    def keyPressEvent(self, event):
        self.currentWidget().keyPressEvent(event)

    def start_game(self, extra_mode):
        if extra_mode:
            self.board = ExtraBoard(self.db_cursor, self.widget(2))
        else:
            self.board = Board(self.db_cursor, self.widget(2))
        self.change_window.emit(2)
        self.currentWidget().layout().insertWidget(0, self.board)
        self.currentWidget().back_button.setFocusPolicy(Qt.NoFocus)
        self.board.start_game()


class Board(QWidget):  # Game board
    def __init__(self, db_cursor: sqlite3.Cursor, main_window):
        super().__init__()
        self.main_window = main_window
        self.PIXEL_SIZE = 30
        self.SPEED = 300
        self.X_WIDTH, self.Y_HEIGHT = db_cursor.execute('''SELECT X_WIDTH, Y_HEIGHT FROM settings
        WHERE TYPE == \'Using\'''').fetchone()
        self.setMinimumSize(self.PIXEL_SIZE * self.X_WIDTH, self.PIXEL_SIZE * self.Y_HEIGHT)
        self.setMaximumSize(self.PIXEL_SIZE * self.X_WIDTH, self.PIXEL_SIZE * self.Y_HEIGHT)
        self.setFocusPolicy(Qt.StrongFocus)
        self.main_window.back_button.setFocusPolicy(Qt.NoFocus)

        self.timer = QBasicTimer()
        self.drop_timer = QBasicTimer()
        self.board = []
        self.is_started = False
        self.next_piece = False

    def start_game(self):
        self.set_clear_board()
        self.is_started = True
        self.waiting_next_piece = False
        self.wait_remove_line = False
        self.score = 0
        self.time = 0
        self.new_piece()
        self.main_window.keyPressEvent = self.keyPressEvent
        self.timer.start(self.SPEED, self)
        self.show()

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            self.time += self.SPEED / 1000
            self.update_data()
            if self.waiting_next_piece:
                self.waiting_next_piece = False
                self.new_piece()
            else:
                self.one_line_down()
            if self.prev_board != self.board:
                self.update()
                self.prev_board = self.board
        if event.timerId() == self.drop_timer.timerId():
            self.piece_dropped()
            self.drop_timer.stop()
            self.update()

    def one_line_down(self):
        if not self.try_move(self.current_piece, self.current_piece.board_coords[0],
                             self.current_piece.board_coords[1] + 1) and \
                not self.drop_timer.isActive():
            self.piece_dropped()

    def piece_dropped(self):
        for i in range(4):
            x = self.current_piece.board_coords[0] + self.current_piece.x(i)
            y = self.current_piece.board_coords[1] - self.current_piece.y(i)
            self.set_shape_at(x, y, self.current_piece.shape)
            if self.current_piece.squares[i] is not None:
                self.current_piece.squares[i].setParent(None)
        self.remove_full_lines()
        self.score += 10
        self.update_data()
        if not self.waiting_next_piece:
            self.new_piece()

    def remove_full_lines(self):
        num_full_lines = 0
        rows_to_remove = []
        for num_of_row in range(self.Y_HEIGHT):
            count_pieces_on_line = 0
            for x in range(self.X_WIDTH):
                if self.shape_at(x, num_of_row) != Tetrominoe.no_shape:
                    count_pieces_on_line += 1
            if count_pieces_on_line == self.X_WIDTH:
                rows_to_remove.append(num_of_row)
        for line_num in rows_to_remove:
            for y in range(line_num, 0, -1):
                for x in range(self.X_WIDTH):
                    self.set_shape_at(x, y, self.shape_at(x, y - 1))
        num_full_lines = num_full_lines + len(rows_to_remove)
        if num_full_lines > 0:
            self.score += num_full_lines * 100
            self.update_data()
            self.waiting_next_piece = True
            self.current_piece.set_shape(Tetrominoe.no_shape)
            self.update()

    def keyPressEvent(self, event):
        if not self.is_started or self.current_piece.shape == Tetrominoe.no_shape:
            return
        if self.drop_timer.isActive():
            return
        key = event.key()
        keys = {func: QKeySequence(key) for func, key in
                zip(['RIGHT_ROTATE', 'LEFT_ROTATE', 'MOVE_LEFT', 'MOVE_RIGHT', 'ONE_BLOCK_DOWN',
                     'DROP_PIECE'], self.main_window.db_cursor.execute('''
        SELECT RIGHT_ROTATE, LEFT_ROTATE, MOVE_LEFT, MOVE_RIGHT, ONE_BLOCK_DOWN, DROP_PIECE
        FROM settings WHERE TYPE == \'Using\'''').fetchone())}
        if key == keys['RIGHT_ROTATE']:
            if self.current_piece.shape != Tetrominoe.square_shape:
                piece = self.current_piece.rotate_clone_right()
                if self.try_move(piece, *self.current_piece.board_coords):
                    self.current_piece.rotate_right()
                for i in range(4):
                    piece.squares[i].setParent(None)
        elif key == keys['LEFT_ROTATE']:
            if self.current_piece.shape != Tetrominoe.square_shape:
                piece = self.current_piece.rotate_clone_left()
                if self.try_move(piece, *self.current_piece.board_coords):
                    self.current_piece.rotate_left()
                for i in range(4):
                    piece.squares[i].setParent(None)
        elif key == keys['MOVE_LEFT']:
            self.try_move(self.current_piece, self.current_piece.board_coords[0] - 1,
                          self.current_piece.board_coords[1])
        elif key == keys['MOVE_RIGHT']:
            self.try_move(self.current_piece, self.current_piece.board_coords[0] + 1,
                          self.current_piece.board_coords[1])
        elif key == keys['ONE_BLOCK_DOWN']:
            self.one_line_down()
        elif key == keys['DROP_PIECE']:
            self.drop_piece()

    def drop_piece(self):
        new_y = self.current_piece.board_coords[1]
        while new_y < self.Y_HEIGHT:
            if not self.try_move(self.current_piece, self.current_piece.board_coords[0], new_y + 1):
                break
            new_y += 1
        self.drop_timer.start(100, self)

    def set_shape_at(self, x, y, piece):
        if y >= 0:
            self.board[y][x] = piece

    def try_move(self, piece, new_x, new_y):
        for i in range(4):
            x = new_x + piece.x(i)
            y = new_y - piece.y(i)
            if x < 0 or x >= self.X_WIDTH or y >= self.Y_HEIGHT:
                return False
            if self.shape_at(x, y) != Tetrominoe.no_shape:
                return False
        piece.animate_self(new_x, new_y)
        return True

    def new_piece(self):
        shape = random.randint(1, 7)
        self.current_piece = Piece(self, self.X_WIDTH // 2,
                                   -1 + Tetrominoe().min_y(shape))
        self.current_piece.set_shape(shape)
        if not self.try_move(self.current_piece, self.current_piece.board_coords[0],
                             self.current_piece.board_coords[1]):
            self.current_piece.set_shape(Tetrominoe.no_shape)
            self.timer.stop()
            self.is_started = False
            self.finish_game()

    def set_clear_board(self):
        self.board = [[Tetrominoe.no_shape for _ in range(self.X_WIDTH)]
                      for _ in range(self.Y_HEIGHT)]
        self.prev_board = self.board

    def update_data(self):
        self.main_window.score_LCD_number.display(self.score)
        self.main_window.time_LCD_number.display(round(self.time))

    def paintEvent(self, event):
        painter = QPainter(self)
        for y in range(self.Y_HEIGHT):
            for x in range(self.X_WIDTH):
                shape = self.shape_at(x, y)
                if shape != Tetrominoe.no_shape:
                    self.draw_square(x, y, shape, painter)

    def draw_square(self, x, y, shape, painter):
        color = QColor(*list(map(int, Tetrominoe.colors[shape].split(', '))))
        rect_path = QPainterPath()
        rect_path.addRoundedRect(QRectF(self.PIXEL_SIZE * x, self.PIXEL_SIZE * y,
                                        self.PIXEL_SIZE, self.PIXEL_SIZE),
                                 2, 2)
        painter.setPen(Qt.NoPen)
        painter.setBrush(color)
        painter.drawPath(rect_path)

    def finish_game(self):
        self.timer.stop()
        self.is_started = False
        self.main_window.main_window.finish_game.emit(self.score)
        record_type = ('Default' if self.__class__ == Board else 'Extra')
        self.main_window.db_cursor.execute(f'''INSERT INTO leader_board (record_type, score) VALUES
        (\'{record_type}\', \'{self.score}\')''')
        self.main_window.main_window.db_connect.commit()

    def shape_at(self, x, y):
        if y < 0:
            y = 0
        return self.board[y][x]


class ExtraBoard(Board):
    def __init__(self, db_cursor: sqlite3.Cursor, main_window):
        super().__init__(db_cursor, main_window)
        self.extra_timer = QBasicTimer()

    def start_game(self):
        super().start_game()
        self.extra_timer.start(3000, self)

    def timerEvent(self, event):
        if event.timerId() == self.extra_timer.timerId():
            self.drop_piece()
        else:
            super().timerEvent(event)

    def piece_dropped(self):
        if self.is_started:
            super().piece_dropped()
            self.extra_timer.start(3000, self)

    def finish_game(self):
        super().finish_game()
        self.extra_timer.stop()


class Piece(QWidget):  # Piece for game
    def __init__(self, board: Board, cur_x, cur_y):
        self.board = board
        self.board_coords = [cur_x, cur_y]
        self.coords = [[0, 0] for _ in range(4)]
        self.squares = [None, None, None, None]
        self.set_shape(Tetrominoe.no_shape)

    def set_shape(self, shape):
        table = Tetrominoe.pieces[shape]
        for i in range(4):
            for j in range(2):
                self.coords[i][j] = table[i][j]
            if type(self.squares[i]) == QWidget:
                self.squares[i].setParent(None)
                self.squares[i] = None
            if shape != Tetrominoe.no_shape:
                self.squares[i] = QWidget(self.board)
                x = self.x(i) + self.board_coords[0]
                y = -self.y(i) + self.board_coords[1]
                self.squares[i].setGeometry(self.board.PIXEL_SIZE * x,
                                            self.board.PIXEL_SIZE * y,
                                            self.board.PIXEL_SIZE, self.board.PIXEL_SIZE)
                self.squares[i].setStyleSheet(f'background-color: rgb({Tetrominoe.colors[shape]});'
                                              f'border-radius:2px;')
                self.squares[i].show()
        self.shape = shape

    def x(self, index):
        return self.coords[index][0]

    def y(self, index):
        return self.coords[index][1]

    def set_x(self, index, x):
        self.coords[index][0] = x

    def set_y(self, index, y):
        self.coords[index][1] = y

    def rotate_clone_left(self):
        result = Piece(self.board, *self.board_coords)
        result.set_shape(self.shape)
        for index in range(4):
            result.set_x(index, -self.y(index))
            result.set_y(index, self.x(index))
        return result

    def rotate_clone_right(self):
        result = Piece(self.board, *self.board_coords)
        result.set_shape(self.shape)
        for index in range(4):
            result.set_x(index, self.y(index))
            result.set_y(index, -self.x(index))
        return result

    def rotate_left(self):
        for index in range(4):
            x, y = self.x(index), self.y(index)
            self.set_x(index, -y)
            self.set_y(index, x)

    def rotate_right(self):
        for index in range(4):
            x, y = self.x(index), self.y(index)
            self.set_x(index, y)
            self.set_y(index, -x)

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
                                                  (-self.coords[i][1] + new_y)))
                self.animation.start()
                self.animations.append(self.animation)


class Tetrominoe:  # Data of pieces
    colors = ['0, 0, 0', '204, 102, 102', '102, 204, 102', '102, 102, 204',
              '204, 204, 102', '204, 102, 204', '102, 204, 204', '218, 170, 0']
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
