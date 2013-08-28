from datamart.models import User

from tests import TestCase


class TestUser(TestCase):

    def test_number_of_users(self):
        assert User.query.count() == 2
