import sqlite3

from PyQt5.QtWidgets import QStackedWidget, QWidget, QButtonGroup, QHBoxLayout, QLabel, \
    QPushButton, QMessageBox
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt

import interfaces.start_page
import interfaces.select_mode_page
import interfaces.game_page
import interfaces.records_page
import interfaces.settings_page
import interfaces.help_page


class Window(QStackedWidget):  # Interface of main window
    def setup_ui(self):
        super().__init__()  # Customisation of main window
        self.setGeometry(350, 100, 530, 624)
        self.setWindowTitle('Tetris Boosted')
        for elem in [StartPage, SelectModePage, GamePage, RecordsPage, SettingsPage,
                     HelpPage]:  # Insert pages into main window
            elem = elem()
            elem.setup_ui(self.db_cursor, self)
            self.addWidget(elem)


class Page(QWidget):  # Default interface of pages
    def setup_ui(self, db_cursor, main_window):
        super().__init__()  # Customisation of page
        self.setupUi(self)
        self.main_window = main_window  # Main window object
        self.db_cursor = db_cursor  # Data base cursor
        self.back_button.clicked.connect(self.exit)
        self.initUi()

    def exit(self):
        self.main_window.change_window.emit(0)


class StartPage(Page, interfaces.start_page.Ui_form):  # Inteface of start page
    def setup_ui(self, db_cursor: sqlite3.Cursor, main_window: Window):
        super().__init__()  # Customisation of main page
        self.setupUi(self)
        self.main_window = main_window
        self.db_cursor = db_cursor
        self.initUi()

    def initUi(self):
        self.start_game_button.clicked.connect(lambda: self.main_window.change_window.emit(1))
        self.records_board_button.clicked.connect(lambda: self.main_window.change_window.emit(3))
        self.settings_button.clicked.connect(lambda: self.main_window.change_window.emit(4))
        self.help_button.clicked.connect(lambda: self.main_window.change_window.emit(5))
        self.exit_button.clicked.connect(lambda: self.main_window.exit.emit())


class SelectModePage(Page, interfaces.select_mode_page.Ui_form):  # Interface of page for select mode
    def initUi(self):
        self.default_mode_button.clicked.connect(lambda: self.select_mode(False))
        self.extra_mode_button.clicked.connect(lambda: self.select_mode(True))

    def select_mode(self, extra_mode):
        self.main_window.start_game(extra_mode)


class GamePage(Page, interfaces.game_page.Ui_game_layout):  # Interface of game
    def exit(self):
        self.layout().itemAt(0).widget().timer.stop()
        self.layout().itemAt(0).widget().is_started = False
        try:
            self.layout().itemAt(0).widget().extra_timer.stop()
        except AttributeError:
            pass
        self.layout().itemAt(0).widget().setParent(None)
        self.state_label.setText('')
        self.main_window.change_window.emit(0)

    def initUi(self):
        self.main_window.finish_game[int].connect(lambda score: self.state_label.setText(
            'Your score: ' + str(score)))


class RecordsPage(Page, interfaces.records_page.Ui_form):  # Interface of records page
    def initUi(self):
        self.records = self.db_cursor.execute('''SELECT * FROM leader_board
        ORDER BY score''').fetchall()[-1:-10:-1]
        self.widget_elements = []
        self.delete_records_button_group = QButtonGroup(self)
        for elem in self.records:
            self.widget_elements.append([elem[0]])  # id from db; Index = 0
            layout = QHBoxLayout()
            self.widget_elements[-1].append(layout)  # layout for interface; Index = 1
            self.records_widget.layout().addLayout(layout)
            label = QLabel(self)
            label.setText(str(elem[1]) + ': ' + str(elem[2]))
            layout.addWidget(label)
            self.widget_elements[-1].append(label)  # label for interface; Index = 2
            button = QPushButton(self)
            button.setText('Delete')
            self.delete_records_button_group.addButton(button)
            layout.addWidget(button)
            self.widget_elements[-1].append(button)  # button for interface; Index = 3
        self.delete_records_button_group.buttonClicked.connect(self.delete_record)
        self.main_window.change_window[int].connect(lambda num: self.update_data() if num == 3 else
                                                    None)

    def update_data(self):
        self.clear_widget()
        self.initUi()

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
                    self.records_widget.repaint()

    def clear_widget(self):
        for layout in map(lambda elem: elem[1], self.widget_elements):
            for i in range(self.records_widget.layout().count()):
                layout_item = self.records_widget.layout().itemAt(i)
                if layout_item.layout() == layout:
                    self.delete_items_of_layout(layout_item.layout())
                    self.records_widget.layout().removeItem(layout_item)
                    break

    def delete_items_of_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                else:
                    self.delete_items_of_layout(item.layout())


