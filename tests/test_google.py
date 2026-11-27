import time
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit
from cryptography.fernet import Fernet
from services.providers.google_drive import OAuthConfig, GoogleDrive, SCOPE, GoogleError

class GoogleAdapterTest(unittest.TestCase):
    def setUp(self):
        self.config = OAuthConfig("test-client", "test-secret", "http://127.0.0.1:8000/oauth/google/callback", Fernet.generate_key().decode())

    def test_oauth_state_and_pkce_and_encryption(self):
        query = parse_qs(urlsplit(self.config.authorization_url("random-state", "test-verifier")).query)
        self.assertEqual(query["state"], ["random-state"])
        self.assertEqual(query["scope"], [SCOPE])
        self.assertEqual(query["code_challenge_method"], ["S256"])
        self.assertNotIn("test-secret", str(query))
        encrypted = self.config.encrypt({"access_token": "private-token"})
        self.assertNotIn("private-token", encrypted)
        self.assertEqual(self.config.decrypt(encrypted)["access_token"], "private-token")

    def test_permissions_and_size(self):
        base = {"id":"abc", "name":"File", "mimeType":"text/plain", "capabilities":{"canDownload":True}}
        self.assertTrue(GoogleDrive.normalize(base)["downloadable"])
        self.assertFalse(GoogleDrive.normalize({**base, "size": str(21*1024*1024)})["downloadable"])
        self.assertFalse(GoogleDrive.normalize({**base, "mimeType":"application/vnd.google-apps.document"})["downloadable"])
        self.assertFalse(GoogleDrive.normalize({**base, "capabilities":{"canDownload":False}})["downloadable"])

    def test_refresh(self):
        saved = []
        adapter = GoogleDrive(self.config, {"access_token":"old","refresh_token":"refresh","expires_at":0}, saved.append)
        with patch.object(self.config, "token_request", return_value={"access_token":"new","expires_at":int(time.time())+3600}):
            self.assertEqual(adapter.headers()["Authorization"], "Bearer new")
        self.assertEqual(saved[0]["refresh_token"], "refresh")

class GoogleRouteTest(unittest.TestCase):
    def setUp(self):
        import tempfile
        from pathlib import Path
        from app import create_app
        self.temp = tempfile.TemporaryDirectory()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "test-key-not-for-deploy",
                               "DATABASE": str(Path(self.temp.name) / "test.sqlite3"),
                               "GOOGLE_CLIENT_ID":"test-client", "GOOGLE_CLIENT_SECRET":"test-secret",
                               "GOOGLE_REDIRECT_URI":"http://127.0.0.1:8000/oauth/google/callback",
                               "CRIB_TOKEN_KEY":Fernet.generate_key().decode()})
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp.cleanup()

    def post(self, client, path, source, **data):
        import re
        token = re.search(rb'name="csrf" value="([^"]+)"', client.get(source).data).group(1).decode()
        return client.post(path, data={"csrf":token, **data})

    def test_callback_single_use_and_session_binding(self):
        self.assertEqual(self.client.post("/signup",data={"csrf":"-"}).status_code,400)
        self.post(self.client,"/signup","/signup",name="A",email="a@example.test",password="Test-password-123")
        result = self.post(self.client,"/providers/google/connect","/providers")
        state = parse_qs(urlsplit(result.location).query)["state"][0]
        other = self.app.test_client()
        self.post(other,"/signup","/signup",name="B",email="b@example.test",password="Test-password-123")
        path = "/oauth/google/callback?state="+state+"&code=example"
        self.assertEqual(other.get(path).status_code,400)
        self.assertEqual(self.client.get("/oauth/google/callback?state=wrong&code=example").status_code,400)
        with patch.object(OAuthConfig,"exchange",return_value={"access_token":"fake-token","expires_at":int(time.time())+3600}) as exchange:
            self.assertEqual(self.client.get(path).status_code,302)
            self.assertEqual(self.client.get(path).status_code,400)
            exchange.assert_called_once()
        self.assertIn(b"Google Drive is connected",self.client.get("/dashboard").data)
        self.assertIn(b"No cloud storage connected",other.get("/dashboard").data)
        with patch.object(OAuthConfig,"revoke"):
            self.post(self.client,"/providers/disconnect","/providers")
        self.assertIn(b"No cloud storage connected",self.client.get("/dashboard").data)
