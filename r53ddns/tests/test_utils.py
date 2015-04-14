from mock import Mock
from testtools import TestCase
from testtools.matchers import StartsWith

from r53ddns.tests.base import Base
import r53ddns.utils
from r53ddns.model import *
from r53ddns.exceptions import *


class TestUtils(Base):
    def setUp(self):
        super(TestUtils, self).setUp()

    def test_is_admin_when_admin(self):
        self.assertTrue(r53ddns.utils._is_admin())

    def test_is_admin_when_admin_user(self):
        context = Mock()
        context.request.environ = {
            'requester': Mock(is_admin=True),
        }
        self.patch(r53ddns.utils, 'context', context)
        self.assertTrue(r53ddns.utils._is_admin())

    def test_is_admin_when_not_admin(self):
        context = Mock()
        context.request.environ = {
            'requester': Mock(is_admin=False),
        }
        self.patch(r53ddns.utils, 'context', context)
        self.assertFalse(r53ddns.utils._is_admin())

    def test_is_admin_with_no_auth(self):
        context = Mock()
        context.request.environ = {}
        context.app.options = {}
        self.patch(r53ddns.utils, 'context', context)
        self.assertFalse(r53ddns.utils._is_admin())

    def test_is_authenticated_when_authenticated(self):
        context = Mock()
        context.request.environ = {
            'requester': Mock(is_admin=False),
        }
        self.patch(r53ddns.utils, 'context', context)
        self.assertTrue(r53ddns.utils._is_authenticated())

    def test_is_authenticated_when_not_authenticated(self):
        context = Mock()
        context.request.environ = {}
        self.patch(r53ddns.utils, 'context', context)
        self.assertFalse(r53ddns.utils._is_authenticated())
