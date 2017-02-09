import bwb_model
import bwb_date_time_dialog
import datetime
import time
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui


class DiaryListWidget(QtWidgets.QWidget):
    """
    Inspiration for this class:
    http://stackoverflow.com/questions/20041385/python-pyqt-setting-scroll-area
    """

    add_text_to_diary_button_pressed_signal = QtCore.pyqtSignal(str, int)
    context_menu_change_date_signal = QtCore.pyqtSignal()
    context_menu_delete_signal = QtCore.pyqtSignal()

    row_last_clicked = None

    def __init__(self):
        super().__init__()

        self.v_box = QtWidgets.QVBoxLayout(self)
        self.list_widget = QtWidgets.QListWidget()
        self.setLayout(self.v_box)
        diary_label = QtWidgets.QLabel("<h3>Diary</h3>")
        self.v_box.addWidget(diary_label)
        #self.list_widget.setMinimumWidth(530)
        # -strange but we have to set a min width to avoid seeing the horizontal scrollbar
        self.v_box.addWidget(self.list_widget)
        self.list_widget.itemPressed.connect(self.on_item_pressed)  # Clicked doesn't work
        self.list_widget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.list_widget.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)

        # Adding new diary entry..
        edit_diary_entry_hbox_l5 = QtWidgets.QHBoxLayout()
        self.v_box.addLayout(edit_diary_entry_hbox_l5)
        # ..label
        diary_entry_label = QtWidgets.QLabel("<h4>New diary entry</h4>")
        self.v_box.addWidget(diary_entry_label)
        # ..text area
        self.adding_text_to_diary_textedit_w6 = QtWidgets.QTextEdit()
        edit_diary_entry_hbox_l5.addWidget(self.adding_text_to_diary_textedit_w6)
        self.adding_text_to_diary_textedit_w6.setFixedHeight(50)
        self.adding_to_diary_date_datetimeedit_w6 = QtWidgets.QDateTimeEdit()
        self.adding_to_diary_date_datetimeedit_w6.setDisplayFormat("dddd")
        self.adding_to_diary_date_datetimeedit_w6.setCalendarPopup(True)
        self.update_gui_date()
        edit_diary_entry_hbox_l5.addWidget(self.adding_to_diary_date_datetimeedit_w6)
        self.adding_to_diary_now_button = QtWidgets.QPushButton("Now/Today")
        self.adding_to_diary_now_button.pressed.connect(self.on_today_button_pressed)
        edit_diary_entry_hbox_l5.addWidget(self.adding_to_diary_now_button)
        self.adding_diary_entry_bn_w5 = QtWidgets.QPushButton("Add new")
        self.v_box.addWidget(self.adding_diary_entry_bn_w5)
        self.adding_diary_entry_bn_w5.clicked.connect(self.on_add_text_to_diary_button_clicked)

    def on_item_pressed(self, i_listwidgetitem):
        row_index_it = i_listwidgetitem.listWidget().row(i_listwidgetitem)
        print("cell clicked -- row = " + str(row_index_it))
        self.row_last_clicked = i_listwidgetitem

    def contextMenuEvent(self, i_QContextMenuEvent):
        """
        Overridden
        Docs: http://doc.qt.io/qt-5/qwidget.html#contextMenuEvent
        """
        self.right_click_menu = QtWidgets.QMenu()
        rename_action = QtWidgets.QAction("Rename")
        rename_action.triggered.connect(self.on_context_menu_rename)
        self.right_click_menu.addAction(rename_action)
        delete_action = QtWidgets.QAction("Delete")
        delete_action.triggered.connect(self.on_context_menu_delete)
        self.right_click_menu.addAction(delete_action)
        change_date_action = QtWidgets.QAction("Change date")
        change_date_action.triggered.connect(self.on_context_menu_change_date)
        self.right_click_menu.addAction(change_date_action)
        self.right_click_menu.exec_(QtGui.QCursor.pos())

    def on_context_menu_delete(self):
        message_box_reply = QtWidgets.QMessageBox.question(
            self, "Remove diary entry?", "Are you sure that you want to remove this diary entry?"
        )
        if message_box_reply == QtWidgets.QMessageBox.Yes:
            bwb_model.DiaryM.remove(int(self.row_last_clicked.data(QtCore.Qt.UserRole)))
            self.update_gui()
            self.context_menu_delete_signal.emit()
        else:
            pass  # -do nothing

    def on_context_menu_rename(self):
        """
        Docs: http://doc.qt.io/qt-5/qinputdialog.html#getText
        """
        last_clicked_row_dbkey_it = int(self.row_last_clicked.data(QtCore.Qt.UserRole))
        diary_entry = bwb_model.DiaryM.get(last_clicked_row_dbkey_it)
        text_input_dialog = QtWidgets.QInputDialog()
        new_text_qstring = text_input_dialog.getText(
            self, "Rename dialog", "New name: ", text=diary_entry.diary_text)
        if new_text_qstring[0]:
            print("new_text_qstring = " + str(new_text_qstring))
            bwb_model.DiaryM.update_note(last_clicked_row_dbkey_it, new_text_qstring[0])
            self.update_gui()
        else:
            pass  # -do nothing

    def on_context_menu_change_date(self):
        last_clicked_row_dbkey_it = int(self.row_last_clicked.data(QtCore.Qt.UserRole))
        diary_item = bwb_model.DiaryM.get(last_clicked_row_dbkey_it)
        updated_time_unix_time_it = bwb_date_time_dialog.DateTimeDialog.get_date_time_dialog(diary_item.date_added_it)
        if updated_time_unix_time_it != -1:
            bwb_model.DiaryM.update_date(diary_item.id, updated_time_unix_time_it)
            self.update_gui()
            self.context_menu_change_date_signal.emit()
        else:
            pass  # -do nothing

    def update_gui(self):
        self.list_widget.clear()
        prev_diary_entry = None

        for diary_entry in bwb_model.DiaryM.get_all():
            # Setting up the underlying data
            observance_list = bwb_model.ObservanceM.get_all_for_diary_id(diary_entry.id)
            diary_entry_obs_sg = ""
            delimiter_sg = ", "
            if observance_list is not None and observance_list != []:
                for obs_entry in observance_list:
                    diary_entry_obs_sg = diary_entry_obs_sg + obs_entry.title + delimiter_sg
            karma_entry = bwb_model.KarmaM.get(diary_entry.ref_karma_id)
            if (prev_diary_entry is None) or (not is_same_day(prev_diary_entry.date_added_it, diary_entry.date_added_it)):
                t_date_as_weekday_sg = datetime.datetime.fromtimestamp(diary_entry.date_added_it).strftime("%A")
                list_item = QtWidgets.QListWidgetItem("     " + t_date_as_weekday_sg.title())
                list_item.setFlags(list_item.flags() & ~ QtCore.Qt.ItemIsSelectable & QtCore.Qt.ItemIsUserCheckable)
                self.list_widget.addItem(list_item)
            karma_title_sg = ""
            if karma_entry is not None:
                karma_title_sg = karma_entry.title_sg.strip() + " "
            label_text_sg = karma_title_sg\
                + "[" + diary_entry_obs_sg.strip(delimiter_sg) + "] "\
                + diary_entry.diary_text.strip()

            # Setting up the display
            list_item = QtWidgets.QListWidgetItem()
            list_item.setData(QtCore.Qt.UserRole, diary_entry.id)  # to read: .data
            row_layout_l7 = QtWidgets.QHBoxLayout()
            row_label_w8 = QtWidgets.QLabel(label_text_sg)
            ##row_label_w8.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
            row_label_w8.setWordWrap(True)
            row_layout_l7.addWidget(row_label_w8)
            row_layout_l7.setContentsMargins(5, 5, 5, 5)
            # -if this is not set we will get a default that is big and looks strange for a list
            row_layout_l7.setSpacing(2)
            row_w6 = QtWidgets.QWidget()
            row_w6.setLayout(row_layout_l7)
            row_w6.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
            row_w6.adjustSize()
            list_item.setSizeHint(row_w6.sizeHint())
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, row_w6) # -http://doc.qt.io/qt-5/qlistwidget.html#setItemWidget

            """
            if i_cur_sel_it == diary_entry.observance_ref:
                #label.setFrameStyle(QFrame.StyledPanel)
                # -http://doc.qt.io/qt-4.8/qframe.html#setFrameStyle
                # -http://nullege.com/codes/search/PyQt4.QtGui.QFrame.setFrameStyle

                #list_item.setFlags(list_item.flags() & ~ Qt.ItemIsSelectable)
                ######################list_item.setBackground(QtCore.Qt.red) <-----------------
            """

            prev_diary_entry = diary_entry  # -used for the weekday labels
        self.list_widget.scrollToBottom()

    def update_gui_date(self, i_unix_time_it = time.time()):
        """
        Not like other update_gui_ functions, this one is not called from the bwb_window.WellBeingWindow.update_gui
        function.
        """
        qdatetime = QtCore.QDateTime()
        qdatetime.setMSecsSinceEpoch(i_unix_time_it * 1000)
        self.adding_to_diary_date_datetimeedit_w6.setDateTime(qdatetime)

    def on_today_button_pressed(self):
        self.update_gui_date(time.time())

    def on_add_text_to_diary_button_clicked(self):
        notes_sg = self.adding_text_to_diary_textedit_w6.toPlainText().strip()
        time_qdatetime = self.adding_to_diary_date_datetimeedit_w6.dateTime()
        unix_time_it = time_qdatetime.toMSecsSinceEpoch() // 1000
        self.add_text_to_diary_button_pressed_signal.emit(notes_sg, unix_time_it)
        self.adding_text_to_diary_textedit_w6.clear()


def is_same_day(i_first_date_it, i_second_date_it):
    first_date = datetime.datetime.fromtimestamp(i_first_date_it)
    second_date = datetime.datetime.fromtimestamp(i_second_date_it)
    return first_date.date() == second_date.date()  # - == operator works for "datetime" type
