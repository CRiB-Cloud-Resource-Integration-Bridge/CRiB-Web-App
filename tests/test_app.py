import re
import tempfile
import unittest
from pathlib import Path
from app import create_app

class AppTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "test-key-not-for-deploy",
                               "DATABASE": str(Path(self.temp.name) / "test.sqlite3")})
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp.cleanup()

    def post(self, client, path, source, **data):
        response = client.get(source)
        token = re.search(rb'name="csrf" value="([^"]+)"', response.data).group(1).decode()
        return client.post(path, data={"csrf": token, **data})

    def signup(self, client, email):
        return self.post(client, "/signup", "/signup", name="Test", email=email, password="Test-password-123")

    def test_journey_and_isolation(self):
        self.assertEqual(self.client.get("/dashboard").status_code, 302)
        self.assertEqual(self.signup(self.client, "one@example.test").status_code, 302)
        self.assertIn(b"No cloud storage connected", self.client.get("/dashboard").data)
        self.assertEqual(self.post(self.client, "/providers/mock/connect", "/providers").status_code, 302)
        self.assertIn(b"Welcome.txt", self.client.get("/files").data)
        self.assertIn(b"Web development notes.txt", self.client.get("/files?folder=1-university").data)
        self.assertIn(b"Project brief.txt", self.client.get("/files?q=brief&kind=file").data)
        self.assertIn(b"No results", self.client.get("/files?q=nonexistent").data)
        download = self.client.get("/files/1-welcome/download")
        self.assertEqual(download.status_code, 200)
        self.assertIn(b"sample data", download.data)
        self.assertIn("attachment", download.headers["Content-Disposition"])
        self.assertEqual(self.client.get("/files/1-restricted/download").status_code, 403)
        other = self.app.test_client()
        self.signup(other, "two@example.test")
        self.assertEqual(other.get("/files/1-welcome/download").status_code, 403)
        self.post(other, "/providers/mock/connect", "/providers")
        self.assertEqual(other.get("/files/1-welcome/download").status_code, 404)
        self.assertEqual(other.get("/files/2-welcome/download").status_code, 200)
        self.post(self.client, "/providers/disconnect", "/providers")
        self.assertEqual(self.client.get("/files/1-welcome/download").status_code, 403)
        self.post(self.client, "/logout", "/dashboard")
        self.assertEqual(self.client.get("/dashboard").status_code, 302)
        self.assertEqual(self.post(self.client, "/signin", "/signin", email="one@example.test", password="Test-password-123").status_code, 302)

    def test_csrf_and_bad_login(self):
        self.assertEqual(self.client.post("/signup", data={}).status_code, 400)
        self.signup(self.client, "one@example.test")
        self.post(self.client, "/logout", "/dashboard")
        response = self.post(self.client, "/signin", "/signin", email="one@example.test", password="wrong")
        self.assertIn(b"Email or password is incorrect", response.data)

if __name__ == "__main__":
    unittest.main()
