import sqlite3
import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget

import interfaces.window_interface as window_interface


class MainWindow(window_interface.Window):
    change_window = pyqtSignal(int)
    exit = pyqtSignal()
    win = pyqtSignal(bool)

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
            self.board = ExtraBoard(self.db_cursor, self)
        else:
            self.board = Board(self.db_cursor, self)
        self.change_window.emit(2)
        self.currentWidget().layout().insertWidget(0, self.board)
        self.board.start_game()


class Board(QWidget):
    def __init__(self, db_cursor: sqlite3.Cursor, main_window: MainWindow):
        super().__init__()
        self.main_window = main_window
        self.PIXEL_SIZE = 30
        self.X_WIDTH, self.Y_HEIGTH = db_cursor.execute('''SELECT X_WIDTH, Y_HEIGTH FROM settings
        WHERE TYPE == \'Using\'''').fetchone()
        self.setMinimumSize(self.PIXEL_SIZE * self.X_WIDTH, self.PIXEL_SIZE * self.Y_HEIGTH)
        self.setMaximumSize(self.PIXEL_SIZE * self.X_WIDTH, self.PIXEL_SIZE * self.Y_HEIGTH)

    def start_game(self):
        pass

    def finish_game(self, win):
        self.main_window.win.emit(win)


class ExtraBoard(Board):
    pass


class Piece(QWidget):
    def __init__(self):
        pass


class Tetrominoe:
    no_shape = 0
    z_shape = 1
    s_shape = 2
    line_shape = 3
    t_shape = 4
    square_shape = 5
    l_shape = 6
    mirrored_l_shape = 7


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
