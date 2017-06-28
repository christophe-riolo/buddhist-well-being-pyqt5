import csv
from bwb.database import (
    DbHelperM,
    DbSchemaM,
    SQLITE_FALSE,
    SQLITE_TRUE,
    DEFAULT_DAYS_BEFORE_NOTIFICATION)

#################
#
# Model
#
# This module contains everything related to the model for the application:
# * The db schema
# * The db connection
# * Data structure classes (each of which contains functions
#   for reading and writing to the db):
#   * ObservanceM
#   * KarmaM
#   * DiaryM
# * Database creation and setup
# * Various functions (for backing up the db etc)
#
# Notes:
# * When inserting values, it's best to use "VALUES (?, ?)"
#   because then the sqlite3 module will take care of
#   escaping values for us
#
#################


class ObservanceM:
    def __init__(self, i_id, i_title, i_description, i_user_text=""):
        self.id = i_id
        self.title = i_title
        self.description = i_description
        self.user_text = i_user_text

    @staticmethod
    def get(i_id):
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor_result = db_cursor.execute(
            "SELECT * FROM " + DbSchemaM.ObservancesTable.name
            + " WHERE " + DbSchemaM.ObservancesTable.Cols.id + "=" + str(i_id)
        )
        t_observance_tuple_from_db = db_cursor_result.fetchone()
        db_connection.commit()

        return ObservanceM(
            t_observance_tuple_from_db[0],
            t_observance_tuple_from_db[1],
            t_observance_tuple_from_db[2],
            t_observance_tuple_from_db[3]
        )

    @staticmethod
    def get_all_for_diary_id(i_diary_id):
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor_result = db_cursor.execute(
            "SELECT * FROM " + DbSchemaM.DiaryObsRefTable.name
            + " WHERE "
            + DbSchemaM.DiaryObsRefTable.Cols.diary_ref
            + "="
            + str(i_diary_id)
        )
        t_diary_obs_ref_tuple_list = db_cursor_result.fetchall()
        db_connection.commit()

        if t_diary_obs_ref_tuple_list is None:
            return None

        ret_obs_list = []

        for t_diary_obs_tuple in t_diary_obs_ref_tuple_list:
            t_obs_id = t_diary_obs_tuple[2]

            db_connection = DbHelperM.get_db_connection()
            db_cursor = db_connection.cursor()
            db_cursor_result = db_cursor.execute(
                "SELECT * FROM "
                + DbSchemaM.ObservancesTable.name
                + " WHERE "
                + DbSchemaM.ObservancesTable.Cols.id
                + "="
                + str(t_obs_id)
            )
            t_obs_tuple = db_cursor_result.fetchone()
            db_connection.commit()

            ret_obs_list.append(
                ObservanceM(
                    t_obs_tuple[0],
                    t_obs_tuple[1],
                    t_obs_tuple[2],
                    t_obs_tuple[3]
                )
            )
        return ret_obs_list

    @staticmethod
    def get_all_for_karma_id(i_karma_id):
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor_result = db_cursor.execute(
            "SELECT * FROM " + DbSchemaM.KarmaObsRefTable.name
            + " WHERE "
            + DbSchemaM.KarmaObsRefTable.Cols.karma_ref
            + "="
            + str(i_karma_id)
        )
        t_karma_obs_ref_tuple_list = db_cursor_result.fetchall()
        db_connection.commit()

        if t_karma_obs_ref_tuple_list is None:
            return None

        ret_obs_list = []

        for t_karma_obs_tuple in t_karma_obs_ref_tuple_list:
            t_obs_id = t_karma_obs_tuple[2]

            db_connection = DbHelperM.get_db_connection()
            db_cursor = db_connection.cursor()
            db_cursor_result = db_cursor.execute(
                "SELECT * FROM " + DbSchemaM.ObservancesTable.name
                + " WHERE "
                + DbSchemaM.ObservancesTable.Cols.id
                + "="
                + str(t_obs_id)
            )
            t_obs_tuple = db_cursor_result.fetchone()
            db_connection.commit()

            ret_obs_list.append(
                ObservanceM(
                    t_obs_tuple[0],
                    t_obs_tuple[1],
                    t_obs_tuple[2],
                    t_obs_tuple[3]
                )
            )
        return ret_obs_list

    @staticmethod
    def get_all():
        ret_observance_lt = []
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor_result = db_cursor.execute(
                "SELECT * FROM "
                + DbSchemaM.ObservancesTable.name)
        t_observances_from_db = db_cursor_result.fetchall()
        for t_tuple in t_observances_from_db:
            ret_observance_lt.append(
                ObservanceM(
                    t_tuple[0],
                    t_tuple[1],
                    t_tuple[2],
                    t_tuple[3]
                )
            )
        db_connection.commit()
        return ret_observance_lt

    @staticmethod
    def update_custom_user_text(i_id, i_text):
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "UPDATE " + DbSchemaM.ObservancesTable.name
            + " SET " + DbSchemaM.ObservancesTable.Cols.user_text + " = ?"
            + " WHERE " + DbSchemaM.ObservancesTable.Cols.title + " = ?",
            (i_text, i_id)
        )
        db_connection.commit()


