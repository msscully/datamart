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


class TestCase(Base):
    """Base TestClass for your application."""

    def create_app(self):
        """Create and return a testing flask app."""

        app = create_app(TestConfig)
        self.twill = Twill(app, port=3000)
        return app

    def init_data(self):
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

    def setUp(self):
        """Reset all tables before testing."""

        db.drop_all()
        db.create_all()
        self.init_data()

    def tearDown(self):
        """Clean db session and drop all tables."""

        db.session.commit()
        db.drop_all()

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
