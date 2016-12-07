import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
import bwb_window

######################
#
# Main
#
######################

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

    sys.exit(app.exec_())
