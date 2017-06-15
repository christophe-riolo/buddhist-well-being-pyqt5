#!/usr/bin/env python3
import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QAction, QSystemTrayIcon, QMenu
from PyQt5 import QtCore
from PyQt5 import Qt
import bwb_window
import bwb_model
import sqlite3

######################
#
# Main
#
######################

BWB_APPLICATION_VERSION_SG = "private prototype"
# BWB_APPLICATION_VERSION_IT = 1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = bwb_window.WellBeingWindow()

    # System tray
    tray_icon = QSystemTrayIcon(QIcon("icon.png"), app)
    tray_menu = QMenu()
    tray_restore_action = QAction("Restore")
    tray_restore_action.triggered.connect(lambda x: main_window.show())
    tray_menu.addAction(tray_restore_action)
    tray_quit_action = QAction("Quit")
    tray_quit_action.triggered.connect(lambda x: sys.exit())
    tray_menu.addAction(tray_quit_action)
    tray_icon.setContextMenu(tray_menu)
    tray_icon.show()

    print("===== Starting Buddhist Well-Being =====")
    print("Python version: " + str(sys.version))
    print("SQLite version: " + str(sqlite3.sqlite_version))
    print("PySQLite (Python module) version: " + str(sqlite3.version))
    print("Qt version: " + str(QtCore.qVersion()))
    print("PyQt (Python module) version: " + str(Qt.PYQT_VERSION_STR))
    print("Buddhist Well-Being application version: "
          + str(BWB_APPLICATION_VERSION_SG))
    t_db_conn = bwb_model.DbHelperM.get_db_connection()
    print("Buddhist Well-Being database schema version: "
          + str(bwb_model.get_schema_version(t_db_conn)))
    print("=====")

    sys.exit(app.exec_())
