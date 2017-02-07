
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import datetime
import logging
import bwb_model


class KarmaCompositeWidget(QtWidgets.QWidget):

    current_row_changed_signal = QtCore.pyqtSignal(int)
    new_karma_button_pressed_signal = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()

        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

        # ..for karma list (left column)
        karma_label = QtWidgets.QLabel("<h3>Activities</h3>")
        vbox.addWidget(karma_label)
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.currentRowChanged.connect(self.on_karma_current_row_changed)
        vbox.addWidget(self.list_widget)
        # ..for adding new karma (left column)
        self.adding_new_karma_ey = QtWidgets.QLineEdit()
        vbox.addWidget(self.adding_new_karma_ey)
        self.adding_new_karma_bn = QtWidgets.QPushButton("Add new")
        vbox.addWidget(self.adding_new_karma_bn)
        self.adding_new_karma_bn.clicked.connect(self.on_add_new_karma_button_pressed)
        """
        #..for notifications
        notifications_label = QLabel("<h4>Notifications</h4>")
        vbox.addWidget(notifications_label)
        self.notifications_lb = QListWidget()
        vbox.addWidget(self.notifications_lb)
        """

    def on_karma_current_row_changed(self):
        current_karma_row_it = self.list_widget.currentRow()
        if current_karma_row_it == -1:
            return
        current_karma_list_item = self.list_widget.item(current_karma_row_it)
        karma_entry = bwb_model.KarmaM.get(current_karma_list_item.data(QtCore.Qt.UserRole))
        self.current_row_changed_signal.emit(karma_entry.id)

    def on_add_new_karma_button_pressed(self):
        t_text_sg = self.adding_new_karma_ey.text().strip()  # strip is needed to remove a newline at the end (why?)
        if not (t_text_sg and t_text_sg.strip()):
            return
        self.new_karma_button_pressed_signal.emit(t_text_sg)
        self.adding_new_karma_ey.clear()

    def open_karma_context_menu(self, i_event):
        print("opening menu")
        #TBD

    def delete_karma(self, i_it):
        print("deleting karma. i_it = " + str(i_it))
        #TBD

    def update_gui_karma(self, i_obs_sel_list):
        self.list_widget.clear()
        if i_obs_sel_list is not None:
            logging.debug("i_obs_sel_list = " + str(i_obs_sel_list))
            karma_entry_list = bwb_model.KarmaM.get_for_observance_list(i_obs_sel_list)
            for karma_item in karma_entry_list:
                duration_sg = "x"
                latest_diary_entry = bwb_model.DiaryM.get_latest_for_karma(karma_item.id)
                if latest_diary_entry is not None:
                    diary_entry_date_added = datetime.datetime.fromtimestamp(latest_diary_entry.date_added_it)
                    today_datetime = datetime.datetime.today()
                    time_delta = today_datetime - diary_entry_date_added
                    duration_sg = str(time_delta.days)
                row = QtWidgets.QListWidgetItem("{" + duration_sg + "}" + karma_item.title_sg)
                row.setData(QtCore.Qt.UserRole, karma_item.id)
                self.list_widget.addItem(row)