class KarmaM:
    def __init__(self, i_id, i_title_sg, i_days_before_notification_it):
        self.id = i_id
        self.title_sg = i_title_sg
        self.days_before_notification_it = i_days_before_notification_it

    @staticmethod
    def add(i_obs_ref_list,
            i_title_sg,
            i_days_before_notification_it=DEFAULT_DAYS_BEFORE_NOTIFICATION):
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "INSERT INTO " + DbSchemaM.KarmaTable.name + "("
            + DbSchemaM.KarmaTable.Cols.title + ", "
            + DbSchemaM.KarmaTable.Cols.days_before_notification
            + ") VALUES (?, ?)",
            (i_title_sg, i_days_before_notification_it)
        )
        db_connection.commit()

        # Nice! More info: https://tinyurl.com/pyIDretrieve
        t_karma_id = db_cursor.lastrowid

        for obs_ref in i_obs_ref_list:
            db_cursor.execute(
                "INSERT INTO " + DbSchemaM.KarmaObsRefTable.name + "("
                + DbSchemaM.KarmaObsRefTable.Cols.karma_ref + ", "
                + DbSchemaM.KarmaObsRefTable.Cols.observance_ref
                + ") VALUES (?, ?)",
                (t_karma_id, obs_ref)
            )
            db_connection.commit()

    @staticmethod
    def get_all():
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor_result = db_cursor.execute(
            "SELECT * FROM "
            + DbSchemaM.KarmaTable.name
            + " WHERE "
            + DbSchemaM.KarmaTable.Cols.archived
            + "="
            + str(SQLITE_FALSE)
        )
        t_karma_tuple_list_from_db = db_cursor_result.fetchall()
        db_connection.commit()
        karma_list_lt = []
        for karma_db_item in t_karma_tuple_list_from_db:
            karma_list_lt.append(KarmaM(
                karma_db_item[0],
                karma_db_item[1],
                karma_db_item[2]
            ))
        return karma_list_lt

    @staticmethod
    def get_for_observance_list(i_observance_id_list):
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()

        t_karma_id_list = [x.id for x in KarmaM.get_all()]

        for obs_item_id in i_observance_id_list:
            db_cursor_result = db_cursor.execute(
                "SELECT * FROM "
                + DbSchemaM.KarmaObsRefTable.name
                + " WHERE "
                + DbSchemaM.KarmaObsRefTable.Cols.observance_ref
                + "="
                + str(obs_item_id)
            )
            t_temp_karma_ref_list = [x[1] for x in db_cursor_result.fetchall()]
            db_connection.commit()
            t_karma_id_list = list(set(t_karma_id_list)
                                   & set(t_temp_karma_ref_list))

        ret_karma_list = []
        for karma_id_ref in t_karma_id_list:
            db_cursor_result = db_cursor.execute(
                "SELECT * FROM " + DbSchemaM.KarmaTable.name
                + " WHERE " + DbSchemaM.KarmaTable.Cols.id
                + "=" + str(karma_id_ref)
                + " AND " + DbSchemaM.KarmaTable.Cols.archived
                + "=" + str(SQLITE_FALSE)
            )
            t_karma_tuple = db_cursor_result.fetchone()
            ret_karma_list.append(KarmaM(
                t_karma_tuple[0],
                t_karma_tuple[1],
                t_karma_tuple[2]
            ))
            db_connection.commit()
        return ret_karma_list

    @staticmethod
    def get(i_id):
        if i_id is None or i_id == -1:
            return None

        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor_result = db_cursor.execute(
            "SELECT * FROM " + DbSchemaM.KarmaTable.name
            + " WHERE " + DbSchemaM.KarmaTable.Cols.id + "=" + str(i_id)
        )
        karma_db_item = db_cursor_result.fetchone()
        db_connection.commit()

        return KarmaM(
            karma_db_item[0],
            karma_db_item[1],
            karma_db_item[2]
        )

    @staticmethod
    def archive(i_id_it):
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "UPDATE " + DbSchemaM.KarmaTable.name
            + " SET " + DbSchemaM.KarmaTable.Cols.archived + " = ?"
            + " WHERE " + DbSchemaM.KarmaTable.Cols.id + " = ?",
            (str(SQLITE_TRUE), str(i_id_it))
        )
        db_connection.commit()


