from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask.ext.mail import Mail
mail = Mail()

from flask.ext.uploads import UploadSet
data_files = UploadSet('data',extensions=('txt','csv'))

from flask.ext.security import Security
security = Security()
