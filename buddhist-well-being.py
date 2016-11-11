import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
import bwb_model
import bwb_diary_list_widget
import time


class WellBeingWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        observances_lt = bwb_model.ObservanceM.get_all()

        self.setGeometry(30, 30, 700, 500)
        self.setWindowTitle("Buddhist Well-Being")
        self.setWindowIcon(QIcon("icon.png"))

        # Creating layouts

        hbox = QHBoxLayout()
        left_vbox = QVBoxLayout()
        left_vbox_widget = QWidget()
        left_vbox_widget.setLayout(left_vbox)
        left_vbox_widget.setFixedWidth(240)

        hbox.addWidget(left_vbox_widget)
        self.right_vbox = QVBoxLayout()
        self.right_vbox_widget = QWidget()
        self.right_vbox_widget.setLayout(self.right_vbox)
        #self.right_vbox_widget.setFixedWidth(510)
        hbox.addWidget(self.right_vbox_widget)
        self.central_widget.setLayout(hbox)
        self.show()

        # Creating widgets..

        # ..for ten practices (left column)
        self.ten_observances_lb = QListWidget()
        left_vbox.addWidget(self.ten_observances_lb)
        self.ten_observances_lb.currentItemChanged.connect(self.observance_selected_fn)
        for observance_item in observances_lt:

            ###########
            # Important: "Alternatively, if you want the widget to have a fixed size based on its contents,
            # you can call QLayout::setSizeConstraint(QLayout::SetFixedSize);"
            #
            # https://doc.qt.io/qt-5/qwidget.html#setSizePolicy-1
            ###########

            #row = QListWidgetItem(observance_item.short_name_sg)
            row = QListWidgetItem()
            layout = QVBoxLayout()
            label1 = QLabel(observance_item.short_name_sg)
            label1.adjustSize()
            label1.setFixedWidth(150)
            text_sg = "[0 0 1 0 2 0 1] asdf1 asdf2 asdf3 asdf4 asdf5 asdf6 asdf7 asdf8 asdf1 asdf2 asdf3 asdf4 asdf5 asdf6 asdf7 asdf8 asdf1 asdf2 asdf3 asdf4 asdf5 asdf6 asdf7 asdf8"
            label2 = QLabel()
            label2.setWordWrap(True)
            label2.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
            label2.setText(text_sg)
            label2.adjustSize()
            label2.setFixedWidth(150)
            layout.setSizeConstraint(QLayout.SetMinimumSize) # <=================
            layout.addWidget(label1)
            layout.addWidget(label2)
            layout.setContentsMargins(0,0,0,0)
            layout.setSpacing(0)
            #layout.update()



            print("layout.sizeHint().height() = " + str(layout.sizeHint().height()))
            #layout.setSizeConstraint(QLayout.SetMinAndMaxSize) #<-------- # QLayout.SetFixedSize
            layout_widget = QWidget()
            layout_widget.setLayout(layout)
            layout_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
            #layout_widget.setMinimumHeight(label2.height() + label1.height())
            layout_widget.adjustSize()
            #layout_widget.updateGeometry()

            print("layout_widget.height() = " + str(layout_widget.height()))
            print("layout_widget.sizeHint().height() = " + str(layout_widget.sizeHint().height()))
            my_size = QSize(-1, layout_widget.height())

            row.setSizeHint(layout_widget.sizeHint())
            # - Please note: If we set the size hint to (-1, height) we will get overflow towards the bottom
            self.ten_observances_lb.addItem(row)
            self.ten_observances_lb.setItemWidget(row, layout_widget)

        #self.ten_observances_lb.setSizeAdjustPolicy(QListWidget.AdjustToContents)

        ## ..for details (left column)
        self.ten_practices_details_ll = QLabel("-----")
        self.ten_practices_details_ll.setWordWrap(True)
        left_vbox.addWidget(self.ten_practices_details_ll)

        #..for karma list (left column)
        self.karma_lb = QListWidget()
        left_vbox.addWidget(self.karma_lb)

        #..for adding new karma (left column)
        self.adding_new_karma_ey = QLineEdit()
        left_vbox.addWidget(self.adding_new_karma_ey)
        self.adding_new_karma_bn = QPushButton("Add new")
        left_vbox.addWidget(self.adding_new_karma_bn)
        self.adding_new_karma_bn.clicked.connect(self.add_new_karma_button_pressed_fn)

        #.. for diary (right column)
        ###self.diary_lb = QListWidget()
        self.diary_lb = bwb_diary_list_widget.DiaryListWidget()
        self.right_vbox.addWidget(self.diary_lb)

        # ..for adding new a diary entry (right column)
        edit_diary_entry_hbox = QHBoxLayout()
        self.right_vbox.addLayout(edit_diary_entry_hbox)
        self.adding_to_diary_date_ey = QDateTimeEdit()
        edit_diary_entry_hbox.addWidget(self.adding_to_diary_date_ey)
        self.adding_to_diary_date_ey.setCalendarPopup(True)
        ###self.adding_to_diary_date_ey.insert(tkinter.END, "2015-01-09 13:42")
        self.adding_text_to_diary_tt = QTextEdit()
        edit_diary_entry_hbox.addWidget(self.adding_text_to_diary_tt)
        self.adding_text_to_diary_tt.setFixedHeight(50)
        self.adding_new_button = QPushButton("Add new")
        self.right_vbox.addWidget(self.adding_new_button)
        self.adding_new_button.clicked.connect(self.add_text_to_diary_button_pressed_fn)


        # Creating the menu bar
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        export_action = QAction("Export", self)
        export_action.triggered.connect(bwb_model.export_all)
        redraw_action = QAction("Redraw", self)
        redraw_action.triggered.connect(self.update_gui)
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_box)
        backup_action = QAction("Backup db", self)
        backup_action.triggered.connect(bwb_model.backup_db_file)

        self.menu_bar = self.menuBar()

        file_menu = self.menu_bar.addMenu("&File")
        debug_menu = self.menu_bar.addMenu("Debu&g")
        observance_menu = self.menu_bar.addMenu("&Observance")
        karma_menu = self.menu_bar.addMenu("&Karma")
        diary_note_menu = self.menu_bar.addMenu("&Diary note")
        help_menu = self.menu_bar.addMenu("&Help")
        file_menu.addAction(exit_action)
        file_menu.addAction(export_action)
        debug_menu.addAction(redraw_action)
        help_menu.addAction(about_action)
        debug_menu.addAction(backup_action)

    def show_about_box(self):
        message_box = QMessageBox.about(self, "About Buddhist Well-Being",
            """Concept and programming by Tord Dellsén
Photography (for icons) by Torgny Dellsén - torgnydellsen.zenfolio.com
Software License: GPLv3
Art license: CC BY-SA 4.0""")

    def on_diary_frame_configure(self, i_event):
        self.diary_canvas.configure(scrollregion=self.diary_canvas.bbox("all"))

    def observance_selected_fn(self, i_curr_item, i_prev_item):
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
        bwb_model.DiaryM.add(int(time.time()), t_observance_pos_it, t_karma_pos_it, notes_pre_sg)

        self.adding_text_to_diary_tt.clear()
        ##self.ten_observances_lb.selection_clear(0)  # Clearing the selection
        ##self.karma_lb.selection_clear(0)
        self.update_gui()


    def open_karma_context_menu(self, i_event):
        print("opening menu")
        #TBD

    def delete_karma(self, i_it):
        print("deleting karma. i_it = " + str(i_it))
        #TBD

    def update_gui(self):
        self.karma_lb.clear()

        t_cur_sel_it = self.ten_observances_lb.currentRow()
        if t_cur_sel_it != -1:
            #print("t_cur_sel_it = " + str(t_cur_sel_it))
            t_karma_lt = bwb_model.KarmaM.get_all_for_observance(t_cur_sel_it)
            for karma_item in t_karma_lt:
                row = QListWidgetItem(karma_item.description_sg)
                self.karma_lb.addItem(row)
        self.karma_lb.show()

        self.diary_lb.update_gui(t_cur_sel_it)

    def diary_entry_clicked(self, i_event):
        print("Diary entry clicked")
        #TBD


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = WellBeingWindow()
    sys.exit(app.exec_())
