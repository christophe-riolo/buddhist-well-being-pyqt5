
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import datetime
import logging
import time
import bwb_model


class ObsCompositeWidget(QtWidgets.QWidget):
    item_selection_changed_signal = QtCore.pyqtSignal()
    current_row_changed_signal = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()

        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

        # ..for ten practices (left column)
        ten_obs_label = QtWidgets.QLabel("<h3>Ten Blessings</h3>") #<b></b>
        vbox.addWidget(ten_obs_label)
        self.list_widget = QtWidgets.QListWidget()
        ############obs_dock_w2.setWidget(self.ten_obs_lb)
        self.list_widget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        vbox.addWidget(self.list_widget)
        self.list_widget.itemSelectionChanged.connect(self.on_item_selection_changed)
        # -currentItemChanged cannot be used since it is activated before the list of selected items is updated
        ##self.ten_observances_lb.setSizeAdjustPolicy(QListWidget.AdjustToContents)
        self.list_widget.currentRowChanged.connect(self.on_current_row_changed)
        # ..for details (left column)
        self.ten_obs_details_ll = QtWidgets.QLabel("-----")
        self.ten_obs_details_ll.setWordWrap(True)
        vbox.addWidget(self.ten_obs_details_ll)

    def on_current_row_changed(self):
        print("self.ten_obs_lb.currentRow() = " + str(self.list_widget.currentRow()))

        current_row_it = self.list_widget.currentRow()
        if current_row_it == -1:
            # We might get here when a karma item has been clicked
            return

        t_current_list_item = self.list_widget.item(current_row_it)
        t_observance = bwb_model.ObservanceM.get(t_current_list_item.data(QtCore.Qt.UserRole))
        self.ten_obs_details_ll.setText(t_observance.description)

        self.current_row_changed_signal.emit(current_row_it)

    def on_item_selection_changed(self):
        print("len(self.ten_obs_lb.selectedItems()) = " + str(len(self.list_widget.selectedItems())))

        self.item_selection_changed_signal.emit()

    def update_gui(self):
        """
        Signs to use for showing observance:
        ☐ ☑ (Ballot ____, )
        ✓
        ◯ ⬤ (Large Circle, Black Large Circle)
        ○ ● (White Circle, Black Circle (Please note that medium white/black cirlce is smaller than these))
        More here:
        https://unicode-table.com/en/blocks/geometric-shapes/
        https://unicode-table.com/en/blocks/miscellaneous-symbols/
        """
        self.list_widget.clear()
        counter = 0
        for observance_item in bwb_model.ObservanceM.get_all():
            # Important: "Alternatively, if you want the widget to have a fixed size based on its contents,
            # you can call QLayout::setSizeConstraint(QLayout::SetFixedSize);"
            # https://doc.qt.io/qt-5/qwidget.html#setSizePolicy-1

            row_i6 = QtWidgets.QListWidgetItem()
            row_layout_l7 = QtWidgets.QVBoxLayout()

            # Updating frequency
            total_number_week_list = []
            today_datetime = datetime.datetime.now()
            today_weekday_nr_it = datetime.datetime.now().weekday()
            #start_weekday_it = today_weekday_nr_it  # (Ex: Monday in Sweden, Sunday in the US)
            for day_weekday_nr_it in range(0, 7):
                check_box_sign_sg = "○"
                day_datetime = today_datetime\
                    - datetime.timedelta(days=today_datetime.weekday() + 1)\
                    + datetime.timedelta(days=day_weekday_nr_it)
                day_unixtime_it = day_datetime.timestamp()
                t_diary_filtered_list = bwb_model.DiaryM.get_all_for_obs_and_day(observance_item.id, day_unixtime_it)
                total_number_it = len(t_diary_filtered_list)
                if total_number_it > 0:
                    check_box_sign_sg = "●"
                t_weekday_one_char_sg = datetime.datetime.fromtimestamp(day_unixtime_it).strftime("%A")[0:1]
                total_number_week_list.append(check_box_sign_sg)  # t_weekday_one_char_sg.capitalize() +

            observance_short_formatted_sg = "" + observance_item.title + ""
            row_label_w8 = QtWidgets.QLabel(
                observance_short_formatted_sg
                + "<br>" + ' '.join(x for x in total_number_week_list) + ""
            )

            row_label_w8.adjustSize()
            row_layout_l7.addWidget(row_label_w8)
            row_layout_l7.setContentsMargins(0, 3, 0, 3)
            row_layout_l7.setSpacing(2)

            row_w6 = QtWidgets.QWidget()
            row_w6.setLayout(row_layout_l7)
            row_w6.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
            row_w6.adjustSize()

            row_i6.setData(QtCore.Qt.UserRole, observance_item.id)

            #my_size = QtCore.QSize(-1, row_w6.height())

            row_i6.setSizeHint(row_w6.sizeHint())
            # - Please note: If we set the size hint to (-1, height) we will get overflow towards the bottom
            self.list_widget.addItem(row_i6)
            self.list_widget.setItemWidget(row_i6, row_w6)

            counter += 1

    def get_selected_id_list(self, i_curr_item=None):
        obs_selected_item_list = self.list_widget.selectedItems()
        ret_obs_selected_id_list = []
        if i_curr_item is not None and i_curr_item.isSelected():
            obs_selected_item_list.append(i_curr_item)
        if obs_selected_item_list is not None:
            ret_obs_selected_id_list = [x.data(QtCore.Qt.UserRole) for x in obs_selected_item_list]
        return ret_obs_selected_id_list

