#!/usr/bin/env python
"""
PyStump
Copyright 2014 Alan D Moore
www.alandmoore.com
Licensed to you under the terms of the GNU GPL v3.
See the included COPYING file for details.

PyStump is a web-based announcements display system.

It's written in python and requires the python flask framework
and your favorite standards-compliant web browser.

"""


from flask import (
    Flask, g, render_template, request, json,
    abort, redirect, session, url_for, Markup
)
from includes.database import Database
from includes.util import debug
from includes.auth.authenticator import Authenticator, dummy_auth
from includes.auth.ad_auth import AD
from includes.auth.edirectory_auth import EDirectory
from functools import wraps
from markdown import markdown

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile("pystump.conf", silent=True)


# Wrapper to secure callbacks
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("auth"):
            return redirect(url_for("login_page", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


# Create a basic markdown filter for jinja
@app.template_filter('markdown')
def markdown_filter(data):
    return Markup(markdown(data))


@app.before_request
def before_request():
    g.debug = app.config.get("DEBUG")
    g.db = Database(app.config.get("DATABASE_FILE"))
    g.missing_tables = g.db.get_missing_tables()
    if len(g.missing_tables) > 0:
        g.db_corrupt = True
    else:
        g.db_corrupt = False
        settings = g.db.get_settings()
        g.std_args = {"settings": settings, "session": session}


@app.route("/")
def index():
    if g.db_corrupt:
        return render_template(
            "corrupt.jinja2",
            missing=g.missing_tables,
            filename=app.config.get("DATABASE_FILE")
        )
    else:
        announcements = g.db.get_active_announcements()
        return render_template(
            "main.jinja2",
            announcements=announcements,
            **g.std_args
        )


@app.route("/list")
@login_required
def list_announcements():
    announcements = g.db.get_all_announcements()
    return render_template(
        "list.jinja2",
        announcements=announcements,
        **g.std_args
    )


@app.route("/edit")
@app.route("/edit/<id>")
def edit_announcement(id=None):
    announcement = g.db.get_announcement(id)
    return render_template(
        "edit.jinja2",
        announcement=announcement,
        **g.std_args
    )


# Login, Logout
@app.route("/login", methods=['GET', 'POST'])
def login_page():
    error = None
    username = None
    authenticators = {"AD": AD, "dummy": dummy_auth, "eDirectory": EDirectory}
    if request.method == 'POST':
        # attempt to authenticate
        auth = Authenticator(
            authenticators[app.config.get("AUTH_BACKEND")],
            **app.config.get("LDAP_CONFIG")
        )
        if auth.check(request.form['username'], request.form['password']):
            session['auth'] = True
            session['username'] = request.form['username']
            session['user_realname'] = auth.get_user_name()
            session['user_email'] = auth.get_user_email()
            return redirect(url_for("index"))
        else:
            username = request.form['username']
            error = "Login Failed"
    return render_template("login.jinja2", error=error, username=username)


@app.route("/logout")
@login_required
def logout():
    session['auth'] = False
    session['username'] = None
    session['user_realname'] = None
    return redirect(url_for("index"))


@app.route("/settings")
@login_required
def settings():
    debug(settings)
    return render_template("settings.jinja2", **g.std_args)


@app.route("/initialize")
def initialize_database():
    return render_template(
        "initialize_form.jinja2",
        filename=app.config['DATABASE_FILE'],
        **g.std_args
    )


@app.route("/post/<callback>", methods=["POST"])
def post(callback):
    callbacks = {
        "announcement": g.db.save_announcement,
        "delete": g.db.delete_announcement,
        "settings": g.db.save_settings,
        "initialize": g.db.do_initialize_db
    }
    if callback not in callbacks.keys() or not session.get("auth"):
        abort(403)
    else:
        result = callbacks.get(callback)(
            request.form, username=session.get("username")
        )
        if request.form.get("_redirect_"):
            return redirect(request.form.get("_redirect_"))
        else:
            return result


@app.route("/json/<callback>")
def json_get(callback):
    callbacks = {
        }
    if callback not in callbacks.keys():
        abort(403)
    else:
        result = callbacks.get(callback)(**request.args.to_dict(flat=True))
        return json.dumps(result)

if __name__ == "__main__":
    app.debug = True
    host = app.config.get("HOST", 'localhost')
    port = app.config.get("PORT", 5000)
    app.run(host=host, port=port)
    print("PyStump is running at http://{}:{}".format(host, port))
