from mock import Mock
from testtools import TestCase
from testtools.matchers import StartsWith
import json

from fresco.exceptions import *

from r53ddns.tests.base import Base
import r53ddns.tests.fakemodel as model
from r53ddns.exceptions import *
import r53ddns.views.host

r53ddns.views.host.model = model
r53ddns.views.host.TransactionIntegrityError = model.TransactionIntegrityError
r53ddns.views.host.ConstraintError = model.ConstraintError

route53 = Mock()
route53_connection = Mock()
zone_example_com = Mock()
zone_example_com.name = 'example.com.'
host_example_com = Mock()
host_example_com.name = 'host.example.com.'
zone_example_com.record_sets = [host_example_com]
route53.connect.return_value = route53_connection
route53_connection.list_hosted_zones.return_value = [
    zone_example_com,
]

r53ddns.views.host.route53 = route53

class TestHost(Base):
    def setUp(self):
        super(TestHost, self).setUp()
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

    def test_get_host_by_name(self):
        res = self.host.get_host('user3', 'host.example.com')
        self.assertEqual(res.get_header('content-type'), 'application/json')
        res = json.loads(res.content)
        self.assertEquals(res['name'], 'host.example.com')

    def test_get_host_by_id(self):
        res = self.host.get_host('user3', '1')
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

    def test_update_host(self):
        host = model.get(host for host in model.Host
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

    def test_get_host_address_missing_host(self):
        self.assertRaises(NotFound, self.host.get_host_address,
                          'user3', 'does_not_exist.example.com')

    def test_update_host_address_missing_host(self):
        self.assertRaises(NotFound, self.host.update_host_address,
                          'user3', 'does_not_exist.example.com',
                          address='auto')

    def test_update_host_address_bad_address(self):
        self.assertRaises(BadRequest, self.host.update_host_address,
                          'user3', 'host.example.com',
                          address='bad_address')

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
