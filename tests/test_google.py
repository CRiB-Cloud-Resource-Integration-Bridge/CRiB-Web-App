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
