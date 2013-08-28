from tests import TestCase
from datamart.models import Variable
from datamart.models import Dimension
from datamart.models import Role
from datamart.models import User
import base64
import json

class TestVariableAPI(TestCase):
    """Tests the Variable API"""

    @classmethod
    def setup_class(self):
        super(TestVariableAPI, self).setup_class()
        self.dim1 = Dimension(name='dim1', description='dim1', data_type='String')
        self.role1 = Role(name='Admin', description='Admin')
        self.db.session.add(self.dim1)
        self.db.session.add(self.role1)
        self.db.session.flush()
        users = User.query.all()
        for user in users:
            roles = [r for r in user.roles]
            roles.append(self.role1)
            user.roles = roles
            self.db.session.add(user)
        var1 = Variable(name='var1', description='var1',
                        dimension_id=self.dim1.id, roles=[self.role1])
        var2 = Variable(name='var2', description='var2', 
                        dimension_id=self.dim1.id, roles=[self.role1])
        self.db.session.add(var1)
        self.db.session.add(var2)
        self.db.session.flush()
        self.db.session.commit()

    def test_anon_get_variables(self):
        """Get /api/variable with wrong username & password."""
        auth = 'Basic ' + base64.b64encode('WRONG@example.com:123456')
        response = self.client.get('/api/variable',
                                   headers={'Authorization': auth }
                                  )
        assert response.status_code == 403

        auth = 'Basic ' + base64.b64encode('demo@example.com:WRONG')
        response = self.client.get('/api/variable',
                                   headers={'Authorization': auth }
                                  )
        assert response.status_code == 403


    def test_admin_get_variables(self):
        """Get /api/variable as admin."""
        auth = self.admin_auth
        response = self.client.get('/api/variable',
                                   headers={'Authorization': auth }
                                  )
        assert response.status_code == 200
        assert 'total_pages' in response.data
        rd = json.loads(response.data)
        assert rd['num_results'] >= 2

    def test_non_admin_get_variables(self):
        """Get /api/variable as non-admin.
        
           Since demo has the required roles the response should include 
           some variables.
        """
        auth = self.demo_auth
        response = self.client.get('/api/variable',
                                   headers={'Authorization': auth }
                                  )
        assert response.status_code == 200
        resp = json.loads(response.data)
        assert resp['num_results'] > 0

    def test_get_variables_wrong_role(self):
        """Get /api/variable as demo without correct role.

           Variables and users have roles associated with them and if a user
           doesn't have any roles overlapping with a variables roles that
           variable should not be displayed to them.
        """
        var = Variable(name='nope', description='not a chance', 
                       dimension=self.dim1, roles=[])
        self.db.session.add(var)
        self.db.session.commit()
        auth = self.demo_auth
        response = self.client.get('/api/variable',
                                   headers={'Authorization': auth }
                                  )
        assert response.status_code == 200
        assert var.description not in response.data

    def test_add_variable(self):
        """Adding a variable using /api/variable."""
        auth = self.admin_auth
        data = {
            'name': 'weight',
            'description': 'how much a subject weighs',
            'dimension_id': self.dim1.id,
            'roles': [{'id': str(self.role1.id)}],
            'in_use': True
        }

        response = self.client.post('/api/variable',
                                    headers={'Authorization': auth,
                                            },
                                    content_type='application/json',
                                    data=json.dumps(data)
                                  )
        assert response.status_code == 201
        assert data['description'] in response.data

        response = self.client.get('/api/variable',
                                   headers={'Authorization': auth }
                                  )
        assert response.status_code == 200
        assert 'total_pages' in response.data
        assert data['description'] in response.data

    def test_admin_get_var_id(self):
        """Get a variable at /api/variable/<ID> as admin."""
        auth = self.admin_auth
        response = self.client.get('/api/variable',
                                   headers={'Authorization': auth }
                                  )
        assert response.status_code == 200
        var = json.loads(response.data)['objects'][0]
        response = self.client.get('/api/variable/%s' % var['id'],
                                   headers={'Authorization': auth }
                                  )
        assert var['name'] in response.data
        assert var['description'] in response.data
        assert 'total_pages' not in response.data

 
    def test_put_variable(self):
        """Update Variable at /api/variable/<ID> using PUT"""
        auth = self.admin_auth
        response = self.client.get('/api/variable',
                                   headers={'Authorization': auth }
                                  )
        var = json.loads(response.data)['objects'][0]
        data = dict(var)
        data.pop('id', None)
        data['name'] = 'barrels of monkeys'
        response = self.client.put('/api/variable/%s' % var['id'],
                                   content_type='application/json',
                                   headers={'Authorization': auth },
                                   data=json.dumps(data)
                                  )
        assert response.status_code == 200

    def test_delete_variable(self):
        """Delete variable using /api/variable/<ID>"""
        auth = self.admin_auth
        response = self.client.get('/api/variable',
                                   headers={'Authorization': auth }
                                  )
        var = json.loads(response.data)['objects'][0]
        response = self.client.delete('/api/variable/%s' % var['id'],
                                   headers={'Authorization': auth },
                                  )
        assert response.status_code == 204
        response = self.client.get('/api/variable',
                                   headers={'Authorization': auth }
                                  )
        assert var['description'] not in response.data
