import sqlite3

from PyQt5 import uic
from PyQt5.QtWidgets import QStackedWidget, QWidget, QButtonGroup, QHBoxLayout, QLabel, QPushButton,\
    QMessageBox


class Window(QStackedWidget):
    def setupUi(self):
        super().__init__()
        self.setGeometry(350, 100, 495, 624)
        self.setWindowTitle('Tetris Boosted')
        for elem in [StartPage, SelectModePage, GamePage, RecordsPage, SettingsPage, HelpPage]:
            elem = elem()
            elem.setupUi(self.db_cursor, self)
            self.addWidget(elem)


class Page(QWidget):
    def setupUi(self, db_cursor, main_window):
        super().__init__()
        uic.loadUi('interfaces/' + self.name_ui_file, self)
        self.main_window = main_window
        self.db_cursor = db_cursor
        self.backButton.clicked.connect(self.exit)
        self.initUi()

    def exit(self):
        self.main_window.change_window.emit(0)


class StartPage(Page):
    name_ui_file = 'start_page.ui'

    def setupUi(self, db_cursor: sqlite3.Cursor, main_window: Window):
        super().__init__()
        uic.loadUi('interfaces/' + self.name_ui_file, self)
        self.main_window = main_window
        self.db_cursor = db_cursor
        self.initUi()

    def initUi(self):
        self.startGameButton.clicked.connect(lambda: self.main_window.change_window.emit(1))
        self.recordsBoardButton.clicked.connect(lambda: self.main_window.change_window.emit(3))
        self.settingsButton.clicked.connect(lambda: self.main_window.change_window.emit(4))
        self.helpButton.clicked.connect(lambda: self.main_window.change_window.emit(5))
        self.exitButton.clicked.connect(lambda: self.main_window.exit.emit())


class SelectModePage(Page):
    name_ui_file = 'select_mode_page.ui'

    def initUi(self):
        self.defaultModeButton.clicked.connect(lambda: self.select_mode(False))
        self.extraModeButton.clicked.connect(lambda: self.select_mode(True))

    def select_mode(self, extra_mode):
        self.main_window.start_game(extra_mode)


class GamePage(Page):
    name_ui_file = 'game_page.ui'

    def exit(self):
        self.layout().removeItem(self.layout().itemAt(0))
        self.stateLabel.setText('')
        self.main_window.change_window.emit(0)

    def initUi(self):
        self.main_window.win[bool].connect(lambda win: self.stateLabel.setText(
            'You' + ('win' if win else 'lose') + '!'))


class RecordsPage(Page):
    name_ui_file = 'records_page.ui'

    def initUi(self):
        self.records = self.db_cursor.execute('''SELECT * FROM leader_board
        ORDER BY score''').fetchall()[-1:-10:-1]
        self.widget_elements = []
        self.deleteRecordsButtonGroup = QButtonGroup(self)
        for elem in self.records:
            self.widget_elements.append([elem[0]])  # id from db; Index = 0
            layout = QHBoxLayout(self)
            self.widget_elements[-1].append(layout)  # layout for interface; Index = 1
            self.recordsWidget.layout().addLayout(layout)
            label = QLabel(self)
            label.setText(str(elem[1]) + ': ' + str(elem[2]))
            layout.addWidget(label)
            self.widget_elements[-1].append(label)  # label for interface; Index = 2
            button = QPushButton(self)
            button.setText('Delete')
            self.deleteRecordsButtonGroup.addButton(button)
            layout.addWidget(button)
            self.widget_elements[-1].append(button)  # button for interface; Index = 3
        self.deleteRecordsButtonGroup.buttonClicked.connect(self.delete_record)

    def delete_record(self, button):
        reply = QMessageBox.question(self, 'Delete Item',
                                     'Are you sure to delete item?', QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            for elem in self.widget_elements:
                if elem[3] == button:
                    self.db_cursor.execute(f'''DELETE FROM leader_board
                    WHERE id == {elem[0]}''')
                    self.main_window.db_connect.commit()
                    self.clear_widget()
                    self.initUi()
                    self.recordsWidget.repaint()

    def clear_widget(self):
        for layout in map(lambda elem: elem[1], self.widget_elements):
            for i in range(self.recordsWidget.layout().count()):
                layout_item = self.recordsWidget.layout().itemAt(i)
                if layout_item.layout() == layout:
                    self.deleteItemsOfLayout(layout_item.layout())
                    self.recordsWidget.layout().removeItem(layout_item)
                    break

    def deleteItemsOfLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                else:
                    self.deleteItemsOfLayout(item.layout())


class SettingsPage(Page):
    name_ui_file = 'settings_page.ui'

    def initUi(self):
        pass


class HelpPage(Page):
    name_ui_file = 'help_page.ui'

    def initUi(self):
        pass
