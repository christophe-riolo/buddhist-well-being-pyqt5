import bwb_model
import datetime
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import QtGui

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

        self.list_widget.itemPressed.connect(self.item_clicked_fn)  # Clicked doesn't work

        # TODO: Change to using self.list_widget.verticalScrollBar()

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

        self.right_click_menu.exec_(QtGui.QCursor.pos())

    def delete_action_fn(self):
        print("now in delete_action_fn function")
        t_message_box_reply = QMessageBox.question(
            self, "Remove diary entry?", "Are you sure that you want to remove this diary entry?"
        )
        if t_message_box_reply == QMessageBox.Yes:
            bwb_model.DiaryM.remove(int(self.row_last_clicked.data(QtCore.Qt.UserRole)))
            self.update_gui(-1)
        else:
            pass  # -Do nothing

    # http://doc.qt.io/qt-5/qinputdialog.html#getText
    def rename_action_fn(self):
        print("now in rename_action_fn")
        t_last_clicked_date_dbkey_it = int(self.row_last_clicked.data(QtCore.Qt.UserRole))
        t_diary_item = bwb_model.DiaryM.get(t_last_clicked_date_dbkey_it)

        #bwb_model.DiaryM.remove(int(self.row_last_clicked.data(Qt.UserRole)))
        text_input_dialog = QInputDialog()
        t_new_text_qstring = text_input_dialog.getText(self, "Rename dialog", "New name: ", text=t_diary_item.diary_text)
        print("t_new_text_sg = " + str(t_new_text_qstring))
        bwb_model.DiaryM.update_note(t_last_clicked_date_dbkey_it, t_new_text_qstring[0])
        self.update_gui(-1)

    def update_gui(self, i_obs_sel_list):
        self.list_widget.clear()
        prev_diary_item = None

        for diary_item in bwb_model.DiaryM.get_all():
            t_observance_list = bwb_model.ObservanceM.get_all_for_diary_id(diary_item.id)
            t_observance = None
            diary_entry_obs_sg = ""
            t_delimeter_sg = ", "
            if t_observance_list is not None and t_observance_list != []:
                t_observance = t_observance_list[0]
                for obs_item in t_observance_list:
                    diary_entry_obs_sg = diary_entry_obs_sg + obs_item.title + t_delimeter_sg

            karma = bwb_model.KarmaM.get(diary_item.ref_karma_id)  ### Previous: get_for_obs_and_pos

            if (prev_diary_item is None) or (not is_same_day(prev_diary_item.date_added_it, diary_item.date_added_it)):
                t_date_as_weekday_sg = datetime.datetime.fromtimestamp(diary_item.date_added_it).strftime("%A")
                ### t_date_as_weekday_formatted_ll = QLabel("<i>" + t_date_as_weekday_sg + "</i>")
                list_item = QListWidgetItem("        " + t_date_as_weekday_sg.title())
                list_item.setFlags(list_item.flags() & ~ QtCore.Qt.ItemIsSelectable & QtCore.Qt.ItemIsUserCheckable)
                self.list_widget.addItem(list_item)
                ### self.list_widget.addW.addItem(t_date_as_weekday_formatted_ll)

            t_diary_entry_karma_sg = ""
            if karma is not None:
                t_diary_entry_karma_sg = karma.title_sg.strip() + " "

            label_text_sg = t_diary_entry_karma_sg + "[" + diary_entry_obs_sg.strip(t_delimeter_sg) + "] "\
                + diary_item.diary_text.strip()

            ###t_diary_entry_ll.bind("<Button-1>", self.diary_entry_clicked)
            #######self.right_vbox.pack_start(t_diary_entry_ll, True, True, 0)
            ###t_diary_entry_ll.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)


            #label = QLabel(label_text_sg)

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
            #label.setWordWrap(True)
            list_item = QListWidgetItem(label_text_sg)
            #list_item = QListWidgetItem()
            list_item.setData(QtCore.Qt.UserRole, diary_item.id)  # to read: .data

            ######################list_item.setBackground(QtCore.Qt.red) <-----------------
            #list_item.setFlags(list_item.flags() & ~ Qt.ItemIsSelectable)
            self.list_widget.setWordWrap(True)
            self.list_widget.addItem(list_item)
            #self.list_widget.setItemWidget(list_item, label) # -http://doc.qt.io/qt-5/qlistwidget.html#setItemWidget

            """
            if i_cur_sel_it == diary_item.observance_ref:
                #label.setFrameStyle(QFrame.StyledPanel)
                # -http://doc.qt.io/qt-4.8/qframe.html#setFrameStyle
                # -http://nullege.com/codes/search/PyQt4.QtGui.QFrame.setFrameStyle
                palette = QPalette()
                palette.setColor(label.backgroundRole(), QColor("yellow"))
                label.setAutoFillBackground(True)
                label.setPalette(palette)
            """

            prev_diary_item = diary_item # -used for the weekday labels

        self.list_widget.scrollToBottom()

        #self.show()

def is_same_day(i_first_date_it, i_second_date_it):
    first_date = datetime.datetime.fromtimestamp(i_first_date_it)
    second_date = datetime.datetime.fromtimestamp(i_second_date_it)
    return first_date.date() == second_date.date()
