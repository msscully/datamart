from tests import TestCase
from werkzeug.urls import url_quote
from datamart.models import Dimension

class TestDimensions(TestCase):

    def test_show_dimensions_anon(self):
        response = self.client.get('/dimensions/', follow_redirects=False)
        new_location='/login?next=%s' % url_quote('/dimensions/', safe='')
        self.assertRedirects(response, location=new_location)
        response = self.client.get('/dimensions/', follow_redirects=True)
        assert 'Please log in to access this page.' in response.data
        self.assertTemplateUsed(name='login.html')

    def test_show_dimensions_admin(self):
        self.login('admin@example.com','123456')
        response = self._test_get_request('/dimensions/', 'dimensions.html')
        assert 'Please log in to access this page.' not in response.data
        self.logout()

    def test_dimension_add(self):
        self.login('admin@example.com', '123456')
        self._test_get_request('/dimensions/add/', 'dimension_edit.html')
        data = {
            'name': 'surprise',
            'description': "it's a monkey",
            'data_type': 'String'
        }
        response = self.client.post('/dimensions/add/', data=data)
        assert 'Please fix errors and resubmit.' not in response.data
        new_dim = Dimension.query.filter_by(name=data['name'])
        assert new_dim.count() == 1
        self.logout()

    def test_dimension_edit(self):
        self.login('admin@example.com', '123456')
        data = {
            'name': 'surprise',
            'description': "it's a monkey",
            'data_type': 'String'
        }
        new_dim = Dimension.query.filter_by(name=data['name'])
        if new_dim.count() != 1:
            response = self.client.post('/dimensions/add/', data=data)
            assert 'Please fix errors and resubmit.' not in response.data
            new_dim = Dimension.query.filter_by(name=data['name'])

        assert new_dim.count() == 1
        data['name'] = 'surprise2'
        response = self.client.post('/dimensions/%s/edit/' % new_dim.first().id, data=data)
        assert 'Please fix errors and resubmit.' not in response.data
        new_dim = Dimension.query.filter_by(name=data['name'])
        assert new_dim.count() == 1
        response = self.client.get('/dimensions/')
        assert data['name'] in response.data
        self.logout()
