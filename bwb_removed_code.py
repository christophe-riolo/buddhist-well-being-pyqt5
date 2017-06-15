"""
# Overridden to intercept the close event for the window
def closeEvent(self, i_QCloseEvent):
    self.hide()
    ###########trayicon.show()
    i_QCloseEvent.ignore()
"""

"""
def on_diary_frame_configure(self, i_event):
    self.diary_canvas.configure(scrollregion=self.diary_canvas.bbox("all"))
"""

"""
def update_gui_notifications(self):
    #######self.notifications_lb.clear()
    t_karma_lt = bwb_model.KarmaM.get_all()
    for karma_item in t_karma_lt:
        duration_sg = "x"
        latest_diary_entry = bwb_model.DiaryM.\
            get_latest_for_karma(karma_item.id)
        days_since_last_done_it = -1
        if latest_diary_entry != None:
            diary_entry_date_added = datetime.datetime.\
                fromtimestamp(latest_diary_entry.date_added_it)
            today = datetime.datetime.today()
            time_delta = today - diary_entry_date_added
            days_since_last_done_it = time_delta.days
            duration_sg = str(days_since_last_done_it)
        row = QListWidgetItem("{" + duration_sg + "}" + karma_item.title_sg)
        if days_since_last_done_it > karma_item.days_before_notification_it:
            self.notifications_lb.addItem(row)
"""

"""
def update_gui_user_text(self, i_current_item):
    if i_current_item is not None:
        self.custom_user_text_te.setText(
            bwb_model.ObservanceM.get(i_current_item.data(QtCore.Qt.UserRole)).user_text
        )
"""


def on_add_text_to_diary_button_pressed(self):
    """
    if selected_item is not None and selected_item.text != "":
        t_karma_pos_it = self.karma_lb.currentRow()

        notes_pre_sg = self.adding_text_to_diary_te_w6.toPlainText().strip()

        bwb_model.DiaryM.add(int(time.time()), notes_pre_sg, t_karma_pos_it,
            [selected_item.data(QtCore.Qt.UserRole), ])

        self.adding_text_to_diary_te_w6.clear()
        ##self.ten_observances_lb.selection_clear(0)  # Clearing the selection
        ##self.karma_lb.selection_clear(0)
        self.update_gui()
    else:
        # We arrive here if there is no observance selected
        # and selection_it is -1
        pass
    """

    # t_observance_pos_it = self.ten_obs_lb_w5.currentRow()
    # t_observance = self.ten_obs_lb_w5.
    # t_selected_observances_it_lt = [
    #     x.row() for x in self.ten_obs_lb_w5.selectedIndexes()]


def on_item_selection_changed(self):
    """
    if i_curr_item is not None:
        print("len(self.ten_obs_lb_w5.selectedItems()) = "
              + str(len(self.ten_obs_lb_w5.selectedItems())))
        print("len(self.get_obs_selected_list()) = "
              + str(len(self.get_obs_selected_list(i_curr_item))))
        t_observance = bwb_model.ObservanceM.get(
            i_curr_item.data(QtCore.Qt.UserRole))
        self.ten_obs_details_ll.setText(t_observance.description)
    else:
        # We arrive here if there is no observance selected
        # and selection_it is -1
        return
    """

    """
    try:
        obs_selected_list = self.ten_obs_lb_w5.selectedItems()
        obs_selected_list.append(i_curr_item)
        # Making sure every element is unique
        obs_selected_list = list(set(obs_selected_list))
    except:
        return
    finally:
        pass
    """

    """
    ###selection_it = self.ten_obs_lb_w5.currentRow() #.selectedItems()[0]
    if 0 <= selection_it < self.ten_obs_lb_w5.count():
        t_observance = bwb_model.ObservanceM.get(selected_item.text)
        self.ten_obs_details_ll.setText(t_observance.description)
    elif selection_it == -1:
        # We arrive here if there is no observance selected
        # and selection_it is -1
        pass
    else:
        warnings.warn("In on_observance_selected: selection_it = "
                      + str(selection_it))
    """
    """
    for diary_item in bwb_model.DiaryM.get_all():
        if diary_item.observance_ref == selection_it:
            diary_item.marked_bl = True
    """


"""
bwb_diary_widget:
init:

# Alternatively:

self.v_box_layout = QVBoxLayout(self)

self.list_widget = QListWidget()

self.scroll_area = QScrollArea()
self.scroll_area.setWidget(self.list_widget)
self.v_box_layout.addWidget(self.scroll_area)
self.scroll_area.setWidgetResizable(True)

# Clicked doesn't work
self.list_widget.itemPressed.connect(self.item_clicked_fn)
self.row_last_clicked = None
"""

"""
            t_time_of_day_format_string = "%H:%M"  # Ex: Sweden
            # Checking if the string is empty (and therefore "falsy")
            if time.strftime("%p"):
                t_time_of_day_format_string = "%I:%M %p"  # Ex: US

            time_of_day_sg = datetime.datetime.\
                fromtimestamp(diary_entry.date_added_it)\
                .strftime(t_time_of_day_format_string)
            t_time_of_day_label = QLabel(time_of_day_sg)
            ##t_time_of_day_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)  # horizontal, vertical

            ###row_layout_l7.addWidget(t_time_of_day_label)  # , QtCore.Qt.AlignRight
"""
