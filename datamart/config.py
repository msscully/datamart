import os
from .utils import make_dir
from .utils import INSTANCE_FOLDER_PATH

class BaseConfig(object):

    PROJECT = "datamart"

    # Get app root path, also can use flask.root_path.
    # ../../config.py
    PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    SSLIFY_ENABLED = True
    DEBUG = False
    TESTING = False

    ADMINS = ['oscully@gmail.com']

    # http://flask.pocoo.org/docs/quickstart/#sessions
    SECRET_KEY = "\xdb\xf1\xf6\x14\x88\xd4i\xda\xbc/E'4\x7f`iz\x98r\xb9s\x1c\xca\xcd"

    make_dir(INSTANCE_FOLDER_PATH)
    LOG_FOLDER = os.path.join(INSTANCE_FOLDER_PATH, 'logs')
    make_dir(LOG_FOLDER)

    # Fild upload, should override in production.
    # Limited the maximum allowed payload to 16 megabytes.
    # http://flask.pocoo.org/docs/patterns/fileuploads/#improving-uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOAD_FOLDER = os.path.join(INSTANCE_FOLDER_PATH, 'uploads')
    make_dir(UPLOAD_FOLDER)
    UPLOADS_DEFAULT_DEST = UPLOAD_FOLDER


    # Configure Flask-Security
    SECURITY_REGISTERABLE = False
    SECURITY_CONFIRMABLE = False
    SECURITY_TRACKABLE = True
    SECURITY_LOGIN_USER_TEMPLATE = 'login.html'
    # Disallow account creation.
    #SECURITY_REGISTER_URL = '/create_account'

class DefaultConfig(BaseConfig):

    DEBUG = True

    WTF_CSRF_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # Flask-Sqlalchemy: http://packages.python.org/Flask-SQLAlchemy/config.html
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://datamart:datamart@localhost/datamart'

    # Flask-mail: http://pythonhosted.org/flask-mail/
    # https://bitbucket.org/danjac/flask-mail/issue/3/problem-with-gmails-smtp-server
    MAIL_DEBUG = DEBUG
    MAIL_SERVER = 'localhost' #'smtp.gmail.com'
    MAIL_PORT = 1025
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    # Should put MAIL_USERNAME and MAIL_PASSWORD in production under instance folder.
    MAIL_USERNAME = 'gmail_username'
    MAIL_PASSWORD = 'gmail_password'
    DEFAULT_MAIL_SENDER = '%s@gmail.com' % MAIL_USERNAME
    SECURITY_PASSWORD_HASH = 'bcrypt'
    SECURITY_FLASH_MESSAGES = True

class TestConfig(BaseConfig):
    SSLIFY_ENABLED = False
    DEBUG = False
    TESTING = False #If true turns off authentication
    DISABLE_LOGGING = True
    WTF_CSRF_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    MAIL_DEBUG = DEBUG
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 1025
    #MAIL_USERNAME = 'username'
    #MAIL_PASSWORD = 'password'

    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://datamart:datamart@localhost/datamart_test'
    SECURITY_PASSWORD_HASH = 'plaintext'
    SECURITY_FLASH_MESSAGES = True
