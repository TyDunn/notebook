"""
Notebook package initializer.

Ty Dunn <ty@tydunn.com>
"""
import flask

app = flask.Flask(__name__) # pylint: disable=invalid-name

app.config.from_object('notebook.config')

import notebook.api # noqa: E402  pylint: disable=wrong-import-position
import notebook.model # noqa: E402  pylint: disable=wrong-import-position
