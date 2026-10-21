import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from app.ui_config import public_ui_config


class UiConfigurationTests(unittest.TestCase):
    def test_default_and_explicit_versions(self):
        self.assertEqual(public_ui_config({}), {"ux_version": 1})
        for version in (1, 2):
            self.assertEqual(public_ui_config({"ux_version": version}), {"ux_version": version})

    def test_rejects_invalid_values_including_boolean(self):
        for value in (None, True, False, 0, 3, "2", 2.0, [], {}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                public_ui_config({"ux_version": value})

    def test_only_allowlisted_configuration_is_public(self):
        self.assertEqual(public_ui_config({"ux_version": 2, "security": {"secret_key": "private"}, "auth": {"ldap": {"bind_password": "private"}}}), {"ux_version": 2})

    def test_api_and_ldap_permissions_for_both_versions(self):
        # Import the application in isolated processes: no real configuration,
        # database, directory service, or stored artifacts are touched.
        repo = Path(__file__).resolve().parents[1]
        script = '''
import sys
from unittest.mock import patch
sys.path.insert(0, sys.argv[1])
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app.auth.security import create_access_token
client = TestClient(app)
response = client.get('/ui-config')
assert response.status_code == 200
assert response.json() == {'ux_version': settings.get('ux_version', 1)}
assert response.headers['cache-control'] == 'no-store'
assert client.get('/me').status_code == 401
assert client.get('/public/license-summary').status_code == 200
with patch('app.api.auth.authenticate_ldap', return_value={'username': 'directory-user', 'role': 'manager'}) as ldap:
    result = client.post('/login', json={'username': 'directory-user', 'password': 'test-only'})
    assert result.status_code == 200
    ldap.assert_called_once_with('directory-user', 'test-only')
    identity = client.get('/me', headers={'Authorization': 'Bearer ' + result.json()['access_token']})
    assert identity.json()['sub'] == 'directory-user'
    assert identity.json()['role'] == 'manager'
with patch('app.api.auth.authenticate_ldap', return_value=None):
    assert client.post('/login', json={'username': 'bad', 'password': 'bad'}).status_code == 401
for role in ('user', 'manager', 'admin'):
    headers = {'Authorization': 'Bearer ' + create_access_token({'sub': 'test', 'role': role})}
    assert client.get('/license-servers', headers=headers).status_code == 200
    assert client.get('/audit-events', headers=headers).status_code == (200 if role == 'admin' else 403)
    if role == 'user':
        assert client.post('/content/publish', headers=headers).status_code == 403
        assert client.post('/license-files/import', headers=headers).status_code == 403
    if role != 'admin':
        assert client.delete('/deployments/999', headers=headers).status_code == 403
        assert client.post('/license-servers', json={'name': 'blocked'}, headers=headers).status_code == 403
'''
        for version in (None, 1, 2):
            with self.subTest(version=version), tempfile.TemporaryDirectory() as directory:
                config = {
                    "auth": {"provider": "ldap"},
                    "database": {"url": "sqlite:///test.db"},
                    "security": {"secret_key": "test-key-only-32-characters-long", "algorithm": "HS256", "access_token_minutes": 10},
                }
                if version is not None:
                    config["ux_version"] = version
                path = Path(directory) / "config"
                path.mkdir()
                (path / "portal.yaml").write_text(json.dumps(config))
                result = subprocess.run([sys.executable, "-c", script, str(repo)], cwd=directory, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
