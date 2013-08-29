from tests import TestCase
from werkzeug.urls import url_quote
from datamart.models import Event
from datamart.models import Dimension
from datamart.models import User
from datamart.models import Role

class TestEvents(TestCase):

    def test_show_events_anon(self):
        """Does accessing /events/ when not logged in redirect to /login?"""
        response = self.client.get('/events/', follow_redirects=False)
        new_location='/login?next=%s' % url_quote('/events/', safe='')
        self.assertRedirects(response, location=new_location)
        response = self.client.get('/events/', follow_redirects=True)
        assert 'Please log in to access this page.' in response.data
        self.assertTemplateUsed(name='login.html')

    def test_show_events_admin(self):
        """Does /events/ display correctly when logged in as admin?"""
        self.login('admin@example.com','123456')
        response = self._test_get_request('/events/', 'events.html')
        assert 'Please log in to access this page.' not in response.data
        self.logout()

    def test_event_add(self):
        """Add event at /events/add/ as admin."""
        self.login('admin@example.com', '123456')
        self._test_get_request('/events/add/', 'event_edit.html')
        data = {
            'name': 'event1',
            'description': "First Event",
        }
 
        response = self.client.post('/events/add/', data=data)
        assert 'Please fix errors and resubmit.' not in response.data
        new_event = Event.query.filter_by(name=data['name'])
        assert new_event.count() == 1
        self.logout()

    def add_event(self):
        """ Add a event to testdb. Must be logged in w/ permissions. """

        event_data = {
            'name': 'length',
            'description': "Subject height",
        }
        response = self.client.post('/events/add/', data=event_data)
        assert 'Please fix errors and resubmit.' not in response.data
        new_event = Event.query.filter_by(name=event_data['name'])
        return new_event, event_data

    def test_event_edit(self):
        """Edit event using /events/<ID>/edit as admin."""
        self.login('admin@example.com', '123456')
        new_event, event_data = self.add_event()
        assert new_event.count() == 1;
        old_name = event_data['name']
        event_data['name'] = 'event2'
        response = self.client.post('/events/%s/edit/' % new_event.first().id, data=event_data)
        assert 'Please fix errors and resubmit.' not in response.data
        new_event = Event.query.filter_by(name=event_data['name'])
        assert new_event.count() == 1;
        response = self.client.get('/events/')
        assert 'Event updated' in response.data
        assert 'Please fix errors and resubmit' not in response.data
        assert old_name not in response.data
        self.logout()
