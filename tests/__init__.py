# -*- coding: utf-8 -*-
"""
    Unit Tests
    ~~~~~~~~~~

    Define TestCase as base class for unit tests.
    Ref: http://packages.python.org/Flask-Testing/

    Requires datamart_test db to exist with the hstore extension.
    createdb --owner=datamart datamart_test
    psql -d datamart_test -c "CREATE EXTENSION HSTORE"
"""

from flask.ext.testing import TestCase as Base, Twill

from datamart import create_app
from datamart.models import User
from datamart.config import TestConfig
from datamart.extensions import db

def init_package_data():
    demo = User(
        username=u'demo',
        email=u'demo@example.com',
        password=u'123456',
        active=True,
        is_admin=False,
    )
    admin = User(
        username=u'admin',
        email=u'admin@example.com',
        password=u'123456',
        active=True,
        is_admin=True,
    )
    db.session.add(demo)
    db.session.add(admin)
    db.session.commit()

def populate_db(app):
    # db setup seems odd, taken from:
    # http://flask.pocoo.org/mailinglist/archive/2010/8/30/sqlalchemy-init-app-problem/#0b707d43d8713f2b6131b5b9210f0c79
    db.app = app
    db.init_app(app)
    db.drop_all()
    db.create_all()
    init_package_data()

def setup_package():
    """
       Code that is run once before all tests in this package.
    """
    app = create_app(TestConfig)
    populate_db(app)

def teardown_package():
    """
       Code that is run once after all tests in this package.
    """
    #Clean db session and drop all tables.
    db.session.remove()
    db.drop_all()


class TestCase(Base):
    """Base TestClass for your application."""

    def create_app(self):
        """Create and return a testing flask app."""

        app = create_app()
        self.twill = Twill(app, port=3000)
        return app

    #def init_data(self):
    #    demo = User(
    #        username=u'demo',
    #        email=u'demo@example.com',
    #        password=u'123456',
    #        active=True,
    #        is_admin=False,
    #    )
    #    admin = User(
    #        username=u'admin',
    #        email=u'admin@example.com',
    #        password=u'123456',
    #        active=True,
    #        is_admin=True,
    #    )
    #    db.session.add(demo)
    #    db.session.add(admin)
    #    db.session.commit()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def login(self, username, password):
        data = {
            'login': username,
            'password': password,
        }
        response = self.client.post('/login', data=data, follow_redirects=True)
        return response

    def _logout(self):
        response = self.client.get('/logout')
        self.assertRedirects(response, location='/')

    def _test_get_request(self, endpoint, template=None):
        response = self.client.get(endpoint)
        self.assert_200(response)
        if template:
            self.assertTemplateUsed(name=template)
        return response
