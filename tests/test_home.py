from tests import TestCase

class TestHome(TestCase):

    def test_show(self):
        """Does the home page use the correct template?"""
        self._test_get_request('/', 'index.html')

    def test_show_login(self):
        """Does the login page use the correct template?"""
        self._test_get_request('/login', 'login.html')

    def test_login_logout(self):
        """Can login/logout and using wrong username/password causes errors."""
        rv = self.login('admin@example.com', '123456')
        assert 'Logout admin' in rv.data
        rv = self.logout()
        assert 'you@example.com' in rv.data
        rv = self.login('adminx@example.com', 'default')
        assert 'Specified user does not exist' in rv.data
        rv = self.login('admin@example.com', 'defaultx')
        assert 'Invalid password' in rv.data
