
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import datetime
import logging
import bwb_model


class KarmaCompositeWidget(QtWidgets.QWidget):

    karma_current_row_changed_signal = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()

        col3_vbox_l4 = QtWidgets.QVBoxLayout()
        self.setLayout(col3_vbox_l4)


        # ..for karma list (left column)
        karma_label = QtWidgets.QLabel("<h3>Karma</h3>")
        col3_vbox_l4.addWidget(karma_label)
        self.karma_lb = QtWidgets.QListWidget()
        self.karma_lb.currentRowChanged.connect(self.on_karma_current_row_changed)
        col3_vbox_l4.addWidget(self.karma_lb)
        # ..for adding new karma (left column)
        self.adding_new_karma_ey = QtWidgets.QLineEdit()
        col3_vbox_l4.addWidget(self.adding_new_karma_ey)
        self.adding_new_karma_bn = QtWidgets.QPushButton("Add new")
        col3_vbox_l4.addWidget(self.adding_new_karma_bn)
        self.adding_new_karma_bn.clicked.connect(self.on_add_new_karma_button_pressed)
        """
        #..for notifications
        notifications_label = QLabel("<h4>Notifications</h4>")
        col3_vbox_l4.addWidget(notifications_label)
        self.notifications_lb = QListWidget()
        col3_vbox_l4.addWidget(self.notifications_lb)
        """


    # TODO: Sending signal back to bwb_window
    def on_karma_current_row_changed(self):
        # Updating the obs list selection
        t_current_karma_row_it = self.karma_lb.currentRow()
        if t_current_karma_row_it == -1:
            return
        t_current_karma_item = self.karma_lb.item(t_current_karma_row_it)
        t_karma = bwb_model.KarmaM.get(t_current_karma_item.data(QtCore.Qt.UserRole))

        self.karma_current_row_changed_signal.emit(t_karma.id)


    def on_add_new_karma_button_pressed(self):
        obs_selected_item_list = self.ten_obs_lb_w5.selectedItems()
        if obs_selected_item_list is not None and len(obs_selected_item_list) >= 1:
            obs_selected_item_id_list = [x.data(QtCore.Qt.UserRole) for x in obs_selected_item_list]
            t_text_sg = self.adding_new_karma_ey.text().strip() # strip is needed to remove a newline at the end (why?)
            if not (t_text_sg and t_text_sg.strip()):
                return
        ###t_last_pos_it = len(bwb_model.KarmaM.get_all_for_observance(observance_pos_it))
        else:
            message_box = QtWidgets.QMessageBox.information(
                self, "About Buddhist Well-Being",
                ("Please select at least one observance before adding a new karma")
            )
            return

        bwb_model.KarmaM.add(obs_selected_item_id_list, t_text_sg)
        self.adding_new_karma_ey.clear()
        self.update_gui()

    def open_karma_context_menu(self, i_event):
        print("opening menu")
        #TBD

    def delete_karma(self, i_it):
        print("deleting karma. i_it = " + str(i_it))
        #TBD


    def update_gui_karma(self, i_obs_sel_list):
        self.karma_lb.clear()

        if i_obs_sel_list is not None:
            logging.debug("i_obs_sel_list = " + str(i_obs_sel_list))
            t_karma_lt = bwb_model.KarmaM.get_for_observance_list(i_obs_sel_list)

            for karma_item in t_karma_lt:
                duration_sg = "x"
                latest_diary_entry = bwb_model.DiaryM.get_latest_for_karma(karma_item.id)
                if latest_diary_entry is not None:
                    diary_entry_date_added = datetime.datetime.fromtimestamp(latest_diary_entry.date_added_it)
                    today = datetime.datetime.today()
                    time_delta = today - diary_entry_date_added
                    duration_sg = str(time_delta.days)
                row = QtWidgets.QListWidgetItem("{" + duration_sg + "}" + karma_item.title_sg)
                row.setData(QtCore.Qt.UserRole, karma_item.id)
                self.karma_lb.addItem(row)

