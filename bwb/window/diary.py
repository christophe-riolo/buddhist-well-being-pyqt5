from bwb import model
from bwb.window import date
from datetime import datetime
import time
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import QStringListModel


class DiaryModel(QStringListModel):
    def __init__(self, ui):
        super().__init__()

        # We need the ui to access the actions.
        self.ui = ui
        self.update_gui()

    def on_item_pressed(self, i_listwidgetitem):
        row_index_it = i_listwidgetitem.listWidget().row(i_listwidgetitem)
        print("cell clicked -- row = " + str(row_index_it))
        self.row_last_clicked = i_listwidgetitem

    # TODO should be in view b
    # not model
    def contextMenuEvent(self, i_QContextMenuEvent):
        """
        Overridden
        Docs: http://doc.qt.io/qt-5/qwidget.html#contextMenuEvent
        """
        print("Making context menu")
        self.menu = QtWidgets.QMenu()

        # Adding the actions to the menu.
        self.menu.addAction(self.ui.actionRename)
        self.menu.addAction(self.ui.actionDelete)
        self.menu.addAction(self.ui.actionChange_date)

        # Connecting the actions to the slots.
        self.ui.actionRename.triggered.connect(self.rename)
        self.ui.actionDelete.triggered.connect(self.delete)
        self.ui.actionChangeDate.triggered.connect(self.change_date)

        # Showing the menu.
        self.menu.exec_(QtGui.QCursor.pos())

    def delete(self):
        message_box_reply = QtWidgets.QMessageBox.question(
                self,
                "Remove diary entry?",
                "Are you sure that you want to remove this diary entry?"
                )
        if message_box_reply == QtWidgets.QMessageBox.Yes:
            model.DiaryM.remove(
                    int(self.row_last_clicked.data(QtCore.Qt.UserRole)))
            self.update_gui()
            self.context_menu_delete_signal.emit()
        else:
            pass  # -do nothing

    def rename(self):
        """
        Docs: http://doc.qt.io/qt-5/qinputdialog.html#getText
        """
        last_clicked_row_dbkey_it = int(
                self.row_last_clicked.data(QtCore.Qt.UserRole))
        diary_entry = model.DiaryM.get(last_clicked_row_dbkey_it)
        text_input_dialog = QtWidgets.QInputDialog()
        new_text_qstring = text_input_dialog.getText(
                self,
                "Rename dialog",
                "New name: ",
                text=diary_entry.diary_text)
        if new_text_qstring[0]:
            print("new_text_qstring = " + str(new_text_qstring))
            model.DiaryM.update_note(
                    last_clicked_row_dbkey_it, new_text_qstring[0])
            self.update_gui()
        else:
            pass  # -do nothing

    def change_date(self):
        last_clicked_row_dbkey_it = int(
                self.row_last_clicked.data(QtCore.Qt.UserRole))
        diary_item = model.DiaryM.get(last_clicked_row_dbkey_it)
        updated_time_unix_time_it = date.DateTimeDialog.\
            get_date_time_dialog(diary_item.date_added_it)
        if updated_time_unix_time_it != -1:
            model.DiaryM.update_date(
                    diary_item.id, updated_time_unix_time_it)
            self.update_gui()
            self.context_menu_change_date_signal.emit()
        else:
            pass  # -do nothing

    def update_gui(self):
        def is_same_day(first_date, second_date):
            first_date = datetime.fromtimestamp(first_date.date_added_it)
            second_date = datetime.fromtimestamp(second_date.date_added_it)

            return first_date.date() == second_date.date()

        prev_diary_entry = None

        # TODO: this could probably be made into a list comprehension
        # using functions.
        data = []
        for diary_entry in model.DiaryM.get_all():
            # Setting up the underlying data.
            observance_list = model.ObservanceM.get_all_for_diary_id(
                    diary_entry.id)
            diary_entry_obs_sg = ""

            # There *should* be observances, else this entry is corrupt.
            if observance_list:
                diary_entry_obs_sg = ", ".join(
                    map(lambda x: x.title, observance_list))
            else:
                continue

            # Getting the activity.
            karma_entry = model.KarmaM.get(diary_entry.ref_karma_id)
            karma_title_sg = ""
            if karma_entry is not None:
                karma_title_sg = karma_entry.title_sg.strip() + " "

            # Putting all the text pieces together.
            label_text_sg = karma_title_sg\
                + "[" + diary_entry_obs_sg + "] "\
                + diary_entry.diary_text.strip()

            # Adding weekday if we have reached a new day.
            # TODO: make it a list separator, not part of an entry.
            if (prev_diary_entry is None
                    or not is_same_day(prev_diary_entry, diary_entry)):
                weekday = datetime.fromtimestamp(
                          diary_entry.date_added_it)\
                          .strftime("%A")
                label_text_sg = ("     "
                                 + weekday.title()
                                 + "\n"
                                 + label_text_sg)

            data.append(label_text_sg)

            prev_diary_entry = diary_entry  # -used for the weekday labels

        self.setStringList(data)

    def update_gui_date(self, i_unix_time_it=time.time()):
        """
        Not like other update_gui_ functions, this one is not called from
        the bwb_window.WellBeingWindow.update_gui function.
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
        self.add_text_to_diary_button_pressed_signal.emit(
                notes_sg, unix_time_it)
