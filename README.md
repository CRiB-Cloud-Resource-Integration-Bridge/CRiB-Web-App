# CRiB Web App

Cloud Resource Integration Bridge — COMP-2002 Web Development.

## Assessment 2 development branch

The existing Penpot-derived interactive prototype remains in `prototype/` and is published separately at https://crib-cloud-resource-integration-bridge.github.io/CRiB-Web-App/. It uses simulated interactions.

This branch adds a Python/Flask application using SQLite, server-rendered HTML and responsive CSS. It implements real CRiB accounts, server-side sessions, a user-scoped demo provider, folder navigation, search/filter, file details, actual sample-file downloads and disconnect. **The demo provider is not Google Drive.** No real cloud account is accessed. Use only synthetic credentials and sample data.

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

For managed hosting, use the platform's required listen address and PORT. Do not expose the Flask development server to the internet. Real-provider authorization, public deployment, browser testing, and final team review remain separate tasks.

### Structure

- app.py: routes, validation, authentication and session management
- database/schema.sql: relational schema
- services/providers/mock.py: provider adapter
- templates/app.html and static/css/mvp.css: working interface
- tests/test_app.py: integration checks
- prototype/: preserved Assessment 1 demonstration
- docs/working-docs/: original requirements and architecture
