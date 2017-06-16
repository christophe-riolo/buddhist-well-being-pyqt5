from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import datetime
import logging
from bwb import model


class KarmaCompositeWidget(QtWidgets.QWidget):

    current_row_changed_signal = QtCore.pyqtSignal(int)
    new_karma_button_pressed_signal = QtCore.pyqtSignal(str)
    delete_signal = QtCore.pyqtSignal()
    last_clicked_list_item = None

    def __init__(self):
        super().__init__()

        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

        # ..for karma list (left column)
        karma_label = QtWidgets.QLabel("<h3>Activities</h3>")
        vbox.addWidget(karma_label)
        self.list_widget = QtWidgets.QListWidget()
        # self.list_widget.currentRowChanged.connect(self.on_karma_current_row_changed)
        self.list_widget.itemSelectionChanged.connect(
                self.on_karma_current_row_changed)
        vbox.addWidget(self.list_widget)
        # ..for adding new karma (left column)
        self.adding_new_karma_ey = QtWidgets.QLineEdit()
        vbox.addWidget(self.adding_new_karma_ey)
        self.adding_new_karma_bn = QtWidgets.QPushButton("Add new")
        vbox.addWidget(self.adding_new_karma_bn)
        self.adding_new_karma_bn.clicked.connect(
                self.on_add_new_karma_button_pressed)
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
        self.last_clicked_list_item = self.list_widget.item(
                current_karma_row_it)

        if QtWidgets.QApplication.mouseButtons() == QtCore.Qt.RightButton:
            print("Right button clicked")
        else:
            current_karma_list_item = self.list_widget.item(
                    current_karma_row_it)
            karma_entry = model.KarmaM.get(
                    current_karma_list_item.data(QtCore.Qt.UserRole))
            self.current_row_changed_signal.emit(karma_entry.id)

    def on_add_new_karma_button_pressed(self):
        # strip is needed to remove a newline at the end (why?)
        t_text_sg = self.adding_new_karma_ey.text().strip()
        if not (t_text_sg and t_text_sg.strip()):
            return
        # self.list_widget.setCurrentRow(-1)  # -experimental
        self.new_karma_button_pressed_signal.emit(t_text_sg)
        self.adding_new_karma_ey.clear()

    def update_gui(self, i_obs_sel_list):
        self.list_widget.clear()
        if i_obs_sel_list is not None:
            logging.debug("i_obs_sel_list = " + str(i_obs_sel_list))
            karma_entry_list = model.KarmaM.\
                get_for_observance_list(i_obs_sel_list)
        else:
            karma_entry_list = model.KarmaM.get_all()
        for karma_item in karma_entry_list:
            duration_sg = "x"
            latest_diary_entry = model.DiaryM.\
                get_latest_for_karma(karma_item.id)
            if latest_diary_entry is not None:
                diary_entry_date_added = datetime.datetime.\
                    fromtimestamp(latest_diary_entry.date_added_it)
                today_datetime = datetime.datetime.today()
                time_delta = today_datetime - diary_entry_date_added
                duration_sg = str(time_delta.days)
            row = QtWidgets.QListWidgetItem(
                    "{"
                    + duration_sg
                    + "}"
                    + karma_item.title_sg)
            row.setData(QtCore.Qt.UserRole, karma_item.id)
            self.list_widget.addItem(row)

    def contextMenuEvent(self, i_QContextMenuEvent):
        """
        Overridden
        Docs: http://doc.qt.io/qt-5/qwidget.html#contextMenuEvent
        """
        self.right_click_menu = QtWidgets.QMenu()
        delete_action = QtWidgets.QAction("Archive")
        # -TODO: Maybe rename this, "delete" is not right,
        # but "archive" implies that it can come back later
        delete_action.triggered.connect(self.on_context_menu_delete)
        self.right_click_menu.addAction(delete_action)
        self.right_click_menu.exec_(QtGui.QCursor.pos())

    def on_context_menu_delete(self):
        message_box_reply = QtWidgets.QMessageBox.question(
            self,
            "Remove activity?",
            "Are you sure that you want to remove this activity?"
        )
        if message_box_reply == QtWidgets.QMessageBox.Yes:
            model.KarmaM.archive(
                int(self.last_clicked_list_item.data(QtCore.Qt.UserRole)))
            self.delete_signal.emit()
        else:
            pass  # -do nothing
