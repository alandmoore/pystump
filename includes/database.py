"""
Database model for PyStump
"""

import sqlite3
from .util import debug, string_to_datetime

import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


class Database:

    def __init__(self, dbfile):
        self.dbfile = dbfile
        self.cx_obj = None
        self.cu_obj = None

    def cx(self):
        if not self.cx_obj:
            self.cx_obj = sqlite3.connect(
                self.dbfile,
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            self.cx_obj.row_factory = sqlite3.Row
        return self.cx_obj

    def cu(self):
        if not self.cu_obj:
            self.cu_obj = self.cx().cursor()
        return self.cu_obj

    def query(self, query, data=None, return_results=True):
        if data is None:
            self.cu().execute(query)
        else:
            self.cu().execute(query, data)
        if return_results:
            results = self.cu().fetchall()
            return [dict(x) for x in results]
        else:
            self.cx().commit()
            return self.cu().rowcount

    def initialize(self):
        """
        Creates a fresh, empty database.
        """
        with open(os.path.join(BASE_DIR,"sql/schema.sql"), 'r') as sqlfile:
            self.cu().executescript(sqlfile.read())
        with open(os.path.join(BASE_DIR, "sql/default.sql"), 'r') as sqlfile:
            self.cu().executescript(sqlfile.read())

    def do_initialize_db(self, formdata, *args, **kwargs):
        confirm = formdata.get("init_db")
        if confirm:
            self.initialize()
        return ''

    def get_missing_tables(self):
        query = """SELECT name FROM sqlite_master WHERE type='table'"""
        are_tables = [x.get("name") for x in self.query(query)]
        debug("Tables that exist: " + are_tables.__str__())
        should_be_tables = ["settings", "announcements"]
        missing = [
            table
            for table in should_be_tables
            if table not in are_tables
        ]
        return missing

    ###########
    # Getters #
    ###########

    def get_settings(self):
        query = """
        SELECT setting_name, setting_value, setting_type FROM settings
        """
        res = self.query(query)
        return dict(
            (x["setting_name"], (x["setting_value"], x["setting_type"]))
            for x in res
        )

    def get_setting_value(self, setting):
        query = """
        SELECT setting_value FROM settings WHERE setting_name LIKE ?
        """
        res = self.query(query, (setting,))
        return (len(res) > 0 and res[0].get("setting_value")) or None

    def get_active_announcements(self):
        query = """SELECT * FROM announcements_v"""
        return self.query(query)

    def get_all_announcements(self):
        query = """SELECT * FROM announcements ORDER BY id ASC"""
        return self.query(query)

    def get_announcement(self, id):
        try:
            id = int(id)
        except (ValueError, TypeError):
            return {}
        query = """SELECT * FROM announcements WHERE id = ?"""
        res = self.query(query, (id,))
        print(res)
        return len(res) > 0 and res[0] or {}

    ###########
    # Setters #
    ###########

    def save_announcement(self, formdata, username="Unknown", **kwargs):
        max_duration = self.get_setting_value("Max Duration")
        min_duration = self.get_setting_value("Min Duration")
        qdata = {
            "title": formdata.get("title"),
            "content": formdata.get("content"),
            "author": username,
            "activate": string_to_datetime(formdata.get("activate")),
            "expire": string_to_datetime(formdata.get("expire")),
            "duration": (
                formdata.get("duration")
                and int(formdata.get("duration"))
                or None
            ),
            "max_duration": int(max_duration) or 999999,
            "min_duration": int(min_duration) or 0,
            "fg_color": formdata.get("fg_color"),
            "bg_color": formdata.get("bg_color")
        }
        debug(qdata)
        if formdata.get("id"):
            debug("UPDATE query, id={}".format(formdata.get("id")))
            qdata["id"] = formdata.get("id")
            query = """UPDATE announcements SET title=:title, content=:content,
            author = :author, activate = :activate, expire = :expire,
            duration=MAX(MIN(:duration, :max_duration), :min_duration),
            fg_color=:fg_color, bg_color=:bg_color,
            updated=DATETIME('now', 'localtime')
            WHERE id=:id"""
        else:  # insert query
            debug("INSERT query")
            query = """INSERT INTO announcements(title, content, author, activate,
            expire, duration, fg_color, bg_color, updated)
            VALUES (:title, :content, :author, :activate, :expire,
            MAX(MIN(:duration, :max_duration), :min_duration),
            :fg_color, :bg_color, DATETIME('now', 'localtime') )
            """
        res = self.query(query, qdata, False)
        debug(res)
        return ""

    def delete_announcement(self, id, **kwargs):
        if not id:
            return None
        query = """DELETE FROM announcments WHERE id=?"""
        self.query(query, id, False)
        return ""

    def save_settings(self, formdata, **kwargs):
        query = """INSERT OR REPLACE INTO
        settings(setting_name, setting_value, setting_type)
        VALUES(:setting, :value,
        (SELECT setting_type FROM settings s
        WHERE s.setting_name LIKE :setting))"""
        settings = self.get_settings().keys()
        for setting in settings:
            value = formdata.get(setting)
            self.query(query, {"setting": setting, "value": value}, False)
        return ""
