#!/usr/bin/env python3
import sys
import sqlite3
from PyQt5.QtWidgets import QApplication
from PyQt5 import Qt, QtCore, uic
from bwb import model
from bwb.window.observances import ObsModel
from bwb.window.diary import DiaryModel

######################
#
# Main
#
######################

BWB_APPLICATION_VERSION_SG = "private prototype"
# BWB_APPLICATION_VERSION_IT = 1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = uic.loadUi("bwb.ui")
    main_window = ui.window()

    main_window.observances.setModel(ObsModel())
    main_window.diary_list.setModel(DiaryModel(ui))

    print("===== Starting Buddhist Well-Being =====")
    print("Python version: " + str(sys.version))
    print("SQLite version: " + str(sqlite3.sqlite_version))
    print("PySQLite (Python module) version: " + str(sqlite3.version))
    print("Qt version: " + str(QtCore.qVersion()))
    print("PyQt (Python module) version: " + str(Qt.PYQT_VERSION_STR))
    print("Buddhist Well-Being application version: "
          + str(BWB_APPLICATION_VERSION_SG))
    t_db_conn = model.DbHelperM.get_db_connection()
    print("Buddhist Well-Being database schema version: "
          + str(model.DbHelperM.get_schema_version(t_db_conn)))
    print("=====")

    main_window.show()
    sys.exit(app.exec_())
