from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object('config')
app.config.from_envvar('DATAMART_APP_SETTINGS')
Bootstrap(app)

db = SQLAlchemy(app)
