from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore, \
            UserMixin, RoleMixin, login_required
from flask_mail import Mail
from flask_debugtoolbar import DebugToolbarExtension


app = Flask(__name__)
app.config.from_object('config')
app.config.from_envvar('DATAMART_APP_SETTINGS')

mail = Mail(app)

toolbar = DebugToolbarExtension(app)

db = SQLAlchemy(app)

# Configure Flask-Security
app.config['SECURITY_REGISTERABLE'] = False
#app.config['SECURITY_CONFIRMABLE'] = True
app.config['SECURITY_TRACKABLE'] = True
#app.config['SECURITY_REGISTER_URL'] = '/create_account'
# Setup Flask-Security
import datamart.models
user_datastore = SQLAlchemyUserDatastore(db, datamart.models.User, datamart.models.Role)
security = Security(app, user_datastore)

import datamart.views
import datamart.api
import admin
