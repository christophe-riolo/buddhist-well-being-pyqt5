from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from PyQt5 import QtCore

import bwb_model
import bwb_diary_widget

import time
import datetime
import enum
import warnings
import logging
import sys


class EventSource(enum.Enum):
    undefined = -1
    obs_selection_changed = 1


#################
# View and controller
#
# Suffix explanation:
# w: widget
# l: layout
# Number: The level in the layout stack
#
#################
class WellBeingWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initializing window
        self.setGeometry(40, 30, 1050, 700)
        self.setWindowTitle("Buddhist Well-Being")
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.global_widget_w1 = QWidget()
        self.setCentralWidget(self.global_widget_w1)

        # Creating layouts..
        global_hbox_l2 = QHBoxLayout()
        # ..leftmost column (column 1)
        col1_vbox_w3 = QWidget()
        col1_vbox_l4 = QVBoxLayout()
        col1_vbox_w3.setLayout(col1_vbox_l4)
        col1_vbox_w3.setFixedWidth(240)
        global_hbox_l2.addWidget(col1_vbox_w3)
        # ..column 2
        self.col2_vbox_w3 = QWidget()
        self.col2_vbox_l4 = QVBoxLayout()
        self.col2_vbox_w3.setLayout(self.col2_vbox_l4)
        global_hbox_l2.addWidget(self.col2_vbox_w3)
        # ..column 3
        col3_vbox_w3 = QWidget()
        col3_vbox_l4 = QVBoxLayout()
        col3_vbox_w3.setLayout(col3_vbox_l4)
        col3_vbox_w3.setFixedWidth(240)
        global_hbox_l2.addWidget(col3_vbox_w3)

        # ..
        self.global_widget_w1.setLayout(global_hbox_l2)

        # Creating widgets..
        # ..for ten practices (left column)
        ten_obs_label = QLabel("<h3>Ten Observances</h3>") #<b></b>
        col1_vbox_l4.addWidget(ten_obs_label)
        self.ten_obs_lb_w5 = QListWidget()
        self.ten_obs_lb_w5.setFixedHeight(360)
        #############self.ten_obs_lb_w5.setSelectionMode(QAbstractItemView.MultiSelection)
        col1_vbox_l4.addWidget(self.ten_obs_lb_w5)
        self.ten_obs_lb_w5.currentItemChanged.connect(self.on_observance_selected)
        ##self.ten_observances_lb.setSizeAdjustPolicy(QListWidget.AdjustToContents)
        # ..for details (left column)
        self.ten_obs_details_ll = QLabel("-----")
        self.ten_obs_details_ll.setWordWrap(True)
        col1_vbox_l4.addWidget(self.ten_obs_details_ll)
        # ..for custom user text (right column)
        custom_notes_label = QLabel("<h4>Notes</h4>")
        col1_vbox_l4.addWidget(custom_notes_label)
        self.custom_user_text_te = QTextEdit()
        self.custom_user_text_te.textChanged.connect(self.on_custom_user_text_text_changed)
        col1_vbox_l4.addWidget(self.custom_user_text_te)
        #.. for diary (middle column)
        diary_label = QLabel("<h3>Diary</h3>")
        self.col2_vbox_l4.addWidget(diary_label)
        self.diary_lb = bwb_diary_widget.DiaryListWidget()
        self.col2_vbox_l4.addWidget(self.diary_lb)
        # ..for adding new a diary entry (middle column)
        diary_entry_label = QLabel("<h4>New diary entry</h4>")
        self.col2_vbox_l4.addWidget(diary_entry_label)
        edit_diary_entry_hbox_l5 = QHBoxLayout()
        self.col2_vbox_l4.addLayout(edit_diary_entry_hbox_l5)
        self.adding_text_to_diary_te_w6 = QTextEdit()
        edit_diary_entry_hbox_l5.addWidget(self.adding_text_to_diary_te_w6)
        self.adding_text_to_diary_te_w6.setFixedHeight(50)
        self.adding_to_diary_date_ey_w6 = QDateTimeEdit()
        edit_diary_entry_hbox_l5.addWidget(self.adding_to_diary_date_ey_w6)
        self.adding_to_diary_date_ey_w6.setCalendarPopup(True)
        self.adding_diary_entry_bn_w5 = QPushButton("Add new")
        self.col2_vbox_l4.addWidget(self.adding_diary_entry_bn_w5)
        self.adding_diary_entry_bn_w5.clicked.connect(self.on_add_text_to_diary_button_pressed)
        #..for karma list (left column)
        karma_label = QLabel("<h3>Karma</h3>")
        col3_vbox_l4.addWidget(karma_label)
        self.karma_lb = QListWidget()
        col3_vbox_l4.addWidget(self.karma_lb)
        #..for adding new karma (left column)
        self.adding_new_karma_ey = QLineEdit()
        col3_vbox_l4.addWidget(self.adding_new_karma_ey)
        self.adding_new_karma_bn = QPushButton("Add new")
        col3_vbox_l4.addWidget(self.adding_new_karma_bn)
        self.adding_new_karma_bn.clicked.connect(self.on_add_new_karma_button_pressed)
        #..for notifications
        notifications_label = QLabel("<h4>Notifications</h4>")
        col3_vbox_l4.addWidget(notifications_label)
        self.notifications_lb = QListWidget()
        col3_vbox_l4.addWidget(self.notifications_lb)

        # Creating the menu bar..
        # ..setup of actions
        export_action = QAction("Export", self)
        export_action.triggered.connect(bwb_model.export_all)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(lambda x: sys.exit())
        redraw_action = QAction("Redraw", self)
        redraw_action.triggered.connect(self.update_gui)
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_box)
        backup_action = QAction("Backup db", self)
        backup_action.triggered.connect(bwb_model.backup_db_file)
        # ..adding menu items
        self.menu_bar = self.menuBar()
        file_menu = self.menu_bar.addMenu("&File")
        debug_menu = self.menu_bar.addMenu("Debu&g")
        # observance_menu = self.menu_bar.addMenu("&Observance")
        # karma_menu = self.menu_bar.addMenu("&Karma")
        # diary_note_menu = self.menu_bar.addMenu("&Diary note")
        help_menu = self.menu_bar.addMenu("&Help")
        file_menu.addAction(export_action)
        file_menu.addAction(exit_action)
        debug_menu.addAction(redraw_action)
        help_menu.addAction(about_action)
        debug_menu.addAction(backup_action)

        self.update_gui()
        self.show()

    # Overridden to intercept the close event for the window
    def closeEvent(self, i_QCloseEvent):
        self.hide()
        ###########trayicon.show()
        i_QCloseEvent.ignore()

    def on_custom_user_text_text_changed(self):
        bwb_model.ObservanceM.update_custom_user_text(
            self.ten_obs_lb_w5.currentRow(),
            self.custom_user_text_te.toPlainText().strip()
        )

    def on_diary_frame_configure(self, i_event):
        self.diary_canvas.configure(scrollregion=self.diary_canvas.bbox("all"))

    def on_observance_selected(self, i_curr_item, i_prev_item):
        selection_it = self.ten_obs_lb_w5.currentRow() #.selectedItems()[0]
        if 0 <= selection_it < self.ten_obs_lb_w5.count():
            t_observance = bwb_model.ObservanceM.get(selection_it)
            self.ten_obs_details_ll.setText(t_observance.sutra_text_sg)
        elif selection_it == -1:
            # We arrive here if there is no observance selected and selection_it is -1
            pass
        else:
            warnings.warn("In on_observance_selected: selection_it = " + str(selection_it))

        """
        for diary_item in bwb_model.DiaryM.get_all():
            if diary_item.observance_ref == selection_it:
                diary_item.marked_bl = True
        """

        self.update_gui(EventSource.obs_selection_changed)  # Showing habits for practice etc

    def on_add_new_karma_button_pressed(self):
        observance_pos_it = self.ten_obs_lb_w5.currentRow()
        t_text_sg = self.adding_new_karma_ey.text().strip() # strip is needed to remove a newline at the end (why?)
        if not (t_text_sg and t_text_sg.strip()):
            return
        t_last_pos_it = len(bwb_model.KarmaM.get_all_for_observance(observance_pos_it))
        bwb_model.KarmaM.add(observance_pos_it, t_last_pos_it, t_text_sg)

        self.adding_new_karma_ey.clear()
        self.update_gui()

    def on_add_text_to_diary_button_pressed(self):
        t_observance_pos_it = self.ten_obs_lb_w5.currentRow()

        ######t_selected_observances_it_lt = [x.row() for x in self.ten_obs_lb_w5.selectedIndexes()]

        t_karma_pos_it = self.karma_lb.currentRow()

        notes_pre_sg = self.adding_text_to_diary_te_w6.toPlainText().strip()
        bwb_model.DiaryM.add(int(time.time()), t_observance_pos_it, t_karma_pos_it, notes_pre_sg)

        self.adding_text_to_diary_te_w6.clear()
        ##self.ten_observances_lb.selection_clear(0)  # Clearing the selection
        ##self.karma_lb.selection_clear(0)
        self.update_gui()

    def on_diary_entry_clicked(self, i_event):
        print("Diary entry clicked")
        #TBD

    def show_about_box(self):
        message_box = QMessageBox.about(
            self, "About Buddhist Well-Being",
            ("Concept and programming by Tord Dellsén\n"
            'Photography (for icons) by Torgny Dellsén - <a href="torgnydellsen.zenfolio.com">asdf</a><br>'
            "Software License: GPLv3\n"
            "Art license: CC BY-SA 4.0")
        )

    def open_karma_context_menu(self, i_event):
        print("opening menu")
        #TBD

    def delete_karma(self, i_it):
        print("deleting karma. i_it = " + str(i_it))
        #TBD

    def update_gui(self, i_event_source = EventSource.undefined):
        if(i_event_source != EventSource.obs_selection_changed):
            self.update_gui_ten_obs()
        cur_sel_it = self.ten_obs_lb_w5.currentRow()
        self.update_gui_karma(cur_sel_it)
        self.diary_lb.update_gui(cur_sel_it)
        self.update_gui_user_text(cur_sel_it)
        self.update_gui_notifications()

    def update_gui_notifications(self):
        self.notifications_lb.clear()
        t_karma_lt = bwb_model.KarmaM.get_all()
        for karma_item in t_karma_lt:
            duration_sg = "x"
            latest_diary_entry = bwb_model.DiaryM.get_latest_for_karma(karma_item.observance_ref_it, karma_item.pos_it)
            days_since_last_done_it = -1
            if latest_diary_entry != None:
                diary_entry_date_added = datetime.datetime.fromtimestamp(latest_diary_entry.date_added_it)
                today = datetime.datetime.today()
                time_delta = today - diary_entry_date_added
                days_since_last_done_it = time_delta.days
                duration_sg = str(days_since_last_done_it)
            row = QListWidgetItem("{" + duration_sg + "}" + karma_item.description_sg)
            if days_since_last_done_it > karma_item.days_before_notification_it:
                self.notifications_lb.addItem(row)

    def update_gui_user_text(self, i_cur_sel_it):
        if i_cur_sel_it != -1:
            self.custom_user_text_te.setText(
                bwb_model.ObservanceM.get(i_cur_sel_it).user_text
            )

    def update_gui_karma(self, i_cur_sel_it):
        self.karma_lb.clear()
        if i_cur_sel_it != -1:
            logging.debug("i_cur_sel_it = " + str(i_cur_sel_it))
            t_karma_lt = bwb_model.KarmaM.get_all_for_observance(i_cur_sel_it)

            for karma_item in t_karma_lt:
                duration_sg = "x"
                latest_diary_entry = bwb_model.DiaryM.get_latest_for_karma(i_cur_sel_it, karma_item.pos_it)
                if latest_diary_entry != None:
                    diary_entry_date_added = datetime.datetime.fromtimestamp(latest_diary_entry.date_added_it)
                    today = datetime.datetime.today()
                    time_delta = today - diary_entry_date_added
                    duration_sg = str(time_delta.days)
                row = QListWidgetItem("{" + duration_sg + "}" + karma_item.description_sg)
                self.karma_lb.addItem(row)

    def update_gui_ten_obs(self):
        self.ten_obs_lb_w5.clear()
        counter = 0
        for observance_item in bwb_model.ObservanceM.get_all():
            # Important: "Alternatively, if you want the widget to have a fixed size based on its contents,
            # you can call QLayout::setSizeConstraint(QLayout::SetFixedSize);"
            # https://doc.qt.io/qt-5/qwidget.html#setSizePolicy-1

            row_i6 = QListWidgetItem()
            row_layout_l7 = QVBoxLayout()

            # Updating frequency
            total_number_week_list = []
            for day_it in range(0, 7):
                total_number_it = len(
                    bwb_model.DiaryM.get_all_for_obs_and_day(
                        counter,
                        int(time.mktime(
                            (datetime.date.today() - datetime.timedelta(days=day_it)).timetuple())))
                )
                total_number_week_list.append(total_number_it)

            observance_short_formatted_sg = "<b>" + observance_item.short_name_sg + "</b>"
            row_label_w8 = QLabel(
                observance_short_formatted_sg
                + "<br>[" + ' '.join(str(x) for x in reversed(total_number_week_list)) + "]"
            )

            row_label_w8.adjustSize()
            row_layout_l7.addWidget(row_label_w8)
            row_layout_l7.setContentsMargins(0, 3, 0, 3)
            row_layout_l7.setSpacing(2)

            row_w6 = QWidget()
            row_w6.setLayout(row_layout_l7)
            row_w6.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
            row_w6.adjustSize()

            my_size = QtCore.QSize(-1, row_w6.height())

            row_i6.setSizeHint(row_w6.sizeHint())
            # - Please note: If we set the size hint to (-1, height) we will get overflow towards the bottom
            self.ten_obs_lb_w5.addItem(row_i6)
            self.ten_obs_lb_w5.setItemWidget(row_i6, row_w6)

            counter += 1

