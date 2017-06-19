import datetime
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QAbstractItemView
from bwb import model


class ObsCompositeWidget(QtWidgets.QWidget):
    """Widget for displaying and selecting the blessings.
    This widget also displays information on the selected blessing."""

    item_selection_changed_signal = QtCore.pyqtSignal()
    current_row_changed_signal = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()

        # The blessings are placed in a vbox layout.
        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

        # Setting the title of widget.
        vbox.addWidget(QtWidgets.QLabel("<h3>Ten Blessings</h3>"))

        # The different blessings are items of a QListWidget.
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        vbox.addWidget(self.list_widget)

        # We need to update the label when we select a blessing.
        self.list_widget.currentRowChanged.connect(
            self.on_item_selection_changed)

        # Explanation of current blessing are put in a
        # QLabel at the bottom.
        self.ten_obs_details_ll = QtWidgets.QLabel("-----")
        self.ten_obs_details_ll.setWordWrap(True)
        vbox.addWidget(self.ten_obs_details_ll)

    def on_item_selection_changed(self, current_row_it):
        print("self.ten_obs_lb.currentRow() = "
              + str(self.list_widget.currentRow()))
        print("len(self.ten_obs_lb.selectedItems()) = "
              + str(len(self.list_widget.selectedItems())))

        # We test whether a blessing has been selected.
        if current_row_it != -1:
            t_current_list_item = self.list_widget.item(current_row_it)
            t_observance = model.\
                ObservanceM.get(t_current_list_item.data(QtCore.Qt.UserRole))
            self.ten_obs_details_ll.setText(t_observance.description)

            self.item_selection_changed_signal.emit()

    def update_gui(self):
        """
        Signs to use for showing observance:
        ☐ ☑ (Ballot ____, )
        ✓
        ◯ ⬤ (Large Circle, Black Large Circle)
        ○ ● (White Circle, Black Circle
            (Please note that medium white/black cirlce is smaller than these))
        More here:
        https://unicode-table.com/en/blocks/geometric-shapes/
        https://unicode-table.com/en/blocks/miscellaneous-symbols/
        """
        self.list_widget.clear()
        for observance_item in model.ObservanceM.get_all():
            # Important: "Alternatively, if you want the widget to have
            # a fixed size based on its contents,
            # you can call QLayout::setSizeConstraint(QLayout::SetFixedSize);"
            # https://doc.qt.io/qt-5/qwidget.html#setSizePolicy-1

            # Updating frequency
            year, month, day, *__ = datetime.date.today().timetuple()
            today = datetime.datetime(year, month, day)

            # Storing the start time of each day of the week.
            week = [
                int((
                    today
                    - datetime.timedelta(days=today.weekday())
                    + datetime.timedelta(days=weekday)
                    ).timestamp()
                    )
                for weekday in range(0, 7)
            ]

            # # List of the actions in the diary for the current observance,
            # # for each day of the week.
            t_diary_filtered_list = map(
                lambda day: model.DiaryM.get_all_for_obs_and_day(
                    observance_item.id,
                    day),
                week
                )

            # Creating the bullets to show the following of the observances
            # during the current week.
            total_number_week_list = ["●" if diary_entry
                                      else "○"
                                      for diary_entry in t_diary_filtered_list
                                      ]

            # We count the number of days with diary entries for current
            # observance during the current week.
            total_number_for_week_it = sum(
                (int(bool(diary_entry))
                 for diary_entry in t_diary_filtered_list)
                )
            # Experimental:
            weekly_goal_reached_sg = ""
            if total_number_for_week_it > 1:
                weekly_goal_reached_sg = " ✔"

            observance_short_formatted_sg = "" + observance_item.title + ""
            row_label_w8 = QtWidgets.QLabel(
                observance_short_formatted_sg
                + "<br>" + ' '.join(total_number_week_list)
                + weekly_goal_reached_sg
            )

            row_i6 = QtWidgets.QListWidgetItem()
            row_layout_l7 = QtWidgets.QVBoxLayout()

            row_label_w8.adjustSize()
            row_layout_l7.addWidget(row_label_w8)
            row_layout_l7.setContentsMargins(0, 3, 0, 3)
            row_layout_l7.setSpacing(2)

            row_w6 = QtWidgets.QWidget()
            row_w6.setLayout(row_layout_l7)
            row_w6.setSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                 QtWidgets.QSizePolicy.Minimum)
            row_w6.adjustSize()

            row_i6.setData(QtCore.Qt.UserRole, observance_item.id)

            row_i6.setSizeHint(row_w6.sizeHint())
            # - Please note: If we set the size hint to (-1, height)
            #   we will get overflow towards the bottom
            self.list_widget.addItem(row_i6)
            self.list_widget.setItemWidget(row_i6, row_w6)
