from tests import TestCase
from werkzeug.urls import url_quote
from datamart.models import User
from flask.ext.security import current_user

class TestUsers(TestCase):

    def test_show_users_anon(self):
        """Verify unathenticated users can't see the users page."""
        response = self.client.get('/users/', follow_redirects=False)
        new_location='/login?next=%s' % url_quote('/users/', safe='')
        self.assertRedirects(response, location=new_location)
        response = self.client.get('/users/', follow_redirects=True)
        assert 'Please log in to access this page.' in response.data
        self.assertTemplateUsed(name='login.html')

    def test_show_roles_non_admin(self):
        """Make sure logged in non-admin users can't see the users page."""
        self.login('demo@example.com','123456')
        assert current_user.is_authenticated
        response = self._test_get_request('/users/', 'index.html', follow_redirects=True)
        assert 'Permission denied' in response.data
        self.logout()

    def test_show_users_admin(self):
        """Verify admin can see users page."""
        self.login('admin@example.com','123456')
        response = self._test_get_request('/users/', 'users.html')
        assert 'Please log in to access this page.' not in response.data
        self.logout()

    def test_user_add(self):
        """Adds a user using a post to /users/add/"""
        self.login('admin@example.com', '123456')
        self._test_get_request('/users/add/', 'user_edit.html')
        data = {
            'username': 'Ruler',
            'email': "ruler@example.com",
            'password': "123456",
            'is_admin': True,
            'active': True
        }
        response = self.client.post('/users/add/', data=data)
        assert 'Please fix errors and resubmit.' not in response.data
        new_user = User.query.filter_by(username=data['username'])
        assert new_user.count() == 1
        self.logout()

    def test_user_edit(self):
        """Test editing a user using webforms.

           Add a user, chance the name and post to /users/<id>/edit/ and verify
        results.
        """
        self.login('admin@example.com', '123456')
        data = {
            'username': 'peon',
            'email': "peon@example.com",
            'password': '123456',
            'active': True
        }
        new_user = User.query.filter_by(username=data['username'])
        if new_user.count() != 1:
            response = self.client.post('/users/add/', data=data)
            assert 'Please fix errors and resubmit.' not in response.data
            new_user = User.query.filter_by(username=data['username'])
        assert new_user.count() == 1
        data['username'] = 'Peon'
        response = self.client.post('/users/%s/edit/' % new_user.first().id, data=data)
        assert 'Please fix errors and resubmit.' not in response.data
        new_user = User.query.filter_by(username=data['username'])
        assert new_user.count() == 1
        response = self.client.get('/users/')
        assert data['username'] in response.data
        self.logout()
