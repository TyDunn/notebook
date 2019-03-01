"""
Notebook package initializer.

Ty Dunn <tydunn@umich.edu>
"""
import flask

app = flask.Flask(__name__)

app.config.from_object('notebook.config')

app.config.from_envvar('NOTEBOOK_SETTINGS', silent=True)

import notebook.api
import notebook.model
