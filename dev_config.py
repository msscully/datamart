DEBUG = True
DEBUG_TB_INTERCEPT_REDIRECTS = False
SECRET_KEY = "\xdb\xf1\xf6\x14\x88\xd4i\xda\xbc/E'4\x7f`iz\x98r\xb9s\x1c\xca\xcd"
CSRF_ENABLED = True
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://datamart:datamart@localhost/datamart'
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
#MAIL_USE_SSL = True
#MAIL_USERNAME = 'username'
#MAIL_PASSWORD = 'password'
SECURITY_PASSWORD_HASH = 'plaintext'

UPLOADS_DEFAULT_DEST = '/Users/mscully/contracts/predict/datamart/uploads'
