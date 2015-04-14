from testtools.matchers import StartsWith
import json

from fresco.exceptions import *

from r53ddns.tests.base import Base
from r53ddns.exceptions import *
import r53ddns.tests.fakemodel as model
import r53ddns.views.user

r53ddns.views.user.model = model
r53ddns.views.user.TransactionIntegrityError = model.TransactionIntegrityError


class TestUser(Base):
    def setUp(self):
        super(TestUser, self).setUp()
        self.user = r53ddns.views.user.UserManager()

    def test_list_users(self):
        res = self.user.list_users()
        self.assertEqual(res.get_header('content-type'), 'application/json')
        res = json.loads(res.content)
        self.assertEqual(res[0]['name'], 'user1')

    def test_get_user_by_name(self):
        res = self.user.get_user('user1')
        self.assertThat(res.status, StartsWith('200'))
        self.assertEqual(res.get_header('content-type'), 'application/json')
        res = json.loads(res.content)
        self.assertEqual(res['name'], 'user1')

    def test_get_user_by_id(self):
        user1 = model.get(account for account in model.Account
                          if account.name == 'user1')
        res = self.user.get_user(str(user1.id))
        self.assertThat(res.status, StartsWith('200'))
        self.assertEqual(res.get_header('content-type'), 'application/json')
        res = json.loads(res.content)
        self.assertEqual(res['name'], 'user1')

    def test_get_unknown_user(self):
        self.assertRaises(NotFound, self.user.get_user, 'does_not_exist')

    def test_create_user(self):
        res = self.user.create_user('new_user', 'secret', False)
        self.assertThat(res.status, StartsWith('201'))
        self.assertEqual(res.get_header('content-type'),
                         'application/json')
        res = json.loads(res.content)
        self.assertEqual(res['name'], 'new_user')

    def test_create_duplicate_user(self):
        self.assertRaises(Conflict, self.user.create_user,
                          'user1', 'secret')

    def test_update_user(self):
        user1 = model.get(account for account in model.Account
                          if account.name == 'user1')
        orig_password = user1.password
        res = self.user.update_user('user1', password='foobar')
        self.assertThat(res.status, StartsWith('200'))
        self.assertEqual(res.get_header('content-type'),
                         'application/json')
        res = json.loads(res.content)
        new_password = user1.password

        self.assertNotEqual(orig_password, new_password)

    def test_update_user_admin(self):
        user1 = model.get(account for account in model.Account
                          if account.name == 'user1')
        res = self.user.update_user_admin('user1', True)
        self.assertTrue(user1.is_admin)
        self.assertEqual(res.get_header('content-type'),
                         'application/json')
        res = json.loads(res.content)
        self.assertTrue(res['is_admin'])

    def test_delete_user(self):
        self.user.delete_user('user2')
        self.assertRaises(NotFound, self.user.get_user, 'user2')
