from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.config.from_object('config')
app.config.from_envvar('DATAMART_APP_SETTINGS')

toolbar = DebugToolbarExtension(app)

db = SQLAlchemy(app)

import datamart.models
import datamart.views
import datamart.api
#import admin
