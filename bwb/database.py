import sqlite3
import datetime
from shutil import copyfile

DATABASE_FILE_NAME = "bwb_database_file.db"
DEFAULT_DAYS_BEFORE_NOTIFICATION = 4
NO_NOTIFICATION = -1
SQLITE_FALSE = 0
SQLITE_TRUE = 1


class DbHelperM(object):
    __db_connection = None  # "Static"

    @staticmethod
    def get_schema_version(i_db_conn):
        t_cursor = i_db_conn.execute("PRAGMA user_version")
        return t_cursor.fetchone()[0]

    @staticmethod
    def set_schema_version(i_db_conn, i_version_it):
        i_db_conn.execute("PRAGMA user_version={:d}".format(i_version_it))

    # Auto-increment is not needed in our case
    @staticmethod
    def initial_schema_and_setup(i_db_conn):
        i_db_conn.execute(
            "CREATE TABLE " + DbSchemaM.ObservancesTable.name + "("
            + DbSchemaM.ObservancesTable.Cols.id + " INTEGER PRIMARY KEY, "
            + DbSchemaM.ObservancesTable.Cols.title + " TEXT NOT NULL, "
            + DbSchemaM.ObservancesTable.Cols.description + " TEXT, "
            + DbSchemaM.ObservancesTable.Cols.user_text + " TEXT DEFAULT '')"
        )
        i_db_conn.execute(
            "CREATE TABLE " + DbSchemaM.KarmaTable.name + "("
            + DbSchemaM.KarmaTable.Cols.id + " INTEGER PRIMARY KEY, "
            + DbSchemaM.KarmaTable.Cols.title + " TEXT, "
            + DbSchemaM.KarmaTable.Cols.days_before_notification + " INTEGER"
            + " DEFAULT '" + str(DEFAULT_DAYS_BEFORE_NOTIFICATION) + "')"
        )
        i_db_conn.execute(
            "CREATE TABLE " + DbSchemaM.KarmaObsRefTable.name + "("
            + DbSchemaM.KarmaObsRefTable.Cols.id + " INTEGER PRIMARY KEY, "
            + DbSchemaM.KarmaObsRefTable.Cols.karma_ref
            + " INTEGER REFERENCES " + DbSchemaM.KarmaTable.name
            + "(" + DbSchemaM.KarmaTable.Cols.id + ") NOT NULL, "
            + DbSchemaM.KarmaObsRefTable.Cols.observance_ref
            + " INTEGER REFERENCES " + DbSchemaM.ObservancesTable.name
            + "(" + DbSchemaM.ObservancesTable.Cols.id + ") NOT NULL)"
        )
        i_db_conn.execute(
            "CREATE TABLE " + DbSchemaM.DiaryTable.name + "("
            + DbSchemaM.DiaryTable.Cols.id + " INTEGER PRIMARY KEY, "
            + DbSchemaM.DiaryTable.Cols.date_added + " INTEGER, "
            + DbSchemaM.DiaryTable.Cols.diary_text + " TEXT, "
            + DbSchemaM.DiaryTable.Cols.karma_ref + " INTEGER "
            + "INTEGER REFERENCES " + DbSchemaM.KarmaTable.name
            + "(" + DbSchemaM.KarmaTable.Cols.id + ") NOT NULL)"
        )
        i_db_conn.execute(
            "CREATE TABLE " + DbSchemaM.DiaryObsRefTable.name + "("
            + DbSchemaM.DiaryObsRefTable.Cols.id + " INTEGER PRIMARY KEY, "
            + DbSchemaM.DiaryObsRefTable.Cols.diary_ref
            + " INTEGER REFERENCES " + DbSchemaM.DiaryTable.name
            + "(" + DbSchemaM.KarmaTable.Cols.id + ") NOT NULL, "
            + DbSchemaM.DiaryObsRefTable.Cols.observance_ref
            + " INTEGER REFERENCES " + DbSchemaM.ObservancesTable.name
            + "(" + DbSchemaM.ObservancesTable.Cols.id + ") NOT NULL)"
        )

        # Adding observances
        t_observances_lt = [
            ("Friends of virtue",
                "Foster relations with people of virtue "
                "and avoid the path of degradation"),
            ("Environment",
             "Live in an environment that is conducive to spiritual practice "
             "and builds good character"),
            ("Learning",
             "Foster opportunities to learn more about the Dharma, "
             "the precepts, and your own trade in greater depth"),
            ("Caring",
                "Take the time to care well for your parents, "
                "spouse, and children"),
            ("Sharing",
                "Share time, resources, and happiness with others"),
            ("Cultivating Virtue",
                "Foster opportunities to cultivate virtue. "
                "Avoid alcohol and gambling"),
            ("Gratitude",
                "Cultivate humility, gratitude, and simple living"),
            ("Monks",
                "Seek opportunities to be close to bhikkhus "
                "in order to study the Way"),
            ("Four Noble Truths",
                "Live a life based on the Four Noble Truths"),
            ("Meditation",
             "Learn how to meditate in order to release sorrows and anxieties")
        ]
        i_db_conn.executemany(
            "INSERT INTO " + DbSchemaM.ObservancesTable.name + " ("
            + DbSchemaM.ObservancesTable.Cols.title + ", "
            + DbSchemaM.ObservancesTable.Cols.description
            + ")"
            + " VALUES (?, ?)", t_observances_lt
        )

    @staticmethod
    def upgrade_1_2(i_db_conn):
        backup_db_file()
        i_db_conn.execute(
            "ALTER TABLE " + DbSchemaM.KarmaTable.name
            + " ADD COLUMN " + DbSchemaM.KarmaTable.Cols.archived + " INTEGER "
            + "DEFAULT '" + str(SQLITE_FALSE) + "'"
        )

    @staticmethod
    def upgrade_steps(current_version):
        upgrade_steps = {
            1: DbHelperM.initial_schema_and_setup,
            2: DbHelperM.upgrade_1_2
        }
        target_version = max(upgrade_steps)
        return (
            (i, upgrade_steps[i])
            for i in range(current_version + 1, target_version + 1)
            if i in upgrade_steps
               )

    @staticmethod
    def get_db_connection():
        if DbHelperM.__db_connection is None:
            DbHelperM.__db_connection = sqlite3.connect(DATABASE_FILE_NAME)

            # Upgrading the database
            # Very good upgrade explanation:
            # http://stackoverflow.com/questions/19331550/database-change-with-software-update
            # More info here:
            # https://www.sqlite.org/pragma.html#pragma_schema_version
            t_current_db_ver_it = DbHelperM.get_schema_version(
                DbHelperM.__db_connection)
            for n, step in DbHelperM.upgrade_steps(t_current_db_ver_it):
                step(DbHelperM.__db_connection)
                DbHelperM.set_schema_version(
                    DbHelperM.__db_connection,
                    n)
            DbHelperM.__db_connection.commit()

            # TODO: Where do we close the db connection?
            # Do we need to close it?
            # http://stackoverflow.com/questions/3850261/doing-something-before-program-exit

        return DbHelperM.__db_connection


