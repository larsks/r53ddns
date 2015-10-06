from mock import Mock
from testtools import TestCase
from contextlib import contextmanager

import r53ddns.tests.fakemodel as model
import r53ddns.utils
import r53ddns.decorators

r53ddns.utils.model = model
r53ddns.decorators.model = model


@contextmanager
def fakeContext(username=None, password=None):
    context = Mock()
    context.request.environ = {
        'REMOTE_ADDR': '127.0.0.1',
    }

    if username:
        context.request.environ['auth_name'] = username
    if password:
        context.request.environ['auth_pass'] = password

    context.app.options = {
        'ADMIN_NAME': 'admin',
        'ADMIN_PASSWORD': 'secret',
    }

    old_context = fresco.context
    fresco.context = context
    yield
    fresco.context = old_context


class Base (TestCase):
    def setUp(self):
        super(Base, self).setUp()
        self.populate_database()
        self.setup_context()

    def tearDown(self):
        super(Base, self).tearDown()
        model.Account.reset()
        model.Credentials.reset()
        model.Host.reset()

    def setup_context(self):
        context = Mock()
        context.request.environ = {
            'REMOTE_ADDR': '127.0.0.1',
            'auth_name': 'admin',
            'auth_pass': 'secret',
        }
        context.app.options = {
            'ADMIN_NAME': 'admin',
            'ADMIN_PASSWORD': 'secret',
        }

        self.context = context
        r53ddns.utils.context = context
        r53ddns.decorators.context = context

    def populate_database(self):
        for id, name in enumerate(['user1', 'user2', 'user3']):
            model.Account(id=id,
                          name=name,
                          password='secret')

        user2 = model.get(account for account in model.Account
                          if account.name == 'user2')
        user3 = model.get(account for account in model.Account
                          if account.name == 'user3')

        model.Credentials(owner=user2,
                          accesskey='access',
                          secretkey='secret',
                          name='default')

        model.Credentials(owner=user3,
                          accesskey='testaccess',
                          secretkey='testsecret',
                          name='testing')

        model.Credentials(owner=user3,
                          accesskey='access',
                          secretkey='secret',
                          name='default')

        cred = model.get(cred for cred in model.Credentials
                         if cred.owner.id == user3.id
                         and cred.name == 'default')

        model.Host(name='host.example.com',
                   zone='example.com',
                   credentials=cred,
                   last_address='1.1.1.1')
