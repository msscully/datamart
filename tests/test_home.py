from tests import TestCase

class TestHome(TestCase):

    def test_show(self):
        self._test_get_request('/', 'index.html')

    def test_show_login(self):
        self._test_get_request('/login', 'login.html')

    def test_login_logout(self):
        rv = self.login('admin@example.com', '123456')
        assert 'Logout admin' in rv.data
        rv = self.logout()
        assert 'you@example.com' in rv.data
        rv = self.login('adminx@example.com', 'default')
        assert 'Specified user does not exist' in rv.data
        rv = self.login('admin@example.com', 'defaultx')
        assert 'Invalid password' in rv.data
