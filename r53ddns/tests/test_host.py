from mock import Mock
from testtools import TestCase
from testtools.matchers import StartsWith
import json

from fresco.exceptions import *

from r53ddns.tests.base import Base
from r53ddns.model import *
from r53ddns.exceptions import *
import r53ddns.views.host

class TestCredentials(Base):
    def setUp(self):
        super(TestCredentials, self).setUp()
        self.host = r53ddns.views.host.HostManager()
        r53ddns.views.host.context = self.context

    def test_list_hosts(self):
        res = self.host.list_hosts('user3')
        self.assertEqual(res.get_header('content-type'), 'application/json')
        res = json.loads(res.content)
        self.assertEquals(res[0]['name'], 'host.example.com')

    def test_create_host(self):
        res = self.host.create_host('user2', 'host2.example.com',
                                    'default')
        self.assertEqual(res.get_header('content-type'), 'application/json')
        res = json.loads(res.content)
        self.assertEquals(res['name'], 'host2.example.com')

    def test_create_host_missing_account(self):
        self.assertRaises(NotFound, self.host.create_host,
                          'does_not_exist', 'host.example.com', 'default')

    def test_create_host_missing_credentials(self):
        self.assertRaises(NotFound, self.host.create_host,
                          'user1', 'host.example.com', 'default')

    def test_create_duplicate_host(self):
        self.assertRaises(Conflict, self.host.create_host,
                          'user3', 'host.example.com', 'default')

    def test_get_host(self):
        res = self.host.get_host('user3', 'host.example.com')
        self.assertEqual(res.get_header('content-type'), 'application/json')
        res = json.loads(res.content)
        self.assertEquals(res['name'], 'host.example.com')

    def test_get_missing_host(self):
        self.assertRaises(NotFound, self.host.get_host,
                          'user1', 'host.example.com')

    def test_delete_host(self):
        self.host.delete_host('user3', 'host.example.com')
        self.assertRaises(NotFound, self.host.get_host,
                          'user3', 'host.example.com')

    def test_delete_missing_host(self):
        self.assertRaises(NotFound, self.host.delete_host,
                          'user1', 'host.example.com')

    @db_session
    def test_update_host(self):
        host = get(host for host in Host
                   if host.credentials.owner.name == 'user3' and
                   host.name == 'host.example.com')

        orig_cred = host.credentials

        res = self.host.update_host('user3', 'host.example.com',
                                    credentials='testing')
        self.assertEqual(res.get_header('content-type'), 'application/json')
        res = json.loads(res.content)
        self.assertEquals(host.credentials.name, 'testing')

    def test_update_host_missing_credentials(self):
        self.assertRaises(NotFound, self.host.update_host,
                          'user3', 'host.example.com', 'does_not_exist')

    def test_get_host_address(self):
        res = self.host.get_host_address('user3', 'host.example.com')
        self.assertThat(res.get_header('content-type'),
                        StartsWith('text/html'))
        self.assertEquals(res.content.strip(), '1.1.1.1')

    def test_update_host_address_auto(self):
        res = self.host.update_host_address('user3', 'host.example.com',
                                            address='auto')
        self.assertEqual(res.get_header('content-type'), 'application/json')
        res = json.loads(res.content)
        self.assertEquals(res['last_address'], '127.0.0.1')

    def test_update_host_address_explicit(self):
        res = self.host.update_host_address('user3', 'host.example.com',
                                            address='2.2.2.2')
        self.assertEqual(res.get_header('content-type'), 'application/json')
        res = json.loads(res.content)
        self.assertEquals(res['last_address'], '2.2.2.2')
