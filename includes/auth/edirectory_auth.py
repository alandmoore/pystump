#!/usr/bin/env python
# Module for authenticating against eDirectory
# by Alan Moore

import ldap3 as ldap
from .authenticator import auth_backend


class EDirectory(auth_backend):
    def __init__(
        self,
        host='localhost',
        port="389",
        base_dn='',
        bind_dn="",
        bind_pw="",
        require_group=None,
        ssl=False
    ):
        """Contructor for the connection.  Assumes plaintext LDAP"""
        self.error = ""
        self.host = host
        self.base_dn = base_dn
        self.bind_dn = bind_dn
        self.bind_pw = bind_pw
        self.authenticated_user = None
        self.authenticated_dn = None
        self.authsource = "Novell eDirectory on {}".format(host)
        self.require_group = require_group
        self.ldap_url = ''.join([
            (ssl and "ldaps://") or "ldap://",
            self.host,
            (port and ":{}".format(port)) or ''
        ])

        # attempt to connect and bind to the server
        self.server = ldap.Server(self.ldap_url, use_ssl=ssl)
        self.con = ldap.Connection(self.server, user=self.bind_dn, password=self.bind_pw)
        self.bound = self.con.bind()
        if not self.bound:
            self.error = "Could not bind to server {}.".format(self.host)
            if self.bind_dn is not None:
                self.error += "as %s" % self.bind_dn
                self.con = False

    def check(self, username, password):
        """Check a username and password to authenticate a user.

        Also ensure that the required group memberships exits.
        Return true if the auth succeeds or false if not.
        """
        if not self.con:
            self.error = "No server connection"
            return False

        # For some stupid reason, ldap will bind successfully
        # with a valid username and a BLANK PASSWORD,
        # so we have to disallow blank passwords.

        if not password:
            self.error = (
                "Invalid credentials: Login as {} failed".format(username)
            )
            return False

        success = self.con.search(
            search_base=self.base_dn,
            search_filter="(uid={})".format(username),
            search_scope=ldap.SUBTREE
        )

        if not success:
            self.error = "Search for {} failed".format(username)
            return False

        user_dn = self.con.response[0].get("dn")

        if not user_dn:
            self.error = "No such user {}.".format(username)
            return False

        try:
            self.con = ldap.Connection(
                self.server, user=user_dn, password=password)
            self.con.bind()
            self.authenticated_user = username
            self.authenticated_dn = user_dn
        except ldap.LDAPException:
            self.error = (
                "Invalid credentials: Login as {} failed".format(username)
            )
            return False

        # If you've gotten to this point, the username/password checks out
        if self.require_group and not (self.in_group(self.require_group)):
            self.error = "Permission denied: not in required group {}".format(
                self.require_group
            )
            return False

        return True  # All tests passed!

    def info_on(self, username):
        """Returns ldap information on the given username"""
        if not self.con:
            return False

        success = self.con.search(
            self.base_dn,
            "(uid={})".format(username),
            search_scope=ldap.SUBTREE,
            attributes=ldap.ALL_ATTRIBUTES
        )
        if not success:
            self.error = "No such user {}".format(username)
            return False

        return self.con.response[0]['attributes']

    def get_auth_user_fullname(self):
        if self.authenticated_user:
            info = self.info_on(self.authenticated_user)
            name = "{} {}".format(
                info.get("givenName", [''])[0],
                info.get("sn", [''])[0]
            )
            return name
        return ""

    def get_auth_user_email(self):
        if self.authenticated_user:
            info = self.info_on(self.authenticated_user)
            email = info.get("mail", [''])[0]
            return email
        return None

    def in_group(self, group):
        if not self.con:
            self.error = "No connection"
            return False

        group_res = self.con.search(
            self.base_dn,
            "(cn={})".format(group),
            search_scope=ldap.SUBTREE
        )
        if group_res:
            group_dn = self.con.response[0].get("dn")
            if group_dn in self.info_on(
                self.authenticated_user
            ).get("groupMembership", []):
                return True
        return False
