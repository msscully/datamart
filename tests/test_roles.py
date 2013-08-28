from tests import TestCase
from werkzeug.urls import url_quote
from datamart.models import Role
from flask.ext.security import current_user

class TestRoles(TestCase):

    def test_show_roles_anon(self):
        """Verify unathenticated users can't see the roles page."""
        response = self.client.get('/roles/', follow_redirects=False)
        new_location='/login?next=%s' % url_quote('/roles/', safe='')
        self.assertRedirects(response, location=new_location)
        response = self.client.get('/roles/', follow_redirects=True)
        assert 'Please log in to access this page.' in response.data
        self.assertTemplateUsed(name='login.html')

    def test_show_roles_non_admin(self):
        """Make sure logged in non-admin users can't see the roles page."""
        self.login('demo@example.com','123456')
        assert current_user.is_authenticated
        response = self._test_get_request('/roles/', 'index.html', follow_redirects=True)
        assert 'Permission denied' in response.data
        self.logout()

    def test_show_roles_admin(self):
        """Make sure logged in admins can see the roles page."""
        self.login('admin@example.com','123456')
        response = self._test_get_request('/roles/', 'roles.html')
        assert 'Please log in to access this page.' not in response.data
        self.logout()

    def test_role_add(self):
        """Adds a role using a post to /roles/add/"""
        self.login('admin@example.com', '123456')
        self._test_get_request('/roles/add/', 'role_edit.html')
        data = {
            'name': 'Ruler',
            'description': "of all I survey.",
        }
        response = self.client.post('/roles/add/', data=data)
        assert 'Please fix errors and resubmit.' not in response.data
        new_role = Role.query.filter_by(name=data['name'])
        assert new_role.count() == 1
        self.logout()

    def test_role_edit(self):
        """Edit a role using webforms."""
        self.login('admin@example.com', '123456')
        data = {
            'name': 'Ruler',
            'description': "of all I survey.",
        }
        new_role = Role.query.filter_by(name=data['name'])
        if new_role.count() != 1:
            response = self.client.post('/roles/add/', data=data)
            assert 'Please fix errors and resubmit.' not in response.data
            new_role = Role.query.filter_by(name=data['name'])
        assert new_role.count() == 1
        data['name'] = 'Peon'
        response = self.client.post('/roles/%s/edit/' % new_role.first().id, data=data)
        assert 'Please fix errors and resubmit.' not in response.data
        new_role = Role.query.filter_by(name=data['name'])
        assert new_role.count() == 1
        response = self.client.get('/roles/')
        assert data['name'] in response.data
        self.logout()
