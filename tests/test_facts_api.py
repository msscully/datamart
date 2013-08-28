from tests import TestCase
from datamart.models import Facts
from datamart.models import Variable
from datamart.models import Dimension
from datamart.models import Role
from datamart.models import User
from datamart.models import Subject
from datamart.models import Event
import base64
import json

class TestFactsAPI(TestCase):
    """Tests the Facts API"""

    @classmethod
    def setup_class(self):
        super(TestFactsAPI, self).setup_class()
        self.subject1 = Subject(internal_id='Facts_Subject1')
        self.dim1 = Dimension(name='facts_dim1', description='facts_dim1', data_type='String')
        self.dim2 = Dimension(name='facts_dim2', description='facts_dim2', data_type='Float')
        self.role1 = Role(name='Facts_Admin', description='Facts_Admin')
        self.db.session.add(self.subject1)
        self.db.session.add(self.dim1)
        self.db.session.add(self.dim2)
        self.db.session.add(self.role1)
        self.db.session.flush()
        users = User.query.all()
        for user in users:
            roles = [r for r in user.roles]
            roles.append(self.role1)
            user.roles = roles
            self.db.session.add(user)
        var1 = Variable(name='facts_var1', description='facts_var1',
                        dimension_id=self.dim1.id, roles=[self.role1],
                        in_use=True)
        var2 = Variable(name='facts_var2', description='facts_var2', 
                        dimension_id=self.dim2.id, roles=[self.role1],
                        in_use=True)
        var3 = Variable(name='facts_var3', description='facts_var3', 
                        dimension_id=self.dim1.id, roles=[self.role1],
                        in_use=True)
        self.db.session.add(var1)
        self.db.session.add(var2)
        self.db.session.add(var3)
        self.db.session.flush()

        self.var1_id = var1.id
        self.var3_id = var3.id
        self.event1 = Event(name="Facts_event1", description="Facts_event1")
        self.event2 = Event(name="Facts_event2", description="Facts_event2")
                           
        self.db.session.add(self.event1)
        self.db.session.add(self.event2)
        self.db.session.flush()

        fact1 = Facts(subject_id=self.subject1.id, event_id=self.event1.id,
                      values={str(self.var1_id): 'thing', str(var2.id): '2.0'})
        fact2 = Facts(subject_id=self.subject1.id, event_id=self.event2.id,
                      values={str(self.var1_id): 'stuff', str(var2.id): '1.0'})

        self.db.session.add(fact1)
        self.db.session.add(fact2)
        self.db.session.commit()

    def test_anon_get_facts(self):
        """Get /api/facts with wrong username & password."""
        auth = 'Basic ' + base64.b64encode('WRONG@example.com:123456')
        response = self.client.get('/api/facts',
                                   headers={'Authorization': auth }
                                  )
        assert response.status_code == 403

        auth = 'Basic ' + base64.b64encode('demo@example.com:WRONG')
        response = self.client.get('/api/facts',
                                   headers={'Authorization': auth }
                                  )
        assert response.status_code == 403


    def test_admin_get_facts(self):
        """Get /api/facts as admin."""
        auth = self.admin_auth
        response = self.client.get('/api/facts',
                                   headers={'Authorization': auth }
                                  )
        assert response.status_code == 200
        assert 'total_pages' in response.data
        rd = json.loads(response.data)
        # Put 2 subjects facts in setup so there should be at least 2 rows in
        # the facts table which corresponds to 2 objects in the api response. 
        assert rd['num_results'] >= 2

    def test_non_admin_get_facts(self):
        """Get /api/facts as non-admin.
        
           Since demo has the required roles the response should include 
           some facts.
        """
        auth = self.demo_auth
        response = self.client.get('/api/facts',
                                   headers={'Authorization': auth }
                                  )
        assert response.status_code == 200
        resp = json.loads(response.data)
        assert resp['num_results'] > 0

    def test_get_facts_wrong_role(self):
        """Get /api/facts as demo without correct role.

           Variables and users have roles associated with them and if a user
           doesn't have any roles overlapping with a variable's roles that
           variable should not be displayed in the fact table for them.
        """
        variable = Variable(name='facts_nope', description='not a chance', 
                       dimension=self.dim1, roles=[])
        self.db.session.add(variable)
        self.db.session.flush()
        facts = Facts.query.all()
        for fact in facts:
            fact.values['variable.id'] = "Should not appear"
            self.db.session.add(fact)
        self.db.session.commit()
        auth = self.demo_auth
        response = self.client.get('/api/facts',
                                   headers={'Authorization': auth }
                                  )
        assert response.status_code == 200
        assert "Sould not appear" not in response.data

    # PUT and POST aren't currently allowed for facts
    #def test_add_fact(self):
    #    """Adding a fact using /api/facts."""
    #    auth = self.admin_auth
    #    data = {
    #        'subject_id': self.subject1.id,
    #        'values': {self.var3_id: 'New Fact Here!'}
    #    }

    #    response = self.client.post('/api/facts',
    #                                headers={'Authorization': auth,
    #                                        },
    #                                content_type='application/json',
    #                                data=json.dumps(data)
    #                              )
    #    import ipdb; ipdb.set_trace()
    #    assert response.status_code == 201
    #    assert 'New Fact Here!' in response.data

    #    response = self.client.get('/api/facts',
    #                               headers={'Authorization': auth }
    #                              )
    #    assert response.status_code == 200
    #    assert 'total_pages' in response.data
    #    assert 'New Fact Here!' in response.data

    def test_admin_get_fact_id(self):
        """Get a fact at /api/facts/<ID> as admin."""
        auth = self.admin_auth
        response = self.client.get('/api/facts',
                                   headers={'Authorization': auth }
                                  )
        assert response.status_code == 200
        fact = json.loads(response.data)['objects'][0]
        response = self.client.get('/api/facts/%s' % fact['id'],
                                   headers={'Authorization': auth }
                                  )
        for id in fact['values']:
            assert fact['values'][id] in response.data

        assert 'total_pages' not in response.data

 
    # PUT and POST aren't currently allowed for facts
    #def test_put_fact(self):
    #    """Update Fact at /api/facts/<ID> using PUT"""
    #    auth = self.admin_auth
    #    response = self.client.get('/api/facts',
    #                               headers={'Authorization': auth }
    #                              )
    #    fact = json.loads(response.data)['objects'][0]
    #    data = dict(fact)
    #    data.pop('id', None)
    #    data['values'][self.var1_id] = 'barrels of monkeys'
    #    response = self.client.put('/api/facts/%s' % fact['id'],
    #                               content_type='application/json',
    #                               headers={'Authorization': auth },
    #                               data=json.dumps(data)
    #                              )
    #    assert response.status_code == 200

    #    response = self.client.get('/api/facts/%s' % fact['id'],
    #                               headers={'Authorization': auth }
    #                              )
    #    assert response.status_code == 200
    #    assert data['values'][self.var1_id] in response.data

    def test_delete_fact(self):
        """Delete fact using /api/facts/<ID>"""
        auth = self.admin_auth
        response = self.client.get('/api/facts',
                                   headers={'Authorization': auth }
                                  )
        fact = json.loads(response.data)['objects'][0]
        response = self.client.delete('/api/facts/%s' % fact['id'],
                                   headers={'Authorization': auth },
                                  )
        assert response.status_code == 204
        response = self.client.get('/api/facts',
                                   headers={'Authorization': auth }
                                  )
