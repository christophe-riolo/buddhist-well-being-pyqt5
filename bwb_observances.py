
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import datetime
import logging
import time
import bwb_model


class ObsCompositeWidget(QtWidgets.QWidget):

    item_selection_changed_signal = QtCore.pyqtSignal(int)
    #####new_karma_button_pressed_signal = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()

        col1_vbox_l4 = QtWidgets.QVBoxLayout()
        self.setLayout(col1_vbox_l4)



        # ..for ten practices (left column)
        ten_obs_label = QtWidgets.QLabel("<h3>Ten Blessings</h3>") #<b></b>
        col1_vbox_l4.addWidget(ten_obs_label)
        self.ten_obs_lb = QtWidgets.QListWidget()
        ############obs_dock_w2.setWidget(self.ten_obs_lb)
        self.ten_obs_lb.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        col1_vbox_l4.addWidget(self.ten_obs_lb)
        self.ten_obs_lb.itemSelectionChanged.connect(self.on_item_selection_changed)
        # -currentItemChanged cannot be used since it is activated before the list of selected items is updated
        ##self.ten_observances_lb.setSizeAdjustPolicy(QListWidget.AdjustToContents)
        # ..for details (left column)
        self.ten_obs_details_ll = QtWidgets.QLabel("-----")
        self.ten_obs_details_ll.setWordWrap(True)
        col1_vbox_l4.addWidget(self.ten_obs_details_ll)

    def on_item_selection_changed(self):
        print("len(self.ten_obs_lb.selectedItems()) = " + str(len(self.ten_obs_lb.selectedItems())))
        print("self.ten_obs_lb.currentRow() = " + str(self.ten_obs_lb.currentRow()))

        t_current_row_it = self.ten_obs_lb.currentRow()
        if t_current_row_it == -1:
            # We might get here when a karma item has been clicked
            return

        t_current_list_item = self.ten_obs_lb.item(t_current_row_it)
        t_observance = bwb_model.ObservanceM.get(t_current_list_item.data(QtCore.Qt.UserRole))
        self.ten_obs_details_ll.setText(t_observance.description)


        self.item_selection_changed_signal.emit(t_current_row_it)


    def update_gui(self):
        self.ten_obs_lb.clear()
        counter = 0
        for observance_item in bwb_model.ObservanceM.get_all():
            # Important: "Alternatively, if you want the widget to have a fixed size based on its contents,
            # you can call QLayout::setSizeConstraint(QLayout::SetFixedSize);"
            # https://doc.qt.io/qt-5/qwidget.html#setSizePolicy-1

            row_i6 = QtWidgets.QListWidgetItem()
            row_layout_l7 = QtWidgets.QVBoxLayout()

            # Updating frequency
            total_number_week_list = []
            for day_it in range(0, 7):
                t_day_as_int = int(time.mktime((datetime.date.today() - datetime.timedelta(days=day_it)).timetuple()))
                t_diary_filtered_list = bwb_model.DiaryM.get_all_for_obs_and_day(observance_item.id, t_day_as_int)
                total_number_it = len(t_diary_filtered_list)
                t_weekday_one_char_sg = datetime.datetime.fromtimestamp(t_day_as_int).strftime("%A")[0:1]
                total_number_week_list.append(t_weekday_one_char_sg.capitalize() + str(total_number_it))

            observance_short_formatted_sg = "<b>" + observance_item.title + "</b>"
            row_label_w8 = QtWidgets.QLabel(
                observance_short_formatted_sg
                + "<br>[" + ' '.join(str(x) for x in reversed(total_number_week_list)) + "]"
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

            my_size = QtCore.QSize(-1, row_w6.height())

            row_i6.setSizeHint(row_w6.sizeHint())
            # - Please note: If we set the size hint to (-1, height) we will get overflow towards the bottom
            self.ten_obs_lb.addItem(row_i6)
            self.ten_obs_lb.setItemWidget(row_i6, row_w6)

            counter += 1

