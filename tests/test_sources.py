from tests import TestCase
from werkzeug.urls import url_quote
from datamart.models import Source
from datamart.models import Dimension
from datamart.models import Variable

class TestSources(TestCase):

    def test_show_sources_anon(self):
        response = self.client.get('/sources/', follow_redirects=False)
        new_location='/login?next=%s' % url_quote('/sources/', safe='')
        self.assertRedirects(response, location=new_location)
        response = self.client.get('/sources/', follow_redirects=True)
        assert 'Please log in to access this page.' in response.data
        self.assertTemplateUsed(name='login.html')

    def test_show_sources_admin(self):
        self.login('admin@example.com','123456')
        response = self._test_get_request('/sources/', 'sources.html')
        assert 'Please log in to access this page.' not in response.data
        self.logout()

    def test_source_add(self):
        self.login('admin@example.com', '123456')
        self._test_get_request('/sources/add/', 'source_edit.html')
        data = {
            'name': 'height',
            'description': "Subject height",
            'url': 'http://example.com'
        }
 
        new_var = Source.query.filter_by(name=data['name'])
        if new_var.count() != 1:
            response = self.client.post('/sources/add/', data=data)
            assert 'Please fix errors and resubmit.' not in response.data
            new_var = Source.query.filter_by(name=data['name'])
        assert new_var.count() == 1;
        self.logout()

    def add_dimension(self):
        """ Add a dimension to testdb. Must be logged in w/ permissions. """
        dim_name = 'Height / Length in feet'
        dim = Dimension.query.filter_by(name=dim_name)
        new_dim = None
        if dim.count() == 0:
            new_dim = Dimension()
            new_dim.name = dim_name
            new_dim.description = "Height / Length in feet"
            new_dim.data_type = "Float"
            self.db.session.add(new_dim)
            self.db.session.commit()
        else:
            new_dim = dim.first()
        return new_dim

    def add_variable(self):
        """ Add a variable to testdb. Must be logged in w/ permissions. """
        new_dim = self.add_dimension()
        var_name = 'Height / Length in feet'
        var = Variable.query.filter_by(name=var_name)
        new_var = None
        if var.count() == 0:
            new_var = Variable()
            new_var.name = var_name
            new_var.description = "Height / Length in feet"
            new_var.dimension = new_dim
            self.db.session.add(new_var)
            self.db.session.commit()
        else:
            new_var = var.first()
        return new_var

    def add_source(self):
        """ Add a source to testdb. Must be logged in w/ permissions. """
        new_source = self.add_variable()
 
        source_data = {
            'name': 'First Visit',
            'description': "First Visit",
            'url': 'http://example.com',
            'variables': [new_source.id]
        }
        response = self.client.post('/sources/add/', data=source_data)
        assert 'Please fix errors and resubmit.' not in response.data
        new_source = Source.query.filter_by(name=source_data['name'])
        return new_source, source_data

    def add_variable_to_source(self, source_id, var_id):
        source = Source.query.get(source_id)
        variables = [str(r.id) for r in source.variables]
        variables.append(str(var_id))
        source_data = {
            'name': source.name,
            'description': source.description,
            'url': source.url,
            'variables': variables
        }
        response = self.client.post('/sources/%s/edit/' % source_id,
                                    data=source_data, follow_redirects=True)
        assert 'Please fix errors and resubmit.' not in response.data
        return response

    def test_source_edit(self):
        self.login('admin@example.com', '123456')
        new_source, source_data = self.add_source()
        assert new_source.count() == 1;
        source_data['name'] = 'Inf Event'
        response = self.client.post('/sources/%s/edit/' % new_source.first().id, data=source_data)
        assert 'Please fix errors and resubmit.' not in response.data
        new_source = Source.query.filter_by(name=source_data['name'])
        assert new_source.count() == 1;
        response = self.client.get('/sources/')
        assert 'Source updated' in response.data
        assert 'Please fix errors and resubmit' not in response.data
        self.logout()
