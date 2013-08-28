from tests import TestCase
from werkzeug.urls import url_quote
from datamart.models import Variable
from datamart.models import Dimension
from datamart.models import User
from datamart.models import Role
from flask import url_for

class TestVariables(TestCase):

    def test_show_variables_anon(self):
        response = self.client.get('/variables/', follow_redirects=False)
        new_location='/login?next=%s' % url_quote('/variables/', safe='')
        self.assertRedirects(response, location=new_location)
        response = self.client.get('/variables/', follow_redirects=True)
        assert 'Please log in to access this page.' in response.data
        self.assertTemplateUsed(name='login.html')

    def test_show_variables_non_admin(self):
        """Make sure logged in users can see the variables page."""
        self.login('demo@example.com','123456')
        response = self._test_get_request('/variables/', 'variables.html')
        assert 'Please log in to access this page.' not in response.data
        self.logout()

    def test_show_variables_admin(self):
        """Make sure logged in admins can see the variables page."""
        self.login('admin@example.com','123456')
        response = self._test_get_request('/variables/', 'variables.html')
        assert 'Please log in to access this page.' not in response.data
        self.logout()

    def test_variable_add(self):
        self.login('admin@example.com', '123456')
        self._test_get_request('/variables/add/', 'variable_edit.html')
        new_var, variable_data = self.add_variable()
        assert new_var.count() == 1
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
 
        variable_data = {
            'name': 'length',
            'description': "Subject height",
            'dimension': new_dim.id
        }
        new_var = Variable.query.filter_by(name=variable_data['name'])
        if new_var.count() != 1:
            response = self.client.post('/variables/add/', data=variable_data)
            assert 'Please fix errors and resubmit.' not in response.data
            new_var = Variable.query.filter_by(name=variable_data['name'])
        return new_var, variable_data

    def add_role_to_variable(self, var_id, role_id):
        var = Variable.query.get(var_id)
        roles = [str(r.id) for r in var.roles]
        roles.append(str(role_id))
        variable_data = {
            'name': var.name,
            'description': var.description,
            'dimension': var.dimension.id,
            'roles': roles
        }
        response = self.client.post('/variables/%s/edit/' % var_id,
                                    data=variable_data, follow_redirects=True)
        assert 'Please fix errors and resubmit.' not in response.data
        return response

    def add_role_to_user(self, user_id, role):
        user = User.query.get(user_id)
        user.roles.append(role)

        self.db.session.add(user)
        self.db.session.commit()

    def test_variable_edit(self):
        self.login('admin@example.com', '123456')
        new_var, variable_data = self.add_variable()
        assert new_var.count() == 1;
        variable_data['name'] = 'Standing Length'
        response = self.client.post('/variables/%s/edit/' % new_var.first().id, 
                                    data=variable_data,
                                    headers={'Referer': url_for('datamart.variables_view')},
                                   follow_redirects=True)
        assert 'Variable updated' in response.data
        assert 'Please fix errors and resubmit.' not in response.data
        new_var = Variable.query.filter_by(name=variable_data['name'])
        assert new_var.count() == 1;
        self.logout()

    def test_variable_by_role(self):
        self.login('admin@example.com', '123456')
        new_var, variable_data = self.add_variable()
        assert new_var.count() == 1
        new_role = Role(name='AdminRole', description='AdminRole')
        self.db.session.add(new_role)
        self.db.session.commit()
        role_id = new_role.id
        response = self.add_role_to_variable(new_var.first().id, role_id)
        assert 'Variable updated' in response.data
        assert 'Please fix errors and resubmit' not in response.data
        new_var = Variable.query.join(Role, Variable.roles).filter(Role.id == role_id)
        assert new_var.count() == 1;
        var_name = new_var.first().name
        response = self.client.get('/variables/')
        assert var_name not in response.data
        assert new_role.name not in response.data
        user = User.query.filter_by(username='admin')
        user_id = user.first().id
        self.add_role_to_user(user_id, new_role)
        response = self.client.get('/variables/')
        assert new_role.name in response.data
        assert var_name in response.data
        self.logout()
        self.login('demo@example.com', '123456')
        response = self.client.get('/variables/')
        assert new_role.name not in response.data
        assert var_name not in response.data
        self.logout()
        self.login('admin@example.com', '123456')
        user = User.query.filter_by(username='demo')
        user_id = user.first().id
        self.add_role_to_user(user_id, new_role)
        response = self.client.get('/variables/')
        assert new_role.name in response.data
        assert var_name in response.data
        self.logout()
