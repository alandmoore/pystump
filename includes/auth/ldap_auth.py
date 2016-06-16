#!/usr/bin/env python
# Module for authenticating against LDAP directories
# by Alan Moore

import ldap3 as ldap
from .authenticator import auth_backend


class LDAPAuth(auth_backend):

    authsource_template = "LDAP on {}"
    user_query_template = "(uid={})"
    group_membership_key = "memberOf"

    def __init__(
            self, host='localhost', port="389", base_dn="",
            bind_dn_username="", bind_dn_password="",
            require_group=None, ssl=False, admins=None
    ):
        """Contructor for the connection.  Assumes plaintext LDAP"""
        super(LDAPAuth, self).__init__(admins=admins)
        self.error = ""
        self.host = host
        self.base_dn = base_dn
        self.bind_dn = bind_dn_username
        self.bind_pw = bind_dn_password
        self.require_group = require_group
        self.authenticated_user = None
        self.authenticated_dn = None
        self.authsource = self.authsource_template.format(base_dn or host)
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
            search_filter=self.user_query_template.format(username),
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

        self.check_admin_rights()

        return True  # All tests passed!

    def check_admin_rights(self):

        if not self.authenticated_user:
            return False

        for principal in self.admins:
            if (
                self.authenticated_user == principal or
                self.authenticated_dn == principal or
                self.in_group(principal)
            ):
                self.is_admin = True

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
            ).get(self.group_membership_key):
                return True
        return False

    def info_on(self, username):
        """Returns ldap information on the given username"""
        if self.con:
            res = self.con.search(
                self.base_dn,
                self.user_query_template.format(username),
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


class AD(LDAPAuth):

    authsource_template = "Active Directory on {}"
    user_query_template = "(sAMAccountName={})"
    group_membership_key = "memberOf"

class EDirectory(LDAPAuth):

    authsource_template = "Novell eDirectory on {}"
    user_query_template = "(uid={})"
    group_membership_key = "groupMembership"
