#!/usr/bin/env python
# Module for authenticating against Active Directory
# by Alan Moore

import ldap3 as ldap
from .authenticator import auth_backend


class AD(auth_backend):
    def __init__(
            self, host='localhost', port="389", base_dn="",
            bind_dn_username="", bind_dn_password="",
            require_group=None, ssl=False
    ):
        """Contructor for the connection.  Assumes plaintext LDAP"""
        self.error = ""
        self.host = host
        self.base_dn = base_dn
        self.bind_dn = bind_dn_username
        self.bind_pw = bind_dn_password
        self.require_group = require_group
        # ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, False)
        # ldap.set_option(ldap.OPT_REFERRALS, 0)
        self.authenticated_user = None
        self.authenticated_dn = None
        self.authsource = "Active Directory on {}".format(base_dn)
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

    def check(self, username=None, password=None):
        """Check a username and password against the LDAP database.

        Return true or false, and set the authenticated_user property.
        """
        if not self.con:
            return False

        # For some stupid reason, ldap will bind successfully with
        # a valid username and a BLANK PASSWORD,
        # so we have to disallow blank passwords.
        if not password:
            self.error = "Invalid credentials: Login as {} failed.".format(username)
            return False

        success = self.con.search(
            search_base=self.base_dn,
            search_filter="(sAMAccountName={})".format(username),
            search_scope=ldap.SUBTREE
        )
        if not success:
            self.error = "Search for {} failed".format(username)
            return False

        user_dn = self.con.response[0].get("dn")

        if not user_dn:
            self.error = "No such user {}.".format(username)
            return False
        else:
            try:
                self.con = ldap.Connection(self.server, user=user_dn, password=password)
                self.con.bind()
                self.authenticated_user = username
                self.authenticated_dn = user_dn
            except:
                self.error = "Invalid credentials: Login as {} failed".format(username)
                return False

        # If you've gotten to this point, the username/password checks out
        if self.require_group and not (self.in_group(self.require_group)):
            self.error = "Permission denied: not in required group {}".format(
                self.require_group
            )
            return False

        return True  # All tests passed!

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
            ).get("memberOf"):
                return True
        return False

    def info_on(self, username):
        """Returns ldap information on the given username"""
        if self.con:
            res = self.con.search(
                self.base_dn,
                "(sAMAccountName={})".format(username),
                search_scope=ldap.SUBTREE,
                attributes=ldap.ALL_ATTRIBUTES
            )
        else:
            return False

        if not res:
            self.error = "No such user {}.".format(username)
            return False

        return self.con.response[0]['attributes']

    def get_auth_user_fullname(self):
        if self.authenticated_user:
            return self.info_on(self.authenticated_user).get("name")[0]
        return ""

    def get_auth_user_email(self):
        if self.authenticated_user:
            email = self.info_on(self.authenticated_user).get("mail", [''])[0]
            return email
        return None
