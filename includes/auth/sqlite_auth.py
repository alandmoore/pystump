import sqlite3
import crypt

from .authenticator import auth_backend


class SQLiteAuth(auth_backend):
    """An authenticator that uses sqlite tables"""

    create_table_query = """
    CREATE TABLE "{table}" (
        "{login}" TEXT PRIMARY KEY,
        "{password}" TEXT,
        "{salt}" TEXT,
        "{name}" TEXT,
        "{email}" TEXT
    )
    """

    def __init__(
            self, dbfile, tablename='users',
            login_field='login',
            password_field='password',
            salt_field='salt',
            name_field='name',
            email_field='email'
    ):
        self.dbfile = dbfile
        self.cx_obj = None
        self.schema = {
            'table': tablename,
            'login': login_field,
            'password': password_field,
            'salt': salt_field,
            'name': name_field,
            'email': email_field
        }

        self.error = ''
        self.auth_user = None
        self.auth_user_name = None
        self.auth_user_email = None

        if not self.check_table():
            self.create_table()

    def __query(self, query, parameters=None, write=False):
        """Run a database query"""

        cx = sqlite3.connect(self.dbfile)
        cursor = cx.cursor()

        if parameters:
            cursor.execute(query, parameters)
        else:
            cursor.execute(query)

        if not write:
            headers = [x[0] for x in cursor.description or []]

            return [dict(zip(headers, row)) for row in cursor.fetchall() or []]
        else:
            cx.commit()

    def check_table(self):
        """See if the user table exists"""

        query = """
        SELECT (:table in
            (SELECT name FROM sqlite_master WHERE type='table'))
        as e
        """
        return self.__query(query, {"table": self.schema['table']})[0]['e']

    def create_table(self):
        """Create the table for storing users"""

        query = self.create_table_query.format(**self.schema)

        self.__query(query)

    def add_user(self, username, password, name='', email=''):
        """Insert a user into the database"""

        salt = crypt.mksalt()
        encrypted_pw = crypt.crypt(password, salt)

        query = """
        INSERT INTO "{table}"
        ("{login}", "{password}", "{salt}", "{name}", "{email}")
        VALUES (:login, :password, :salt, :name, :email)
        """.format(**self.schema)

        self.__query(query, {
            "login": username,
            "password": encrypted_pw,
            "salt": salt,
            "name": name,
            "email": email
        }, write=True)

    def check(self, username, password):

        user = self.__query(
            """SELECT * FROM "{table}" WHERE "{login}" = :login """
            .format(**self.schema),
            {"login": username}
        )

        if not user:
            self.error = "No such user: {}".format(username)
            return False

        user = user[0]
        encrypted_pw = crypt.crypt(password, user[self.schema["salt"]])

        if user[self.schema["password"]] != encrypted_pw:
            self.error = "Wrong password for user {}.".format(username)
            return False

        self.auth_user = username
        self.auth_user_name = user[self.schema["name"]]
        self.auth_user_email = user[self.schema["email"]]

        return True

    def get_user_email(self):

        return self.auth_user_email

    def get_user_name(self):

        return self.auth_user_name
