# CRiB Web App

Cloud Resource Integration Bridge — COMP-2002 Web Development.

## Assessment 2 development branch

The existing Penpot-derived interactive prototype remains in `prototype/` and is published separately at https://crib-cloud-resource-integration-bridge.github.io/CRiB-Web-App/. It uses simulated interactions.

This branch adds a Python/Flask application using SQLite, server-rendered HTML and responsive CSS. It implements real CRiB accounts, server-side sessions, a user-scoped demo provider, folder navigation, search/filter, file details, actual sample-file downloads and disconnect. **The demo provider is not Google Drive.** No cloud account is accessed in demo mode. An optional real Google Drive adapter is available when explicitly configured. Use only synthetic credentials and dedicated Google test accounts.

### Local setup (Python 3.11+)

Windows PowerShell:

    py -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    $env:CRIB_SECRET_KEY = (.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))")
    .\.venv\Scripts\python.exe app.py

Linux/macOS:

    python3 -m venv .venv
    .venv/bin/python -m pip install -r requirements.txt
    export CRIB_SECRET_KEY="$(.venv/bin/python -c 'import secrets; print(secrets.token_hex(32))')"
    .venv/bin/python app.py

Open http://127.0.0.1:8000. Create a test account and connect Demo storage. Save the secret securely between restarts; never commit it.

### Tests

    python -m unittest discover -s tests -v

### Deployment

GitHub Pages hosts only the original static prototype, not Flask. For a live demo use a Python web host or a dedicated server running Waitress behind an HTTPS reverse proxy. Set a strong persistent CRIB_SECRET_KEY, CRIB_HTTPS=1 and CRIB_DATABASE to a persistent writable file outside the repository. Start with:

    waitress-serve --listen=127.0.0.1:8000 --call app:create_app

For managed hosting, use the platform's required listen address and PORT. Do not expose the Flask development server to the internet. Public deployment, live Google authorization, browser testing, and final team review remain separate tasks.

### Structure

- app.py: routes, validation, authentication and session management
- database/schema.sql: relational schema
- services/providers/mock.py: provider adapter
- templates/app.html and static/css/mvp.css: working interface
- tests/test_app.py: integration checks
- prototype/: preserved Assessment 1 demonstration
- docs/working-docs/: original requirements and architecture

### Optional real Google Drive integration (educational test mode)

1. At https://console.cloud.google.com/ create or select a project and enable the Google Drive API.
2. In Google Auth Platform configure Branding, Audience (External, Testing) and add a dedicated Google test account. Configure the read-only Drive scope: https://www.googleapis.com/auth/drive.readonly. This is a restricted scope; do not publish for general users or connect personal or sensitive files.
3. Create an OAuth client of type Web application. Add the exact authorized redirect URI: http://127.0.0.1:8000/oauth/google/callback for local development. For deployment, use the actual HTTPS app URL with the same callback path.
4. Set GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI, and CRIB_TOKEN_KEY in the process environment. Generate the encryption key locally with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`. Store it persistently and privately. Never commit secrets, paste them in chat, or include them in screenshots.
5. Restart the app, register a CRiB test account, and select Connected providers → Connect Google Drive. If demo storage is active, disconnect it first.
6. In the Google test account, upload a small TXT/PDF, create a folder, and verify listing, search, folder navigation, download, disconnect and reauthorization. Google-native Docs/Sheets/Slides exports, shared-drive completeness, large downloads, and full pagination are not implemented. Results are capped at 500, individual downloads at 20 MB. The mock provider remains available if OAuth is not configured.
7. Only declare live integration verified after completing these steps. Google test-mode grants may expire; reconnect if needed.

References: https://developers.google.com/identity/protocols/oauth2/web-server and https://developers.google.com/workspace/drive/api/guides/api-specific-auth.

OAuth state and PKCE verifier are stored server-side, bound to the current session, consumed once and expire after ten minutes. Python must use SQLite 3.35+ for the atomic callback operation (standard on the supported CI runtime).
