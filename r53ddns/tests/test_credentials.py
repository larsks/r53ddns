from mock import Mock
from testtools import TestCase
from testtools.matchers import StartsWith
import json

from fresco.exceptions import *

from r53ddns.tests.base import Base
import r53ddns.tests.fakemodel as model
from r53ddns.exceptions import *

import r53ddns.views.credentials
r53ddns.views.credentials.model = model
r53ddns.views.credentials.TransactionIntegrityError = (
    model.TransactionIntegrityError)
r53ddns.views.credentials.ConstraintError = model.ConstraintError


class TestCredentials(Base):
    def setUp(self):
        super(TestCredentials, self).setUp()
        self.creds = r53ddns.views.credentials.CredentialManager()

    def test_list_credentials(self):
        res = self.creds.list_credentials('user2')
        self.assertEqual(res.get_header('content-type'), 'application/json')
        res = json.loads(res.content)
        self.assertEquals(res[0]['accesskey'], 'access')
        self.assertEquals(res[0]['secretkey'], 'secret')

    def test_list_credentials_missing_account(self):
        self.assertRaises(NotFound, self.creds.list_credentials,
                          'does_not_exist')

    def test_get_credentials_by_name(self):
        res = self.creds.get_credentials('user2', 'default')
        self.assertEqual(res.get_header('content-type'), 'application/json')
        res = json.loads(res.content)
        self.assertEquals(res['accesskey'], 'access')
        self.assertEquals(res['secretkey'], 'secret')

    def test_get_credentials_by_id(self):
        user2 = model.get(a for a in model.Account
                          if a.name == 'user2')
        cred = model.get(c for c in model.Credentials
                         if c.owner == user2 and c.name == 'default')

        res = self.creds.get_credentials('user2', str(cred.id))
        self.assertEqual(res.get_header('content-type'), 'application/json')
        res = json.loads(res.content)
        self.assertEquals(res['accesskey'], 'access')
        self.assertEquals(res['secretkey'], 'secret')

    def test_get_credentials_missing_account(self):
        self.assertRaises(NotFound, self.creds.get_credentials,
                          'does_not_exist', 'default')

    def test_get_missing_credentials(self):
        self.assertRaises(NotFound, self.creds.get_credentials,
                          'user1', 'default')

    def test_create_credentials(self):
        res = self.creds.create_credentials('user1', 'access',
                                            'secret', name='default')
        self.assertEqual(res.get_header('content-type'), 'application/json')
        res = json.loads(res.content)
        self.assertEquals(res['accesskey'], 'access')
        self.assertEquals(res['secretkey'], 'secret')

    def test_create_credentials_missing_account(self):
        self.assertRaises(NotFound, self.creds.create_credentials,
                          'does_not_exist', 'access',
                          'secret', name='default')

    def test_create_duplicate_credentials(self):
        self.assertRaises(Conflict, self.creds.create_credentials,
                          'user2', 'access', 'secret', 'default')

    def test_update_credentials(self):
        res = self.creds.update_credentials('user2', 'default',
                                            accesskey='access2',
                                            secretkey='secret2')
        self.assertEqual(res.get_header('content-type'), 'application/json')
        res = json.loads(res.content)
        self.assertEquals(res['accesskey'], 'access2')

    def test_update_credentials_name(self):
        self.creds.update_credentials('user2', 'default',
                                      name='testing')
        self.assertRaises(NotFound, self.creds.get_credentials,
                          'user2', 'default')
        assert(self.creds.get_credentials('user2', 'testing'))

    def test_delete_credentials(self):
        self.creds.delete_credentials('user2', 'default')
        self.assertRaises(NotFound, self.creds.get_credentials,
                          'user2', 'default')

    def test_delete_inuse_credentials(self):
        self.assertRaises(Conflict, self.creds.delete_credentials,
                          'user3', 'default')
