from tests import TestCase
from datamart.models import Dimension
import base64
import json

class TestDimensionAPI(TestCase):
    """Tests the Dimension API"""

    @classmethod
    def setup_class(self):
        super(TestDimensionAPI, self).setup_class()
        dim1 = Dimension(name='dim1', description='dim1', data_type='String')
        dim2 = Dimension(name='dim2', description='dim2', data_type='String')
        self.db.session.add(dim1)
        self.db.session.add(dim2)
        self.db.session.commit()

    def test_anon_get_dimensions(self):
        """Get /api/dimension with wrong username & password."""
        auth = 'Basic ' + base64.b64encode('WRONG@example.com:123456')
        response = self.client.get('/api/dimension',
                                   headers={'Authorization': auth }
                                  )
        assert response.status_code == 403

        auth = 'Basic ' + base64.b64encode('demo@example.com:WRONG')
        response = self.client.get('/api/dimension',
                                   headers={'Authorization': auth }
                                  )
        assert response.status_code == 403


    def test_admin_get_dimensions(self):
        """Get /api/dimension as admin."""
        auth = self.admin_auth
        response = self.client.get('/api/dimension',
                                   headers={'Authorization': auth }
                                  )
        assert response.status_code == 200
        assert 'total_pages' in response.data

    def test_non_admin_get_dimensions(self):
        """Get /api/dimension as non-admin."""
        auth = self.demo_auth
        response = self.client.get('/api/dimension',
                                   headers={'Authorization': auth }
                                  )
        assert response.status_code == 200
        assert 'total_pages' in response.data

    def test_add_dimension(self):
        """Adding a dimension using /api/dimension."""
        auth = self.admin_auth
        data = {
            'name': 'weight',
            'description': 'how much something weighs',
            'data_type': 'Float'
        }

        response = self.client.post('/api/dimension',
                                    headers={'Authorization': auth,
                                            },
                                    content_type='application/json',
                                    data=json.dumps(data)
                                  )
        assert response.status_code == 201
        assert data['description'] in response.data

        response = self.client.get('/api/dimension',
                                   headers={'Authorization': auth }
                                  )
        assert response.status_code == 200
        assert 'total_pages' in response.data
        assert data['description'] in response.data

    def test_admin_get_dim_id(self):
        auth = self.admin_auth
        response = self.client.get('/api/dimension',
                                   headers={'Authorization': auth }
                                  )
        dim = json.loads(response.data)['objects'][0]
        response = self.client.get('/api/dimension/%s' % dim['id'],
                                   headers={'Authorization': auth }
                                  )
        assert dim['name'] in response.data
        assert dim['description'] in response.data
        assert 'total_pages' not in response.data

 
    def test_put_dimension(self):
        auth = self.admin_auth
        response = self.client.get('/api/dimension',
                                   headers={'Authorization': auth }
                                  )
        dim = json.loads(response.data)['objects'][0]
        data = dict(dim)
        data.pop('id', None)
        data['name'] = 'barrels of monkeys'
        response = self.client.put('/api/dimension/%s' % dim['id'],
                                   content_type='application/json',
                                   headers={'Authorization': auth },
                                   data=json.dumps(data)
                                  )
        assert response.status_code == 200

    def test_delete_dimension(self):
        auth = self.admin_auth
        response = self.client.get('/api/dimension',
                                   headers={'Authorization': auth }
                                  )
        dim = json.loads(response.data)['objects'][0]
        response = self.client.delete('/api/dimension/%s' % dim['id'],
                                   headers={'Authorization': auth },
                                  )
        assert response.status_code == 204
        response = self.client.get('/api/dimension',
                                   headers={'Authorization': auth }
                                  )
        assert dim['description'] not in response.data
