from .extensions import db
from .extensions import mail
from .extensions import data_files
from .extensions import security
from . import models
from .api import manager
from .api import preprocessors
from .api import auth_func
from .api import get_single_variable_preprocessor
from .api import get_many_variables_preprocessor
from .api import admin_only_proprocessors
from .jinja_filters import remove_invalid_vars
from .config import DefaultConfig
from .utils import INSTANCE_FOLDER_PATH
from flask.ext.uploads import configure_uploads
from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask
from flask import render_template
from flask.ext.security import SQLAlchemyUserDatastore
from .views import datamart
from .views import render_template_with_login
import os

DEFAULT_BLUEPRINTS = (
    datamart,
)

def create_app(config=None, app_name=None, blueprints=None):
    """Create a Flask app."""

    if app_name is None:
        app_name = DefaultConfig.PROJECT
    if blueprints is None:
        blueprints = DEFAULT_BLUEPRINTS

    app = Flask(app_name, instance_path=INSTANCE_FOLDER_PATH, instance_relative_config=True)
    configure_app(app, config)
    configure_blueprints(app, blueprints)
    configure_extensions(app)
    configure_logging(app)
    configure_error_handlers(app)
    configure_jinja_filters(app)
    configure_api(app)

    return app

def configure_app(app, config=None):
    """Different ways of configurations."""

    # http://flask.pocoo.org/docs/api/#configuration
    app.config.from_object(DefaultConfig)

    # http://flask.pocoo.org/docs/config/#instance-folders
    app.config.from_pyfile('production.cfg', silent=True)

    if config:
        app.config.from_object(config)

    if app.config["DEBUG"]:
        toolbar = DebugToolbarExtension(app)

    # Use instance folder instead of env variables to make deployment easier.
    #app.config.from_envvar('%s_APP_CONFIG' % DefaultConfig.PROJECT.upper(), silent=True)

def configure_extensions(app):
    # flask-sqlalchemy
    db.init_app(app)

    # flask-mail
    mail.init_app(app)

    # SSLify can't be defined without an app
    from flask_sslify import SSLify
    if app.config["SSLIFY_ENABLED"]:
        sslify = SSLify(app)

    # Setup Flask-Security
    # Flask-Security has some weirdness when using factory style.
    # See https://github.com/mattupstate/flask-security/issues/141
    user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
    security._state = security.init_app(app, datastore=user_datastore)
    security.datastore = user_datastore

    # Uploaded data files
    configure_uploads(app, (data_files))

def configure_logging(app):
    """Configure file(info) and email(error) logging."""

    if app.debug or app.testing:
        # Skip debug and test mode. Just check standard output.
        return

    import logging
    from logging.handlers import SMTPHandler

    # Set info level on logger, which might be overwritten by handers.
    # Suppress DEBUG messages.
    app.logger.setLevel(logging.INFO)

    info_log = os.path.join(app.config['LOG_FOLDER'], 'info.log')
    info_file_handler = logging.handlers.RotatingFileHandler(info_log, maxBytes=100000, backupCount=10)
    info_file_handler.setLevel(logging.INFO)
    info_file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]')
    )
    app.logger.addHandler(info_file_handler)

    # Testing
    #app.logger.info("testing info.")
    #app.logger.warn("testing warn.")
    #app.logger.error("testing error.")

    mail_handler = SMTPHandler((app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                               app.config['MAIL_USERNAME'],
                               app.config['ADMINS'],
                               'O_ops... %s failed!' % app.config['PROJECT'],
                               (app.config['MAIL_USERNAME'],
                                app.config['MAIL_PASSWORD']))
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]')
    )
    app.logger.addHandler(mail_handler)

def configure_error_handlers(app):

    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template_with_login("errors/forbidden_page.html"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template_with_login("errors/page_not_found.html"), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template_with_login("errors/server_error.html"), 500

def configure_jinja_filters(app):
    app.jinja_env.filters['remove_invalid_vars'] = remove_invalid_vars

def configure_api(app):
    # Flask Restless API
    RESULTS_PER_PAGE = 50
    MAX_RESULTS_PER_PAGE = 10000
    manager.init_app(app, flask_sqlalchemy_db=db)

    manager.create_api(models.Dimension, 
                       methods=['GET', 'POST', 'DELETE', 'PUT'], 
                       results_per_page=RESULTS_PER_PAGE,
                       preprocessors=preprocessors)
    manager.create_api(models.Variable, 
                       methods=['GET', 'POST', 'DELETE', 'PUT'], 
                       results_per_page=RESULTS_PER_PAGE,
                       preprocessors={'GET_SINGLE':[auth_func, get_single_variable_preprocessor],
                                      'GET_MANY':[auth_func, get_many_variables_preprocessor]
                                     })
    manager.create_api(models.Facts, 
                       methods=['GET', 'DELETE'],
                       results_per_page=RESULTS_PER_PAGE,
                       preprocessors=preprocessors)
    manager.create_api(models.Role, 
                       methods=['GET', 'POST', 'DELETE', 'PUT'],
                       results_per_page=RESULTS_PER_PAGE,
                       preprocessors=admin_only_proprocessors)
    manager.create_api(models.Event, 
                       methods=['GET', 'POST', 'DELETE', 'PUT'],
                       results_per_page=RESULTS_PER_PAGE,
                       preprocessors=preprocessors)
    manager.create_api(models.Source, 
                       methods=['GET', 'POST', 'DELETE', 'PUT'],
                       results_per_page=RESULTS_PER_PAGE,
                       preprocessors=preprocessors)
    manager.create_api(models.Subject, 
                       methods=['GET', 'POST', 'DELETE', 'PUT'],
                       results_per_page=RESULTS_PER_PAGE,
                       preprocessors=admin_only_proprocessors)
    manager.create_api(models.ExternalID, 
                       methods=['GET', 'POST', 'DELETE', 'PUT'],
                       results_per_page=RESULTS_PER_PAGE,
                       preprocessors=preprocessors)

def configure_blueprints(app, blueprints):
    """Configure blueprints in views."""

    for blueprint in blueprints:
        app.register_blueprint(blueprint)
