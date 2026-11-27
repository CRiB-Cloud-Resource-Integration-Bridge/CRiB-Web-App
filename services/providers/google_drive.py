"""Optional read-only Google Drive adapter for dedicated educational test accounts."""
import base64
import hashlib
import json
import re
import time
from io import BytesIO
from urllib.parse import urlencode, quote, urlsplit

import requests
from cryptography.fernet import Fernet, InvalidToken

SCOPE = "https://www.googleapis.com/auth/drive.readonly"
TOKEN_URL = "https://oauth2.googleapis.com/token"
DRIVE_URL = "https://www.googleapis.com/drive/v3/files"
MAX_BYTES = 20 * 1024 * 1024
FIELDS = "id,name,mimeType,parents,modifiedTime,size,trashed,capabilities(canDownload)"
FOLDER = "application/vnd.google-apps.folder"

class GoogleError(Exception):
    """Only user-safe messages should be passed to this exception."""

def http(method, url, **kwargs):
    try:
        return requests.request(method, url, timeout=(5, 25), allow_redirects=False, **kwargs)
    except requests.RequestException:
        raise GoogleError("Google service is temporarily unavailable. Try again.") from None

def payload(response):
    with response:
        if response.status_code == 401:
            raise GoogleError("Google access has expired. Reauthorize from Connected providers.")
        if response.status_code == 403:
            raise GoogleError("Google denied access or a service limit was reached.")
        if response.status_code == 404:
            return None
        if not response.ok or response.is_redirect:
            raise GoogleError("Google could not complete this request. Reauthorize or try again.")
        try:
            return response.json()
        except ValueError:
            raise GoogleError("Google returned an unexpected response.") from None

class OAuthConfig:
    def __init__(self, client_id, client_secret, redirect_uri, key):
        self.client_id, self.client_secret, self.redirect_uri = client_id, client_secret, redirect_uri
        uri = urlsplit(redirect_uri)
        if not (uri.scheme == "https" and uri.hostname or
                uri.scheme == "http" and uri.hostname in ("localhost", "127.0.0.1")):
            raise RuntimeError("GOOGLE_REDIRECT_URI must be HTTPS or localhost HTTP.")
        self.cipher = Fernet(key.encode())

    @classmethod
    def from_config(cls, config):
        vals = [config.get(k) for k in ("GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "GOOGLE_REDIRECT_URI", "CRIB_TOKEN_KEY")]
        if not any(vals):
            return None
        if not all(vals):
            raise RuntimeError("Set all four Google OAuth configuration values, or none.")
        return cls(*vals)

    def encrypt(self, tokens):
        return self.cipher.encrypt(json.dumps(tokens).encode()).decode()

    def decrypt(self, encrypted):
        try:
            return json.loads(self.cipher.decrypt(encrypted.encode()))
        except (InvalidToken, ValueError):
            raise GoogleError("Stored authorization cannot be read. Disconnect and reconnect.") from None

    def authorization_url(self, state, verifier):
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
        return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode({
            "client_id": self.client_id, "redirect_uri": self.redirect_uri,
            "response_type": "code", "scope": SCOPE, "access_type": "offline",
            "prompt": "consent", "state": state, "code_challenge": challenge,
            "code_challenge_method": "S256",
        })

    def exchange(self, code, verifier):
        data = self.token_request({"code": code, "code_verifier": verifier,
                                   "redirect_uri": self.redirect_uri, "grant_type": "authorization_code"})
        if SCOPE not in data.get("scope", "").split():
            raise GoogleError("The required read-only Drive permission was not granted.")
        return data

    def token_request(self, data):
        result = payload(http("POST", TOKEN_URL, data={
            "client_id": self.client_id, "client_secret": self.client_secret, **data}))
        if not result or not result.get("access_token"):
            raise GoogleError("Google authorization failed. Try reconnecting.")
        result["expires_at"] = int(time.time()) + int(result.get("expires_in", 3600))
        return result

    def revoke(self, tokens):
        response = http("POST", "https://oauth2.googleapis.com/revoke",
                        data={"token": tokens.get("refresh_token") or tokens["access_token"]})
        with response:
            if response.status_code != 200:
                raise GoogleError("Google revocation could not be confirmed.")

class GoogleDrive:
    def __init__(self, oauth, tokens, save):
        self.oauth, self.tokens, self.save = oauth, tokens, save

    def headers(self):
        if self.tokens.get("expires_at", 0) <= time.time() + 60:
            refresh = self.tokens.get("refresh_token")
            if not refresh:
                raise GoogleError("Google access expired. Reauthorize from Connected providers.")
            updated = self.oauth.token_request({"refresh_token": refresh, "grant_type": "refresh_token"})
            self.tokens = {**self.tokens, **updated}
            self.save(self.tokens)
        return {"Authorization": "Bearer " + self.tokens["access_token"]}

    @staticmethod
    def normalize(item):
        mime = item.get("mimeType", "")
        kind = "folder" if mime == FOLDER else "file"
        size = int(item["size"]) if item.get("size") else None
        return dict(id=item["id"], name=item.get("name", "Unnamed file"), kind=kind,
                    parent=(item.get("parents") or ["root"])[0],
                    modified=item.get("modifiedTime", "Unavailable")[:10],
                    size=size, provider="Google Drive",
                    downloadable=kind=="file" and not mime.startswith("application/vnd.google-apps.")
                    and bool(item.get("capabilities", {}).get("canDownload"))
                    and (size is None or size<=MAX_BYTES))

    def get(self, ident):
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,200}", ident):
            return None
        item = payload(http("GET", DRIVE_URL + "/" + quote(ident, safe=""),
                            params={"fields": FIELDS}, headers=self.headers()))
        if not item or item.get("trashed"):
            return None
        return self.normalize(item)

    def list(self, folder="root", query="", kind=""):
        def literal(s):
            return s.replace("\\", "\\\\").replace("'", "\\'")
        filters = ["trashed = false"]
        if query:
            filters.append("name contains '" + literal(query) + "'")
        else:
            filters.append("'" + literal(folder) + "' in parents")
        if kind:
            filters.append("mimeType " + ("=" if kind=="folder" else "!=") + " '" + FOLDER + "'")
        params = {"q": " and ".join(filters), "fields": "nextPageToken,files(" + FIELDS + ")",
                  "pageSize": 100, "orderBy": "folder,name", "spaces": "drive"}
        rows = []
        for _ in range(5):
            data = payload(http("GET", DRIVE_URL, params=params, headers=self.headers()))
            if data is None:
                raise GoogleError("Drive resources could not be listed.")
            rows.extend(self.normalize(i) for i in data.get("files", []))
            if not data.get("nextPageToken"):
                break
            params["pageToken"] = data["nextPageToken"]
        return rows

    def download(self, ident):
        item = self.get(ident)
        if not item or not item["downloadable"]:
            raise GoogleError("This resource is unavailable or not permitted for download.")
        response = http("GET", DRIVE_URL + "/" + quote(ident, safe=""),
                        params={"alt": "media"}, headers=self.headers(), stream=True)
        with response:
            if response.status_code != 200:
                raise GoogleError("Google declined the download. Check permissions or reauthorize.")
            buffer = BytesIO()
            try:
                for chunk in response.iter_content(chunk_size=65536):
                    if buffer.tell() + len(chunk) > MAX_BYTES:
                        raise GoogleError("This demo limits downloads to 20 MB.")
                    buffer.write(chunk)
            except requests.RequestException:
                raise GoogleError("Download interrupted. Try again.") from None
        buffer.seek(0)
        return buffer