class SettingsPage(Page, interfaces.settings_page.Ui_form):
    name_ui_file = 'settings_page.ui'

    def initUi(self):
        data_for_line_edits = self.db_cursor.execute('''SELECT X_WIDTH, Y_HEIGHT, RIGHT_ROTATE,
        LEFT_ROTATE, MOVE_LEFT, MOVE_RIGHT, ONE_BLOCK_DOWN, DROP_PIECE FROM settings
        WHERE TYPE == \'Using\'''').fetchone()  # Get data for line edit
        for index in range(len(data_for_line_edits)):
            data_for_line_edit_index = index
            if index <= 1:  # Find line edit in board settings
                line_edit = self.board.layout().itemAtPosition(index, 1)
            else:  # Find line edit in control settings
                line_edit = self.control.layout().itemAtPosition(index - 2, 1)
            line_edit = line_edit.widget()  # Get line edit
            if data_for_line_edit_index <= 1:  # Set data for line edit in board settings
                line_edit.setText(str(data_for_line_edits[data_for_line_edit_index]))
            else:  # Set data for line edit in control settings
                line_edit.setText(  # Set text
                    QKeySequence.toString(  # Get string from number
                        QKeySequence(  # Get key from number
                            data_for_line_edits[data_for_line_edit_index])))
        self.tracking_function_input = None
        self.board_settings_button_group.buttonClicked.connect(self.input_board_settings_clicked)
        self.control_settings_button_group.buttonClicked.connect(self.input_control_settings_clicked)
        self.back_to_default_button.clicked.connect(self.return_to_default)

    def input_control_settings_clicked(self, event):
        self.clear_widget()
        self.tracking_function_input = event
        event.setText('Click button')

    def keyPressEvent(self, event):
        if self.tracking_function_input is not None:
            if event.key() == Qt.Key_Escape:  # "Escape" button deselects button
                self.clear_widget()
            else:
                setting_name = ('RIGHT_ROTATE', 'LEFT_ROTATE', 'MOVE_LEFT', 'MOVE_RIGHT',
                                'ONE_BLOCK_DOWN',
                                'DROP_PIECE')[
                    self.control.layout().getItemPosition(
                        self.control.layout().indexOf(self.tracking_function_input))[0]]
                individual_key = True  # Check on individual of button
                for check_setting in (('RIGHT_ROTATE', 'LEFT_ROTATE', 'MOVE_LEFT', 'MOVE_RIGHT',
                                       'ONE_BLOCK_DOWN', 'DROP_PIECE')):
                    if check_setting != setting_name and event.key() \
                            == QKeySequence(self.db_cursor.execute(f'''
                    SELECT {check_setting} FROM settings WHERE Type == \'Using\'''').fetchone()[0]):
                        individual_key = False
                if not individual_key:
                    self.clear_widget()
                    self.control_settings_state_label.setText('Select not using button!')
                else:
                    self.db_cursor.execute(f'''UPDATE settings
                    SET {setting_name} = {event.key()}
                    WHERE TYPE == \'Using\'''')
                    self.main_window.db_connect.commit()
                    self.clear_widget()
                    self.initUi()

    def input_board_settings_clicked(self, event):
        button_pos = self.board.layout().getItemPosition(self.board.layout().indexOf(event))
        line_edit = self.board.layout().itemAtPosition(button_pos[0], 1).widget()
        setting_name = ('X_WIDTH', 'Y_HEIGHT')[self.board.layout().getItemPosition(
            self.board.layout().indexOf(event))[0]]
        num = line_edit.text()
        if not num.isdigit():
            self.clear_widget()
            self.board_settings_state_label.setText('Select number!')
        else:
            num = int(num)
            if 5 < num < 30:
                self.clear_widget()
                self.db_cursor.execute(f'''UPDATE settings
                SET {setting_name} = {num}
                WHERE TYPE = \'Using\'''')
                self.main_window.db_connect.commit()
            else:
                self.clear_widget()
                self.board_settings_state_label.setText('Select number bigger than 5 and '
                                                        'lower than 30')

    def return_to_default(self):
        self.db_cursor.execute('''UPDATE settings
        SET X_WIDTH = (SELECT X_WIDTH FROM settings WHERE TYPE == \'Default\'),
        Y_HEIGHT = (SELECT Y_HEIGHT FROM settings WHERE TYPE == \'Default\'),
        RIGHT_ROTATE = (SELECT RIGHT_ROTATE FROM settings WHERE TYPE == \'Default\'),
        LEFT_ROTATE = (SELECT LEFT_ROTATE FROM settings WHERE TYPE == \'Default\'),
        MOVE_LEFT = (SELECT MOVE_LEFT FROM settings WHERE TYPE == \'Default\'),
        MOVE_RIGHT = (SELECT MOVE_RIGHT FROM settings WHERE TYPE == \'Default\'),
        ONE_BLOCK_DOWN = (SELECT ONE_BLOCK_DOWN FROM settings WHERE TYPE == \'Default\'),
        DROP_PIECE = (SELECT DROP_PIECE FROM settings WHERE TYPE == \'Default\')
        WHERE TYPE == \'Using\'''')
        self.main_window.db_connect.commit()
        self.initUi()

    def exit(self):
        self.clear_widget()
        self.main_window.change_window.emit(0)

    def clear_widget(self):  # Function for return page to default state
        if self.tracking_function_input is not None:
            self.tracking_function_input.setText('Remap key')
            self.tracking_function_input = None
        self.control_settings_state_label.setText('')
        self.board_settings_state_label.setText('')


class HelpPage(Page, interfaces.help_page.Ui_form):
    def initUi(self):
        self.set_text()
        self.main_window.change_window[int].connect(lambda num: self.set_text() if num == 5
                                                    else None)

    def set_text(self):
        control_data = self.db_cursor.execute('''SELECT RIGHT_ROTATE,
        LEFT_ROTATE, MOVE_LEFT, MOVE_RIGHT, ONE_BLOCK_DOWN, DROP_PIECE FROM settings
        WHERE TYPE == \'Using\'''').fetchone()  # Get data for line edit
        data_names = ['Right rotate',
                      'Left rotate', 'Move left', 'Move right', 'One block down', 'Drop piece']
        out = f'''Goal:
Fill as many blocks as possible with blocks.
From ever delivered piece you get 10 points
From ever filled line you get 100 points
Extra mode:
You have 3 seconds before the item falls
Control:'''
        for index, data in enumerate(control_data):
            out += f'\n{data_names[index]}:' \
                   f' "{QKeySequence.toString(QKeySequence(control_data[index]))}"'
        self.help_text_label.setText(out)
