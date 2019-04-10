"""
Notebook package initializer.

Ty Dunn <ty@tydunn.com>
"""
import flask

app = flask.Flask(__name__)

app.config.from_object('notebook.config')

import notebook.api
import notebook.model
