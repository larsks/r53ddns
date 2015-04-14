from mock import Mock
from testtools import TestCase
import r53ddns.utils
from r53ddns.model import *

setup_database(':memory:')


class Base (TestCase):
    def setUp(self):
        super(Base, self).setUp()

        db.drop_all_tables(with_all_data=True)
        db.create_tables()
        self.populate_database()
        self.setup_context()

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
            'NO_ROUTE53_UPDATE': True,
        }

        self.context = context
        r53ddns.utils.context = context

    @db_session
    def populate_database(self):
        for id, name in enumerate(['user1', 'user2', 'user3']):
            Account(id=id,
                    name=name,
                    password='secret')

        user2 = get(account for account in Account
                    if account.name == 'user2')
        user3 = get(account for account in Account
                    if account.name == 'user3')

        Credentials(owner=user2,
                    accesskey='access',
                    secretkey='secret',
                    name='default')

        Credentials(owner=user3,
                    accesskey='testaccess',
                    secretkey='testsecret',
                    name='testing')

        cred = Credentials(owner=user3,
                           accesskey='access',
                           secretkey='secret',
                           name='default')

        Host(name='host.example.com',
             zone='example.com',
             credentials=cred,
             last_address='1.1.1.1')
