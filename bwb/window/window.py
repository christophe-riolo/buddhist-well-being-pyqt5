import enum
import sys
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from bwb import model
from bwb.window import diary, karma, observances


class EventSource(enum.Enum):
    undefined = -1
    obs_selection_changed = 1
    obs_current_row_changed = 2
    # karma_current_row_changed = 3


class WellBeingWindow(QtWidgets.QMainWindow):
    """
    View and controller
    Suffix explanation:
    _w: widget
    _l: layout
    _# (number): The level in the layout stack
    """
    # noinspection PyArgumentList,PyUnresolvedReferences
    def __init__(self):
        super().__init__()

        # Initializing window
        self.setGeometry(40, 30, 800, 700)
        self.setWindowTitle("Buddhist Well-Being")
        self.setWindowIcon(QtGui.QIcon("icon.png"))

        # Setup of widgets..
        # ..observances
        obs_dock_w2 = QtWidgets.QDockWidget("Blessings", self)
        self.obs_composite_w3 = observances.ObsCompositeWidget()
        self.obs_composite_w3.item_selection_changed_signal.connect(
            self.on_obs_item_selection_changed)
        self.obs_composite_w3.current_row_changed_signal.connect(
            self.on_obs_current_row_changed)
        obs_dock_w2.setWidget(self.obs_composite_w3)
        obs_dock_w2.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
        obs_dock_w2.setFixedHeight(440)  # -TODO: Find a better way to do this
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, obs_dock_w2)

        # ..diary
        self.diary_composite_w2 = diary.DiaryListWidget()
        self.diary_composite_w2.add_text_to_diary_button_pressed_signal.\
            connect(self.on_diary_add_entry_button_pressed)
        self.diary_composite_w2.context_menu_change_date_signal.\
            connect(self.on_diary_context_menu_change_date)
        self.diary_composite_w2.context_menu_delete_signal.connect(
            self.on_diary_context_menu_delete)
        self.setCentralWidget(self.diary_composite_w2)

        # ..karma
        karma_dock_w2 = QtWidgets.QDockWidget("Activities", self)
        self.karma_composite_widget_w3 = karma.KarmaCompositeWidget()
        self.karma_composite_widget_w3.current_row_changed_signal.connect(
            self.on_karma_current_row_changed)
        self.karma_composite_widget_w3.new_karma_button_pressed_signal.connect(
            self.on_karma_add_new_button_pressed)
        self.karma_composite_widget_w3.delete_signal.connect(
            self.on_karma_deleted)
        karma_dock_w2.setWidget(self.karma_composite_widget_w3)
        karma_dock_w2.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable)
        karma_dock_w2.setAllowedAreas(
            QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, karma_dock_w2)

        # Creating the menu bar..
        # ..setup of actions
        export_action = QtWidgets.QAction("Export", self)
        export_action.triggered.connect(model.export_all)
        exit_action = QtWidgets.QAction("Exit", self)
        exit_action.triggered.connect(lambda x: sys.exit())
        redraw_action = QtWidgets.QAction("Redraw", self)
        redraw_action.triggered.connect(self.update_gui)
        about_action = QtWidgets.QAction("About", self)
        about_action.triggered.connect(self.show_about_box)
        backup_action = QtWidgets.QAction("Backup db", self)
        backup_action.triggered.connect(model.backup_db_file)

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
        self.obs_composite_w3.list_widget.clearSelection()
        observance_list = model.ObservanceM.get_all_for_karma_id(
                            i_karma_id_it)
        list_length_it = self.obs_composite_w3.list_widget.count()
        for i in range(0, list_length_it):
            obs_list_item = self.obs_composite_w3.list_widget.item(i)
            for obs in observance_list:
                if obs_list_item.data(QtCore.Qt.UserRole) == obs.id:
                    obs_list_item.setSelected(True)

    def on_karma_add_new_button_pressed(self, i_karma_text_sg):
        obs_selected_item_list = self.obs_composite_w3.list_widget.\
                                 selectedItems()
        if obs_selected_item_list is not None \
           and len(obs_selected_item_list) >= 1:
            obs_selected_item_id_list = [
                x.data(QtCore.Qt.UserRole)
                for x in obs_selected_item_list]
            model.KarmaM.add(obs_selected_item_id_list, i_karma_text_sg)
            self.update_gui()
        else:
            # message_box = QtWidgets.QMessageBox.information(
            QtWidgets.QMessageBox.information(
                self, "New Activity Message",
                ("Please select at least one observance " +
                    "before adding a new activity")
            )

    def on_obs_current_row_changed(self, i_current_row_it):
        pass
        # self.update_gui(EventSource.obs_current_row_changed)

    def on_obs_item_selection_changed(self):
        # Showing habits for practice etc
        self.update_gui(EventSource.obs_selection_changed)

    def on_diary_add_entry_button_pressed(self, i_text_sg, i_unix_time_it):
        obs_selected_item_list = self.obs_composite_w3.\
                                 list_widget.selectedItems()
        if obs_selected_item_list is not None\
           and len(obs_selected_item_list) > 0:
            t_karma_current_item = self.karma_composite_widget_w3.list_widget.\
                currentItem()
            t_karma_id = -1
            if t_karma_current_item is not None:
                t_karma_id = self.karma_composite_widget_w3.list_widget.\
                    currentItem().data(QtCore.Qt.UserRole)
            obs_selected_item_id_list = [
                x.data(QtCore.Qt.UserRole)
                for x in obs_selected_item_list]
            print("t_unix_time_it = " + str(i_unix_time_it))
            model.DiaryM.add(
                i_unix_time_it,
                i_text_sg,
                t_karma_id,
                obs_selected_item_id_list)
            self.update_gui()
            self.diary_composite_w2.adding_text_to_diary_textedit_w6.clear()
        else:
            # message_box = QtWidgets.QMessageBox.information(
            QtWidgets.QMessageBox.information(
                self, "New Diary Entry Message",
                ("Please select at least one observance " +
                    "before adding a new diary entry")
            )

    def show_about_box(self):
        # message_box = QtWidgets.QMessageBox.about(
        QtWidgets.QMessageBox.about(
            self,
            "About Buddhist Well-Being",
            "<html>Concept and programming by Tord Dellsén<br/>"
            'Photography (for icons) by '
            '<a href="torgnydellsen.zenfolio.com">Torgny Dellsén</a><br/>'
            "Software License: GPLv3<br/>"
            "Art license: CC BY-SA 4.0</html>"
        )

    def update_gui(self, i_event_source=EventSource.undefined):
        obs_current_row_item = self.obs_composite_w3.list_widget.currentItem()
        obs_nr_of_selected_rows_it = len(
            self.obs_composite_w3.list_widget.selectedItems())
        if i_event_source == EventSource.obs_selection_changed or\
           i_event_source == EventSource.undefined:
            if obs_current_row_item is not None:
                obs_current_entry_id = obs_current_row_item.data(
                    QtCore.Qt.UserRole)
                self.karma_composite_widget_w3.update_gui(
                    [obs_current_entry_id])
                # -the current row is sent instead of the list of selected
                # rows, but the function is kept as it is in case we want
                # to change things in the future
        if obs_nr_of_selected_rows_it == 0:
            # -the current row changed signal is activated before the selection
            # is updated, therefore  we have to exclude this event source here
            self.karma_composite_widget_w3.update_gui(None)
        if i_event_source == EventSource.undefined:
            self.obs_composite_w3.update_gui()
        self.diary_composite_w2.update_gui()
        # self.update_gui_user_text(t_current_obs_item)
        # self.update_gui_notifications()

    def on_diary_context_menu_change_date(self):
        self.update_gui()

    def on_diary_context_menu_delete(self):
        self.update_gui()

    def on_karma_deleted(self):
        self.update_gui()
