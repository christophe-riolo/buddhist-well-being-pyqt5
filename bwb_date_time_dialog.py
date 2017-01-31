
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import QtGui
import sys
import time


##
# Inspiration: Answer by lou here:
# https://stackoverflow.com/questions/18196799/how-can-i-show-a-pyqt-modal-dialog-and-get-data-out-of-its-controls-once-its-clo
##
class DateTimeDialog(QDialog):
    def __init__(self, i_unix_time_it, i_parent = None):
        super(DateTimeDialog, self).__init__(i_parent)

        ####self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        t_vertical_layout = QVBoxLayout(self)

        self.date_time_edit = QDateTimeEdit(self)
        self.date_time_edit.setCalendarPopup(True)
        t_date_time = QtCore.QDateTime()
        t_date_time.setMSecsSinceEpoch(1000 * i_unix_time_it)
        self.date_time_edit.setDateTime(t_date_time)

        t_vertical_layout.addWidget(self.date_time_edit)
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal,
            self
        )
        t_vertical_layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def get_unix_time(self):
        t_date_time = self.date_time_edit.dateTime()
        t_unix_time_it = t_date_time.toMSecsSinceEpoch() // 1000
        return t_unix_time_it

    @staticmethod
    def get_date_time_dialog(i_unix_time_it):
        t_dialog = DateTimeDialog(i_unix_time_it)
        t_dialog_result = t_dialog.exec_()
        t_unix_time = t_dialog.get_unix_time()
        t_result_bl = t_dialog_result == QDialog.Accepted
        return (t_result_bl, t_unix_time)

if __name__ == "__main__":

    app = QApplication(sys.argv)
    t_result_tuple = DateTimeDialog.get_date_time_dialog(time.time())
    print("t_result_tuple = " + str(t_result_tuple))

    sys.exit(app.exec_())
