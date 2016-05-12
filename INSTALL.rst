==============
 Installation
==============

If this documentation is unclear, please post questions to PyStump's github page and I will try to incorporate the answers here.


Requirements
============

PyStump should, in theory, run on any platform that can run Python; in practice, it's developed and tested on Linux (Arch and Debian), and not routinely tested on other platforms.

It should also, in theory, work with any reasonably standards-compliant browser.  In practice, it's tested against Firefox and sometimes Chromium.

Before you can run PyStump, you need to install Python and the dependencies listed in requirements.txt

Python
------

Python 3.x preferred; 2.x may work, though you can probably expect bugs if your version is older than 2.6.

Please see http://www.python.org/getit/ for instructions on installing Python on your operating system.  Linux and OSX users should be aware that Python is probably already installed on your system; make sure it's a new enough version, though.

Dependencies
------------

Dependencies are listed in requirements.txt.  These should probably be installed using pip.


Optional: SQLite3
-----------------

You don't need SQLite installed to run PyStump (Python comes with the necessary library support), but if you find you need to make manual changes to the database, it wouldn't hurt to have it handy.  See http://www.sqlite.org.


Setup
=====

These instructions are for setting up PyStump on a unix-like OS using flask's built-in webserver.  It's probably not suitable for large-scale deployment.

- Download the latest PyStump source from https://github.com/alandmoore/pystump/archive/master.zip and extract it to a directory where you have read/write access (e.g. your home directory or Documents folder).  Alternately, if you have git installed and know how to use it, you can do::

    git clone http://github.com/alandmoore/pystump

- Create an instance config.  This will contain values for your particular installation and won't be overwritten if you update (using ``git pull``, e.g.)::

    cd pystump
    mkdir instance && cp config.py instance/

- The user who will be running PyStump needs read/write access to the database file and the directory it's in.  If this isn't the case, edit the ``instance/config.py`` file and point the database file location to somewhere where the user can read/write.

- Create an uploads folder.  This needs to be somewhere that your Pystump user can write.  Add the path to this folder to ``instance/config.py``

- Create a directory for the virtual environment and install the dependencies::

    mkdir env
    virtualenv -p $(which python3) env
    env/bin/pip install -r requirements.txt

- If you'd like PyStump to be available outside of localhost, edit ``instance/config.py`` and uncomment ``HOST = "0.0.0.0"``.

- Launch pystump.py with Python::

    env/bin/python pystump.py

- Open a web browser and point it to http://localhost:5000.  You'll see an error about the database file needing to be initialized, so just click "Initialize".

- You should now find yourself looking at an empty PyStump reference. Click "New Announcement" and start creating announcement slides!



Advanced
--------

Running on a Server
~~~~~~~~~~~~~~~~~~~

If you want to run PyStump on a lot of screens and give access to a lot of users, it's probably better to install it behind a real webserver.

Like any Flask or WSGI application, you can run PyStump behind a web server like Apache or Nginx.  Check out http://flask.pocoo.org/docs/deploying/ for various options to deploy Flask applications behind a server like this.  Warning:  this takes a bit of tweaking and server expertise.

The included ``pystump.wsgi`` file can be used to run PyStump behind Apache using mod_wsgi.  Simply add a file like this to your Apache sites configuration::

    WSGIScriptAlias /pystump /path/to/pystump/pystump.wsgi
    WSGIDaemonProcess /pystump user=myuser group=users python-path=/path/to/pystump home=/path/to/pystump

    # Uncomment for debugging
    # SetEnv PYSTUMP_DEBUG 1

    <Directory /srv/www/it-announcements>
        Require all granted
    </Directory>

You'll need to change the paths and username to match your server.

Make sure the database file and uploads directory are accessible and writable by the user that is running Apache (e.g. ``www-data`` on Debian or Ubuntu).

Configuring Authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~

PyStump supports multiple modes of authentication:

- Microsoft Active Directory
- Novell eDirectory
- SQLite tables

Active Directory and eDirectory have similar configurations:

- In your ``instance/config.py``, set ``AUTH_BACKEND`` to "AD" or "eDirectory".
- Now set ``AUTH_CONFIG`` to a dictionary with these keys:

  - ``host``: The IP or hostname of the AD/eDirectory server
  - ``port``: The port used for LDAP access, default 389 for plaintext or 636 for SSL.
  - ``base_dn``: The base DN in which you'll search for user accounts.
  - ``bind_dn_username``: This is a username for a user that you can bind to the directory with. This should just be an account with limited permissions.
  - ``bind_dn_password``: The password for the bind DN user.
  - ``require_group``: If you want to restrict login to certain users, create a group in your directory and specify it here.
  - ``ssl``: True or False to use SSL.
  - ``admins``: This is a list or tuple of group and/or user names that identify admin users.  If left blank, everyone is an admin user.

For SQLite Auth the configuration is simpler:

- In ``instance/config.py`` set ``AUTH_BACKEND`` to "sqlite"
- Now set ``AUTH_CONFIG`` to a dictionary with ``dbfile`` set to the path to the sqlite file.  You can use the same file you use for announcments, or a different file.
- Optionally, you can specify any of these options (useful if you have a sqlite file used for other things):

  - ``table``: The name of the table holding users.  Default is "users".
  - ``login``: The name of the field holding user login names.  Default is "login".
  - ``password``: The name of the field holding the user's (encrypted and salted) password.  Default is "password".  Passwords are encrypted using Unix ``crypt`` from the standard library ``crypt`` module.
  - ``salt``:  The name of the field holding the salt value.  Default is "salt".
  - ``name``:  The name of the field containing the user's full name.  Default is "name".
  - ``email``: The name of the field containing the user's email address.  Default is "email".
  - ``admins``: This is a list or tuple of usernames who are admin users.  If left blank, all users are admins.

Currently there's no interface for creating sqlite users; to do this, you'll need to open a python shell in the PyStump directory and run this::

    from includes.auth.sqlite_auth import SQLiteAuth
    sqlauth = SQLiteAUth("/path/to/your/dbfile")  # add any keyword options here too
    sqlauth.add_user("LoginName", "Plaintext Password", "user's full name", "user's email address")
    # repeat previous line for each user you need to add...


Admin Users
~~~~~~~~~~~

If you configure the "admins" option on your authentication backend, only users in the admins list (or users in groups in that list) will be able to initialize the databse or adjust the settings.  If you leave the setting blank, everyone will be an admin and be able to do those things.


Transition Backends
~~~~~~~~~~~~~~~~~~~

The default transitions are provided by animate.css.  You can optionally switch to the legacy jquery-ui transitions.  There aren't as many, but you may prefer them or find them more compatible, etc.

This is set by changing the ``TRANSITIONS`` setting in the config.  Valid values are ``animatecss`` or ``jquery-ui``.

Note that the names of the transitions are not the same between the two backends, so if you change this your existing slides will default to no transition effects until you go back and change them all.
