from tests import TestCase
from werkzeug.urls import url_quote
from datamart.models import Facts
from datamart.models import Subject
from datamart.models import Variable
from datamart.models import Event
from datamart.models import Dimension
from datamart.models import User
from datamart.models import Role
from flask import url_for
from StringIO import StringIO
from datamart.extensions import data_files
import glob
import os

class TestFacts(TestCase):

    @classmethod
    def setup_class(self):
        super(TestFacts, self).setup_class()
        subject1 = Subject(internal_id='Facts_Subject1')
        subject2 = Subject(internal_id='Facts_Subject2')
        self.dim1 = Dimension(name='facts_dim1', description='facts_dim1', data_type='String')
        self.dim2 = Dimension(name='facts_dim2', description='facts_dim2', data_type='Float')
        self.role1 = Role(name='Facts_Admin', description='Facts_Admin')
        self.db.session.add(subject1)
        self.db.session.add(subject2)
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

        self.subject1_id = subject1.id
        self.subject2_id = subject2.id

        self.var1_id = var1.id
        self.var2_id = var2.id
        self.var3_id = var3.id
        event1 = Event(name="Facts_event1", description="Facts_event1")
        event2 = Event(name="Facts_event2", description="Facts_event2")
        event3 = Event(name="Facts_event3", description="Facts_event3")
                           
        self.db.session.add(event1)
        self.db.session.add(event2)
        self.db.session.add(event3)
        self.db.session.flush()

        self.event1_id = event1.id
        self.event2_id = event2.id
        self.event3_id = event3.id

        fact1 = Facts(subject_id=subject1.id, event_id=self.event1_id,
                      values={str(self.var1_id): 'thing', str(var2.id): '2.0'})
        fact2 = Facts(subject_id=subject1.id, event_id=self.event2_id,
                      values={str(self.var1_id): 'stuff', str(var2.id): '1.0'})
        fact3 = Facts(subject_id=subject1.id, event_id=self.event3_id,
                      values={str(self.var1_id): 'blah', str(var2.id): '3.0'})

        self.db.session.add(fact1)
        self.db.session.add(fact2)
        self.db.session.add(fact3)
        self.db.session.commit()

        self.fact1_id = fact1.id
        self.fact2_id = fact2.id
        self.fact3_id = fact3.id

    def tearDown(self):
        """Delete the uploaded facts files."""
        data_dir = data_files.config.destination
        file_list = glob.glob(os.path.join(data_dir,"*facts_test_data*.csv"))
        for f in file_list:
            os.remove(f)

    def test_show_facts_anon(self):
        """Does accessing /facts/ when not logged in redirect to /login?"""
        response = self.client.get('/facts/', follow_redirects=False)
        new_location='/login?next=%s' % url_quote('/facts/', safe='')
        self.assertRedirects(response, location=new_location)
        response = self.client.get('/facts/', follow_redirects=True)
        assert 'Please log in to access this page.' in response.data
        self.assertTemplateUsed(name='login.html')

    def test_show_facts_non_admin(self):
        """Make sure logged in users can see the facts page."""
        self.login('demo@example.com','123456')
        response = self._test_get_request('/facts/', 'facts.html')
        assert 'Please log in to access this page.' not in response.data
        self.logout()

    def test_show_facts_admin(self):
        """Make sure logged in admins can see the facts page."""
        self.login('admin@example.com','123456')
        response = self._test_get_request('/facts/', 'facts.html')
        assert 'Please log in to access this page.' not in response.data
        self.logout()

    def test_fact_add(self):
        """Add a fact using /facts/add as admin."""
        self.login('admin@example.com', '123456')
        self._test_get_request('/facts/add/', 'fact_edit.html')
        fact_data = {
            'subject': self.subject2_id,
            'event': self.event1_id,
            'values-1-variable_id': str(self.var1_id),
            'values-1-value': 'another_thing',
            'action_save': True
        }
        response = self.client.post('/facts/add/', data=fact_data)
        assert 'Please fix errors and resubmit.' not in response.data
        fact = Facts.query.filter_by(subject_id=self.subject2_id,
                                     event_id=self.event1_id)
        assert "another_thing" == fact.first().values[str(self.var1_id)]
        self.logout()

    def test_fact_edit(self):
        """Edit a fact at /facts/<ID>/edit/ as admin."""
        self.login('admin@example.com', '123456')
        fact_data = {
            'subject': self.subject2_id,
            'event': self.event2_id,
            'values-1-variable_id': str(self.var1_id),
            'values-1-value': 'the_third_thing',
            'action_save': True
        }
        response = self.client.post('/facts/add/', data=fact_data)
        assert 'Please fix errors and resubmit.' not in response.data
        fact = Facts.query.filter_by(subject_id=self.subject2_id,
                                     event_id=self.event2_id)
        assert "the_third_thing" == fact.first().values[str(self.var1_id)]
  
        fact_data['values-1-value'] = 'something_else'
        response = self.client.post('/facts/%s/edit/' % fact.first().id, 
                                    data=fact_data,
                                    headers={'Referer': url_for('datamart.facts_view')},
                                    follow_redirects=True)
        assert 'Fact updated' in response.data
        assert 'Please fix errors and resubmit.' not in response.data
        fact = Facts.query.filter_by(subject_id=self.subject2_id,
                                     event_id=self.event2_id)
        assert "something_else" == fact.first().values[str(self.var1_id)]
        self.logout()

    def test_fact_by_role(self):
        """Are facts only displayed if a user has the correct role?"""
        return False
        self.login('admin@example.com', '123456')
        new_var, fact_data = self.add_fact()
        assert new_var.count() == 1
        new_role = Role(name='AdminRole', description='AdminRole')
        self.db.session.add(new_role)
        self.db.session.commit()
        role_id = new_role.id
        response = self.add_role_to_fact(new_var.first().id, role_id)
        assert 'Fact updated' in response.data
        assert 'Please fix errors and resubmit' not in response.data
        new_var = Facts.query.join(Role, Facts.roles).filter(Role.id == role_id)
        assert new_var.count() == 1;
        var_name = new_var.first().name
        response = self.client.get('/facts/')
        assert var_name not in response.data
        assert new_role.name not in response.data
        user = User.query.filter_by(username='admin')
        user_id = user.first().id
        self.add_role_to_user(user_id, new_role)
        response = self.client.get('/facts/')
        assert new_role.name in response.data
        assert var_name in response.data
        self.logout()
        self.login('demo@example.com', '123456')
        response = self.client.get('/facts/')
        assert new_role.name not in response.data
        assert var_name not in response.data
        self.logout()
        self.login('admin@example.com', '123456')
        user = User.query.filter_by(username='demo')
        user_id = user.first().id
        self.add_role_to_user(user_id, new_role)
        response = self.client.get('/facts/')
        assert new_role.name in response.data
        assert var_name in response.data
        self.logout()

    def test_fact_upload(self):
        """Test uploading a csv of facts."""
        self.login('admin@example.com', '123456')
        response = self._test_get_request('/facts/upload/', 'upload.html')
        assert 'Please log in to access this page.' not in response.data
        with open('tests/facts_test_data.csv') as test_file_content:

            upload_settings = {
                'header_row': '',
                'create_subjects': '',
                'create_events': '',
                'data_file': (StringIO(test_file_content.read()),
                              'facts_test_data.csv'),
                'action_save': True
            }
    
            response = self.client.post('/facts/upload/',
                                        data = upload_settings,
                                        follow_redirects=True
                                       )
            self.assert_200(response)
            self.assertTemplateUsed('label_upload.html')

        self.logout()
        return True

    def test_fact_label_upload(self):
        """Test labeling an uploading csv of facts."""
        self.login('admin@example.com', '123456')
        response = self._test_get_request('/facts/upload/', 'upload.html')
        assert 'Please log in to access this page.' not in response.data
        with open('tests/facts_test_data.csv') as test_file:
            test_file_content = test_file.read()

        upload_settings = {
            'header_row': 'y',
            #'create_subjects': '',
            #'create_events': '',
            'data_file': (StringIO(test_file_content),
                          'facts_test_data.csv'),
            'action_save': True
        }
    
        response = self.client.post('/facts/upload/',
                                    data = upload_settings,
                                    #follow_redirects=True
                                   )
        assert 302 == response.status_code
        new_data_url = response.location.split('/')[6]
        assert "facts_test_data.csv" in new_data_url
        #self.assertTemplateUsed('label_upload.html')
        #assert 'Facts_New_Event' in response.data
        #assert 'other stuff' in response.data
        #assert "Error" not in response.data

        label_settings = {
            'column_0': 'subjects',
            'column_1': 'events',
            'column_2': str(self.var1_id),
            'column_3': str(self.var2_id)
        }
        response = self.client.post('/facts/upload/label/'+new_data_url+'/',
                                    data = label_settings,
                                    follow_redirects=True
                                   )

        self.assert_200(response)
        self.assertTemplateUsed('label_upload.html')
        # Shouldn't succed as we didn't enable the creation of new subjects /
        # events.
        assert "alert-success" not in response.data
        assert "Error: Not all data in Column 2 is a valid Event ID or name." in response.data
        assert "Error: Not all data in Column 1 is a valid Subject ID or internal ID" in response.data

        upload_settings['create_subjects'] = 'y'
        upload_settings['data_file'] =  (StringIO(test_file_content), 'facts_test_data.csv')
        response = self.client.post('/facts/upload/',
                                    data = upload_settings,
                                    follow_redirects=True
                                   )
        self.assert_200(response)
        self.assertTemplateUsed('label_upload.html')
        assert 'Facts_New_Event' in response.data
        assert 'other stuff' in response.data
        assert "Error" not in response.data

        response = self.client.post('/facts/upload/label/'+new_data_url+'/',
                                    data = label_settings,
                                    follow_redirects=True
                                   )

        self.assert_200(response)
        self.assertTemplateUsed('label_upload.html')
        # Shouldn't succed as we didn't enable the creation of new subjects /
        # events.
        assert "alert-success" not in response.data
        assert "Error: Not all data in Column 2 is a valid Event ID or name." in response.data
        # Subject creation is on, so this error should go away.
        assert "Error: Not all data in Column 1 is a valid Subject ID or internal ID" not in response.data

        upload_settings['create_events'] = 'y'
        upload_settings['data_file'] =  (StringIO(test_file_content), 'facts_test_data.csv')
        response = self.client.post('/facts/upload/',
                                    data = upload_settings,
                                    follow_redirects=True
                                   )
        self.assert_200(response)
        self.assertTemplateUsed('label_upload.html')
        assert 'Facts_New_Event' in response.data
        assert 'other stuff' in response.data
        assert "Error" not in response.data

        response = self.client.post('/facts/upload/label/'+new_data_url+'/',
                                    data = label_settings,
                                    follow_redirects=True
                                   )

        self.assert_200(response)
        self.assertTemplateUsed('label_upload.html')
        # Everything should work, so there should be a success message.
        assert "alert-success" in response.data
        # Subject & Event creation is on, so these errors shouldn't be there.
        assert "Error: Not all data in Column 2 is a valid Event ID or name." not in response.data
        assert "Error: Not all data in Column 1 is a valid Subject ID or internal ID" not in response.data
        # Make sure the new Subject & Event were added to the database.
        new_subjects = Subject.query.filter(Subject.internal_id == "Some1").all()
        new_events = Event.query.filter(Event.name == "Facts_New_Event").all()
        assert len(new_subjects) > 0
        assert len(new_events) > 0
        new_subject_id = new_subjects[0].id
        new_event_id = new_events[0].id
        new_facts = Facts.query.filter(Facts.subject_id == new_subject_id).filter(Facts.event_id == new_event_id).all()
        assert "other stuff" == new_facts[0].values[str(self.var1_id)]

        self.logout()
        return True
