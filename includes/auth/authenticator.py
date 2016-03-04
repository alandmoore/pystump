"""
Defines a generic authenticator object which will take a
user/password pair and return authentication status and user details.
"""


class Authenticator(object):

    def __init__(self, backend, **kwargs):
        self.backend = backend(**kwargs)

    def check(self, username, password):
        return self.backend.check(username, password)

    def get_user_name(self):
        return self.backend.get_auth_user_fullname()

    def get_user_email(self):
        return self.backend.get_auth_user_email()

    def is_admin(self):
        return self.backend.is_admin


class auth_backend(object):
    """
    This is a base class for an auth backend.
    Any auth backend should subclass it and override its functions.
    """
    authenticated = False

    def __init__(self, **kwargs):
        # This function should connect to authentication sources
        # and configure basic settings

        # get the admin users/groups.  If this isn't set,
        # everyone is an admin.

        self.admins = kwargs.get("admins", [])
        self.is_admin = not self.admins

    def check(self, username=None, password=None):
        # This function should return a boolean value
        # True if the credentials check out, False if not
        # it should also set self.authenticated accordingly
        pass

    def get_auth_user_fullname(self):
        # This function will return the full name of the authenticated user
        # assuming it's available, e.g. from an LDAP or Database table.
        # It returns None if there's no authenticated user.
        # If there's no name available, it can return the username

        pass

    def get_auth_user_email(self):
        # This function will return the default email address of the
        # authenticated user, assuming it's available from LDAP or something
        # Returns None if there's no authenticated user.
        # If there's no email available, it returns an empty string

        pass


class dummy_auth(auth_backend):
    """
    This is just a sample auth backend class.
    It's totally insecure and only for testing purposes.
    It will authenticate any username provided the password is not blank.
    And give them full privileges.
    """
    def __init__(self, **kwargs):
        super(dummy_auth, self).__init__(**kwargs)
        self.username = None

    def check(self, username=None, password=None):
        auth = False
        if username is not None and password is not None and password != '':
            self.authenticated = True
            self.username = username
            auth = True

        if username in self.admins:
            self.is_admin = True

        return auth

    def get_auth_user_fullname(self):
        return self.username

    def get_auth_user_email(self):
        return (self.authenticated and '{}@localhost'.format(self.username)) or None