class DbSchemaM:
    class ObservancesTable:
        name = "observances"

        class Cols:
            id = "id"  # key
            title = "title"
            description = "description"
            user_text = "user_text"

    class KarmaTable:
        name = "karma"

        class Cols:
            id = "id"  # key
            title = "title"
            days_before_notification = "days_before_notification"
            archived = "archived"

    class DiaryTable:
        name = "diary"

        class Cols:
            id = "id"  # key
            date_added = "date_added"
            diary_text = "diary_text"
            karma_ref = "karma_ref"  # ref

    class KarmaObsRefTable:
        name = "karma_obs_ref"

        class Cols:
            id = "id"  # key
            karma_ref = "karma_ref"  # ref
            observance_ref = "observance_ref"  # ref

    class DiaryObsRefTable:
        name = "diary_obs_ref"

        class Cols:
            id = "id"  # key
            diary_ref = "diary_ref"  # ref
            observance_ref = "observance_ref"  # ref


def backup_db_file():
    date_sg = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    new_file_name_sg = DATABASE_FILE_NAME + "_" + date_sg
    copyfile(DATABASE_FILE_NAME, new_file_name_sg)
    return
    """
    Alternative: Appending a number to the end of the file name
    i = 1
    while(True):
        if not os.path.isfile(new_file_name_sg):
            break
        i += 1
    """
