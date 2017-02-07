from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from PyQt5 import QtCore

import bwb_model
import bwb_diary_widget
import bwb_karma
import bwb_observances

import time
import datetime
import enum
import warnings
import logging
import sys


class EventSource(enum.Enum):
    undefined = -1
    obs_selection_changed = 1
    karma_current_row_changed = 2


#################
# View and controller
#
# Suffix explanation:
# _w: widget
# _l: layout
# _# (number): The level in the layout stack
#
#################
class WellBeingWindow(QMainWindow):
    # noinspection PyArgumentList,PyUnresolvedReferences
    def __init__(self):
        super().__init__()

        # Initializing window
        self.setGeometry(40, 30, 1050, 700)
        self.setWindowTitle("Buddhist Well-Being")
        self.setWindowIcon(QtGui.QIcon("icon.png"))

        # Creating layouts..
        obs_dock_w2 = QDockWidget("Blessings", self)
        karma_dock_w2 = QDockWidget("Activities", self)
        # ..observances


        self.obs_composite_widget_w3 = bwb_observances.ObsCompositeWidget()
        self.obs_composite_widget_w3.item_selection_changed_signal.connect(self.on_item_selection_changed)


        # ..diary
        self.col2_vbox_w3 = QWidget()
        self.diary_vbox_l4 = QVBoxLayout()
        self.col2_vbox_w3.setLayout(self.diary_vbox_l4)
        self.setCentralWidget(self.col2_vbox_w3)
        # ..karma
        self.karma_composite_widget_w3 = bwb_karma.KarmaCompositeWidget()
        self.karma_composite_widget_w3.current_row_changed_signal.connect(self.on_karma_current_row_changed)
        self.karma_composite_widget_w3.new_karma_button_pressed_signal.connect(self.on_add_new_karma_button_pressed)

        # Creating widgets..
        #.. for diary (middle column)
        diary_label = QLabel("<h3>Diary</h3>")
        self.diary_vbox_l4.addWidget(diary_label)
        self.diary_widget = bwb_diary_widget.DiaryListWidget()  # - diary_lb contains a list widget
        ##bwb_diary_widget.DiaryListWidget.list_widget.currentRowChanged.connect(self.on_diary_row_changed)

        self.diary_vbox_l4.addWidget(self.diary_widget)
        # ..for adding new a diary entry (middle column)
        diary_entry_label = QLabel("<h4>New diary entry</h4>")
        self.diary_vbox_l4.addWidget(diary_entry_label)
        edit_diary_entry_hbox_l5 = QHBoxLayout()
        self.diary_vbox_l4.addLayout(edit_diary_entry_hbox_l5)
        self.adding_text_to_diary_te_w6 = QTextEdit()
        edit_diary_entry_hbox_l5.addWidget(self.adding_text_to_diary_te_w6)
        self.adding_text_to_diary_te_w6.setFixedHeight(50)


        self.adding_to_diary_date_ey_w6 = QDateTimeEdit()
        self.adding_to_diary_date_ey_w6.setDisplayFormat("dddd")
        self.adding_to_diary_date_ey_w6.setCalendarPopup(True)
        self.update_gui_date()

        edit_diary_entry_hbox_l5.addWidget(self.adding_to_diary_date_ey_w6)

        self.adding_to_diary_now = QPushButton("Now/Today")
        self.adding_to_diary_now.pressed.connect(self.on_today_button_pressed)
        edit_diary_entry_hbox_l5.addWidget(self.adding_to_diary_now)

        self.adding_diary_entry_bn_w5 = QPushButton("Add new")
        self.diary_vbox_l4.addWidget(self.adding_diary_entry_bn_w5)
        self.adding_diary_entry_bn_w5.clicked.connect(self.on_add_text_to_diary_button_pressed)




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




        obs_dock_w2.setWidget(self.obs_composite_widget_w3)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, obs_dock_w2)
        obs_dock_w2.setFeatures(QDockWidget.NoDockWidgetFeatures)

        karma_dock_w2.setWidget(self.karma_composite_widget_w3)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, karma_dock_w2)
        karma_dock_w2.setFeatures(QDockWidget.DockWidgetMovable)




        self.update_gui()
        self.show()


    def get_obs_selected_list(self, i_curr_item=None):
        t_obs_selected_item_list = self.obs_composite_widget_w3.ten_obs_lb.selectedItems()
        ret_obs_selected_id_list = []
        if i_curr_item is not None and i_curr_item.isSelected():
            t_obs_selected_item_list.append(i_curr_item)
        if t_obs_selected_item_list is not None:
            ret_obs_selected_id_list = [x.data(QtCore.Qt.UserRole) for x in t_obs_selected_item_list]
        return ret_obs_selected_id_list


    def on_add_text_to_diary_button_pressed(self):
        obs_selected_item_list = self.obs_composite_widget_w3.ten_obs_lb.selectedItems()
        if obs_selected_item_list is not None and len(obs_selected_item_list) > 0:
            t_karma_current_item = self.karma_composite_widget_w3.karma_lb.currentItem()
            t_karma_id = -1
            if t_karma_current_item is not None:
                t_karma_id = self.karma_composite_widget_w3.karma_lb.currentItem().data(QtCore.Qt.UserRole)
            notes_pre_sg = self.adding_text_to_diary_te_w6.toPlainText().strip()
            obs_selected_item_id_list = [x.data(QtCore.Qt.UserRole) for x in obs_selected_item_list]

            #### time_qdatetime = self.adding_to_diary_date_ey_w6.dateTime()
            time_qdatetime = self.adding_to_diary_date_ey_w6.dateTime()


            t_unix_time_it = time_qdatetime.toMSecsSinceEpoch() // 1000
            print("t_unix_time_it = " + str(t_unix_time_it))
            bwb_model.DiaryM.add(t_unix_time_it, notes_pre_sg, t_karma_id, obs_selected_item_id_list)



            self.adding_text_to_diary_te_w6.clear()

            self.update_gui()

        else:
            message_box = QMessageBox.information(
                self, "About Buddhist Well-Being",
                ("Please select at least one observance before adding a new diary entry")
            )



    def on_today_button_pressed(self):
        self.update_gui_date(time.time())

    def on_karma_current_row_changed(self, i_karma_id_it):
        self.obs_composite_widget_w3.ten_obs_lb.clearSelection()
        t_observance_list = bwb_model.ObservanceM.get_all_for_karma_id(i_karma_id_it)
        t_count_it = self.obs_composite_widget_w3.ten_obs_lb.count()
        for i in range(0, t_count_it):
            t_obs_item = self.obs_composite_widget_w3.ten_obs_lb.item(i)
            for obs in t_observance_list:
                if t_obs_item.data(QtCore.Qt.UserRole) == obs.id:
                    t_obs_item.setSelected(True)
        self.update_gui(EventSource.karma_current_row_changed)

    def on_add_new_karma_button_pressed(self, i_karma_text_sg):
        obs_selected_item_list = self.obs_composite_widget_w3.ten_obs_lb.selectedItems()
        if obs_selected_item_list is not None and len(obs_selected_item_list) >= 1:
            obs_selected_item_id_list = [x.data(QtCore.Qt.UserRole) for x in obs_selected_item_list]
        else:
            message_box = QMessageBox.information(
                self, "About Buddhist Well-Being",
                ("Please select at least one observance before adding a new karma")
            )
            return

        bwb_model.KarmaM.add(obs_selected_item_id_list, i_karma_text_sg)
        self.update_gui()

    def on_item_selection_changed(self, i_current_row_it):
        self.update_gui(EventSource.obs_selection_changed)  # Showing habits for practice etc


    def show_about_box(self):
        message_box = QMessageBox.about(
            self, "About Buddhist Well-Being",
            ("Concept and programming by Tord Dellsén\n"
            'Photography (for icons) by Torgny Dellsén - <a href="torgnydellsen.zenfolio.com">asdf</a><br>'
            "Software License: GPLv3\n"
            "Art license: CC BY-SA 4.0")
        )


    def update_gui(self, i_event_source = EventSource.undefined):
        if i_event_source != EventSource.obs_selection_changed and i_event_source != EventSource.karma_current_row_changed:
            self.obs_composite_widget_w3.update_gui()
        t_current_obs_item = self.obs_composite_widget_w3.ten_obs_lb.currentItem()  # , i_curr_item = None
        t_obs_selected_list = self.get_obs_selected_list()
        if i_event_source != EventSource.karma_current_row_changed:
            self.karma_composite_widget_w3.update_gui_karma(t_obs_selected_list)
            ## Old: self.update_gui_karma(t_obs_selected_list)
        self.diary_widget.update_gui(t_obs_selected_list)
        ###self.update_gui_user_text(t_current_obs_item)
        ###self.update_gui_notifications()


    def update_gui_date(self, i_unix_time_it = time.time()):
        t_date_time = QtCore.QDateTime()
        t_date_time.setMSecsSinceEpoch(i_unix_time_it * 1000)
        self.adding_to_diary_date_ey_w6.setDateTime(t_date_time)
