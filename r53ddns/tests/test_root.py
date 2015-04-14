import json

from r53ddns.tests.base import Base
import r53ddns.views.root
import r53ddns.utils


class TestRoot(Base):
    def setUp(self):
        super(TestRoot, self).setUp()
        self.root = r53ddns.views.root.RootManager()
        r53ddns.views.root.context = self.context

    def test_root_entrypoint(self):
        res = self.root.index()
        assert res.get_header('content-type') == 'application/json'
        res = json.loads(res.content)
        assert('endpoints' in res and 'documentation' in res)

    def test_ip(self):
        res = self.root.ip()
        ctype = res.get_header('content-type').split(';')[0]
        self.assertEquals(ctype, 'text/html')
        self.assertEquals(res.content.strip(), '127.0.0.1')