class DiaryM:
    def __init__(self,
                 i_id,
                 i_date_added_it,
                 i_diary_text="",
                 i_ref_karma_id=-1):
        self.id = i_id
        self.date_added_it = i_date_added_it
        self.diary_text = i_diary_text
        self.ref_karma_id = i_ref_karma_id

    @staticmethod
    def add(i_date_added_it,
            i_diary_text,
            i_karma_ref,
            i_observance_ref_id_it_list):
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "INSERT INTO " + DbSchemaM.DiaryTable.name + "("
            + DbSchemaM.DiaryTable.Cols.date_added + ", "
            + DbSchemaM.DiaryTable.Cols.diary_text + ", "
            + DbSchemaM.DiaryTable.Cols.karma_ref
            + ") VALUES (?, ?, ?)",
            (i_date_added_it, i_diary_text, i_karma_ref)
        )
        db_connection.commit()

        t_diary_id = db_cursor.lastrowid

        for obs_ref in i_observance_ref_id_it_list:
            db_cursor = db_connection.cursor()
            db_cursor.execute(
                "INSERT INTO " + DbSchemaM.DiaryObsRefTable.name + "("
                + DbSchemaM.DiaryObsRefTable.Cols.diary_ref + ", "
                + DbSchemaM.DiaryObsRefTable.Cols.observance_ref
                + ") VALUES (?, ?)",
                (t_diary_id, obs_ref)
            )
            db_connection.commit()

    @staticmethod
    def update_note(i_id_it, i_new_text_sg):
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "UPDATE " + DbSchemaM.DiaryTable.name
            + " SET " + DbSchemaM.DiaryTable.Cols.diary_text + " = ?"
            + " WHERE " + DbSchemaM.DiaryTable.Cols.id + " = ?",
            (i_new_text_sg, str(i_id_it))
        )
        db_connection.commit()

    @staticmethod
    def update_date(i_id_it, i_new_time_it):
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "UPDATE " + DbSchemaM.DiaryTable.name
            + " SET " + DbSchemaM.DiaryTable.Cols.date_added + " = ?"
            + " WHERE " + DbSchemaM.DiaryTable.Cols.id + " = ?",
            (str(i_new_time_it), str(i_id_it))
        )
        db_connection.commit()

    @staticmethod
    def remove(i_id_it):
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "DELETE FROM " + DbSchemaM.DiaryTable.name
            + " WHERE " + DbSchemaM.DiaryTable.Cols.id + "=" + str(i_id_it)
        )
        db_connection.commit()

        db_cursor.execute(
            "DELETE FROM " + DbSchemaM.DiaryObsRefTable.name
            + " WHERE " + DbSchemaM.DiaryObsRefTable.Cols.diary_ref
            + "=" + str(i_id_it)
        )
        db_connection.commit()

    @staticmethod
    def get(i_id_it):
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor_result = db_cursor.execute(
            "SELECT * FROM " + DbSchemaM.DiaryTable.name + " WHERE "
            + DbSchemaM.DiaryTable.Cols.id + "=" + str(i_id_it)
        )
        t_diary_tuple_from_db = db_cursor_result.fetchone()
        db_connection.commit()

        return DiaryM(
            t_diary_tuple_from_db[0],
            t_diary_tuple_from_db[1],
            t_diary_tuple_from_db[2],
            t_diary_tuple_from_db[3]
        )

    @staticmethod
    def get_all(i_reverse_bl=False):
        t_direction_sg = "ASC"
        if i_reverse_bl:
            t_direction_sg = "DESC"
        ret_diary_lt = []
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor_result = db_cursor.execute(
            "SELECT * FROM "
            + DbSchemaM.DiaryTable.name
            + " ORDER BY "
            + DbSchemaM.DiaryTable.Cols.date_added
            + " "
            + t_direction_sg
        )
        t_diary_from_db = db_cursor_result.fetchall()
        for t_tuple in t_diary_from_db:
            ret_diary_lt.append(DiaryM(
                t_tuple[0],
                t_tuple[1],
                t_tuple[2],
                t_tuple[3]
            ))
        db_connection.commit()
        return ret_diary_lt

    @staticmethod
    def get_all_for_obs_and_day(i_obs_id,
                                i_start_of_day_as_unix_time_it,
                                i_reverse_bl=True):
        """
        :param i_obs_id:
        :param i_start_of_day_as_unix_time_it:
             It's very important that this is given as the start of the day
        :param i_reverse_bl:
        :return:
        """
        ret_diary_lt = []
        db_connection = DbHelperM.get_db_connection()

        db_cursor = db_connection.cursor()
        db_cursor_result = db_cursor.execute(
            "SELECT * FROM " + DbSchemaM.DiaryObsRefTable.name
            + " WHERE " + DbSchemaM.DiaryObsRefTable.Cols.observance_ref
            + "=" + str(i_obs_id)
        )
        t_diary_tuple_list = db_cursor_result.fetchall()
        t_diary_id_list = [x[1] for x in t_diary_tuple_list]

        for t_diary_id in t_diary_id_list:

            db_cursor = db_connection.cursor()
            db_cursor_result = db_cursor.execute(
                "SELECT * FROM " + DbSchemaM.DiaryTable.name
                + " WHERE " + DbSchemaM.DiaryTable.Cols.id
                + "=" + str(t_diary_id)
                + " AND " + DbSchemaM.DiaryTable.Cols.date_added
                + ">=" + str(i_start_of_day_as_unix_time_it)
                + " AND " + DbSchemaM.DiaryTable.Cols.date_added
                + "<" + str(i_start_of_day_as_unix_time_it + 24 * 3600)
            )
            t_diary_from_db = db_cursor_result.fetchall()
            for t_tuple in t_diary_from_db:
                ret_diary_lt.append(DiaryM(
                    t_tuple[0],
                    t_tuple[1],
                    t_tuple[2],
                    t_tuple[3]
                ))
            db_connection.commit()

        if i_reverse_bl:
            ret_diary_lt.reverse()

        return ret_diary_lt

    @staticmethod
    def get_latest_for_karma(i_karma_id_it):
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor_result = db_cursor.execute(
            "SELECT * FROM " + DbSchemaM.DiaryTable.name
            + " WHERE " + DbSchemaM.DiaryTable.Cols.karma_ref
            + "=" + str(i_karma_id_it)
        )
        diary_entry_list_for_karma_list = db_cursor_result.fetchall()
        if diary_entry_list_for_karma_list == []:
            return None
        last_diary_entry_for_karma_tuple = diary_entry_list_for_karma_list[-1]

        return DiaryM(
            last_diary_entry_for_karma_tuple[0],
            last_diary_entry_for_karma_tuple[1],
            last_diary_entry_for_karma_tuple[2],
            last_diary_entry_for_karma_tuple[3]
        )


