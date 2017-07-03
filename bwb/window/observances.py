import datetime
from PyQt5.QtCore import QStringListModel, Qt
from bwb import model


class ObsModel(QStringListModel):
    """Widget for displaying and selecting the blessings.
    This widget also displays information on the selected blessing."""

    def __init__(self):
        # Storing the start time of each day of the current week.
        year, month, day, *__ = datetime.date.today().timetuple()
        today = datetime.datetime(year, month, day)
        self.week = [
            int((
                today
                - datetime.timedelta(days=today.weekday())
                + datetime.timedelta(days=weekday)
                ).timestamp()
                )
            for weekday in range(0, 7)
        ]

        # Creating the initial data
        data = []
        self.details = []

        for observance_item in model.ObservanceM.get_all():
            # List of the actions in the diary for the current observance,
            # for each day of the week.
            t_diary_filtered_list = map(
                lambda day: model.DiaryM.get_all_for_obs_and_day(
                    observance_item.id,
                    day),
                self.week
                )

            # Creating the bullets to show the following of the observances
            # during the current week.
            bullet_list = ["●" if diary_entry
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

            data.append(
                observance_item.title
                + "\n" + ' '.join(bullet_list)
                + weekly_goal_reached_sg
            )

            self.details.append(observance_item.description)

        # We initialize the QStringListModel
        super().__init__(data)


# Decorating the data() method to give tooltips.
def tooltip_detail(data):
    def decorated(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return data(self, index, role)
        elif role == Qt.ToolTipRole:
            return self.details[index.row()]
        else:
            pass
    return decorated


ObsModel.data = tooltip_detail(ObsModel.data)
