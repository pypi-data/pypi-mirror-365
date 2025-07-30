

import pytest
from odoo_connector.api import OdooConnector

class FakeServer:
    def __init__(self):
        self.data = {}

    def authenticate(self, db, user, pwd, _):
        return 1  # fake UID

    def version(self):
        return {'server_version': '17.0'}

    def execute_kw(self, db, uid, pwd, model, method, args, kwargs=None):
        return f"{method} called on {model} with {args} and {kwargs}"

@pytest.fixture
def connector(monkeypatch):
    monkeypatch.setattr('xmlrpc.client.ServerProxy', lambda url: FakeServer())
    return OdooConnector('http://fakeurl', 'fake_db', 'user', 'pass')

def test_authentication(connector):
    assert connector.uid == 1

def test_get_version(connector):
    version = connector.get_version()
    assert version['server_version'] == '17.0'

def test_read_method(connector):
    response = connector.read('res.partner', fields=['name'])
    assert 'search_read' in response
