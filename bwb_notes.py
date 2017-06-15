

"""
# ..for custom user text
custom_notes_label = QLabel("<h4>Notes</h4>")
col1_vbox_l4.addWidget(custom_notes_label)
self.custom_user_text_te = QTextEdit()
self.custom_user_text_te.textChanged.connect(self.on_custom_user_text_text_changed)
col1_vbox_l4.addWidget(self.custom_user_text_te)
"""

"""
def on_custom_user_text_text_changed(self):
    t_current_observance_id =\
            self.ten_obs_lb_w5.currentItem().data(QtCore.Qt.UserRole)
    bwb_model.ObservanceM.update_custom_user_text(
        t_current_observance_id,
        self.custom_user_text_te.toPlainText().strip()
    )
"""
