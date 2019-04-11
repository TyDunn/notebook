"""
Notebook package initializer.

Ty Dunn <ty@tydunn.com>
"""
import flask
import notebook.api
import notebook.model

APP = flask.Flask(__name__)

APP.config.from_object('notebook.config')
