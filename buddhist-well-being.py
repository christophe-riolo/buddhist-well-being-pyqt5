
"""
Documentation:
https://developer.gnome.org/gtk3/stable/
http://lazka.github.io/pgi-docs/Gtk-3.0/index.html
https://python-gtk-3-tutorial.readthedocs.io/en/latest/index.html


"""

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
import bwb_model
import bwb_diary_list_widget
import time
from functools import partial

TEN_OBS_TEXT_WIDTH = 17 # in number of characters (so pixels can very)
TEN_OBS_TEXT_FONT_SIZE = 14
KARMA_TEXT_WIDTH = 30
KARMA_TEXT_FONT_SIZE = 10

DIARY_DATE_TEXT_WIDTH = 40
ADDING_TO_DIARY_TEXT_WIDTH = 80
DIARY_PIXEL_WIDTH = 300

class WellBeingWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        t_observances_lt = bwb_model.ObservanceM.get_all()

        self.setGeometry(30, 30, 700, 500)
        self.setWindowTitle("Buddhist Well-Being")
        self.setWindowIcon(QIcon("icon.png"))

        t_hbox = QHBoxLayout()
        t_left_vbox = QVBoxLayout()
        t_left_vbox_widget = QWidget()
        t_left_vbox_widget.setLayout(t_left_vbox)
        t_left_vbox_widget.setFixedWidth(190)

        t_hbox.addWidget(t_left_vbox_widget)
        self.right_vbox = QVBoxLayout()
        self.right_vbox_widget = QWidget()
        self.right_vbox_widget.setLayout(self.right_vbox)
        #self.right_vbox_widget.setFixedWidth(510)
        t_hbox.addWidget(self.right_vbox_widget)
        self.central_widget.setLayout(t_hbox)
        self.show()

        # Creating widgets..
        # ..for ten practices

        self.ten_observances_lb = QListWidget()
        t_left_vbox.addWidget(self.ten_observances_lb)
        self.ten_observances_lb.currentItemChanged.connect(self.observance_selected_fn)
        for observance_item in t_observances_lt:
            row = QListWidgetItem(observance_item.short_name_sg)
            self.ten_observances_lb.addItem(row)

        ## ..for details
        self.ten_practices_details_ll = QLabel("-----")
        self.ten_practices_details_ll.setWordWrap(True)
        t_left_vbox.addWidget(self.ten_practices_details_ll)

        #..for karma list
        self.karma_lb = QListWidget()
        t_left_vbox.addWidget(self.karma_lb)

        #..for adding new karma
        self.adding_new_karma_ey = QLineEdit()
        t_left_vbox.addWidget(self.adding_new_karma_ey)
        self.adding_new_karma_bn = QPushButton("Add new")
        t_left_vbox.addWidget(self.adding_new_karma_bn)
        self.adding_new_karma_bn.clicked.connect(self.add_new_karma_button_pressed_fn)

        #.. for diary
        ###self.diary_lb = QListWidget()
        self.diary_lb = bwb_diary_list_widget.DiaryListWidget()
        self.right_vbox.addWidget(self.diary_lb)

        # ..for adding new diary entry
        t_edit_diary_entry_hbox = QHBoxLayout()
        self.right_vbox.addLayout(t_edit_diary_entry_hbox)

        self.adding_to_diary_date_ey = QDateTimeEdit()
        t_edit_diary_entry_hbox.addWidget(self.adding_to_diary_date_ey)
        self.adding_to_diary_date_ey.setCalendarPopup(True)
        ###self.adding_to_diary_date_ey.insert(tkinter.END, "2015-01-09 13:42")
        self.adding_text_to_diary_tt = QTextEdit()
        t_edit_diary_entry_hbox.addWidget(self.adding_text_to_diary_tt)
        self.adding_text_to_diary_tt.setFixedHeight(50)
        self.adding_new_button = QPushButton("Add new")
        self.right_vbox.addWidget(self.adding_new_button)
        self.adding_new_button.clicked.connect(self.add_text_to_diary_button_pressed_fn)



        # Menu bar
        exit_command = QAction("Exit", self)
        exit_command.triggered.connect(self.close)
        redraw_command = QAction("Redraw", self)
        redraw_command.triggered.connect(self.update_gui)

        self.menu_bar = self.menuBar()
        file_menu = self.menu_bar.addMenu("&File")
        file_menu.addAction(exit_command)
        file_menu.addAction(redraw_command)



        """

        self.diary_labels_lt = []  # Used in the gui update function



        """


    def on_diary_frame_configure(self, i_event):
        self.diary_canvas.configure(scrollregion=self.diary_canvas.bbox("all"))

    def observance_selected_fn(self, i_curr_item, i_prev_item):
        #- http://lazka.github.io/pgi-docs/#Gtk-3.0/classes/ListBox.html#Gtk.ListBox.signals.row_activated
        t_selection_it = self.ten_observances_lb.currentRow() #.selectedItems()[0]
        t_observance = bwb_model.ObservanceM.get(t_selection_it)
        self.ten_practices_details_ll.setText(t_observance.sutra_text_sg)

        """
        for diary_item in bwb_model.DiaryM.get_all():
            if diary_item.observance_ref == t_selection_it:
                diary_item.marked_bl = True
        """

        self.update_gui()  # Showing habits for practice etc

    def add_new_karma_button_pressed_fn(self):
        t_observance_pos_it = self.ten_observances_lb.currentRow()
        t_text_sg = self.adding_new_karma_ey.text().strip() # strip is needed to remove a newline at the end (why?)
        if not (t_text_sg and t_text_sg.strip()):
            return
        t_last_pos_it = len(bwb_model.KarmaM.get_all_for_observance(t_observance_pos_it))
        bwb_model.KarmaM.add(t_observance_pos_it, t_last_pos_it, t_text_sg)

        self.adding_new_karma_ey.clear()
        self.update_gui()

    def add_text_to_diary_button_pressed_fn(self):
        t_observance_pos_it = self.ten_observances_lb.currentRow()

        t_karma_pos_it = self.karma_lb.currentRow()

        notes_pre_sg = self.adding_text_to_diary_tt.toPlainText().strip()
        """
        if notes_pre_sg == "":
            notes_sg = notes_pre_sg
        else:
            notes_sg = notes_pre_sg + "\n"
        """
        bwb_model.DiaryM.add(int(time.time()), t_observance_pos_it, t_karma_pos_it, notes_pre_sg)

        self.adding_text_to_diary_tt.clear()
        ####self.ten_observances_lb.selection_clear(0)  # Clearing the selection
        ####self.karma_lb.selection_clear(0)
        self.update_gui()
        self.update_gui()

    def open_karma_context_menu(self, i_event):
        print("opening menu")
        self.karma_context_menu.post(i_event.x_root, i_event.y_root)

    def delete_karma(self, i_it):
        print("deleting karma. i_it = " + str(i_it))

    def update_gui(self):

        self.karma_lb.clear()

        t_cur_sel_it = self.ten_observances_lb.currentRow()
        if t_cur_sel_it != -1:
            print("t_cur_sel_it = " + str(t_cur_sel_it))
            t_karma_lt = bwb_model.KarmaM.get_all_for_observance(t_cur_sel_it)
            for karma_item in t_karma_lt:
                row = QListWidgetItem(karma_item.description_sg)
                print("karma_item.description_sg = " + karma_item.description_sg)
                self.karma_lb.addItem(row)
        self.karma_lb.show()


        self.diary_lb.update_gui()
        ###self.diary_lb.show()



    def diary_entry_clicked(self, i_event):
        print("Diary entry clicked")
        print(i_event.widget)
        i_event.widget.config(relief="sunken")


def pixels_from_monospace_characters(i_nr_of_chars_it):
    # i_font,
    '''
    t_width_it = i_font.measure("0")
    return i_nr_of_chars_it * t_width_it
    '''
    return i_nr_of_chars_it * 8


if __name__ == "__main__":
    t_app = QApplication(sys.argv)
    t_win = WellBeingWindow()
    sys.exit(t_app.exec_())