def export_all():
    csv_writer = csv.writer(open("exported.csv", "w"))
    t_space_tab_sg = "    "
    for obs_item in ObservanceM.get_all():
        csv_writer.writerow((obs_item.title, obs_item.description))
    csv_writer.writerow(("\n\n\n",))
    # -TODO: This doesn't work since we may skip indexes
    for obs in ObservanceM.get_all():
        csv_writer.writerow((obs.title,))
        for karma_item in KarmaM.get_for_observance_list([obs.id]):
            csv_writer.writerow((t_space_tab_sg + karma_item.title_sg,))
    csv_writer.writerow(("\n\n\n",))

    # TODO:
    """
    for diary_item in DiaryM.get_all():
        t_diary_entry_obs_sg = ObservanceM.get(diary_item.observance_ref).title
        t_karma = KarmaM.get(diary_item.karma_ref)
        if t_karma is None:
            t_diary_entry_karma_sg = ""
        else:
            t_diary_entry_karma_sg = t_karma.title_sg
        csv_writer.writerow((t_diary_entry_obs_sg,
                             t_diary_entry_karma_sg,
                             diary_item.diary_text))
    """

    for diary_item in DiaryM.get_all():
        t_karma = KarmaM.get(diary_item.ref_karma_id)
        if t_karma is None:
            t_diary_entry_karma_sg = ""
        else:
            t_diary_entry_karma_sg = t_karma.title_sg
        csv_writer.writerow((t_diary_entry_karma_sg, diary_item.diary_text))
