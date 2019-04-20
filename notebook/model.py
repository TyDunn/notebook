# env/bin/python

"""
Notebook database API.

Ty Dunn <ty@tydunn.com>
"""

import sqlite3
import flask
import notebook

def dict_factory(cursor, row):
    """Convert database row objects to a dictionary."""
    output = {}
    for idx, col in enumerate(cursor.description):
        output[col[0]] = row[idx]
    return output


def get_db():
    """Open a new database connection."""
    if not hasattr(flask.g, 'sqlite_db'):
        flask.g.sqlite_db = sqlite3.connect(
            notebook.app.config['DATABASE_FILENAME'])
        flask.g.sqlite_db.row_factory = dict_factory
        flask.g.sqlite_db.execute("PRAGMA foreign_keys = ON")

    return flask.g.sqlite_db


def query_db(query, args=(), one=False):
    """Submit query to the database."""
    cur = get_db().execute(query, args)
    val = cur.fetchall()
    cur.close()
    return (val[0] if val else None) if one else val


def update_db(query, args=()):
    """Update the database."""
    database = get_db()
    cur = database.execute(query, args)
    database.commit()
    cur.close()


@notebook.app.teardown_appcontext
def close_db():
    """Close the database at the end of the request."""
    if hasattr(flask.g, 'sqlite_db'):
        flask.g.sqlite_db.commit()
        flask.g.sqlite_db.close()
