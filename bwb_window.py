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

        # Setup of widgets..
        # ..observances
        obs_dock_w2 = QDockWidget("Blessings", self)
        self.obs_composite_w3 = bwb_observances.ObsCompositeWidget()
        self.obs_composite_w3.item_selection_changed_signal.connect(self.on_obs_item_selection_changed)
        obs_dock_w2.setWidget(self.obs_composite_w3)
        obs_dock_w2.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, obs_dock_w2)
        # ..diary
        self.diary_composite_w2 = bwb_diary_widget.DiaryListWidget()
        self.diary_composite_w2.add_text_to_diary_button_pressed_signal.connect(
            self.on_diary_add_entry_button_pressed)
        self.setCentralWidget(self.diary_composite_w2)
        # ..karma
        karma_dock_w2 = QDockWidget("Activities", self)
        self.karma_composite_widget_w3 = bwb_karma.KarmaCompositeWidget()
        self.karma_composite_widget_w3.current_row_changed_signal.connect(self.on_karma_current_row_changed)
        self.karma_composite_widget_w3.new_karma_button_pressed_signal.connect(self.on_karma_add_new_button_pressed)
        self.karma_composite_widget_w3.delete_signal.connect(self.on_karma_deleted)
        karma_dock_w2.setWidget(self.karma_composite_widget_w3)
        karma_dock_w2.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        karma_dock_w2.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, karma_dock_w2)

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
        help_menu = self.menu_bar.addMenu("&Help")
        file_menu.addAction(export_action)
        file_menu.addAction(exit_action)
        debug_menu.addAction(redraw_action)
        help_menu.addAction(about_action)
        debug_menu.addAction(backup_action)

        self.update_gui()
        self.show()

    def on_karma_current_row_changed(self, i_karma_id_it):
        self.obs_composite_w3.ten_obs_lb.clearSelection()
        observance_list = bwb_model.ObservanceM.get_all_for_karma_id(i_karma_id_it)
        list_length_it = self.obs_composite_w3.ten_obs_lb.count()
        for i in range(0, list_length_it):
            obs_list_item = self.obs_composite_w3.ten_obs_lb.item(i)
            for obs in observance_list:
                if obs_list_item.data(QtCore.Qt.UserRole) == obs.id:
                    obs_list_item.setSelected(True)
                    # -TODO: Maybe we can change the background color instead? (Right now this does nothing because of
                    # selection has been disabled for the observances list)
        self.update_gui(EventSource.karma_current_row_changed)

    def on_karma_add_new_button_pressed(self, i_karma_text_sg):
        obs_selected_item_list = self.obs_composite_w3.ten_obs_lb.selectedItems()
        if obs_selected_item_list is not None and len(obs_selected_item_list) >= 1:
            obs_selected_item_id_list = [x.data(QtCore.Qt.UserRole) for x in obs_selected_item_list]
            bwb_model.KarmaM.add(obs_selected_item_id_list, i_karma_text_sg)
            self.update_gui()
        else:
            message_box = QMessageBox.information(
                self, "About Buddhist Well-Being",
                ("Please select at least one observance before adding a new karma")
            )

    def on_obs_item_selection_changed(self, i_current_row_it):
        self.update_gui(EventSource.obs_selection_changed)  # Showing habits for practice etc

    def on_diary_add_entry_button_pressed(self, i_text_sg, i_unix_time_it):
        obs_selected_item_list = self.obs_composite_w3.ten_obs_lb.selectedItems()
        if obs_selected_item_list is not None and len(obs_selected_item_list) > 0:
            t_karma_current_item = self.karma_composite_widget_w3.list_widget.currentItem()
            t_karma_id = -1
            if t_karma_current_item is not None:
                t_karma_id = self.karma_composite_widget_w3.list_widget.currentItem().data(QtCore.Qt.UserRole)
            obs_selected_item_id_list = [x.data(QtCore.Qt.UserRole) for x in obs_selected_item_list]
            print("t_unix_time_it = " + str(i_unix_time_it))
            bwb_model.DiaryM.add(i_unix_time_it, i_text_sg, t_karma_id, obs_selected_item_id_list)
            self.update_gui()
        else:
            message_box = QMessageBox.information(
                self, "About Buddhist Well-Being",
                ("Please select at least one observance before adding a new diary entry")
            )

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
            self.obs_composite_w3.update_gui()
        t_obs_selected_list = self.obs_composite_w3.get_selected_id_list()
        if i_event_source != EventSource.karma_current_row_changed:
            self.karma_composite_widget_w3.update_gui(t_obs_selected_list)
        self.diary_composite_w2.update_gui()
        ###self.update_gui_user_text(t_current_obs_item)
        ###self.update_gui_notifications()

    def on_karma_deleted(self):
        self.update_gui()  # - EventSource.karma_current_row_changed
