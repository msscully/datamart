from tests import TestCase
from werkzeug.urls import url_quote
from datamart.models import Subject
from datamart.models import ExternalID

class TestSubjects(TestCase):

    def test_show_subjects_anon(self):
        response = self.client.get('/subjects/', follow_redirects=False)
        new_location='/login?next=%s' % url_quote('/subjects/', safe='')
        self.assertRedirects(response, location=new_location)
        response = self.client.get('/subjects/', follow_redirects=True)
        assert 'Please log in to access this page.' in response.data
        self.assertTemplateUsed(name='login.html')

    def test_show_subjects_admin(self):
        self.login('admin@example.com','123456')
        response = self._test_get_request('/subjects/', 'subjects.html')
        assert 'Please log in to access this page.' not in response.data
        self.logout()

    def test_subject_add(self):
        self.login('admin@example.com', '123456')
        self._test_get_request('/subjects/add/', 'subject_edit.html')
        data = {
            'internal_id': 'subject1',
            'external_ids': [],
        }
 
        response = self.client.post('/subjects/add/', data=data)
        assert 'Please fix errors and resubmit.' not in response.data
        new_subject = Subject.query.filter_by(internal_id=data['internal_id'])
        assert new_subject.count() == 1
        self.logout()

    def add_subject(self):
        """ Add a subject to testdb. Must be logged in w/ permissions. """

        subject_data = {
            'internal_id': 'notherSubject',
            'external_ids': [],
        }
        response = self.client.post('/subjects/add/', data=subject_data)
        assert 'Please fix errors and resubmit.' not in response.data
        new_subject = Subject.query.filter_by(internal_id=subject_data['internal_id'])
        return new_subject, subject_data

    def test_subject_edit(self):
        self.login('admin@example.com', '123456')
        new_subject, subject_data = self.add_subject()
        assert new_subject.count() == 1;
        old_name = subject_data['internal_id']
        subject_data['internal_id'] = 'subject2'
        response = self.client.post('/subjects/%s/edit/' % new_subject.first().id, data=subject_data)
        assert 'Please fix errors and resubmit.' not in response.data
        new_subject = Subject.query.filter_by(internal_id=subject_data['internal_id'])
        assert new_subject.count() == 1;
        response = self.client.get('/subjects/')
        assert 'Subject updated' in response.data
        assert 'Please fix errors and resubmit' not in response.data
        assert old_name not in response.data
        self.logout()

class TestExternalIDs(TestCase):

    def test_show_externalids_anon(self):
        response = self.client.get('/externalids/', follow_redirects=False)
        new_location='/login?next=%s' % url_quote('/externalids/', safe='')
        self.assertRedirects(response, location=new_location)
        response = self.client.get('/externalids/', follow_redirects=True)
        assert 'Please log in to access this page.' in response.data
        self.assertTemplateUsed(name='login.html')

    def test_show_externalids_admin(self):
        self.login('admin@example.com','123456')
        response = self._test_get_request('/externalids/', 'externalids.html')
        assert 'Please log in to access this page.' not in response.data
        self.logout()

    def test_externalid_add(self):
        self.login('admin@example.com', '123456')
        self._test_get_request('/externalids/add/', 'externalid_edit.html')
        new_subject = self.add_subject() 
        data = {
            'name': 'externalid1',
            'description': '',
            'subject': new_subject.id,
        }
 
        response = self.client.post('/externalids/add/', data=data)
        assert 'Please fix errors and resubmit.' not in response.data
        new_externalid = ExternalID.query.filter_by(name=data['name'])
        assert new_externalid.count() == 1
        self.logout()

    def add_subject(self):
        subjects = Subject.query.filter_by(internal_id='test_subject')
        if subjects.count() != 1:
            new_subject = Subject(internal_id='test_subject')
            self.db.session.add(new_subject)
            self.db.session.commit()
        else:
            new_subject = subjects.first()
        return new_subject

    def add_externalid(self):
        """ Add a externalid to testdb. Must be logged in w/ permissions. """

        new_subject = self.add_subject() 
        externalid_data = {
            'name': 'notherExternalID',
            'description': '',
            'subject': new_subject.id,
        }
        response = self.client.post('/externalids/add/', data=externalid_data)
        assert 'Please fix errors and resubmit.' not in response.data
        new_externalid = ExternalID.query.filter_by(name=externalid_data['name'])
        return new_externalid, externalid_data

    def test_externalid_edit(self):
        self.login('admin@example.com', '123456')
        new_externalid, externalid_data = self.add_externalid()
        assert new_externalid.count() == 1;
        old_name = externalid_data['name']
        externalid_data['name'] = 'externalid2'
        response = self.client.post('/externalids/%s/edit/' % new_externalid.first().id, data=externalid_data)
        assert 'Please fix errors and resubmit.' not in response.data
        new_externalid = ExternalID.query.filter_by(name=externalid_data['name'])
        assert new_externalid.count() == 1;
        response = self.client.get('/externalids/')
        assert 'Externalid updated' in response.data
        assert 'Please fix errors and resubmit' not in response.data
        assert old_name not in response.data
        self.logout()
