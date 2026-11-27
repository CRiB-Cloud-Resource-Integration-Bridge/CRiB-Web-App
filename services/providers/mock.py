"""Deterministic, per-user sample resources. Never contacts a cloud service."""
from io import BytesIO

SAMPLES = (
    ("university", "University", "folder", "root", None),
    ("projects", "Projects", "folder", "root", None),
    ("welcome", "Welcome.txt", "file", "root", "Welcome to CRiB. This is sample data, not a Google Drive file.\n"),
    ("notes", "Web development notes.txt", "file", "university", "COMP-2002: HTML, CSS, JavaScript and server-side development.\n"),
    ("brief", "Project brief.txt", "file", "projects", "CRiB: connect, browse, search and download.\n"),
    ("restricted", "Restricted sample.txt", "file", "projects", None),
)

class MockProvider:
    def __init__(self, user_id):
        self.items = {}
        for key, name, kind, parent, content in SAMPLES:
            ident = f"{user_id}-{key}"
            self.items[ident] = dict(id=ident, name=name, kind=kind,
                parent="root" if parent == "root" else f"{user_id}-{parent}",
                modified="2026-11-27", provider="Demo storage (mock)",
                downloadable=content is not None, size=len(content.encode()) if content else None,
                content=content)

    def get(self, ident):
        return self.items.get(ident)

    def list(self, folder="root", query="", kind=""):
        return sorted((item for item in self.items.values()
                       if (query or item["parent"] == folder)
                       and query.casefold() in item["name"].casefold()
                       and (not kind or item["kind"] == kind)),
                      key=lambda x: (x["kind"] != "folder", x["name"].casefold()))

    def download(self, ident):
        item = self.get(ident)
        if not item or not item["downloadable"]:
            raise PermissionError("Download unavailable")
        return BytesIO(item["content"].encode())
