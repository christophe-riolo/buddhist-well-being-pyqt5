import bwb_model
import datetime
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtGui import *

"""
Inspiration for this class:
http://stackoverflow.com/questions/20041385/python-pyqt-setting-scroll-area
"""


class DiaryListWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.v_box_layout = QVBoxLayout(self)
        self.scroll_area = QScrollArea()
        self.table  = QTableWidget()
        #self.tabel = QTableWidget()
        self.vbox_layout = QVBoxLayout()
        self.table.setLayout(self.vbox_layout)
        self.scroll_area.setWidget(self.table)
        self.v_box_layout.addWidget(self.scroll_area)

        self.scroll_area.setWidgetResizable(True)

        self.table.cellPressed.connect(self.my_cell_clicked_fn)

    def my_cell_clicked_fn(self, i_row_it, i_column_it):
        print("cell clicked")

    # http://doc.qt.io/qt-5/qwidget.html#contextMenuEvent
    def contextMenuEvent(self, i_QContextMenuEvent):
        self.right_click_menu = QMenu()
        action = QAction("Action ---")
        self.right_click_menu.triggered.connect(self.action_function)
        self.right_click_menu.addAction(action)
        self.right_click_menu.exec_(QCursor.pos())

    def action_function(self):
        print("now in action function")

    def update_gui(self, i_cur_sel_it):
        for i in reversed(range(self.vbox_layout.count())):
            widget_item = self.vbox_layout.takeAt(0)
            if widget_item is not None and isinstance(widget_item, QWidgetItem):
                widget_item.widget().deleteLater()
                self.vbox_layout.removeItem(widget_item)

        prev_diary_item = None
        for diary_item in bwb_model.DiaryM.get_all():
            diary_entry_obs_sg = bwb_model.ObservanceM.get(diary_item.observance_ref).short_name_sg
            karma = bwb_model.KarmaM.get_for_observance_and_pos(
                diary_item.observance_ref, diary_item.karma_ref)

            if prev_diary_item == None or not is_same_day(prev_diary_item.date_added_it, diary_item.date_added_it):
                date_sg = datetime.datetime.fromtimestamp(diary_item.date_added_it).strftime("%A")

                new_day_ll = QLabel(date_sg)
                new_day_ll.setAlignment(QtCore.Qt.AlignCenter)
                self.vbox_layout.addWidget(new_day_ll)

            if karma is None:
                t_diary_entry_karma_sg = ""
            else:
                t_diary_entry_karma_sg = karma.description_sg.strip() + " "

            label_text_sg = t_diary_entry_karma_sg + "[" + diary_entry_obs_sg.strip() + "] " + diary_item.notes_sg.strip()

            ###t_diary_entry_ll.bind("<Button-1>", self.diary_entry_clicked)
            #######self.right_vbox.pack_start(t_diary_entry_ll, True, True, 0)
            ###t_diary_entry_ll.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

            label = QLabel(label_text_sg)
            #label.setStyleSheet("border: 1px solid black")
            label.setFrameStyle(QFrame.StyledPanel)
            # -http://doc.qt.io/qt-4.8/qframe.html#setFrameStyle
            # -http://nullege.com/codes/search/PyQt4.QtGui.QFrame.setFrameStyle
            ####label.setFixedWidth(320)
            label.setWordWrap(True)
            self.vbox_layout.addWidget(label)

            if i_cur_sel_it == diary_item.observance_ref:
                palette = QPalette()
                palette.setColor(label.backgroundRole(), QColor("yellow"))
                label.setAutoFillBackground(True)
                label.setPalette(palette)

            prev_diary_item = diary_item # -used for the weekday labels

        #self.show()

def is_same_day(i_first_date_it, i_second_date_it):
    first_date = datetime.datetime.fromtimestamp(i_first_date_it)
    second_date = datetime.datetime.fromtimestamp(i_second_date_it)
    return first_date.date() == second_date.date()
