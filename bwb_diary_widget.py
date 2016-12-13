import bwb_model
import datetime
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.Qt import *

"""
Inspiration for this class:
http://stackoverflow.com/questions/20041385/python-pyqt-setting-scroll-area
"""

class DiaryListWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.v_box_layout = QVBoxLayout(self)
        self.scroll_area = QScrollArea()
        self.list_widget = QListWidget()
        self.scroll_area.setWidget(self.list_widget)
        self.v_box_layout.addWidget(self.scroll_area)

        self.scroll_area.setWidgetResizable(True)

        self.list_widget.itemPressed.connect(self.item_clicked_fn) # Clicked doesn't work

        self.row_last_clicked = None

    def item_clicked_fn(self, i_listwidgetitem):
        t_index_it = i_listwidgetitem.listWidget().row(i_listwidgetitem)
        print("cell clicked. row = " + str(t_index_it))
        self.row_last_clicked = i_listwidgetitem


    # http://doc.qt.io/qt-5/qwidget.html#contextMenuEvent
    # Overridden
    def contextMenuEvent(self, i_QContextMenuEvent):
        self.right_click_menu = QMenu()

        rename_action = QAction("Rename")
        rename_action.triggered.connect(self.rename_action_fn)
        self.right_click_menu.addAction(rename_action)
        delete_action = QAction("Delete")
        delete_action.triggered.connect(self.delete_action_fn)
        self.right_click_menu.addAction(delete_action)

        self.right_click_menu.exec_(QCursor.pos())

    def delete_action_fn(self):
        print("now in delete_action_fn function")
        bwb_model.DiaryM.remove(int(self.row_last_clicked.data(Qt.UserRole)))
        self.update_gui(-1)

    # http://doc.qt.io/qt-5/qinputdialog.html#getText
    def rename_action_fn(self):
        print("now in rename_action_fn")
        last_clicked_date_dbkey_it = int(self.row_last_clicked.data(Qt.UserRole))
        t_diary_item = bwb_model.DiaryM.get(last_clicked_date_dbkey_it)

        #bwb_model.DiaryM.remove(int(self.row_last_clicked.data(Qt.UserRole)))
        text_input_dialog = QInputDialog()
        text_input_dialog.getText(self, "Rename dialog", "New name: ", text=t_diary_item.notes_sg)
        self.update_gui(-1)

    def update_gui(self, i_cur_sel_it):
        self.list_widget.clear()
        prev_diary_item = None

        for diary_item in bwb_model.DiaryM.get_all():
            diary_entry_obs_sg = bwb_model.ObservanceM.get(diary_item.observance_ref).short_name_sg
            karma = bwb_model.KarmaM.get_for_observance_and_pos(
                diary_item.observance_ref, diary_item.karma_ref)



            if prev_diary_item == None or not is_same_day(prev_diary_item.date_added_it, diary_item.date_added_it):
                t_date_sg = datetime.datetime.fromtimestamp(diary_item.date_added_it).strftime("%A")
                self.list_widget.addItem(t_date_sg)



            if karma is None:
                t_diary_entry_karma_sg = ""
            else:
                t_diary_entry_karma_sg = karma.description_sg.strip() + " "

            label_text_sg = t_diary_entry_karma_sg + "[" + diary_entry_obs_sg.strip() + "] " + diary_item.notes_sg.strip()

            ###t_diary_entry_ll.bind("<Button-1>", self.diary_entry_clicked)
            #######self.right_vbox.pack_start(t_diary_entry_ll, True, True, 0)
            ###t_diary_entry_ll.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)


            label = QLabel(label_text_sg)

            """
            palette = QPalette()
            color = QColor(100, 100, 100, 100)
            palette.setColor(QPalette.Foreground, color)
            #label.setAutoFillBackground(True)
            label.setPalette(palette)
            """

            ########label.setStyleSheet("color: rgba(0, 255, 255, 255)")

            #layout = QVBoxLayout()
            #layout.addWidget(label)

            #label.setStyleSheet("border: 1px solid black")
            ############label.setFrameStyle(QFrame.StyledPanel)
            label.setWordWrap(True)
            list_item = QListWidgetItem(label_text_sg)
            #list_item = QListWidgetItem()
            list_item.setData(Qt.UserRole, diary_item.date_added_it)
            self.list_widget.setWordWrap(True)
            self.list_widget.addItem(list_item)
            #self.list_widget.setItemWidget(list_item, label) # -http://doc.qt.io/qt-5/qlistwidget.html#setItemWidget

            if i_cur_sel_it == diary_item.observance_ref:
                label.setFrameStyle(QFrame.StyledPanel)
                # -http://doc.qt.io/qt-4.8/qframe.html#setFrameStyle
                # -http://nullege.com/codes/search/PyQt4.QtGui.QFrame.setFrameStyle
                """
                palette = QPalette()
                palette.setColor(label.backgroundRole(), QColor("yellow"))
                label.setAutoFillBackground(True)
                label.setPalette(palette)
                """

            prev_diary_item = diary_item # -used for the weekday labels

        #self.show()

def is_same_day(i_first_date_it, i_second_date_it):
    first_date = datetime.datetime.fromtimestamp(i_first_date_it)
    second_date = datetime.datetime.fromtimestamp(i_second_date_it)
    return first_date.date() == second_date.date()